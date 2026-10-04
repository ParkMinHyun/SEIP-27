# SEIP-27 Chapter 3 Patch Guide — Admission/Pacing Algorithms Removed Version

이 문서는 **Algorithm 1만 남기고 Admission과 Pacing의 별도 알고리즘 박스를 제거한 현재 버전**에 바로 적용할 수 있도록 작성했다.

목표는 다음 세 가지다.

1. Cold start를 “예측값 없이도 안전하다”가 아니라 **runtime estimate bootstrap**으로 설명한다.
2. Pacing의 deadline 기준과 `1/2`를 **early queue-pressure control + admission과의 역할 분담**으로 설명한다.
3. 기존 reserve 식을 변경하지 않고, **full-sequence reserve − disabled workload**라는 직관적인 의미로 다시 설명한다.

실험과 구현은 변경하지 않는다.

---

## 1. §3.3 Admission — Cold Start 문단 추가

### 권장 위치

`P_hat(K)=0`일 때 admit하는 조건을 설명한 직후.

### 바로 붙여넣을 수 있는 문장

> **Cold start.**
> Cold-start executions are admitted to bootstrap runtime estimates.
> A configuration that cannot complete an isolated first capture within the timeout is treated as a release-blocking defect and must be corrected before deployment.
> The controller therefore targets runtime degradation caused by repeated captures and accumulated shared-worker backlog, rather than configurations that are infeasible from the first capture.

### 이 문장의 역할

이 문단으로 다음 질문을 닫을 수 있다.

- 왜 estimate가 0인데 실행시키는가?
- mandatory reserve도 아직 모르는 최초 capture는 어떻게 보는가?
- 첫 capture가 timeout 나면 controller가 해결해야 하는가?

답은 다음과 같다.

> 첫 capture 자체가 deadline을 만족하지 못하는 configuration은 출시 대상이 아니다.
> 따라서 cold start는 관측값을 확보하기 위해 실행하고, 이후부터 runtime controller가 반복 촬영으로 인한 degradation을 제어한다.

### 피해야 할 표현

다음과 같이 쓰지 않는 것이 좋다.

> The first capture is safe because the queue is empty.

queue가 비어 있는 것과 Draft-stage decision 시점의 remaining budget이 충분한 것은 동일하지 않다.

---

## 2. §3.3 Admission — Residual 계산의 기준 시점 복구

### 권장 위치

Residual factor 정의 직전.

### 바로 붙여넣을 수 있는 문장

> For residual calibration, the controller retains the stage-duration predictions made before execution and compares them with the observed durations at completion.
> This preserves the prediction error that was visible at the original admission decision point.

더 짧게 하려면:

> Residual factors use the stage-duration predictions retained before execution, rather than estimates updated at completion.

### 왜 필요한가

남아 있는 Algorithm 1에서 completion 시 predictor update와 admission update가 연속해서 나타난다면,
독자는 residual이 updated predictor를 사용하는지 의문을 가질 수 있다.

이 한 문장으로 실제 구현에서 보존하는 **pre-execution prediction snapshot**을 명확히 하면 충분하다.

별도 Admission Algorithm을 다시 넣을 필요는 없다.

---

## 3. §3.4 Pacing — Deadline 기준의 의미 설명

현재 pacing 식은 backlog 마지막 capture의 remaining deadline을 기준으로 다음 arrival delay를 결정한다.

이 deadline은 `i+1`의 deadline을 직접 예측하는 값이 아니다.

### 권장 위치

Pacing delay 식 직후.

### 바로 붙여넣을 수 있는 문장

> Pacing uses the projected completion margin of the current queue as an early deadline-pressure signal, rather than as a direct feasibility test for capture \(i+1\).
> When this margin shrinks, pacing delays the next arrival before the queue becomes critical.

Admission과의 관계까지 포함하려면:

> Pacing uses the projected completion margin of the current queue as an early deadline-pressure signal, rather than as a direct feasibility test for capture \(i+1\).
> It slows the next arrival before queue pressure becomes critical, while admission handles residual per-capture risk after the capture reaches the draft worker.

### 핵심 의미

Pacing의 목적은:

> **현재 queue pressure를 보고, 그 위험이 다음 capture로 전파되기 전에 backlog 유입 속도를 낮추는 것**

이다.

즉 pacing은 `i+1`을 정확히 safe/unsafe로 분류하려는 기법이 아니다.

---

## 4. §3.4 Pacing — `1/2` heuristic 설명

현재 식이 다음과 같다고 가정한다.

\[
d_i =
\left\lceil
\frac{
\max(0,\hat B_i + 2\hat C - T_i^{\mathrm{end}})
}{2}
\right\rceil.
\]

### 바로 붙여넣을 수 있는 문장

> The projected excess is not fully converted into arrival delay.
> We use half of it as a coordination heuristic: pacing reduces queue growth early, while admission handles remaining per-capture risk.
> This avoids placing the entire safety burden on pacing and unnecessarily increasing shot-to-shot latency.

더 짧게 쓰려면:

> We convert only half of the projected excess into arrival delay so that pacing reduces queue pressure early without carrying the entire safety burden; residual risk is handled by admission.

### 논문에서의 위치

`1/2`를 수학적으로 optimal한 값처럼 설명하지 않는다.

권장 표현:

- `coordination heuristic`
- `responsiveness-oriented heuristic`

피해야 할 표현:

- `optimal split`
- `guaranteed safe delay`
- `sufficient delay`

---

## 5. §3.4 Reserve — 현재 수식은 유지하되 동치식으로 재표현

현재 식:

\[
\hat C =
\max\left(
C_\tau -
[\hat P(\mathcal K)-\hat P(\mathcal K^{\mathrm{eff}})],
\hat P(\mathcal K^{\mathrm{eff}})
\right).
\]

이 식은 다음과 정확히 동치다.

\[
\boxed{
\hat C
=
\max(C_\tau,\hat P(\mathcal K))
-
\left[
\hat P(\mathcal K)-\hat P(\mathcal K^{\mathrm{eff}})
\right]
}
\]

### 추천

**현재 식을 위 동치식으로 교체하는 것을 추천**한다.

실험, 구현, 결과는 전혀 바뀌지 않는다.

단지 의미가 훨씬 쉽게 읽힌다.

\[
\text{effective reserve}
=
\text{full-sequence reserve}
-
\text{predicted cost of disabled work}
\]

---

## 6. Reserve 설명 문단 전체 교체안

현재 `Admission-aware reserve` 설명을 다음과 같이 정리하는 것을 추천한다.

> **Admission-aware reserve.**
> Pacing first takes the larger of the historical sequence-duration quantile \(C_\tau\) and the configured-sequence point estimate \(\hat P(\mathcal K)\) as the full-sequence reserve.
> When admission disables optional work, pacing subtracts only the predicted cost of the disabled stages:
>
> \[
> \hat C
> =
> \max(C_\tau,\hat P(\mathcal K))
> -
> \left[
> \hat P(\mathcal K)-\hat P(\mathcal K^{\mathrm{eff}})
> \right].
> \]
>
> Thus, admission reduces the workload component of the reserve immediately, while any positive historical margin above the configured-sequence point estimate is retained.

이 문단 하나로 현재 수식의 설계 의도를 거의 모두 설명할 수 있다.

---

## 7. Reserve의 핵심 성질을 한 줄 더 넣고 싶다면

현재 식에서는:

\[
\hat C-\hat P(\mathcal K^{\mathrm{eff}})
=
\max(0,C_\tau-\hat P(\mathcal K)).
\]

따라서 다음 문장을 추가할 수 있다.

> In particular, disabling stages does not remove an existing historical headroom: the margin above the effective point estimate remains \(\max(0,C_\tau-\hat P(\mathcal K))\).

이 성질은 reviewer가 가장 쉽게 납득할 수 있는 포인트다.

---

## 8. Reserve 예시 — 논문에는 넣지 않아도 되지만 설명용으로 유용

Admission 전:

\[
\hat P(\mathcal K)=100,\quad C_\tau=120.
\]

Full reserve:

\[
\hat C_{\mathrm{full}}=120.
\]

즉 point estimate 대비 headroom은 20이다.

Bokeh가 skip되어:

\[
\hat P(\mathcal K^{\mathrm{eff}})=60
\]

이면 disabled cost는 40이다.

따라서:

\[
\hat C=120-40=80.
\]

결과:

- workload: 100 → 60
- reserve: 120 → 80
- historical headroom: 20 → 20

즉 admission이 줄인 workload는 즉시 반영되지만,
기존 historical headroom은 유지된다.

---

## 9. \(C_\tau < \hat P(\mathcal K)\)인 경우의 올바른 해석

예:

\[
\hat P(\mathcal K)=100,\quad C_\tau=95.
\]

Admission 전 reserve는:

\[
\max(95,100)=100.
\]

즉 historical history가 point estimate 위에 추가 headroom을 제공하지 않는다.

Admission 후 effective estimate가 60이면:

\[
\hat C=60.
\]

이는 “skip 때문에 보수성이 사라진 것”이 아니다.

정확한 의미는:

> the historical quantile provided no additional headroom before the skip, so the reserve remains at the effective point estimate after the skip.

---

## 10. Reserve 명칭

현재 reserve는 admission에서 사용하는 residual-calibrated upper estimate와 목적이 다르다.

따라서 다음 표현을 추천한다.

- `pacing reserve`
- `sequence-level reserve`
- `historical completion reserve`

다음 표현은 피하는 것이 좋다.

- `statistical upper bound`
- `guaranteed upper bound`
- `safe bound`

Pacing은 early queue-pressure control이므로,
reserve도 **coarse sequence-level pacing estimate**로 두는 것이 자연스럽다.

---

## 11. Algorithm 1에 남아 있어야 할 coordination 연결

Admission/Pacing 알고리즘을 제거했더라도 Algorithm 1은 전체 시스템 흐름을 보여준다.

따라서 Draft sequence 시작 시 effective workload가 정해지고 pacing state에 반영된다는 사실은 보이면 좋다.

예시:

```text
K_i_eff ← ApplyAdmissionState(K_i, D)
pacing.UpdateSequenceEstimate(i, K_i, K_i_eff)
```

함수명 자체가 중요한 것은 아니다.

중요한 것은 독자가 다음 관계를 볼 수 있는 것이다.

> admission decision → effective sequence → pacing reserve update

### Disabled group notation

Algorithm 1에서 `admission.D` 또는 \(\mathcal D\)를 사용한다면,
본문 §3.3에 다음과 같이 짧게 정의한다.

> We denote by \(\mathcal D\) the set of optional-stage groups disabled for the current session.

실제 정책이 session 단위가 아니라 capture 단위라면 그에 맞춰 `current capture/session`을 수정한다.

---

## 12. §3.4 마지막에 넣기 좋은 coordination 문단

> Pacing and admission operate at different control points.
> Pacing reacts early to queue-level deadline pressure and slows future arrivals before backlog becomes critical.
> Because this projection is intentionally coarse and responsiveness-sensitive, it does not attempt to eliminate all future risk.
> Admission then performs a per-capture remaining-budget check at the draft worker and removes optional work when necessary.

이 문단은 다음을 한꺼번에 설명한다.

- 왜 pacing이 기존 queue deadline을 보는가
- 왜 `1/2`처럼 보수성을 전부 pacing에 넣지 않는가
- 왜 reserve가 admission upper bound만큼 정교할 필요가 없는가
- 왜 admission과 pacing이 모두 필요한가

---

## 13. 현재 버전에서 실제로 수정할 우선순위

### 반드시 수정

1. Cold start를 release prerequisite + runtime bootstrap으로 설명
2. Residual이 pre-execution prediction을 사용한다고 명시
3. Pacing deadline을 queue-pressure signal이라고 설명
4. `1/2`를 admission과 역할 분담하는 coordination heuristic으로 설명
5. Reserve를 `full reserve − disabled workload` 동치식으로 표현

### 있으면 좋은 수정

6. Algorithm 1에 sequence-start pacing update 연결
7. \(\mathcal D\) 정의
8. Historical headroom 보존 성질 한 문장 추가
9. Reserve를 `upper bound`가 아닌 `pacing reserve`로 명명

---

## 14. 최종 적용 후 방법론의 읽히는 구조

이 수정이 들어가면 reviewer는 3장을 다음과 같이 읽게 된다.

### Admission

- 첫 실행: runtime timing을 bootstrap
- 이후: remaining budget vs remaining-sequence upper estimate
- miss 가능성이 있으면 optional work 제거

### Pacing

- current queue margin을 early pressure signal로 사용
- 위험이 커지기 전에 다음 arrival을 늦춤
- responsiveness를 위해 projected excess의 절반만 pacing으로 흡수
- pacing이 놓친 residual risk는 admission이 처리

### Admission-aware reserve

- full-sequence reserve 계산
- admission으로 제거된 workload 비용만 차감
- 기존 positive historical headroom은 유지

이렇게 정리하면 별도 Admission/Pacing 알고리즘 없이도
**수식 + 본문만으로 설계 이유와 상호작용을 충분히 설명할 수 있다.**

---

## 최종 판단

현재 제출 일정과 실험 완료 상태를 고려하면,
**수식을 새로 설계하거나 실험을 다시 할 필요는 없다.**

특히 reserve는 새 방법을 넣는 것보다 현재 수식을 다음처럼 해석하는 것이 더 적합하다.

\[
\boxed{
\text{pacing reserve}
=
\text{full-sequence reserve}
-
\text{disabled workload}
}
\]

그리고 전체 control philosophy는 다음 한 문장으로 정리할 수 있다.

> **Pacing reduces queue pressure early; admission corrects residual per-capture risk later.**

이 해석은 현재 구현과 실험 결과를 그대로 유지하면서도,
cold start, pacing deadline, `1/2`, admission-aware reserve를 하나의 일관된 설계로 연결해준다.
