"""인턴 경험을 확장한 4M 품질 분석 대시보드.

실행: streamlit run code/app/dashboard.py
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from pipeline import generate, add_features  # noqa: E402

st.set_page_config(page_title="4M 합성 데이터 분석 예제", layout="wide")

st.title("현장 경험에서 확장한 4M 품질 분석")
st.caption(
    "인턴 경험에서 확장한 학습용 분석입니다. 코드로 생성한 데이터를 사용하며 회사 생산 데이터나 모델의 실시간 예측 화면이 아닙니다."
)

# ── 데이터 ──────────────────────────────────────────────
@st.cache_data
def load(n=4000, rate=0.06, seed=42):
    df = generate(n, rate, seed)
    return add_features(df)

n = st.sidebar.slider("분석 표본 수", 1000, 20000, 4000, step=1000)
rate = st.sidebar.slider("생성 양성률", 0.01, 0.20, 0.06, step=0.01)
df = load(n, rate, seed=42)
st.sidebar.caption("재현 seed: 42")

# ── KPI ────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("분석 행", f"{len(df):,}")
c2.metric("생성 양성률", f"{df.defect.mean()*100:.1f}%")
c3.metric("평균 경과시간", f"{df.elapsed_s.mean():.1f}s")
c4.metric("평균 대기시간", f"{df.wait_s.mean():.1f}s")
st.caption(
    "KPI 카드는 전체 생성 데이터 기준입니다. 아래 차트와 표는 4M 필터가 적용된 부분집합 기준입니다."
)

st.divider()

# ── 4M 필터 ────────────────────────────────────────────
st.subheader("4M 필터")
f1, f2, f3, f4 = st.columns(4)

with f1:
    w = st.multiselect("Man / 작업자", sorted(df.worker_id.unique()),
                       default=sorted(df.worker_id.unique())[:4])
with f2:
    m = st.multiselect("Machine / 호기", sorted(df.machine_id.unique()),
                       default=sorted(df.machine_id.unique()))
with f3:
    t = st.multiselect("Method / 단위작업", sorted(df.task_id.unique()),
                       default=sorted(df.task_id.unique())[:8])
with f4:
    s = st.multiselect("Shift", sorted(df["shift"].unique()),
                       default=sorted(df["shift"].unique()))

view = df[
    df.worker_id.isin(w) & df.machine_id.isin(m)
    & df.task_id.isin(t) & df["shift"].isin(s)
]

st.write(f"필터 결과: **{len(view):,}건**")

# ── 차트 ───────────────────────────────────────────────
st.subheader("4M별 관측 결함률")
a, b = st.columns(2)

with a:
    by_worker = view.groupby("worker_id")["defect"].agg(["mean", "count"])
    by_worker.columns = ["결함률", "건수"]
    st.bar_chart(by_worker["결함률"], height=260)
    st.caption("Man: 작업자별 결함률")

with b:
    by_machine = view.groupby("machine_id")["defect"].agg(["mean", "count"])
    by_machine.columns = ["결함률", "건수"]
    st.bar_chart(by_machine["결함률"], height=260)
    st.caption("Machine: 호기별 결함률")

c, d = st.columns(2)
with c:
    by_task = view.groupby("task_id")["defect"].mean().sort_values(ascending=False).head(8)
    st.bar_chart(by_task, height=260)
    st.caption("Method: 단위작업별 결함률 (상위 8)")

with d:
    by_lot = view.groupby("material_lot")["defect"].mean().sort_values(ascending=False).head(8)
    st.bar_chart(by_lot, height=260)
    st.caption("Material: 자재 로트별 결함률 (상위 8)")

# ── 관측 결함률 그룹 ────────────────────────────────────
st.subheader("관측 결함률 상위 그룹")
topn = st.slider("표시 개수", 5, 30, 10)
observed_groups = (
    view.groupby(["task_id", "worker_id", "machine_id"])
    .agg(건수=("defect", "size"), 결함률=("defect", "mean"),
         평균경과=("elapsed_s", "mean"), 평균대기=("wait_s", "mean"))
    .query("건수 >= 5")
    .sort_values("결함률", ascending=False)
    .head(topn)
)
st.dataframe(
    observed_groups.style.format(
        {"결함률": "{:.1%}", "평균경과": "{:.1f}s", "평균대기": "{:.1f}s"}
    ),
    width="stretch",
)
