# decay 0.90 선택 근거 (3.3절)

원고 문장 (`3_3_admission.tex:54`):

> We set the weight decay to 0.90, the knee of the overrun rate against the size of \(U\).
> Applying the selected factor to \(\hat P\) gives the upper estimate [Eq. upper-estimate]

"overrun rate"는 실제 처리 시간이 U를 넘은 비율(아래 표의 miss)이고, "the size of U"는 U의 크기(아래 표의 mean U)다. 가로축을 U의 크기로, 세로축을 overrun 비율로 그린 곡선의 knee가 0.90이라는 뜻이다. U의 식은 바로 다음 문장에서 정의되고, 그 문장이 "gives the upper estimate"로 앞 문장의 U를 받는다. 즉 가로축을 U의 크기, 세로축을 overrun 비율로 그린 곡선의 knee가 0.90이라는 뜻이다. "overrun"은 3.3절 앞부분("accounts for these overruns")에서 이미 쓰는 용어다.

## 1. 요약

- decay 0.90은 2026-06-27 개발 단계에서 정했다(ML 커밋 `3fea7a2`). 평가 데이터(0729 이후)를 수집하기 전이다.
- 당시 커밋 메시지: decay를 0.80에서 0.90으로 올리자 mandatory stage(encoding부터 draft 저장까지)의 예약 U(E_i) coverage가 약 85%→91%(normal), 83%→90%(memory)로 올랐고, 이 개선이 "at small slack cost"라고 적혀 있다.
- 같은 개발 데이터를 당시 predictor로 재현했다. 커밋에 적힌 수치가 재현된다. decay를 0.70–0.99로 바꿔 보면 다음과 같다.
  - miss 비율 자체는 decay에 따라 거의 직선으로 줄어든다. 이 곡선에는 knee가 없다.
  - miss를 **예약 시간(mean U)** 에 대해 그리면 0.90 부근에서 꺾인다. 0.90을 넘기면 예약 1 ms당 줄어드는 miss가 절반 이하로 떨어진다. 원고의 "trade-off의 knee"는 이 뜻이다.

## 2. 데이터와 재현 방법

- 데이터: ML repo 커밋 `683f103`의 `data/8U_metrics_normal_0626.xlsx`, `data/8U_metrics_memory_0626.xlsx`. 개발 단계 기록이고 12MP 단일 draft chain이다. cold start를 빼면 normal은 캡처 710개, memory는 163개다. 파일을 꺼내려면 `git -C ../ML show 683f103:data/8U_metrics_normal_0626.xlsx > <file>`처럼 하면 된다.
- 기록 당시 설정: EWMA alpha 0.2, decay 0.8.
- Predictor: `3fea7a2`의 `DraftSequenceExecutionPredictor.kt`를 Python으로 한 줄씩 옮겼다.
  - 기록된 U와의 일치율: normal은 95.5%가 정확히 같고 97.6%가 2 ms 이내다. memory는 각각 71.2%와 81.0%다. memory의 불일치는 기록이 빠진 캡처 직후에 몰려 있다.
  - 캡처별 covered/missed 판정 일치: 708/710, 160/163.
- 커밋 수치 재현:
  - 기록된 U의 coverage: 85.63%(normal), 83.44%(memory).
  - decay 0.9로 replay: alpha 0.3이면 91.55% / 90.18%, alpha 0.2이면 92.11% / 89.57%.
- 검증: 별도 에이전트가 encoding만 따로 replay해 아래 곡선을 숫자까지 똑같이 재현했다.

## 3. 결과

**normal (alpha 0.2, n=710)**

| decay | miss (%) | mean U (ms) | median slack (ms) | 직전 구간의 miss 감소 / 예약 증가 |
|---|---|---|---|---|
| 0.80 | 14.08 | 388.8 | 38.5 | |
| 0.85 | 10.70 | 395.4 | 44.2 | 0.51 pp/ms |
| 0.90 | 7.89 | 405.1 | 55.7 | 0.29 pp/ms |
| 0.95 | 5.63 | 424.5 | 74.1 | 0.12 pp/ms |
| 0.99 | 3.52 | 470.4 | 123.4 | 0.046 pp/ms |

- Kneedle(0.70–0.99 구간 11점)로 knee를 찾으면, miss vs mean U와 miss vs median slack 모두 **0.900**이 나온다(Dmax 0.46).
- miss vs decay 곡선은 거의 직선이다. 0.01 증가당 기울기가 -0.28 ~ -0.87 pp로 흩어져 있고, 0.90에서 특별한 변화가 없다.

**memory (alpha 0.2, n=163)**

| decay | miss (%) | mean U (ms) | 직전 구간의 miss 감소 / 예약 증가 |
|---|---|---|---|
| 0.80 | 17.18 | 518.6 | |
| 0.85 | 14.11 | 533.7 | 0.20 pp/ms |
| 0.90 | 10.43 | 552.2 | 0.20 pp/ms |
| 0.95 | 8.59 | 576.7 | 0.075 pp/ms |
| 0.99 | 6.75 | 590.1 | 0.14 pp/ms |

- Kneedle은 0.875가 나온다. 표본이 163개라 캡처 하나가 0.61 pp를 움직이므로 잡음이 크다.

## 4. 한계 (리뷰어 질문 대비)

- knee는 비용 대비 곡선에서만 나타난다. miss 비율을 decay에 대해 그리면 거의 직선이다.
- 0.90 한 점으로 딱 떨어지지 않는다.
  - normal에서 0.90과 0.925가 거의 동점이다(Kneedle 거리 0.460 대 0.456).
  - grid 범위를 바꾸거나 alpha를 0.3(실제로 함께 배포한 값)으로 하면 knee가 0.87–0.925 사이에서 움직인다.
  - memory에서는 0.87–0.875다.
  - 이 knee는 U가 decay에 대해 볼록하게 커지는 데서 주로 생긴다. 그러니 "0.875–0.925 부근의 knee 구간"이라고 답하는 편이 정확하다.
- 근거는 개발 데이터 한 종류(0626, 이전 predictor build)다. 평가 데이터에서는 결과가 다르다.
  - RQ3 audit(0729/0803)를 replay하면 0.90에서 뚜렷한 knee가 없다.
  - 2026-08-25 세션(0803 데이터)도 knee가 없다고 결론 냈다.
  - 같은 세션의 p95 pinball loss는 0.86–0.915 구간이 평평한 최소이고, 0.90은 그 안에 있다. 다만 in-sample 결과다.
- 반대 기록이 있다. 2026-07-03 메모에 encoding tail의 decay를 0.95로 했을 때 시뮬레이션에서 가장 좋았다고 적혀 있다(timeout 6→4, near-miss 69→54).
- 6/27 튜닝 세션(Claude "EWMA hyperparameter optimization")은 transcript가 남아 있지 않다. 당시 0.8과 0.9 외의 값을 비교했는지는 확인할 수 없다. 따라서 "knee"는 당시 데이터로 사후에 재구성한 근거다.
- 쓰지 않기로 한 논리: n_eff→19 / τ→0.95 (2026-09-24 저자 결정).

## 5. 리뷰어 답변 예시 (영문)

> We fixed the decay at 0.90 on pre-release development traces, before the evaluation data were collected. On those traces, raising the decay from 0.80 to 0.90 raised the share of captures whose mandatory stage finished within its reserved upper estimate from about 85% to 91% while the mean reserve grew by only 16 ms; beyond 0.90, each additional millisecond of reserve removed less than half as many misses (0.12 vs. 0.29 percentage points per millisecond).

## 6. 재현 파일 위치

- 재현 스크립트와 출력은 로컬 임시 폴더 `%LOCALAPPDATA%\Temp\claude\prov\recon\`에 있다. 지워질 수 있다.
  - `june_predictor.py`: `3fea7a2` predictor의 Python 포팅
  - `replay0626.py`, `load0626.py`: 0626 데이터 replay
  - `enc_cov.py` → `enc_cov_out.txt`: decay별 coverage, mean U, slack
  - `knee.py`, `knee_tradeoff.py` → `knee_tradeoff.txt`: Kneedle 결과
  - `src_3fea7a2/`: 당시 Kotlin 소스
- 원 기록: ML 커밋 `3fea7a2`의 메시지, 데이터는 ML 커밋 `683f103`.

---

## 부록: RQ1 "about 55%" 문장 근거

원고 문장 (`4_2_rq1_effectiveness.tex:25`):

> Across cells with pacing during the first five captures, \(d\)~P50 reached a maximum of 737~ms, about 55\% of the corresponding delay with parallel capture disabled.

- 737 ms: S26 Ultra, 24MP memory pressure, Lv5 cell의 첫 5장 d P50이다. 출처는 `data/S26_Ultra/SM-S948U_metrics_24MP_memory_0906.xlsx`이고, CAPTURE_TIMEOUT이 아닌 run 11개, pacing이 걸린 전환 18개에서 나왔다.
- 비교 기준: pacing이 걸린 각 전환 **직전 캡처의 draft sequence 시간**이다. 중앙값은 1,348.5 ms이고 737/1,348.5 = **54.7%**다. parallel capture를 끄면 다음 캡처는 이 draft가 끝날 때까지 기다린다.
- 주의할 점:
  - 기준을 cell 전체의 첫 5장 draft P50(1,484 ms)이나 Baseline 값(1,499 ms)으로 잡으면 약 50%가 된다.
  - 18개 delay 중 4개(1,373–1,774 ms)는 직전 draft보다 길다. 중앙값끼리 비교해야 약 55%가 된다.
  - 원래 55%는 원고에서 빠진 옛 cadence 표(1,341 ms, 0803 데이터 Lv5–6 pooled)에서 계산된 것으로 보인다. 위의 직전 캡처 기준이 같은 run 집합에서 뽑은 대응값이다.
- 저자 규칙(2026-09-22, AGENTS.md `ee339d3`, 이후 정리하면서 삭제됨): 이 비교는 문장을 줄이려고 지우지 않고 유지한다.
