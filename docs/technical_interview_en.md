# Mintech project: technical explanation

## What was the internship role?

The internship was in manufacturing technology at Mintech, supporting OLED deposition-equipment manufacturing. It lasted one month. The work began with factory assistance and continued with practical tasks under a supervisor's direction.

## What is the follow-up project?

The follow-up project presents a proposed carrier and witness-coupon record structure, preparation checklist, paired comparison plan, workbook and Python record validator. It focuses on what information must be recorded before comparing two preparation methods.

## Why is record validation the main project?

A calculation can return a number even when its inputs refer to different conditions. The validator checks required fields, consistency within a run, matching conditions between methods and agreement on measurement-point sets before calculating thickness-range differences.

## Give an example of an important check.

If two methods have equal numbers of measurements but different measurement-point identifiers, their point sets do not match. The validator withholds the pair because the spatial ranges would refer to different locations.

## Why count errors once per run?

Preparation-error counts belong to a run, while thickness values belong to individual measurement points. A run-level error count should therefore be counted once even when the run has several point rows.

## What would be needed for a field comparison?

The proposed procedure needs engineering review, a repeatability check and matched A/B records with order and block information. Outcomes need traceable measurement and correction histories. A supervised field trial would be needed to assess whether the checklist affects preparation errors or thickness-range differences.
