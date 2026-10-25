# Constructed thickness inputs: software example

Evidence category: `SOFTWARE_TEST`. These constants were generated for program tests. They are not field measurements, company records or observations from the internship.

## Follow the calculation

The baseline test uses two pairs, TEST-AB and TEST-BA. Each method has three point-level rows. The values below come from the saved `valid_AB_and_BA` fixture in [test_cases.csv](../outputs/software_validation/test_cases.csv).

| Software pair | Method | P1 (nm) | P2 (nm) | P3 (nm) | Range (nm) |
|---|---|---|---|---|---|
| TEST-AB | A | 100 | 103 | 106 | 6 |
| TEST-AB | B | 100 | 102 | 104 | 4 |
| TEST-BA | A | 100 | 104 | 108 | 8 |
| TEST-BA | B | 100 | 105 | 110 | 10 |

The calculation uses `range = maximum - minimum` and `difference = A range - B range`. The differences are +2 nm for TEST-AB and -2 nm for TEST-BA. The two signs exercise both directions of the calculation. They do not estimate a checklist effect.

## Alter one condition

Changing a point identifier to P4 makes the A and B point sets differ. The `measurement_point_mismatch` case then returns `POINT_SET` and zero accepted pairs. Removing a required recipe value produces `MISSING_FIELD` and zero accepted pairs. Thickness values remain present in these examples, but the records no longer satisfy the comparison rules.

## Keep the input categories separate

The fixture uses TEST-prefixed IDs, a fixed software date of 2000-01-01 and the `SOFTWARE_TEST` category. The field CSV remains a blank template. The validator's normal field-input path excludes these test records from field calculations.

The [English report](engineering_report.md) explains the validation rules. The [saved test results](../outputs/software_validation/test_results.json) contain the case outcomes and source hashes.

## 한국어 설명

위 수치는 저장된 소프트웨어 시험 입력을 옮긴 계산 예제다. TEST-AB는 A 범위 6 nm, B 범위 4 nm이고 TEST-BA는 각각 8 nm와 10 nm다. 차이는 A에서 B를 빼서 +2 nm와 -2 nm로 계산한다. 현장 활동이나 실측 결과를 재구성한 값은 아니다.
