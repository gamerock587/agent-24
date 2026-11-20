"""Readable views of recorded model messages; never a second model summary."""
import json


def decoded(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            pass
    return value


def prose(value, depth=0):
    value = decoded(value)
    if isinstance(value, dict):
        return '\n\n'.join(str(k).replace('_', ' ').capitalize() + ':\n' + prose(v, depth + 1) for k, v in value.items())
    if isinstance(value, list):
        return '\n'.join('• ' + prose(v, depth + 1) for v in value) or '(empty)'
    return str(value) if value is not None else '(none)'


def exchange(row):
    request = decoded(row.get('input')) or {}
    response = decoded(row.get('output')) or {}
    sent = []
    if request.get('system_prompt'):
        sent.append({'label': 'Instructions', 'text': request['system_prompt']})
    for message in request.get('messages', []):
        sent.append({'label': str(message.get('role', 'message')).capitalize(), 'text': prose(message.get('content', ''))})
    if 'input' in request:
        context=decoded(request['input'])
        conversation=context.get('conversation') if isinstance(context,dict) else None
        if isinstance(conversation,list) and conversation:
            sent.append({'label':'Latest message','text':prose(conversation[-1].get('content',''))})
            if len(conversation)>1:
                sent.append({'label':'Conversation history sent','text':'\n\n'.join(str(m.get('role','message')).capitalize()+': '+prose(m.get('content','')) for m in conversation[:-1]),'collapsed':True})
            background={k:v for k,v in context.items() if k!='conversation'}
            if background:sent.append({'label':'Assessment context sent','text':prose(background),'collapsed':True})
        else:sent.append({'label': 'Message & context', 'text': prose(context)})
    if 'questions' in request:
        sent.append({'label': 'Decision request', 'text': prose(request['questions'])})
        sent.append({'label': 'Observed context', 'text': prose(request.get('state', {}))})
    body = decoded(response.get('body', response))
    received = []
    if isinstance(body, dict):
        for message in body.get('output', []):
            if message.get('type') == 'message':
                received.append(prose(message.get('content', '')))
        for choice in body.get('choices', []):
            received.append(prose(choice.get('message', {}).get('content', '')))
        if 'answers' in body:
            received.append(prose(body['answers']))
    if not received and body:
        received.append(prose(body))
    return {'sent': sent or [{'label': 'Request', 'text': prose(request)}], 'received': '\n\n'.join(received)}
