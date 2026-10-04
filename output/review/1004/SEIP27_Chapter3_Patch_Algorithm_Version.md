# SEIP-27 Chapter 3 Patch Guide — Algorithm Version

이 문서는 **Algorithm 1 + Admission Algorithm + Pacing Algorithm이 모두 있는 버전**에 바로 적용할 수 있도록 작성했다.

목표는 다음 세 가지다.

1. Cold start를 “안전성 판단”이 아니라 **runtime estimate bootstrap**으로 명확히 설명한다.
2. Pacing의 deadline 기준과 `1/2`를 **early pressure control + admission과의 역할 분담**으로 설명한다.
3. 기존 reserve 식을 바꾸지 않고, **full-sequence reserve − disabled workload**라는 의미로 재해석한다.

실험과 구현은 변경하지 않는다.

---

## 1. §3.3 Admission — Cold Start 설명 추가

### 권장 위치

Cold-start execution을 설명하는 문단 또는 `\hat P(\mathcal K)=0`일 때 admit하는 조건 직후.

### 바로 적용 가능한 문장

> **Cold start.**
> Cold-start executions are admitted to bootstrap runtime estimates.
> A configuration that cannot complete an isolated first capture within the timeout is treated as a release-blocking defect and must be corrected before deployment.
> The controller therefore targets runtime degradation caused by repeated captures and accumulated shared-worker backlog, rather than configurations that are infeasible from the first capture.

### 이 문장의 의미

- 첫 capture 자체가 deadline을 못 맞추는 경우는 CAPER가 runtime에서 해결해야 하는 문제가 아니다.
- 그런 configuration은 출시 전에 반드시 병목을 파악하고 수정해야 한다.
- 따라서 cold start는 실행시켜서 관측값을 확보한다.
- 이후부터 관측값을 기반으로 admission과 pacing이 runtime degradation을 제어한다.

### Algorithm 2에 반영할 경우

현재 `\hat P(\mathcal K)=0` 조건이 이미 있다면 로직은 바꾸지 말고, **주석만 명확히 하는 것을 추천**한다.

예:

```text
if P_hat(K_i,j) = 0 then
    return ADMIT   ▷ cold-start execution to bootstrap runtime estimates
```

또는 기존 조건이

```text
if U(K_i,j) <= T_i,j or P_hat(K_i,j) = 0 then
```

이라면:

```text
if U(K_i,j) <= T_i,j or P_hat(K_i,j) = 0 then
    return ADMIT   ▷ zero estimate denotes cold-start bootstrap
```

### 피해야 할 표현

다음과 같이 쓰지 않는 것이 좋다.

> The first capture has enough budget because the queue is empty.

queue가 비어 있다는 사실과 optional-stage decision 시점의 remaining budget이 충분하다는 사실은 동일하지 않기 때문이다.

---

## 2. §3.3 Admission — Residual 계산 기준 시점 명확화

### 권장 위치

Residual factor 또는 calibration 정의 직전.

### 바로 적용 가능한 문장

> Residual factors use the stage-duration predictions retained before execution, rather than estimates updated at completion.

또는 조금 더 설명적으로:

> For residual calibration, the controller retains the stage-duration predictions made before execution and compares them with the observed durations at completion.
> This preserves the prediction error that was visible at the original admission decision point.

### Algorithm 2에 반영할 경우

`ComputeResidualFactor`가 있다면, 입력이 **pre-execution prediction snapshot**임을 드러내는 정도면 충분하다.

예:

```text
phi ← ComputeResidualFactor(K_i, p_hat_pre, p_actual)
```

중요한 것은 `p_hat_pre`가 `predictor.Observe(...)` 이후 재계산한 값이 아니라는 점이다.

### Algorithm 1 완료 처리와의 연결

Algorithm 1에서 순서가

```text
predictor.Observe(...)
admission.Update(...)
```

처럼 보인다면, 다음 중 하나를 권장한다.

#### 방법 A — snapshot이 이미 저장된다는 주석 추가

```text
admission.Update(i, observed, preExecutionPrediction)
predictor.Observe(observed)
```

또는 실제 구현 순서를 바꾸고 싶지 않다면:

```text
predictor.Observe(observed)
admission.Update(i, observed, preExecutionPrediction)
```

본문에서 `preExecutionPrediction`이 별도로 보존된 값임을 설명한다.

실제 구현 동작을 바꾸는 것이 목적이 아니라, **잔차 계산에 쓰는 기준 시점이 실행 전이라는 사실을 독자에게 보이는 것**이 목적이다.

---

## 3. §3.4 Pacing — Deadline 기준의 의미 명확화

현재 pacing은 backlog 마지막 capture의 remaining deadline을 사용해 다음 arrival에 delay를 건다.

이 값은 `i+1` capture의 deadline feasibility를 직접 계산하는 값이 아니다.

### 권장 위치

Pacing delay 식을 소개한 직후.

### 바로 적용 가능한 문장

> Pacing uses the projected completion margin of the current queue as an early deadline-pressure signal, rather than as a direct feasibility test for capture \(i+1\).
> When this margin shrinks, pacing delays the next arrival before the queue becomes critical.

조금 더 coordination을 강조하려면:

> Pacing uses the projected completion margin of the current queue as an early deadline-pressure signal, rather than as a direct feasibility test for capture \(i+1\).
> It slows the next arrival before queue pressure becomes critical, while admission handles residual per-capture risk after the capture reaches the draft worker.

### 의미

현재 backlog가 예측대로 끝났을 때 남게 될 margin을 기준으로,
`i+1`이 들어오기 전에 **선제적으로 arrival pressure를 낮춘다**는 뜻이다.

즉:

- Pacing = early / coarse arrival control
- Admission = later / per-capture workload control

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

### 바로 적용 가능한 문장

> The projected excess is not fully converted into arrival delay.
> We use half of it as a coordination heuristic: pacing reduces queue growth early, while admission handles remaining per-capture risk.
> This avoids placing the entire safety burden on pacing and unnecessarily increasing shot-to-shot latency.

조금 더 짧게 쓰려면:

> We convert only half of the projected excess into arrival delay so that pacing reduces queue pressure early without carrying the entire safety burden; residual risk is handled by admission.

### 중요한 표현

- `optimal`
- `provably sufficient`
- `guarantees safety`

와 같은 표현은 피한다.

`coordination heuristic` 또는 `responsiveness-oriented heuristic` 정도가 적절하다.

---

## 5. §3.4 Reserve — 기존 식을 더 이해하기 쉬운 동치식으로 표현

현재 reserve가 다음과 같다고 가정한다.

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

논문에서는 **동치식을 메인 식으로 쓰는 것을 추천**한다.

이유는 훨씬 쉽게 읽히기 때문이다.

\[
\text{effective reserve}
=
\text{full-sequence reserve}
-
\text{predicted cost of disabled work}
\]

여기서

\[
\hat C_{\mathrm{full}}
=
\max(C_\tau,\hat P(\mathcal K))
\]

로 정의할 수 있다.

그러면:

\[
\boxed{
\hat C
=
\hat C_{\mathrm{full}}
-
\Delta_{\mathrm{skip}}
}
\]

where

\[
\Delta_{\mathrm{skip}}
=
\hat P(\mathcal K)
-
\hat P(\mathcal K^{\mathrm{eff}}).
\]

---

## 6. Reserve 식의 핵심 의미를 설명하는 문장

### 바로 적용 가능한 문장

> **Admission-aware reserve.**
> Pacing first takes the larger of the historical sequence-duration quantile \(C_\tau\) and the configured-sequence point estimate \(\hat P(\mathcal K)\) as the full-sequence reserve.
> When admission disables optional work, pacing subtracts only the predicted cost of the disabled stages.
> Therefore, workload reduction is reflected immediately, while any positive historical margin above the point estimate is preserved.

이 문장이 현재 식의 의미를 가장 잘 설명한다.

### 수학적으로 보이는 성질

현재 식에서는

\[
\hat C-\hat P(\mathcal K^{\mathrm{eff}})
=
\max(0,C_\tau-\hat P(\mathcal K)).
\]

즉 optional stage가 skip되어도 **full-sequence point estimate 위에 존재하던 absolute historical headroom은 그대로 유지**된다.

이를 본문에서 한 문장으로 표현하려면:

> In particular, disabling stages does not remove an existing historical headroom: the margin above the effective point estimate remains \(\max(0,C_\tau-\hat P(\mathcal K))\).

### 예시

Admission 전:

\[
\hat P(\mathcal K)=100,\quad C_\tau=120
\]

이면 full reserve는 120이고, headroom은 20이다.

Bokeh skip 후:

\[
\hat P(\mathcal K^{\mathrm{eff}})=60
\]

이면 disabled cost는 40이므로

\[
\hat C=120-40=80.
\]

즉:

- workload: 100 → 60
- reserve: 120 → 80
- historical headroom: 20 → 20

Admission이 줄인 workload는 반영하지만, 기존 headroom은 유지된다.

---

## 7. \(C_\tau < \hat P(\mathcal K)\)인 경우의 해석

예를 들어:

\[
\hat P(\mathcal K)=100,\quad C_\tau=95
\]

이면 admission 전부터

\[
\hat C_{\mathrm{full}}=100
\]

이다.

즉 historical quantile이 point estimate보다 작기 때문에 추가 headroom은 원래부터 0이다.

Admission으로 effective point estimate가 60이 되면

\[
\hat C=60.
\]

이를 “skip 때문에 보수성이 사라졌다”고 설명하면 안 된다.

정확한 해석은:

> the historical quantile did not provide additional headroom before the skip, so the reserve remains at the effective point estimate after the skip.

---

## 8. Reserve를 `upper bound`라고 부르지 않는 것을 권장

Pacing reserve는 admission의 residual-calibrated upper estimate와 역할이 다르다.

권장 표현:

- `pacing reserve`
- `sequence-level reserve`
- `historical completion reserve`
- `deadline-pressure reserve`

피하는 표현:

- `statistical upper bound`
- `guaranteed bound`
- `safe upper bound`

현재 reserve는 **early pacing heuristic을 위한 sequence-level reserve**라고 두는 것이 가장 자연스럽다.

---

## 9. Algorithm 3에 반영할 reserve 계산

현재 Algorithm 3에 reserve 계산 line이 있다면 다음 형태를 추천한다.

```text
fullReserve ← max(C_tau, P_hat(K_i))
disabledCost ← P_hat(K_i) - P_hat(K_i_eff)
C_hat ← fullReserve - disabledCost
```

이 표현이 기존 식보다 훨씬 읽기 쉽다.

또는 한 줄:

```text
C_hat ← max(C_tau, P_hat(K_i))
        - (P_hat(K_i) - P_hat(K_i_eff))
```

로직은 기존 수식과 완전히 동일하다.

---

## 10. Algorithm 1과 3의 coordination이 보이게 할 것

Algorithm 1에서 Draft sequence가 시작될 때 admission 결과로 effective sequence가 정해진 뒤,
pacing이 해당 effective sequence를 반영한다는 연결점이 보여야 한다.

예:

```text
K_i_eff ← ApplyAdmissionState(K_i, D)
pacing.ReconcileSequenceStart(i, K_i, K_i_eff)
```

함수명은 실제 구현 이름일 필요가 없다.

중요한 것은 다음 흐름이 보이는 것이다.

1. Admission state 결정
2. Effective workload 결정
3. Pacing reserve 재계산
4. 다음 arrival에 대한 delay 판단

---

## 11. 전체 설계 철학을 한 문단으로 묶는 문장

3.4 끝 또는 3.1 overview 마지막에 다음과 같이 정리할 수 있다.

> Pacing and admission operate at different control points.
> Pacing reacts early to queue-level deadline pressure and slows future arrivals before backlog becomes critical.
> Because this projection is intentionally coarse and responsiveness-sensitive, it does not attempt to eliminate all future risk.
> Admission then performs a per-capture remaining-budget check at the draft worker and removes optional work when necessary.

이 문단은 cold start, pacing deadline, `1/2`, reserve heuristic을 모두 하나의 control philosophy로 연결해준다.

---

## 12. 최종 적용 우선순위

### 반드시 반영

1. Cold start를 release prerequisite + runtime bootstrap으로 설명
2. Residual이 pre-execution prediction을 사용한다고 명시
3. Pacing deadline을 queue-pressure signal이라고 명시
4. `1/2`를 admission과 역할을 나누는 coordination heuristic으로 설명
5. Reserve 식을 `full reserve − disabled workload`로 재표현

### 있으면 좋은 보완

6. Algorithm 1에서 sequence-start pacing reconciliation 연결
7. Reserve를 upper bound가 아니라 pacing reserve로 명명
8. Historical headroom 보존 성질 한 문장 추가

---

## 최종 판단

이 버전에서는 **알고리즘을 유지해도 충분히 방어 가능하다.**

중요한 것은 알고리즘의 개수를 늘리는 것이 아니라,
각 알고리즘이 다음 역할을 명확히 드러내는 것이다.

- Admission: per-capture feasibility correction
- Pacing: early queue-pressure reduction
- Cold start: runtime model bootstrap
- Reserve: full-sequence reserve에서 disabled workload만 제거
- `1/2`: responsiveness를 위해 pacing과 admission에 safety burden을 분산하는 heuristic

이렇게 정리하면 현재 구현과 실험을 변경하지 않고도 방법론의 설계 의도를 훨씬 쉽게 납득시킬 수 있다.
