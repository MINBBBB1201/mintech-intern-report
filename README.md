# Manufacturing records portfolio

An anonymized, AI-assisted engineering supplement based on supervised manufacturing-support experience. The project defines carrier and witness-coupon records, validates paired comparisons and demonstrates classification on generated 4M data.

## Read the project

- [Project brief](reports/project_brief.pdf): a short introduction to the role, record checks and analysis.
- [Engineering report](reports/engineering_report.pdf): design rules, test cases and interpretation.
- [Editable report](docs/engineering_report.md) and [worked software example](docs/validation_example.md).
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

## Rebuild the anonymized PDFs

```bash
pip install -r code/requirements-report.txt
python code/build_reports.py
```

The IBM Plex Sans KR font files are included with their OFL license and source manifest in `assets/fonts/`. The report mark is a project graphic, not an employer logo.

## 한국어 안내

이 저장소는 제조 지원 인턴십 이후의 기록 설계와 소프트웨어 검증을 담은 익명화 사본이다. 회사명, 근무지와 정확한 근무일, 증빙 원본, 지원 학교별 문구와 비공개 초안은 포함하지 않았다. 현장 측정 CSV는 빈 양식이며 수치 예제는 소프트웨어 시험 또는 생성 데이터다. 원본 제출 자료와 별도로 관리한다.
