# Mintech Internship Report

An AI-assisted engineering portfolio following a supervised manufacturing-support internship at Mintech. The project defines carrier and witness-coupon records, validates paired comparisons and demonstrates classification on generated 4M data.

This is a student portfolio, not an official Mintech publication or a company-endorsed specification. The company name identifies the internship context. Equipment identifiers, exact employment dates, personal evidence and company-internal files are excluded.

## Read the project

- [Project brief](reports/project_brief.pdf): a short introduction to the role, record checks and analysis.
- [Engineering report](reports/engineering_report.pdf): design rules, test cases and interpretation.
- [Editable report](docs/engineering_report.md) and [worked software example](docs/validation_example.md).
- [Complete contents and coverage](docs/contents.md), including Korean reports, the workbook and technical interview notes.
- [AI and machine-learning guide](docs/ai_analysis.md): pipeline, dashboard, model results and reproduction.
- [Privacy and scope](PRIVACY.md): export exclusions and data categories.

The internship role was supervised manufacturing support. The later project used AI tools for technical drafts, implementation, editing and automated checks. The applicant supplied the internship account, set the engineering-and-AI follow-up goal and directed report revisions. This repository does not claim independent authorship of all code or field effectiveness of the proposed checklist.

## Reproduce the record checks

The CSV validator and its tests use Python's standard library:

```bash
python code/verify_records.py --out .validation/software_validation
python code/record_validation.py templates/field_records.csv --out .validation/empty_input.json
```

The configured suite contains 55 constructed software cases. The empty field template returns `EMPTY`. Saved test fixtures use `SOFTWARE_TEST`; they are never observations from the workplace.

## Synthetic classification example

```bash
pip install -r code/requirements.txt
python code/pipeline.py --n 4000 --defect-rate 0.06 --seed 42 --out .validation/models
streamlit run code/app/dashboard.py
```

The 4,000 rows in `outputs/4m_quality_analysis_data.csv` are generated. Labels share variables with model inputs, so evaluation demonstrates a classification workflow, not independent production-defect prediction. Saved package versions and split conditions are in `outputs/run_metadata.json`.

## Rebuild the privacy-filtered PDFs

```bash
pip install -r code/requirements-report.txt
python code/build_reports.py
```

The IBM Plex Sans KR font files are included with their OFL license and source manifest in `assets/fonts/`. The report mark is a project graphic, not an employer logo.

## 한국어 안내

민테크 제조 지원 인턴십과 이후의 엔지니어링·AI 프로젝트를 정리한 학생 포트폴리오다. 기록 검증 코드, 4M 합성 데이터 분석, 두 분류모델의 결과, 대시보드, 비교분석 엑셀, 한국어·영어 설명을 포함한다. 현장 역할과 인턴십 이후 개발은 구분했다. 회사 내부 자료와 개인정보, 정확한 근무일, 지원 대학별 문구는 제외했다. 회사의 공식 보고서나 승인된 장비 사양서는 아니다.
