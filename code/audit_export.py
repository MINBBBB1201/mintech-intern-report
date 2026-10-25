"""Check export structure and declared data categories using the standard library."""
import ast
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROHIBITED_SUFFIXES = {'.xlsx', '.docx', '.pem', '.key', '.jpg', '.jpeg', '.png'}
PROHIBITED_PARTS = {'_internal', 'applications_2027', 'research_notes', 'submission'}
SECRET_PATTERNS = [
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'[A-Za-z]:[\\/]Users[\\/][^\s"\']+'),
]


def main():
    reviewed = 0
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(part in {'.git', '.validation', '__pycache__'} for part in path.relative_to(ROOT).parts):
            continue
        relative = path.relative_to(ROOT)
        assert not PROHIBITED_PARTS.intersection(relative.parts), str(relative)
        assert path.suffix.lower() not in PROHIBITED_SUFFIXES, str(relative)
        if path.name.startswith('.env'):
            raise AssertionError('Environment file in export')
        if path.suffix in {'.md', '.py', '.json', '.csv', '.svg', '.txt', '.yml'}:
            text = path.read_text(encoding='utf-8-sig')
            for pattern in SECRET_PATTERNS:
                assert not pattern.search(text), f'Sensitive pattern in {relative}'
            if path.suffix == '.py':
                ast.parse(text)
            if path.suffix == '.md':
                for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
                    if not target.startswith(('http://', 'https://', '#')):
                        assert (path.parent/target.split('#')[0]).exists(), f'Broken link in {relative}: {target}'
        reviewed += 1
    with (ROOT/'templates/field_records.csv').open(encoding='utf-8-sig', newline='') as stream:
        assert not list(csv.DictReader(stream)), 'Field template contains observations'
    results = json.loads((ROOT/'outputs/software_validation/test_results.json').read_text(encoding='utf-8'))
    assert results['evidence_status'] == 'SOFTWARE_TEST'
    assert results['case_count'] == results['passed'] == 55 and results['failed'] == 0
    for filename, key in [('record_validation.py', 'validator_sha256'), ('verify_records.py', 'verification_script_sha256')]:
        digest = hashlib.sha256((ROOT/'code'/filename).read_bytes()).hexdigest()
        assert digest == results[key], f'Stale saved results: {filename}'
    fonts = json.loads((ROOT/'assets/fonts/sources.json').read_text(encoding='utf-8'))
    for item in fonts:
        digest = hashlib.sha256((ROOT/'assets/fonts'/item['file']).read_bytes()).hexdigest()
        assert digest == item['sha256'], f'Font or license differs from source manifest: {item["file"]}'
    print(f'Export structure and evidence checks passed: {reviewed} files')


if __name__ == '__main__':
    main()
