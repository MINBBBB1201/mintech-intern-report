# Mintech Internship Report

An engineering portfolio based on a one-month supervised manufacturing-support internship and a follow-up project about recording and comparing preparation methods. It presents proposed carrier and witness-coupon records, a checklist, comparison rules and a CSV validator.

This is a student portfolio, not an official Mintech publication or a company-endorsed specification. The company name identifies the internship context. Equipment identifiers, exact employment dates, personal evidence and company-internal files are excluded.

## Read the project

- [Project brief](reports/project_brief.pdf): a short introduction to the internship and record-validation project.
- [Engineering report](reports/engineering_report.pdf): proposed record structure, comparison rules and scope.
- [Editable report](docs/engineering_report.md) and [project brief](docs/project_brief.md).
- [Technical interview notes](docs/technical_interview_en.md).
- [Complete contents and coverage](docs/contents.md), including Korean reports, the workbook and supporting materials.
- [Privacy and scope](PRIVACY.md): export exclusions and data categories.

The internship role was supervised manufacturing support. The follow-up materials describe a proposed record-validation project; they do not claim a measured field improvement or a company-approved specification.

## Reproduce the record checks

The CSV validator and its verification command use Python's standard library:

```bash
python code/verify_records.py --out .validation/software_validation
python code/record_validation.py templates/field_records.csv --out .validation/empty_input.json
```

The field template is blank and contains no workplace measurements.

## Rebuild the privacy-filtered PDFs

```bash
pip install -r code/requirements-report.txt
python code/build_reports.py
```

For a private submission copy, the PDF builder accepts `--applicant` for the name used on the application and `--out` for a separate output directory. Keep that directory outside this checkout. The default reports omit the applicant name for public sharing.

The IBM Plex Sans KR font files are included with their OFL license and source manifest in `assets/fonts/`. The report mark is a project graphic, not an employer logo.

## 한국어 안내

민테크 제조 지원 인턴십과 이후 기록 검증 프로젝트를 정리한 학생 포트폴리오다. 캐리어·witness coupon 기록 구조, 비교 기준, 검증 코드와 보조 설계 자료를 포함한다. 현장 역할과 인턴십 이후의 제안은 구분했으며, 회사 공식 보고서나 승인된 장비 사양서는 아니다. 개인정보, 회사 내부 자료, 정확한 근무일과 대학별 지원 문구는 공개본에서 제외했다.
