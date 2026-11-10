# Manufacturing records for consistent comparisons

## Mintech internship and follow-up engineering project

During a one-month manufacturing technology internship at Mintech, I assisted with factory tasks and supported OLED deposition-equipment manufacturing under my supervisor's direction.

## A record-validation project

The follow-up project organizes preparation and measurement records so two methods can be compared under matched conditions. Its outputs are a proposed carrier and witness-coupon checklist, a paired comparison plan, a workbook and a Python CSV validator.

The proposed record connects each carrier and sample to its preparation conditions and measurement points. Before calculating a difference in thickness range, the validator checks required fields, consistency within a run, matching comparison conditions and the measurement-point set.

## Comparison rules

The proposed A method follows the existing approved preparation procedure. B adds the checklist. Preparation errors are counted once per run. Film thickness is recorded at fixed points, and its range is the maximum minus the minimum across the same point set.

If the two methods use different measurement-point sets, the validator withholds the comparison. If a run-level preparation-error count appears on several point rows, it is counted once for that run.

## Scope

The checklist and comparison plan are proposals for a supervised field trial. The package does not report field A/B observations or claim that the checklist improved manufacturing outcomes. Equipment constraints, measurement repeatability, matched conditions and recorded trial order would need review before a field evaluation.
