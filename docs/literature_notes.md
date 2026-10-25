# OLED 박막 문헌 벤치마크

**데이터 범주: LITERATURE_BENCHMARK**

OLED 전극과 투명전도막 연구에서 보고한 측정값을 정리했다. the manufacturer 규격이나 작성자의 측정값이 아니며, `FIELD_MEASUREMENT` 또는 A/B 계산에 넣지 않는다. 재료, 적층 구조, 기판, 증착 조건과 측정 정의가 다르므로 합격 기준이나 연구 간 순위로 사용하지 않는다.

## 문헌 수치

표에는 2026-10-24 검토에서 논문 본문 또는 저자의 기관에 등록된 초록과 대조한 수치를 넣었다. `미기재`는 접근 가능한 출처에 해당 정보가 없다는 뜻이다.

| 재료·층 | 기판 | 증착 맥락 | 측정 물성·값 | DOI 또는 원문 |
|---|---|---|---|---|
| AZO 혼합 ITO, 150 nm | 미기재 | dual-target DC magnetron sputtering, 실온 성장, 기판 약 50 °C, AZO target 20 W | 비저항 4.6 × 10^-4 Ω·cm; 투과율 85% at 550 nm; FoM 9.83 × 10^-3 Ω^-1; 일함수 5.2 eV | [Park et al., 2008](https://doi.org/10.1149/1.2976160) |
| AZO, 두께 미기재 | PET | linear facing-target sputtering, 실온, 기판 가열과 dopant 활성화 없음 | 면저항 39 Ω/□; 가시광 평균 투과율 84.86% | [Jeong et al., 2010](https://doi.org/10.1088/0022-3727/43/46/465403) |
| AgNW / IZO / PEDOT:PSS, 값별 시편 구분 | PEN | IZO sputtering 후 polymer coating, sputtering 중 약 100 °C 가열 | 초록: 면저항 5.9 Ω/□, 투과율 86% at 550 nm; 본문 AFM: RMS 4.3 nm, peak-to-valley 33.5 nm. 특정 한 두께 시편의 묶음으로 해석하지 않음 | [Yun et al., 2016, Sci. Rep.](https://doi.org/10.1038/srep34150) |
| 32/0/32 nm AZO/Ag/AZO | glass | in-line magnetron sputtering, 실온 증착, 열처리 단계 보고 없음; AZO 2 kW pulsed DC, 200 kHz, 0.5 µs, 5 mTorr, 50 sccm Ar | 면저항 717.03 Ω/□; 투과율 82.77% at 550 nm; FoM 0.21 mΩ^-1 | [Lee et al., 2024, Micromachines 15(1), 146](https://doi.org/10.3390/mi15010146) |
| 32/6/32 nm AZO/Ag/AZO | glass | 위 AZO 조건; Ag 60 W RF, 3 mTorr, 30 sccm Ar, 실온 | 면저항 64.17 Ω/□; 투과율 77.06% at 550 nm; FoM 1.15 mΩ^-1 | [Lee et al., 2024, Micromachines 15(1), 146](https://doi.org/10.3390/mi15010146) |
| 32/12/32 nm AZO/Ag/AZO | glass | 위 AZO·Ag 조건, 실온 | 면저항 12.22 Ω/□; 투과율 76.62% at 550 nm; FoM 4.65 mΩ^-1 | [Lee et al., 2024, Micromachines 15(1), 146](https://doi.org/10.3390/mi15010146) |

Park는 [저자 소속기관의 논문 초록](https://pure.skku.edu/en/publications/transparent-conducting-azo-cosputtered-ito-anode-films-grown-by-a/), Jeong은 출판사 초록과 [저자 소속기관의 초록](https://pure.skku.edu/en/publications/flexible-al-doped-zno-films-grown-on-pet-substrates-using-linear-/)에서 확인했다. Yun은 초록과 본문, Lee는 공개 본문과 대조했다. Jeong의 가시광 평균 투과율을 다른 연구의 550 nm 단일 파장 투과율과 같은 값으로 비교하지 않는다. 면저항과 체적 비저항을 바꾸어 쓰거나 논문별 FoM을 합치지 않는다.

기존 초안의 [Kim et al., 2015](https://doi.org/10.7567/JJAP.54.090301)와 [Choi et al., 2008](https://doi.org/10.1149/1.2979143)는 이번 검토에서 출판사 본문이나 초록을 직접 대조하지 못해 수치표와 워크북에서 제외했다. 이 제외는 출처 접근과 대조 범위에 따른 결정이며 논문의 오류를 판정한 결과는 아니다. 현재 표는 6개 재료 구성과 19개 개별 물성값으로 구성돼 있다.

## 산포와 계측 해석

- **범위**: `R = max(t_i) - min(t_i)`이다. 두 극값만 사용하며 측정 지점 수와 극값의 영향을 받는다.
- **표본 표준편차**: `s = sqrt[sum((t_i - mean(t))^2)/(n - 1)]`이다. 한 두께 맵 안의 공간 산포를 원자료와 같은 단위로 나타낸다.
- **CV와 RSD**: `CV = s/mean(t)`, `RSD(%) = 100s/abs(mean(t))`이다. 의미 있는 0이 있는 비율척도에 사용하며 평균이 0에 가까우면 불안정하다.
- **반복성**: 같은 측정량을 같은 절차, 관측자, 장비, 위치와 사용 조건에서 짧은 시간 안에 반복 측정했을 때의 산포다. 한 장의 공간 맵에서 얻은 `s`나 CV를 장비 반복성으로 부르지 않는다.
- **측정불확도**: 측정 결과에 귀속되는 평가다. 결합 표준불확도와 확대불확도 `U = ku_c`를 구분하고, 결과에는 단위, coverage factor `k`, 해석과 실제 uncertainty budget을 함께 적는다.
- **순서·블록 효과**: 시간, run, source campaign, carrier slot처럼 통제할 변수를 block으로 정하고 각 block에 A와 B를 같은 횟수로 배치한다. 남은 실행 순서는 무작위화하거나 AB·BA로 균형을 맞춘다. 실행 순서와 경과시간을 기록해 drift를 확인하며, 순서 차이를 준비 방법 효과로 바꾸어 해석하지 않는다.

범위, `s`, CV/RSD를 보고할 때는 좌표, 측정 순서, 유효 지점 수 `n`, 제외 지점과 사유, 단위와 계산식을 함께 남긴다. 이 문헌 묶음에서는 OLED 박막에 공통으로 적용할 합격 기준을 확인하지 못했다.

## 통계 정의 출처

- [NIST/SEMATECH, Measures of Scale](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm)
- [NIST Dataplot, Coefficient of Variation](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/coefvari.htm)
- [NIST TN 1297, Terminology](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-d1-terminology)
- [NIST/SEMATECH, Analysis of Repeatability](https://www.itl.nist.gov/div898/handbook/mpc/section4/mpc441.htm)
- [NIST TN 1297, Reporting Uncertainty](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-7-reporting-uncertainty)
- [NIST/SEMATECH, Randomized Block Designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)
