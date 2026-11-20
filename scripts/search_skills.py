"""Read-only metadata search. Does not load instructions or execute skill tools."""
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='+')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--curated', action='store_true')
    args = parser.parse_args()
    words = [word.lower() for word in ' '.join(args.query).split()]
    items = json.loads((ROOT / 'registry/all-skills.json').read_text(encoding='utf-8'))
    matches = []
    for item in items:
        if args.curated and item['repo'] != 'Agent 24 original drafts':
            continue
        text = ' '.join(str(item.get(key, '')) for key in ('name', 'description', 'declared_domain', 'path')).lower()
        if all(word in text for word in words):
            score = sum(3 if word in item['name'].lower() else 1 for word in words)
            matches.append((score, item))
    for _, item in sorted(matches, key=lambda row: (-row[0], row[1]['id']))[:max(1, args.limit)]:
        print(item['id'])
        print('  ' + item['description'][:300])
        print('  ' + item['path'])
        print('  status: ' + item['status'])
    print(f'{len(matches)} matching documents. Nothing was executed or activated.')

if __name__ == '__main__':
    main()
