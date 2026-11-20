"""Autonomous mission loop: observe, hypothesize, test, learn, repeat.

Each call to assess() runs one evidence-driven cycle.  After every cycle the
loop reads what the assessment found, asks Qwen to synthesise hypotheses and
concrete next-cycle objectives, persists that state in the agent_state table and
then returns.  missions.py tick() re-queues the run on the configured schedule;
the saved state is loaded at the start of the next cycle so each run benefits
from every previous one.
"""

import asyncio
import json
import re
import time
from urllib.parse import urlsplit

from .model_trace import trace_context
from .store import canonical, uid

# ── schema for the JSON blob in agent_state.state ──────────────────────────
_BLANK_STATE: dict = {
    'version': 2,
    'hypotheses': [],       # [{id, description, status, cycle_proposed}]
    'gaps': [],             # [{area, tool, reason, cycle}]
    'cycle_objectives': [], # [str] injected into planning at cycle start
    'insights': [],         # confirmed patterns (from confirmed findings)
    'surface': {},          # host -> {findings: [], observations: []}
}


def _load(engine, mission_id: str) -> dict:
    rows = engine.store.rows(
        'SELECT state FROM agent_state WHERE mission_id=?', (mission_id,)
    )
    if rows:
        try:
            return json.loads(rows[0]['state'])
        except Exception:
            pass
    return dict(_BLANK_STATE)


def _save(engine, mission_id: str, state: dict) -> None:
    state['updated'] = time.time()
    engine.store.execute(
        'INSERT OR REPLACE INTO agent_state(mission_id,state,updated) VALUES(?,?,?)',
        (mission_id, canonical(state), time.time()),
    )


# ── main entry point ────────────────────────────────────────────────────────

async def assess(engine, ident: str, worker: str):
    """Run one autonomous evidence-driven cycle and persist the learned state."""
    run = engine.store.run(ident)
    spec = dict(run['spec'])
    mission_id = spec.get('mission_id') or ident
    spec['mission_id'] = mission_id
    # Clear the flag so _assess / deep_assess don't recurse back here.
    spec['autonomous'] = False
    engine.store.execute('UPDATE runs SET spec=? WHERE id=?', (canonical(spec), ident))

    state = _load(engine, mission_id)
    cycle_row = engine.store.rows('SELECT cycles FROM missions WHERE id=?', (mission_id,))
    cycle_num = cycle_row[0]['cycles'] if cycle_row else 1

    # Announce the cycle with context from prior cycles.
    engine.store.event(
        ident, 'mission',
        f'Autonomous cycle {cycle_num}: '
        f'{len(state["hypotheses"])} hypothesis(es), '
        f'{len(state["gaps"])} known gap(s), '
        f'{len(state["cycle_objectives"])} saved objective(s).',
        {
            'mission_id': mission_id,
            'cycle': cycle_num,
            'objectives': state['cycle_objectives'][:6],
            'hypotheses': [h['description'] for h in state['hypotheses'][-4:]],
        },
    )

    if state['cycle_objectives']:
        engine.store.event(
            ident, 'plan',
            'Saved objectives for this cycle: ' +
            '; '.join(o[:100] for o in state['cycle_objectives'][:4]),
            {'source': 'mission-memory', 'objectives': state['cycle_objectives']},
        )

    # ── run the assessment ──────────────────────────────────────────────────
    try:
        if spec.get('deep', True):
            from .deep_assessment import assess as _deep
            await _deep(engine, ident, worker)
        else:
            await engine._assess(ident, worker)
    except Exception:
        # Record failure but still update mission state so the next cycle
        # knows what went wrong; missions.py applies a backoff delay.
        try:
            detail = engine.store.detail(ident)
            await _post_cycle(engine, ident, mission_id, state, cycle_num, detail)
        except Exception:
            pass
        # Schedule the next cycle; the worker's finally block won't do it
        # because autonomous=False was saved to the DB to prevent recursion.
        try:
            from .missions import finished as _mission_finished
            _mission_finished(engine, ident)
        except Exception:
            pass
        raise

    # ── post-cycle learning ─────────────────────────────────────────────────
    detail = engine.store.detail(ident)
    await _post_cycle(engine, ident, mission_id, state, cycle_num, detail)
    # Hand lifecycle back to missions so the next cycle is scheduled properly.
    try:
        from .missions import finished as _mission_finished
        _mission_finished(engine, ident)
    except Exception:
        pass
    return engine.store.run(ident)


# ── post-cycle: update mission state ───────────────────────────────────────

async def _post_cycle(engine, ident, mission_id, state, cycle_num, detail):
    coverage = detail.get('coverage') or {}

    # Always seed the target host so surface is populated even on short cycles.
    target_host = urlsplit(detail.get('url', '')).hostname
    if target_host:
        state['surface'].setdefault(target_host, {'findings': [], 'observations': []})

    # Update surface map for each host that the deep crawler reported.
    for host in coverage.get('hosts', []):
        state['surface'].setdefault(host, {'findings': [], 'observations': []})

    # Carry findings into the surface map; confirmed findings become insights.
    # Also pull confirmed findings from the entire mission history so manually
    # injected findings (from direct analysis) are never lost by a cycle save.
    run_domain = detail.get('domain', '')
    all_confirmed = engine.store.rows(
        "SELECT f.title, f.endpoint FROM findings f "
        "JOIN runs r ON f.run_id = r.id "
        "WHERE r.domain = ? AND f.status = 'confirmed'",
        (run_domain,)
    )
    for row in all_confirmed:
        if row['title'] not in state['insights']:
            state['insights'].append(row['title'])

    for f in detail.get('findings', []):
        ep = f.get('endpoint', '')
        host = urlsplit(ep).hostname if ep else ''
        if host and host in state['surface']:
            titles = [x['title'] for x in state['surface'][host]['findings']]
            if f['title'] not in titles:
                state['surface'][host]['findings'].append({
                    'title': f['title'],
                    'status': f['status'],
                    'severity': f.get('severity', ''),
                    'cycle': cycle_num,
                })

    # Record tool failures as gaps the next cycle may address.
    for a in detail.get('actions', []):
        if a['status'] == 'failed':
            gap = {
                'area': a.get('url', ''),
                'tool': a.get('tool', ''),
                'reason': 'tool-failed',
                'cycle': cycle_num,
            }
            key = (gap['area'], gap['tool'])
            if not any((g.get('area'), g.get('tool')) == key for g in state['gaps']):
                state['gaps'].append(gap)

    # Record budget-exhausted frontiers so the next cycle can continue them.
    if coverage.get('frontier_remaining', 0) > 0:
        state['gaps'].append({
            'area': 'crawl-frontier',
            'count': coverage['frontier_remaining'],
            'reason': 'budget-exhausted',
            'cycle': cycle_num,
        })
    if coverage.get('tests_remaining', 0) > 0:
        state['gaps'].append({
            'area': 'endpoint-tests',
            'count': coverage['tests_remaining'],
            'reason': 'budget-exhausted',
            'cycle': cycle_num,
        })
    # Keep gap history bounded.
    state['gaps'] = state['gaps'][-60:]

    # Ask Qwen to synthesise hypotheses and plan the next cycle.
    if detail.get('actions'):
        await _synthesise(engine, ident, mission_id, state, detail, cycle_num)

    _save(engine, mission_id, state)
    engine.store.event(
        ident, 'mission',
        f'Cycle {cycle_num} state saved: '
        f'{len(state["hypotheses"])} hypothesis(es), '
        f'{len(state["gaps"])} gap(s), '
        f'{len(state["cycle_objectives"])} objective(s) for next cycle, '
        f'{len(state["insights"])} confirmed insight(s).',
        {
            'mission_id': mission_id,
            'hypotheses': len(state['hypotheses']),
            'gaps': len(state['gaps']),
            'objectives': state['cycle_objectives'],
            'insights': state['insights'][-10:],
            'surface_hosts': list(state['surface'].keys()),
        },
    )


# ── Qwen synthesis: hypotheses + next-cycle objectives ─────────────────────

async def _synthesise(engine, ident, mission_id, state, detail, cycle_num):
    coverage = detail.get('coverage') or {}
    context = {
        'mission_id': mission_id,
        'cycle': cycle_num,
        'target': detail['url'],
        'findings': [
            {'title': f['title'], 'status': f['status'], 'endpoint': f.get('endpoint', '')}
            for f in detail.get('findings', [])
        ],
        'coverage': {
            'hosts': coverage.get('hosts', []),
            'pages_fetched': coverage.get('pages_fetched', 0),
            'frontier_remaining': coverage.get('frontier_remaining', 0),
            'tests_remaining': coverage.get('tests_remaining', 0),
            'stop_reason': coverage.get('stop_reason', ''),
        },
        'gaps': [
            {'area': g.get('area', ''), 'reason': g.get('reason', '')}
            for g in state['gaps'][-8:]
        ],
        'prior_hypotheses': [
            {'description': h['description'], 'status': h['status']}
            for h in state['hypotheses'][-5:]
        ],
        'insights': state['insights'][-6:],
        'failed_tools': [
            a.get('tool') for a in detail.get('actions', []) if a['status'] == 'failed'
        ],
    }

    try:
        with trace_context(engine.store, ident, 'mission-synthesis'):
            raw = await asyncio.wait_for(
                engine.models.generate(
                    'You are a security assessment planner reviewing evidence from one cycle '
                    'of an ongoing mission. Output ONLY valid JSON, nothing else:\n'
                    '{"hypotheses":["<under 100 chars each, max 3>"],'
                    '"objectives":["<specific: endpoint + technique, max 3>"]}\n'
                    'Base everything on the supplied recorded evidence. '
                    'Do not invent findings or claim access that is not recorded.',
                    context,
                    limit=350,
                    raw=True,
                ),
                25.0,
            )
        if not isinstance(raw, str):
            return
        match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            return
        parsed = json.loads(match.group())
        new_hyps = [h for h in parsed.get('hypotheses', []) if isinstance(h, str)][:3]
        new_objs = [o for o in parsed.get('objectives', []) if isinstance(o, str)][:3]

        existing_desc = {h['description'] for h in state['hypotheses']}
        for h in new_hyps:
            if h not in existing_desc:
                state['hypotheses'].append({
                    'id': uid(),
                    'description': h[:200],
                    'status': 'proposed',
                    'cycle_proposed': cycle_num,
                })
        # Keep hypothesis list bounded.
        state['hypotheses'] = state['hypotheses'][-30:]
        state['cycle_objectives'] = new_objs

        engine.store.event(
            ident, 'mission',
            f'Mission synthesis: {len(new_hyps)} new hypothesis(es), '
            f'{len(new_objs)} objective(s) queued for the next cycle.',
            {'hypotheses': new_hyps, 'objectives': new_objs},
        )
    except (asyncio.TimeoutError, json.JSONDecodeError):
        # Model unavailable or non-JSON output — objectives stay from last cycle.
        engine.store.event(
            ident, 'model_error',
            'Mission synthesis skipped (model timeout or non-JSON output). '
            'Prior objectives retained.',
            {'mission_id': mission_id},
        )
    except Exception as exc:
        engine.store.event(
            ident, 'model_error',
            f'Mission synthesis failed: {type(exc).__name__}: {str(exc)[:200]}',
            {'mission_id': mission_id},
        )
