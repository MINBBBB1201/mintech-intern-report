"""4M 품질 분석 데이터 파이프라인.

데이터 생성 → 학습 → 평가 → 지표 출력

실행:
    python code/pipeline.py --n 4000 --defect-rate 0.06 --out outputs
"""
import argparse
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, confusion_matrix


# ── 1. 4M 분석 데이터 생성 ───────────────────────────────────────────
def generate(n=4000, defect_rate=0.06, seed=42):
    rng = np.random.default_rng(seed)

    n_workers = 8
    n_machines = 3
    n_tasks = 12
    n_lots = 40

    df = pd.DataFrame({
        "worker_id":    rng.integers(0, n_workers, n),
        "machine_id":   rng.integers(0, n_machines, n),
        "task_id":      rng.integers(0, n_tasks, n),
        "material_lot": rng.integers(0, n_lots, n),
        "shift":        rng.integers(0, 2, n),
    })

    # 4M 효과를 의도적으로 심는다 (검증 가능하도록)
    base = 60.0
    df["active_s"] = (
        base
        + df["worker_id"] * 3.2           # Man: 작업자 숙련도 차이
        + df["task_id"] * 2.5             # Method: 작업 난이도
        + df["machine_id"] * 4.0          # Machine: 호기 차이
        + rng.normal(0, 8, n)
    ).clip(10, None)

    df["wait_s"] = rng.gamma(2.0, 15.0, n).round(1)
    df["retry_count"] = rng.poisson(0.7, n)
    df["rework"] = (df["retry_count"] > 1).astype(int)

    # 결함: 특정 로트 + 야간 + 재작업 이력이 위험
    logit = (
        -3.2
        + 0.9 * (df["material_lot"] % 7 == 0)
        + 0.7 * df["shift"]
        + 0.8 * df["rework"]
        + 0.015 * (df["wait_s"] - df["wait_s"].mean()) / 10
        + rng.normal(0, 0.5, n)
    )
    p = 1 / (1 + np.exp(-logit))

    # 목표 결함률에 맞춰 조정
    target = int(n * defect_rate)
    idx = np.argsort(-p)
    df["defect"] = 0
    df.loc[idx[:target], "defect"] = 1
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    return df


# ── 2. 피처 ──────────────────────────────────────────────────────────
CAT = ["worker_id", "machine_id", "task_id", "material_lot", "shift"]
NUM = ["active_s", "wait_s", "retry_count", "rework"]


def add_features(df):
    df = df.copy()
    df["elapsed_s"] = df["active_s"] + df["wait_s"]
    df["wait_ratio"] = df["wait_s"] / df["elapsed_s"]
    df["total_time"] = df["elapsed_s"]
    df["retry_per_min"] = df["retry_count"] / (df["active_s"] / 60 + 1)
    return df


# 행 단위 값만 사용한다. 전체 데이터의 작업자·로트 집계를 분할 전에
# 계산하면 테스트 데이터 정보가 학습 피처에 섞일 수 있다.
# elapsed_s and total_time are equal by definition, so only total_time enters the model.
NUM_EXT = NUM + ["wait_ratio", "total_time", "retry_per_min"]


# ── 3. 학습 ──────────────────────────────────────────────────────────
def build_model(kind="lightgbm"):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
        ("num", "passthrough", NUM_EXT),
    ])

    if kind == "logistic":
        clf = LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=0
        )
        estimator_name = "LogisticRegression"
    else:
        try:
            from lightgbm import LGBMClassifier
            clf = LGBMClassifier(
                n_estimators=400, learning_rate=0.05, num_leaves=31,
                class_weight="balanced", random_state=0, verbose=-1,
            )
            estimator_name = "LightGBM"
        except ImportError:
            print("[!] lightgbm 없음 → RandomForest로 대체")
            from sklearn.ensemble import RandomForestClassifier
            clf = RandomForestClassifier(
                n_estimators=300, class_weight="balanced", random_state=0
            )
            estimator_name = "RandomForestClassifier"

    return Pipeline([("pre", pre), ("clf", clf)]), estimator_name


def evaluate(name, y_true, y_prob, thr=0.5):
    y_pred = (y_prob >= thr).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    return {
        "model": name,
        "roc_auc": round(roc_auc_score(y_true, y_prob), 4),
        "pr_auc": round(average_precision_score(y_true, y_prob), 4),
        "f1_defect": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "tn": int(cm[0, 0]), "fp": int(cm[0, 1]),
        "fn": int(cm[1, 0]), "tp": int(cm[1, 1]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--defect-rate", type=float, default=0.06)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default="outputs")
    args = ap.parse_args()

    df = generate(args.n, args.defect_rate, args.seed)
    print(f"[data] n={len(df)}, defect_rate={df.defect.mean():.3f}")

    df = add_features(df)
    X = df[CAT + NUM_EXT]
    y = df["defect"]

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.25, random_state=args.seed, stratify=y
    )

    threshold = 0.5
    results = []
    estimator_names = []
    for kind in ["logistic", "lightgbm"]:
        pipe, estimator_name = build_model(kind)
        pipe.fit(Xtr, ytr)
        prob = pipe.predict_proba(Xte)[:, 1]
        results.append(evaluate(estimator_name, yte, prob, threshold))
        estimator_names.append(estimator_name)

    # 비지도 이상탐지 (참고용)
    iso = IsolationForest(contamination=args.defect_rate, random_state=args.seed)
    iso.fit(Xtr[NUM_EXT])
    iso_score = -iso.score_samples(Xte[NUM_EXT])
    iso_pred = (iso_score > np.quantile(iso_score, 1 - args.defect_rate)).astype(int)
    print("\n[unsupervised] IsolationForest")
    print("  precision(defect) =", round(
        (iso_pred[yte.values == 1].sum() / max(iso_pred.sum(), 1)), 4))

    out = pd.DataFrame(results)
    print("\n[evaluation]")
    print(out.to_string(index=False))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_dir / "results.csv", index=False)
    data_file = "4m_quality_analysis_data.csv"
    df.to_csv(out_dir / data_file, index=False)
    try:
        import lightgbm
        lightgbm_version = lightgbm.__version__
    except ImportError:
        lightgbm_version = None

    metadata = {
        "estimators": estimator_names,
        "n": args.n,
        "seed": args.seed,
        "requested_positive_rate": args.defect_rate,
        "realized_positive_rate": round(float(y.mean()), 6),
        "positive_rows": int(y.sum()),
        "split": {
            "train": 0.75,
            "test": 0.25,
            "stratified": True,
            "train_rows": int(len(ytr)),
            "test_rows": int(len(yte)),
            "train_positive_rows": int(ytr.sum()),
            "test_positive_rows": int(yte.sum()),
        },
        "threshold": threshold,
        "data_file": data_file,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "lightgbm": lightgbm_version,
        },
    }
    with (out_dir / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\n[saved] {out_dir / 'results.csv'}")
    print(f"[saved] {out_dir / data_file}")
    print(f"[saved] {out_dir / 'run_metadata.json'}")


if __name__ == "__main__":
    main()
