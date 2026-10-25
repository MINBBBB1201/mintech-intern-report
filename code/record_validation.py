"""Validate carrier/coupon CSV records without changing the source observations.

FIELD_MEASUREMENT is a declared provenance label, not proof of authenticity.
Software fixtures are validated separately and never exported as field inputs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
import json
import math
from pathlib import Path

FIELDS = (
    'record_id', 'date', 'method', 'run_order', 'block_id', 'pair_id', 'carrier_id',
    'carrier_seating_check', 'carrier_pin_check', 'carrier_surface_check',
    'carrier_seating_error_count', 'preparation_error_count', 'rework_count', 'recipe_id',
    'coupon_id', 'coupon_x_mm', 'coupon_y_mm', 'coupon_orientation_deg',
    'coupon_position_error_count', 'coupon_orientation_error_count', 'measurement_tool',
    'measurement_point', 'thickness_nm', 'measured_by', 'evidence_status', 'notes',
)
COUNTS = (
    'carrier_seating_error_count', 'preparation_error_count', 'rework_count',
    'coupon_position_error_count', 'coupon_orientation_error_count',
)
MEASURES = ('coupon_x_mm', 'coupon_y_mm', 'coupon_orientation_deg', 'thickness_nm')
CHECKS = ('carrier_seating_check', 'carrier_pin_check', 'carrier_surface_check')


def number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def validate_records(rows, expected_evidence='FIELD_MEASUREMENT'):
    """Check row integrity and pair comparability; retain all invalid source rows.

    Coordinates use the nonnegative convention in the supplied workbook.
    Counts describe one execution, repeated unchanged on its point records.
    Repeated point measurements require review before a pair range is computed.
    """
    if expected_evidence not in ('FIELD_MEASUREMENT', 'SOFTWARE_TEST'):
        raise ValueError('Unsupported evidence category')
    rows = [{key: str(value).strip() if value is not None else ''
             for key, value in row.items()} for row in rows]
    issues = []
    invalid = set()

    def issue(code, row_numbers, detail):
        indices = sorted(set(row_numbers))
        invalid.update(indices)
        issues.append({'code': code, 'csv_rows': [i + 2 for i in indices], 'detail': detail})

    ids = Counter(row.get('record_id') for row in rows if row.get('record_id'))
    for i, row in enumerate(rows):
        for key in FIELDS[:-1]:
            if not row.get(key):
                issue('MISSING_FIELD', [i], key)
        if row.get('record_id') and ids[row['record_id']] > 1:
            issue('DUPLICATE_ID', [i], row['record_id'])
        if row.get('evidence_status') and row['evidence_status'] != expected_evidence:
            issue('EVIDENCE_CATEGORY', [i], row['evidence_status'])
        if row.get('method') and row['method'] not in ('A', 'B'):
            issue('METHOD', [i], row['method'])
        if row.get('run_order') and row['run_order'] not in ('1', '2'):
            issue('ORDER', [i], row['run_order'])
        if row.get('date'):
            try:
                parsed = date.fromisoformat(row['date'])
                if parsed.isoformat() != row['date']:
                    raise ValueError('Expected YYYY-MM-DD')
            except ValueError:
                issue('DATE', [i], row['date'])
        for key in CHECKS:
            if row.get(key) and row[key] not in ('PASS', 'FAIL'):
                issue('CHECK_VALUE', [i], key)
        for key in COUNTS:
            if row.get(key):
                value = number(row[key])
                if value is None or value < 0 or not value.is_integer():
                    issue('COUNT', [i], key)
        for key in MEASURES:
            if row.get(key):
                value = number(row[key])
                if value is None or value < 0:
                    issue('MEASUREMENT', [i], key)
                elif key == 'coupon_orientation_deg' and value >= 360:
                    issue('ORIENTATION', [i], key)

    groups = defaultdict(list)
    for i, row in enumerate(rows):
        if row.get('pair_id'):
            groups[row['pair_id']].append(i)
    pairs = []
    for pair_id, indices in groups.items():
        by_method = {method: [i for i in indices if rows[i].get('method') == method]
                     for method in ('A', 'B')}
        if any(not items for items in by_method.values()):
            issue('MISSING_METHOD', indices, pair_id)
            continue
        for key in ('block_id', 'recipe_id', 'measurement_tool'):
            if len({rows[i].get(key) for i in indices}) != 1:
                issue('PAIR_CONDITION', indices, key)
        for method, items in by_method.items():
            for key in ('date', 'run_order', 'carrier_id', 'coupon_id', *CHECKS,
                        'coupon_x_mm', 'coupon_y_mm', 'coupon_orientation_deg', *COUNTS):
                # Numeric equality tolerates equivalent CSV spellings such as 0 and 0.0.
                values = {number(rows[i].get(key)) if key in (*COUNTS, *MEASURES)
                          else rows[i].get(key) for i in items}
                if len(values) != 1:
                    issue('RUN_CONSISTENCY', items, f'{method}:{key}')
            points = [rows[i].get('measurement_point') for i in items]
            if len(set(points)) < 2:
                issue('POINT_COUNT', items, method)
            if len(points) != len(set(points)):
                issue('REPEATED_POINT_REVIEW', items, method)
        a, b = by_method['A'], by_method['B']
        if rows[a[0]].get('run_order') == rows[b[0]].get('run_order'):
            issue('PAIR_ORDER', indices, pair_id)
        if {rows[i].get('measurement_point') for i in a} != {
                rows[i].get('measurement_point') for i in b}:
            issue('POINT_SET', indices, pair_id)
        if any(i in invalid for i in indices):
            continue
        ranges = {}
        for method, items in by_method.items():
            thicknesses = [number(rows[i]['thickness_nm']) for i in items]
            ranges[method] = max(thicknesses) - min(thicknesses)
        pairs.append({
            'pair_id': pair_id, 'block_id': rows[a[0]]['block_id'],
            'A_order': int(rows[a[0]]['run_order']), 'B_order': int(rows[b[0]]['run_order']),
            'point_count_per_method': len(a),
            'A_thickness_range_nm': ranges['A'], 'B_thickness_range_nm': ranges['B'],
            'delta_nm_A_minus_B': ranges['A'] - ranges['B'],
            'A_error_counts': {key: int(float(rows[a[0]][key])) for key in COUNTS},
            'B_error_counts': {key: int(float(rows[b[0]][key])) for key in COUNTS},
            'evidence_status': expected_evidence,
        })
    return {
        'evidence_status': expected_evidence, 'record_count': len(rows),
        'accepted_pair_count': len(pairs), 'issue_count': len(issues),
        'status': 'EMPTY' if not rows else ('REVIEW' if issues else 'VALID'),
        'issues': issues, 'pairs': pairs,
        'provenance_limit': 'CSV labels do not authenticate observations; source records require review.',
    }


def main():
    parser = argparse.ArgumentParser(description='캐리어/쿠폰 CSV의 누락과 비교 조건 검사')
    parser.add_argument('csv', type=Path)
    parser.add_argument('--out', type=Path,
                        default=Path('outputs/software_validation/field_input_check.json'))
    args = parser.parse_args()
    with args.csv.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != FIELDS:
            parser.error('CSV header must match the supplied record template')
        rows = list(reader)
    result = validate_records(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{result['status']}: records={len(rows)}, pairs={len(result['pairs'])}, issues={len(result['issues'])}")
    raise SystemExit(1 if result['issues'] else 0)


if __name__ == '__main__':
    main()
