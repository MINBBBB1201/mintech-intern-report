# Mintech project: technical explanation

## What was the internship role?

The internship was in manufacturing technology at Mintech, supporting OLED deposition-equipment manufacturing. The work began with factory assistance and continued with practical tasks under a supervisor's direction.

## What was developed afterwards?

The follow-up package contains a proposed carrier and witness-coupon record structure, a preparation checklist, a paired comparison plan, a workbook and a Python record validator. A separate synthetic-data pipeline compares two classifiers. Documents and software were developed with AI assistance.

## Why is record validation the main project?

A calculation can return a number even when its inputs refer to different conditions. The validator checks whether the records satisfy the declared comparison rules before calculating thickness-range differences. The rules can be checked with valid and deliberately altered input files.

## Give an example of an important check.

The `measurement_point_mismatch` software test changes one measurement-point identifier to P4. Both methods still have the same number of rows, but they refer to different point sets. The validator returns `POINT_SET` and withholds the pair. Matching the number of measurements alone would miss that problem.

## Why count errors once per run?

One run may have several measurement-point rows. If its preparation-error count is copied onto each row and then summed, the count is multiplied by the number of points. A test uses two errors for A and one for B across three points each. The validator retains two and one.

## What do the 55 tests prove?

They show that the constructed inputs produce the expected issue codes and accepted-pair counts. They do not establish the frequency of errors in factory work or a field improvement rate. The fixtures are labelled SOFTWARE_TEST and saved alongside the results.

## How does AI connect to the engineering work?

AI tools helped develop the documents and code. A separate machine-learning exercise classifies generated 4M records. Connecting these tools requires agreement on the observation unit, identifiers, timing and label. The current classifier does not consume field records from the checklist.

## Which classifier performs better?

At the saved threshold of 0.5, LogisticRegression finds 50 of 60 positives with 119 false alarms. LightGBM finds 26 with 29 false alarms. Choosing between them requires the relative costs of missed defects and unnecessary inspections. The dataset is generated, so these are workflow examples rather than company production-performance estimates.

## What would be needed for a real field comparison?

The proposed procedure needs engineering review, a repeatability check and matched A/B records with order and block information. Outcomes need traceable measurement and correction histories. For prediction, labels must be independently observed and features must exist at the intended prediction time.
