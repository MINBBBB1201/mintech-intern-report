"""Reproducible fault-injection verification; every fixture is SOFTWARE_TEST."""
from __future__ import annotations

import argparse
from copy import deepcopy
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from record_validation import FIELDS, validate_records


def fixtures():
    rows = []
    # Two opposite range differences avoid building an apparent improvement into the example.
    for pair, orders, thicknesses in (
        ('TEST-AB', (1, 2), ((100, 103, 106), (100, 102, 104))),
        ('TEST-BA', (2, 1), ((100, 104, 108), (100, 105, 110))),
    ):
        for method, order, values in zip(('A', 'B'), orders, thicknesses):
            for point, thickness in enumerate(values, 1):
                values_by_field = [
                    f'{pair}-{method}-{point}', '2000-01-01', method, order, 'TEST-BLOCK', pair,
                    f'TEST-CARRIER-{method}', 'PASS', 'PASS', 'PASS', 0, 0, 0, 'TEST-RECIPE',
                    f'TEST-COUPON-{method}', 0, 0, 0, 0, 0, 'TEST-TOOL', f'P{point}',
                    thickness, 'SOFTWARE', 'SOFTWARE_TEST', 'Programmatically constructed fixture; not observed.',
                ]
                rows.append(dict(zip(FIELDS, values_by_field)))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('outputs/software_validation'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    base = fixtures()
    cases = []

    def add(name, rows, expected_codes=(), pair_count=1, evidence='SOFTWARE_TEST'):
        cases.append((name, rows, set(expected_codes), pair_count, evidence))

    add('valid_AB_and_BA', base, pair_count=2)
    add('empty_is_not_a_measured_zero', [], pair_count=0)
    # Optional notes are not required for a first, non-repeated observation.
    rows = deepcopy(base[:6])
    for row in rows:
        row['notes'] = ''
        row['preparation_error_count'] = 2 if row['method'] == 'A' else 1
    add('optional_notes_blank', rows)
    for key in FIELDS[:-1]:
        rows = deepcopy(base[:6])
        rows[0][key] = ''
        add(f'missing_{key}', rows, ('MISSING_FIELD',), 0)
    for name, key, value, code in (
        ('duplicate_id', 'record_id', base[1]['record_id'], 'DUPLICATE_ID'),
        ('invalid_date', 'date', '2000-02-30', 'DATE'),
        ('unknown_method', 'method', 'C', 'METHOD'),
        ('invalid_order', 'run_order', '3', 'ORDER'),
        ('unknown_check', 'carrier_pin_check', 'OK', 'CHECK_VALUE'),
        ('negative_count', 'preparation_error_count', -1, 'COUNT'),
        ('fractional_count', 'rework_count', 0.5, 'COUNT'),
        ('text_count', 'rework_count', 'zero', 'COUNT'),
        ('negative_thickness', 'thickness_nm', -1, 'MEASUREMENT'),
        ('nonfinite_thickness', 'thickness_nm', 'nan', 'MEASUREMENT'),
        ('infinite_thickness', 'thickness_nm', 'inf', 'MEASUREMENT'),
        ('negative_coordinate', 'coupon_x_mm', -1, 'MEASUREMENT'),
        ('orientation_360', 'coupon_orientation_deg', 360, 'ORIENTATION'),
        ('literature_cannot_enter', 'evidence_status', 'LITERATURE_BENCHMARK', 'EVIDENCE_CATEGORY'),
        ('reconstruction_cannot_enter', 'evidence_status', 'RECONSTRUCTED_EXAMPLE', 'EVIDENCE_CATEGORY'),
        ('block_mismatch', 'block_id', 'OTHER-BLOCK', 'PAIR_CONDITION'),
        ('recipe_mismatch', 'recipe_id', 'OTHER-RECIPE', 'PAIR_CONDITION'),
        ('tool_mismatch', 'measurement_tool', 'OTHER-TOOL', 'PAIR_CONDITION'),
        ('carrier_changes_within_run', 'carrier_id', 'OTHER-CARRIER', 'RUN_CONSISTENCY'),
        ('counts_change_within_run', 'preparation_error_count', 1, 'RUN_CONSISTENCY'),
        ('measurement_point_mismatch', 'measurement_point', 'P4', 'POINT_SET'),
        ('repeat_requires_review', 'measurement_point', 'P2', 'REPEATED_POINT_REVIEW'),
    ):
        rows = deepcopy(base[:6])
        rows[0][key] = value
        add(name, rows, (code,), 0)
    rows = deepcopy(base[:6])
    for row in rows[3:]:
        row['run_order'] = 1
    add('same_AB_order', rows, ('PAIR_ORDER',), 0)
    add('missing_B', deepcopy(base[:3]), ('MISSING_METHOD',), 0)
    add('single_point_cannot_define_range', [deepcopy(base[0]), deepcopy(base[3])], ('POINT_COUNT',), 0)
    add('software_fixture_excluded_from_field', deepcopy(base[:6]), ('EVIDENCE_CATEGORY',), 0,
        'FIELD_MEASUREMENT')
    rows = deepcopy(base[:6])
    for row in rows:
        row['thickness_nm'] = 0
    add('observed_numeric_zero_preserved_in_test', rows)

    outcomes, exported = [], []
    for name, rows, expected_codes, pair_count, evidence in cases:
        result = validate_records(rows, evidence)
        codes = {issue['code'] for issue in result['issues']}
        passed = expected_codes.issubset(codes) and result['accepted_pair_count'] == pair_count
        if not expected_codes:
            passed = passed and not codes
        if name == 'valid_AB_and_BA':
            passed = passed and [pair['delta_nm_A_minus_B'] for pair in result['pairs']] == [2.0, -2.0]
            passed = passed and all(pair['point_count_per_method'] == 3 for pair in result['pairs'])
        if name == 'empty_is_not_a_measured_zero':
            passed = passed and result['status'] == 'EMPTY'
        if name == 'optional_notes_blank':
            passed = passed and result['pairs'][0]['A_error_counts']['preparation_error_count'] == 2
            passed = passed and result['pairs'][0]['B_error_counts']['preparation_error_count'] == 1
        outcomes.append({
            'case_id': name, 'passed': passed, 'expected_issue_codes': sorted(expected_codes),
            'actual_issue_codes': sorted(codes), 'expected_pairs': pair_count,
            'actual_pairs': result['accepted_pair_count'], 'record_count': len(rows),
        })
        exported.extend({'case_id': name, **row} for row in rows)
    with (args.out / 'test_cases.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=('case_id', *FIELDS))
        writer.writeheader()
        writer.writerows(exported)
    source = Path(__file__).with_name('record_validation.py')
    result = {
        'evidence_status': 'SOFTWARE_TEST',
        'executed_at_utc': datetime.now(timezone.utc).isoformat(),
        'fixture_date_meaning': '2000-01-01 is a fixed test constant, not an internship date.',
        'validator_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'verification_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'case_count': len(outcomes), 'passed': sum(row['passed'] for row in outcomes),
        'failed': sum(not row['passed'] for row in outcomes), 'cases': outcomes,
        'scope': 'Record integrity and range arithmetic on constructed inputs only.',
        'limit': 'Does not establish real preparation-error reduction, deposition quality, provenance or workplace adoption.',
    }
    (args.out / 'test_results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"SOFTWARE_TEST: {result['passed']}/{result['case_count']} cases passed")
    if result['failed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
