# SEIP-27 Chapter 3 (3.1–3.4) Review

## 전체 판정

큰 방향은 맞습니다. 교수님 스타일을 알고리즘의 외형뿐 아니라 본문을 전개하는 방식까지 상당히 잘 가져왔습니다. 특히 알고리즘의 단계와 본문 소제목을 대응시킨 구성은 유지하는 편이 좋겠습니다.

다만, **“잘 읽히는 방법론 장”에는 가까워졌지만, “리뷰어가 추가 가정을 하지 않고 알고리즘을 납득할 수 있는 상태”까지 완성되지는 않았습니다.** 남아 있는 문제는 대부분 영어 문체가 아니라 **초기 상태의 처리, 예측값의 기준 시점, pacing이 관리하는 시간·큐 상태의 정의**입니다.

확인한 `Update 3_4` 커밋(`5667295`)의 3.1–3.4와 세 알고리즘을 기준으로 평가했습니다. 교수님 논문은 **TOPSEED와 ParaSuit 원문을 대조**했습니다. 말씀하신 세 번째 파일은 확인하지 못해, 문체 비교는 이 두 편을 기준으로 했습니다. 이번 평가는 방법론 서술과 의사코드에 대한 것이며, 실제 구현 코드의 동작까지 검증한 결과는 아닙니다.

| 평가 항목 | 제 판단 |
|---|---|
| 교수님 스타일과의 일치 | **높음.** 알고리즘 중심의 단계별 설명 방식이 잘 맞습니다. |
| 3.1–3.4의 구성 | **적절함.** 전체 흐름 → 공통 추정기 → admission → pacing의 순서를 유지하면 됩니다. |
| 처음 읽을 때의 이해도 | **전체 아이디어는 명확함.** 다만 3.4에서는 상태와 시간 기준을 다시 읽게 됩니다. |
| 알고리즘과 본문의 일치 | **주요 동작은 일치하지만, 중요한 전제 일부가 본문이나 보조 함수 안에만 있습니다.** |
| 현재 상태의 ACCEPT 준비도 | **방법론 장만 놓고는 Borderline–Weak Accept 경계입니다.** 안정적으로 ACCEPT를 지지하려면 아래 핵심 사항을 닫아야 합니다. |

핵심은 다음과 같습니다.

> **구성이나 문체 때문에 다시 써야 하는 원고는 아닙니다. 다만, 알고리즘이 정확히 어떤 상태에서 어떤 근거로 판단하는지 설명이 덜 끝난 부분이 있습니다.**

---

## 1. 교수님 스타일대로 작성되었는가?

### 상당히 잘 맞는 부분

TOPSEED는 전체 상호작용을 먼저 소개한 다음, 주요 알고리즘을 제시하고 `Gather → Select → Learn`의 단계에 맞춰 설명합니다. ParaSuit 역시 알고리즘의 입력·출력과 초기 상태를 설명한 뒤, 각 단계의 목적과 구체적인 계산을 연결합니다. 단순히 줄 번호를 따라 읽는 것이 아니라 **“이 단계에서 무엇을 얻으려는가 → 어떻게 계산하는가 → 왜 이 계산이 필요한가”**의 순서를 사용합니다.

현재 원고의 다음 구성이 그 방식과 잘 맞습니다.

- **3.1:** 전체 capture workflow와 두 제어 지점 소개.
- **3.3:** `Estimation → Decision → Calibration`.
- **3.4:** `Projection → Decision → Reconciliation`.

특히 3.3과 3.4에서 **알고리즘의 단계 이름을 본문 설명의 기준으로 사용한 점**이 좋습니다. 독자가 알고리즘과 본문을 오갈 때 같은 작업을 다른 이름으로 다시 해석하지 않아도 됩니다.

또한 교수님 스타일을 따른다는 이유로 모든 보조 함수를 알고리즘 안에 펼쳐 쓸 필요는 없습니다. ParaSuit도 `Score`, `Select`, `Sample` 같은 함수를 추상화하고, 본문에서 필요한 의미를 설명합니다. **현재의 보조 함수 활용 자체는 타당합니다.**

### 아직 차이가 나는 부분: 중요한 설계 선택에서는 ‘왜’가 한 문장 더 필요합니다

현재 원고는 **무엇을 계산하는지**는 비교적 잘 설명합니다. 반면, 아래와 같은 결정에서는 독자가 스스로 이유를 보충해야 합니다.

> 왜 이 deadline을 압력의 기준으로 삼는가?  
> 왜 현재 capture의 작업을 이 시점에 가상 backlog에 반영하는가?  
> 왜 과거 전체 sequence의 처리시간에서 현재 configured sequence의 점추정값을 빼는가?

이것은 영어 연결어나 표현을 바꿔서 해결할 문제라기보다, **각 계산이 해결하는 문제와 그 계산의 한계를 짧게 명시해야 하는 문제**입니다.

따라서 교수님 스타일에 더 가깝게 만들려면 `At line ...` 문장을 늘리기보다, 중요한 계산 앞이나 뒤에 다음 종류의 설명을 넣는 것이 효과적입니다.

> **이 값은 무엇을 나타내며, 왜 다른 값이 아니라 이것을 사용하는가?**

**현재 구조는 유지하고, 핵심 설계 선택의 근거만 보강하는 것이 맞습니다.**

---

## 2. 절별 평가

### 3.1 — 전체 흐름과 제어 목적은 잘 잡혔습니다

가장 좋은 점은 admission과 pacing을 단순히 두 기능으로 나열하지 않고, **같은 deadline margin에 서로 다른 방향으로 작용하는 제어 수단**으로 설명했다는 것입니다.

\[
\mu_i=\mu_{i-1}+\delta_i-\pi_i
\]

여기서 admission은 완료 간격을 줄이는 쪽으로, pacing은 다음 요청 간격을 늘리는 쪽으로 작용합니다. 이어서 admission이 이미 소비된 대기시간을 되돌릴 수 없고, pacing이 이미 시작된 작업을 바꿀 수 없다는 설명도 두 제어의 상보성을 이해하는 데 도움이 됩니다.

이 수식은 **margin 변화의 관계를 설명하는 식**으로 충분히 유용합니다. 이를 최적 제어법이나 안전성 증명으로 확장할 필요는 없습니다.

Algorithm 1의 이벤트 기반 구성도 타당합니다. `Capture` procedure와 여러 `upon` handler를 분리한 것은 비동기 capture workflow에 맞습니다. 이를 억지로 하나의 순차 procedure 안에 넣거나, 비동기적으로 생성되는 이미지를 형식상 `Output`으로 붙일 필요는 없습니다.

다만 초기화 부분에는 **predictor와 두 controller가 capture마다 재생성되는 것이 아니라 지속적으로 유지된다는 점**을 짧은 주석으로 분명히 해두면 좋겠습니다. 의도는 본문에서 이해되지만, 알고리즘만 보는 독자에게도 수명이 드러나면 더 좋습니다.

### 3.2 — 역할 분리가 좋습니다. 갱신에 사용하는 표본의 범위만 더 명확하면 됩니다

공통 점추정기를 3.2에 두고, 잔차에 따른 상향 보정을 admission 쪽에서 설명하는 분리는 좋습니다. 독자가 “기본 처리시간 예측”과 “그 예측의 과소추정을 반영하는 보정”을 구분할 수 있습니다.

현재는 이전 baseline으로 비율을 계산하고, 이전 \(\gamma\)로 관측값을 정규화한 다음, baseline과 \(\gamma\)를 갱신하는 순서까지 설명합니다. **별도의 알고리즘을 추가하지 않아도 되는 정도의 구성입니다.**

다만 \(\gamma\)를 갱신할 때 사용하는 **recorded ratios의 범위**는 명시하는 편이 좋습니다.

현재 완료된 sequence에서 얻은 비율들의 median인지, 여러 완료 sequence에서 유지한 이력의 median인지에 따라 적응 속도와 의미가 달라집니다. 이것은 용어 취향이 아니라 **같은 추정기를 재구현하는 데 필요한 정보**입니다.

### 3.3 — 설명 구조는 가장 안정적입니다. 그러나 cold start와 예외 경로를 정리해야 합니다

전체 remaining sequence를 기준으로 optional stage의 실행 여부를 판단하고, 그룹별 실행 중단을 유지하며, 완료 후 관측으로 보정하는 흐름은 잘 보입니다.

또한 stage별 \(\max(\hat p,p)\)를 합산하는 잔차 정의는, 다른 stage가 빨리 끝났다는 이유로 특정 stage의 지연이 상쇄되지 않게 하려는 목적이 분명합니다. **이런 “계산과 이유의 연결”은 교수님 스타일에 잘 맞는 부분입니다.**

문제는 아래에서 설명할 **cold-start 예외와 calibration의 초기 상태**입니다.

### 3.4 — 가장 중요한 기여가 담겼지만, 아직 가장 많이 되읽게 되는 절입니다

`Projection → Decision → Reconciliation`은 좋은 구분입니다. 특히 admission에 의해 줄어든 workload를 pacing에 반영한다는 점이 두 모듈의 결합을 보여줍니다.

하지만 현재 독자는 `\hat t_{\mathrm{queue}}`, `timeout_queue`, `ExtendBacklog`, `RebaseBacklog`를 이해하면서 **물리적인 큐와 가상으로 예약한 작업을 머릿속에서 따로 조립해야 합니다.** 주요 계산은 보이지만, 그 계산에 들어가는 상태의 의미가 충분히 닫혀 있지는 않습니다.

**현재 원고에서 가장 우선적으로 다듬을 절은 3.4입니다.**

---

## 3. ACCEPT 판단에 직접 영향을 줄 핵심 사항

### ① Cold start: ‘큐가 비었다’와 ‘남은 예산이 충분하다’를 분리해야 합니다

현재 admission은 다음 조건을 사용합니다.

\[
U(\mathcal K_{i,j})\le T_{i,j}
\quad\text{or}\quad
\hat P(\mathcal K_{i,j})=0.
\]

그리고 configuration은 queue가 비워진 뒤에 바뀌므로 새 configuration의 첫 capture가 fresh timeout budget으로 시작한다고 설명합니다.

여기서 두 사실은 구분해야 합니다.

**첫 capture에 이전 draft의 대기가 없을 수 있다는 것**과, **optional stage를 판단하는 시점에도 예산이 충분하다는 것**은 다릅니다. Capture가 시작된 뒤 frame 수집 등에서 시간을 소비했다면, draft queue가 비어 있어도 admission 시점의 \(T_{i,j}\)는 작을 수 있습니다.

더 직접적으로는, 현재 조건만 읽으면 **\(\hat P=0\)일 때 남은 예산의 크기와 무관하게 admit**합니다.

이것을 곧바로 구현 결함이라고 단정하는 것은 아닙니다. 초기 관측을 얻기 위한 실행을 허용하는 설계는 가능합니다. 다만 다음과 같이 구분해야 합니다.

> **초기 관측을 얻기 위한 실행 예외**인지,  
> **예산 안에 완료할 수 있다고 판단한 실행**인지.

현재 설명은 이 둘을 너무 가깝게 연결합니다.

추가로, **일부 key만 처음 보는 경우**도 정의가 필요합니다. 예를 들어 mandatory key에는 관측이 있지만 optional key에는 관측이 없다면, 전체 합은 0이 아닐 수 있습니다. 이때 신규 optional stage가 단순히 비용 0으로 들어가는 것인지, 별도의 cold-start 판단을 받는지가 분명해야 합니다.

**필요한 수정은 새로운 복잡한 추정기를 만드는 것이 아닙니다.** Cold start의 정확한 조건과 저예산 상태에서의 정책을 적고, queue drain을 안전성의 근거처럼 쓰지 않으면 됩니다.

현재 문장의 대안으로는 다음이 더 정확합니다.

> Configuration changes occur only after the queue drains, so the first capture under a new configuration does not wait behind an earlier draft sequence. Its remaining budget at admission still depends on the time spent before draft execution.

이 문장은 기존의 유리한 조건은 살리면서, 그 조건이 보장하지 않는 것까지 주장하지 않습니다.

---

### ② Calibration: 본문에 있는 ‘실행 전 예측값’이 알고리즘에도 드러나야 합니다

본문은 잔차를 **실행 전에 유지한 예측값**과 관측값으로 계산한다고 설명합니다. 따라서 의도는 올바릅니다.

반면 Algorithm 1에서는 먼저 `predictor.Observe`를 수행하고, 그다음 `admission.Update`를 호출합니다. Algorithm 2의 `ComputeResidualFactor` 인자에는 실행 전 예측값이 보이지 않습니다.

리뷰어는 여기서 다음을 확인하려 할 것입니다.

> “잔차는 방금 관측값으로 갱신된 predictor가 아니라, 정말 실행 전 predictor의 출력으로 계산되는가?”

**현재 구현이 잘못되었다는 뜻은 아닙니다.** 본문대로 snapshot을 저장한다면 문제가 없습니다. 다만 그것이 알고리즘에서 확인되지 않습니다.

해결은 작게 할 수 있습니다. 실행 전 예측 snapshot을 보존한다는 주석을 추가하거나, residual 계산 함수가 그 snapshot을 사용한다는 인자·설명을 넣으면 됩니다. 이미 올바른 순서로 구현되어 있다면 호출 순서를 바꿀 필요도 없습니다.

같은 맥락에서 **관측 이력이 없는 경우의 기본 동작**도 정리해야 합니다.

첫 실행처럼 잔차 이력이 비었을 때 `SelectResidualFactor`가 무엇을 반환하는지, 잔차의 분모가 0인 sequence는 어떤 방식으로 제외하는지 명시해야 합니다. 실제 구현이 기본 factor 1을 사용하는지, 다른 규칙을 사용하는지는 구현에 맞춰 적으면 됩니다.

이 부분은 알고리즘을 장황하게 만드는 보충이 아니라, **첫 실행부터 정의된 알고리즘으로 만드는 보충**입니다.

---

### ③ Pacing: ‘어느 작업을, 어느 deadline을 기준으로 계산하는가’를 명확히 해야 합니다

현재 pacing 식은 다음과 같습니다.

\[
\mathrm{delay}_i
=
\left\lceil
\frac{
\max(0,\hat B_i+2\hat C-T_{\mathrm{queue}})
}{2}
\right\rceil.
\]

여기서 가장 중요한 질문은 \(1/2\) 자체보다, **각 항이 동일한 시간·작업 기준에서 해석되는가**입니다.

#### `timeout_queue`의 생성·갱신 규칙

본문에는 newest queued capture의 deadline이라고 설명하지만, 알고리즘에는 이 값이 언제 갱신되는지 드러나지 않습니다. 빈 큐에서는 전체 timeout window를 사용한다는 본문의 규칙도 알고리즘의 계산과 직접 연결되어 있지 않습니다.

여기에는 적어도 다음 의미가 고정되어야 합니다.

> 물리적으로 enqueue된 capture만 포함하는가, 아니면 아직 enqueue되지 않았지만 pacing이 예약한 capture도 포함하는가?

이를 정의하지 않으면 독자마다 `T_queue`를 다르게 구현할 수 있습니다.

#### `ExtendBacklog`와 `RebaseBacklog`의 핵심 규칙

이 두 함수는 단순한 구현 세부 사항이 아니라 **pacing이 얼마나 많은 작업이 남았다고 판단하는지 결정하는 부분**입니다.

모든 큐 연산을 의사코드로 펼칠 필요는 없습니다. 그러나 두 함수가 현재 실행 중인 작업, 대기 작업, 아직 enqueue되지 않은 예약 작업을 어떻게 세며, 실제 enqueue 시 중복 계산을 어떻게 피하는지는 본문이나 짧은 수식으로 드러나야 합니다.

특히 현재 capture의 작업을 `now + delay` 기준으로 반영한다면, 이 시간이 **실제 current capture의 도착 시각이 아니라 가상 accounting 기준**인지 설명이 필요합니다. Delay가 직접 미루는 것은 다음 capture의 기회이기 때문입니다.

#### 오래된 deadline을 이용한 ‘압력 지표’와 다음 capture의 실제 deadline

\(\hat B_i+2\hat C\)에는 앞으로 처리할 작업이 들어가지만, \(T_{\mathrm{queue}}\)는 이미 존재하는 queued capture에서 가져옵니다.

따라서 이 비교를 **다음 capture가 자신의 deadline 안에 끝난다는 직접적인 feasibility test**처럼 읽히게 해서는 안 됩니다. 현재 선택이 의도된 것이라면, 다음과 같이 위치를 명확히 하는 편이 좋습니다.

> The queued capture’s remaining budget serves as a deadline-pressure signal, rather than the deadline of the next capture.

그다음 왜 이 신호를 쓰는지 설명해야 합니다. 예를 들면, 이미 outstanding인 capture의 예산 소진 상태를 바탕으로 새 workload를 더 넣는 것을 조절한다는 취지입니다.

**이 세 가지가 정리되면 3.4의 이해도가 크게 좋아집니다.** 현재 필요한 것은 새로운 notation을 많이 추가하는 일이 아니라, 이미 있는 상태의 의미를 고정하는 일입니다.

---

### ④ Empirical estimate에 기대는 경로를 안전성 보장처럼 표현하지 않아야 합니다

현재 watchdog 설명의 마지막에는 fallback을 통해 backlog가 cascading timeout 없이 정리된다는 취지의 표현이 있습니다. 하지만 terminal processing에 남겨두는 시간도 \(U(\mathcal K_{i,m})\)라는 경험적 추정값에 의존합니다.

여기서는 다음 둘이 다릅니다.

**“추가 optional work를 우회해 timeout 전파 위험을 줄인다.”**

**“어떤 경우에도 cascading timeout 없이 queue를 비운다.”**

현재 근거로 방어하기 쉬운 것은 전자입니다. 갑작스러운 mandatory-stage 지연까지 포함한 보장으로 읽히면, 리뷰어가 필요 이상으로 강한 안전성 논증을 요구하게 됩니다.

다음 정도가 적절합니다.

> Queued draft sequences also bypass optional processing until the queue drains, reducing the risk that an overrun propagates to subsequent captures.

마찬가지로 \(U\)도 한 번은 **empirical high-side estimate**라는 성격을 분명히 해두면 좋습니다. 경험적 상향 추정치를 사용하는 것이 문제가 아니라, 그 추정치의 성격보다 강한 결론을 쓰는 것이 문제입니다.

---

## 4. 3.4에서 추가로 확인할 중요한 계산 하나

아래 식은 admission 결과를 pacing에 반영하는 핵심입니다.

\[
\hat C
=
\hat P_{\mathrm{eff}}
+
\max\!\left(0,C_\tau-\hat P(\mathcal K_i)\right).
\]

**전체 configured workload에서 줄어든 비용을 reserve에서도 제거하려는 의도는 이해됩니다.** 다만 이 설명은 \(C_\tau\)가 어떤 workload의 관측으로 구성되어 있는지에 따라 달라집니다.

설명을 위한 가상 예를 들겠습니다. 실험 결과가 아니라 식의 해석을 확인하는 예입니다.

\[
\hat P(\mathcal K_i)=100,\qquad
\hat P_{\mathrm{eff}}=40,\qquad
C_\tau=60.
\]

이미 optional group이 비활성화된 뒤의 관측이 이력을 주로 구성해서, 실제 effective workload의 상위 처리시간이 60이라고 합시다. 그러면 현재 식은

\[
\hat C=40+\max(0,60-100)=40
\]

을 반환합니다.

즉, **이력이 이미 줄어든 workload를 반영한다면, 그 workload에서 관측된 추가 시간 20이 reserve에 남지 않을 수 있습니다.**

이것을 식의 오류라고 바로 판단할 수는 없습니다. Admission skip 이후 보수성을 줄이고 점추정값으로 돌아가는 것이 의도일 수 있기 때문입니다. 다만 다음 중 어느 설명이 실제 설계와 맞는지는 분명해야 합니다.

- **이력이 주로 demotion 이전 workload를 반영한다는 전제인지**
- 아니면 **demotion 이후에는 일부 보수성을 의도적으로 줄이는 heuristic인지**

이 부분은 교수님이나 리뷰어가 물었을 때 답이 준비되어 있어야 합니다. “disabled cost를 빼기 위한 식”이라는 설명만으로는 이력의 구성 변화까지 모두 설명되지는 않습니다.

한편 **delay를 절반으로 나누는 선택 자체를 없앨 필요는 없습니다.** 이미 coordination heuristic으로 제시한 방향은 적절합니다. 두 capture를 고려한다는 사실이 자동으로 \(1/2\)를 수학적으로 도출하는 것은 아니므로, responsiveness와 workload reduction 사이의 설계 선택이라는 점과 평가 근거를 연결하면 됩니다. 이를 최적해로 증명할 필요는 없습니다.

---

## 5. 문장 표현에서 바로 고칠 부분

문체 전반을 바꾸기보다, **대상이 잘못 읽힐 수 있는 표현**을 먼저 고치는 것이 좋습니다.

### “remaining sequence에 대해 admit/skip을 반환한다”

실제 실행 판단의 대상은 현재 optional stage이고, remaining sequence는 판단에 사용하는 비용 범위입니다. 현재 표현은 suffix 전체를 한 번에 허용하거나 거부하는 것으로 읽힐 수 있습니다.

추천 문장:

> Algorithm 2 decides whether to execute the current optional stage \(k_j\) by comparing the estimated duration of the entire remaining sequence \(\mathcal K_{i,j}\) with the remaining budget.

### “알고리즘은 계산한다” 앞에 단계의 목적을 둡니다

예를 들어 3.4의 도입에서는 상세 변수 설명에 들어가기 전에 다음 정도의 목적 문장이 도움이 됩니다.

> The goal of pacing is to limit additional capture arrivals when outstanding draft work creates deadline pressure.

그다음 Algorithm 3의 입력 상태와 delay 계산을 설명하면, 독자는 식을 보기 전에 **이 계산이 해결하려는 문제**를 알고 들어갑니다.

### `Reconciliation`이라는 이름은 유지해도 좋습니다

현재 단계가 단순한 처리시간 이력 갱신뿐 아니라, admission의 workload reduction과 완료된 작업을 pacing 상태에 반영하는 역할을 한다면 `Reconciliation`은 적절합니다. 이름을 다시 바꾸기보다, **무엇과 무엇을 일치시키는 단계인지** 첫 문장에서 설명하는 편이 좋습니다.

---

## 6. SEIP 리뷰어 관점의 최종 판단

ICSE SEIP는 산업적 관련성, 기여의 중요성, 발표 품질을 평가하며, 실제로 중요한 문제를 체계적으로 조사하고 결론을 뒷받침하는 기술적·경험적 근거를 제시할 것을 요구합니다. 따라서 이 논문에서 중요한 것은 새로운 scheduling theorem을 제시하는가보다, **산업적 제약 아래에서 제안한 제어가 명확히 정의되고, 그 선택이 실제 증거로 뒷받침되는가**입니다.

현재 방법론을 읽은 제 평가를 리뷰 문장으로 옮기면 다음에 가깝습니다.

> 실제 capture workflow의 제약에 맞춰 optional workload control과 arrival pacing을 결합한 접근은 설득력이 있다. 알고리즘에 맞춘 설명 구조도 명확하다. 다만 초기 관측이 없는 경우의 admission 정책과 pacing의 가상 backlog·deadline 상태가 충분히 명세되지 않아, 제안한 제어의 동작을 그대로 재구성하기 어렵다. 일부 fallback 설명은 경험적 추정에 의존하는 설계보다 강한 안전성을 암시한다.

따라서 **현재 상태에 대한 제 판단은 “방향이 좋은 Borderline–Weak Accept”이지, “이대로 확실히 ACCEPT”는 아닙니다.**

그렇다고 전면 재작성이나 새로운 방법론이 필요하다는 뜻도 아닙니다. 우선순위는 세 가지입니다.

1. **Cold start와 빈 이력의 동작을 정확하게 정의합니다.** 관측 확보 예외와 예산 기반 실행 판단을 구분합니다.
2. **Pacing의 시간·큐 상태를 명확하게 정의합니다.** 특히 `timeout_queue`, 가상 예약 작업, `ExtendBacklog`와 `RebaseBacklog`의 관계를 정리합니다.
3. **본문의 전제와 알고리즘을 일치시킵니다.** 실행 전 snapshot, watchdog의 추상화 범위, empirical estimate에 맞는 주장 강도를 맞춥니다.

**교수님 스타일은 이미 상당히 잘 반영되어 있습니다. 지금 더 필요한 것은 문장을 더 학술적으로 꾸미는 일이 아니라, 리뷰어가 머릿속에서 보충하고 있는 알고리즘의 전제를 원고에 명시하는 일입니다.** 이 부분이 정리되면, 적어도 3장 때문에 ACCEPT를 망설이게 되는 요소는 상당히 줄어들겠습니다.
