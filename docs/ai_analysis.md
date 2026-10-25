# AI and machine-learning analysis

Two uses of AI appear in this project. AI tools assisted the technical documents, code and automated checks. Separately, a machine-learning exercise compares classifiers on generated manufacturing-style 4M records. Neither constitutes a deployed company AI system.

## Files and data flow

1. [Pipeline](../code/pipeline.py) generates records and features, makes a stratified split, fits Logistic Regression and LightGBM, and saves evaluation outputs.
2. [Dashboard](../code/app/dashboard.py) explores generated records with 4M filters. It is not a live production-prediction service.
3. [Generated dataset](../outputs/4m_quality_analysis_data.csv), [metrics](../outputs/results.csv) and [run metadata](../outputs/run_metadata.json) preserve the example's data and evaluation settings.
4. [Code notes](code_notes.md) explain the variables and modelling choices. [Engineering report](engineering_report.md) connects the exercise to the record-design project.

The saved run uses 4,000 generated rows, 240 positives, seed 42 and a stratified 75/25 split. The held-out set contains 1,000 rows and 60 positives. At threshold 0.5:

| Model | ROC AUC | PR AUC | F1, positive class | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.9166 | 0.4604 | 0.4367 | 50 | 119 | 10 | 821 |
| LightGBM | 0.9035 | 0.4849 | 0.4522 | 26 | 29 | 34 | 911 |

In this run LightGBM produced fewer false positives and missed more positives at the selected threshold. These metrics come from synthetic labels that share variables with the model inputs. They demonstrate implementation and a threshold trade-off, not independent evidence of production-defect prediction. The model pipeline does not consume the carrier/coupon field template.

## Reproduce

From the repository root:

```bash
pip install -r code/requirements.txt
python code/pipeline.py --n 4000 --defect-rate 0.06 --seed 42 --out .validation/models
streamlit run code/app/dashboard.py
```

The recorded package versions are in the run metadata. The broad dependency ranges permit installation but do not promise byte-identical results across future environments. Worker, machine and task identifiers in this dataset are generated identifiers.
