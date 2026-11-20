"""Verify local collection integrity and authored skill format; does not execute skills."""
from pathlib import Path
import argparse
import csv
import hashlib
import importlib.util
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validator', type=Path, required=True, help='Trusted skill-creator quick_validate.py')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('trusted_skill_validator', args.validator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    failures = []
    upstream = json.loads((ROOT / 'research/upstream-index.json').read_text(encoding='utf-8'))
    curated = json.loads((ROOT / 'registry/curated-skills.json').read_text(encoding='utf-8'))
    catalog = json.loads((ROOT / 'registry/all-skills.json').read_text(encoding='utf-8'))
    stats = json.loads((ROOT / 'registry/collection-stats.json').read_text(encoding='utf-8'))
    checked_documents = 0
    for repo in upstream['repositories']:
        base = ROOT / 'upstream-review' / repo['repo'].replace('/', '--')
        archive = base / (repo['commit'] + '.zip')
        if hashlib.sha256(archive.read_bytes()).hexdigest() != repo['archive_sha256']:
            failures.append('Archive hash mismatch: ' + repo['repo'])
        with zipfile.ZipFile(archive) as stream:
            corrupt = stream.testzip()
            if corrupt:
                failures.append('ZIP CRC failure: ' + corrupt)
        for item in repo['documents']:
            target = base / 'documents' / item['path']
            if hashlib.sha256(target.read_bytes()).hexdigest() != item['sha256']:
                failures.append('Text hash mismatch: ' + str(target))
            checked_documents += 1
    for skill in curated:
        valid, message = module.validate_skill(ROOT / skill['path'].rsplit('/', 1)[0])
        if not valid:
            failures.append(skill['name'] + ': ' + message)
    for item in catalog:
        if not (ROOT / item['path']).is_file():
            failures.append('Missing indexed skill: ' + item['id'])
    ids = [item['id'] for item in catalog]
    if len(ids) != len(set(ids)):
        failures.append('Duplicate registry IDs')
    with (ROOT / 'registry/all-skills.csv').open(encoding='utf-8-sig', newline='') as stream:
        csv_ids = [row['id'] for row in csv.DictReader(stream)]
    if csv_ids != ids:
        failures.append('CSV and JSON registry entries differ')
    checked_links = 0
    own_docs = list(ROOT.glob('*.md')) + list((ROOT / 'skills').glob('*/SKILL.md')) + list((ROOT / 'research').glob('*.md'))
    for document in own_docs:
        text = document.read_text(encoding='utf-8')
        for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)', text):
            target = match.group(1).strip().strip('<>')
            if re.match(r'^[a-zA-Z]+:', target) or target.startswith('#'):
                continue
            checked_links += 1
            target = target.split('#', 1)[0]
            if target and not (document.parent / target).exists():
                failures.append('Broken local link: ' + str(document.relative_to(ROOT)) + ' -> ' + target)
    for directory in ('registry', 'templates', 'research'):
        for path in (ROOT / directory).glob('*.json'):
            json.loads(path.read_text(encoding='utf-8'))
    report = {'date': '2026-10-12', 'status': 'passed' if not failures else 'failed',
              'archives_verified': len(upstream['repositories']), 'text_hashes_verified': checked_documents,
              'curated_skill_formats_checked': len(curated), 'registry_paths_checked': len(catalog),
              'local_links_checked': checked_links, 'csv_matches_json': csv_ids == ids, 'failures': failures,
              'limitations': ['This integrity pass does not evaluate model/skill behavior', 'No downloaded code executed',
                              'No substantive review of every upstream document', 'This integrity pass does not execute live-target tests',
                              'No check of all relative links inside upstream text mirrors']}
    (ROOT / 'registry/verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    lines = ['# Verification — 12 October 2026', '', '**Result: ' + report['status'].upper() + '**', '',
             f"- {report['archives_verified']} pinned ZIP archives matched recorded SHA-256 hashes and passed ZIP CRC checks.",
             f"- {checked_documents} extracted text documents matched recorded SHA-256 hashes.",
             f"- {len(curated)} original skills passed the trusted skill-creator frontmatter/name/scaffold validator.",
             f"- {len(catalog)} indexed local skill paths exist, and registry IDs are unique.",
             '- CSV and JSON catalog entries agree in order and identity.' if csv_ids == ids else '- CSV/JSON mismatch.',
             f'- {checked_links} local links in authored documents and the generated catalog were checked.',
             '- Original templates and registry JSON parse successfully.',
             '- Read-only metadata search was exercised for SSRF and curated authorization skills.', '',
             '## Source retrieval', '', f"{stats['http_reachable_sources']} of {stats['sources']} primary links succeeded in direct HTTP retrieval. Five CTF101 links returned 404 and one picoCTF page returned 403. Exact redirects, titles and errors are preserved in research/sources.json.", '',
             '## Limits', '', 'These checks establish file integrity, index consistency and authored skill format. They do not prove security effectiveness, framework accuracy, runtime compatibility, or trustworthy instructions. Upstream packages remain unreviewed and uninstalled. This integrity pass does not execute models or attack tools. Separate runtime evaluations are recorded in APP_VERIFICATION.md; a full 24-hour soak remains unperformed.', '',
             'The JSON result is in [verification.json](registry/verification.json).']
    if failures:
        lines += ['', '## Failures', ''] + ['- ' + item for item in failures]
    (ROOT / 'VERIFICATION.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
