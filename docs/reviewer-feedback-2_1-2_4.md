# 2.1--2.4절 리뷰 피드백

## 검토 범위

이 문서는 SEIP 리뷰어의 관점에서 다음 원고와 포함된 그림 및 표를 검토한 결과를 기록한다.

- `2_1_release_process.tex`
- `2_2_parallel_capture.tex`
- `2_3_draft_sequence.tex`
- `2_4_static_safeguards.tex`
- `figures/fig_draft_overlap.tex`
- `figures/fig_camera_pipeline.tex`
- `tables/tab_timeout_index.tex`

검토의 초점은 처음 읽을 때 바로 이해되지 않는 부분, 현재 제시된 근거만으로 쉽게 납득하기 어려운 주장, 제출 전 바로잡아야 할 불일치이다. 전체 서사의 방향은 다음과 같이 타당하다.

```text
출시를 막는 산업 문제
-> 병렬 촬영이 capture 간 deadline 경합을 증가시킴
-> 직렬 실행되고 점점 무거워진 Draft Sequence가 원인을 설명함
-> 정적 safeguard로 capture별 deadline 위험을 관리하기 어려움
-> runtime admission과 pacing의 필요성이 도출됨
```

가장 우선적으로 해결해야 할 문제는 2.4절의 실험 기호와 수치 불일치이다. 그다음으로 실험 절차의 누락과 2.1--2.3절의 이벤트 시점 및 인과관계를 명확히 해야 한다.

## 리뷰 피드백

### 1. M/S가 정의되지 않았고 표는 B/F를 사용한다

**위치:** `2_3_draft_sequence.tex:17`, `2_4_static_safeguards.tex:11-12`, `tables/tab_timeout_index.tex:61-64`

2.3절은 lightweight multi-frame stage를 설명하지만 기호 M을 부여하지 않는다. 그런데 2.4절은 M과 S가 앞에서 이미 정의된 것처럼 사용하며, 표에서는 다시 B와 B+F를 사용한다. 따라서 독자는 M이 B이고 S가 F인지 알 수 없다.

**필요한 수정:** 2.3절에서 기존 single-frame stage S와 연구 대상 multi-frame stage M을 명시적으로 정의한다. 본문, 표, 캡션, 범례를 모두 M과 M+S로 통일한다.

### 2. 본문의 핵심 수치가 표와 충돌한다

**위치:** `2_4_static_safeguards.tex:22`, `tables/tab_timeout_index.tex:75-78`

Level 3, 24MP, memory-pressure 조건에서 본문은 M의 첫 실패가 15번째 capture라고 서술하지만, 대응하는 표의 값은 16으로 보인다. M+S의 값 7은 본문과 표가 일치한다. 또한 다음 본문 문장은 15번의 capture가 성공하고 16번째에서 실패했다는 해석을 뒷받침한다.

**필요한 수정:** 원시 trace를 다시 확인하여 “15번째 capture에서 첫 실패”인지 “15번 성공한 뒤 16번째 capture에서 첫 실패”인지 확정한다. 본문과 표를 정확히 일치시킨다.

### 3. first-timeout 값을 해석하기 위한 실험 절차가 부족하다

**위치:** `2_4_static_safeguards.tex:13-17`, `tables/tab_timeout_index.tex:6-11`

현재 원고에는 다음 정보가 없다.

- 조건별 burst 반복 횟수
- 각 Overheat Level에 도달하고 이를 유지한 방법
- memory pressure를 생성하고 정량화한 방법
- production guard를 우회한 방법
- 각 표 셀이 단일 burst인지, 반복 실험의 집계 결과인지
- timeout이 없음을 나타내는 대시가 몇 회의 실험을 대표하는지

표 소스에도 raw trace와 셀의 대응 관계 및 guard 우회 절차에 관한 evidence TODO가 남아 있다. 이 정보가 없으면 리뷰어는 표가 반복 가능한 tail behavior를 보여주는지, 하나의 사례성 trace만 보여주는지 판단할 수 없다.

**필요한 수정:** 간결한 실험 프로토콜과 집계 방식을 추가한다. 제출 전에 각 셀과 원시 trace의 대응 관계를 확정한다.

### 4. 익명화와 용어 사용이 일관되지 않다

**위치:** `2_4_static_safeguards.tex:13-15`, `tables/tab_timeout_index.tex:44`, `tables/tab_timeout_index.tex:61-66`

본문은 장치를 anonymized flagship이라고 부르지만 표에는 `S948U`가 표시된다. 본문과 캡션에는 기밀 shot-mode 명칭이 남아 있으며, 표의 B/F 표기는 본문의 M/S 익명화와도 일치하지 않는다.

**필요한 수정:** `S948U`가 익명화된 별칭이라면 그 사실을 밝히고, 아니라면 `Device H`와 같은 중립적인 식별자로 바꾼다. 기밀 mode 용어를 프로젝트에서 정한 익명 용어로 교체하고, 제출 패키지를 만들기 전에 소스 주석도 점검한다.

### 5. 2.2절이 Draft Sequence의 성질을 설명하기 전에 이를 전제로 사용한다

**위치:** `2_2_parallel_capture.tex:4-11`, `2_3_draft_sequence.tex:4-23`

2.2절의 contention 설명은 Draft Sequence가 하나의 worker에서 직렬 실행된다는 사실에 의존한다. 그러나 Draft path와 이러한 production 설계의 이유는 2.3절에서야 설명된다. 독자는 자연스럽게 “Draft worker를 하나 더 추가하면 되지 않는가?”라는 의문을 갖게 된다.

교수님이 요청한 절 순서는 유지해야 한다. 해결책은 반드시 2.3절을 2.2절 앞으로 옮기는 것이 아니라, 2.1--2.2절에서 필요한 만큼만 Draft Sequence를 black box로 정의하고 2.3절에서 상세 설명이 이어진다는 점을 명시하는 것이다.

**필요한 수정:** contention을 이해하는 데 필요한 Draft의 deadline 관련 출력과 single-worker 실행 사실만 먼저 소개한다. 2.2절 마지막에서 2.3절이 ordered execution과 증가한 Draft cost를 설명한다고 예고한다.

### 6. Capture Timeout의 시작과 종료 사건이 모호하다

**위치:** `2_1_release_process.tex:10-12`

`request acceptance`가 application, framework, HAL 중 어디에서 발생하는 사건인지 알기 어렵다. 종료 시점 역시 Draft 계산 완료, 저장 완료, publication, 사용자 표시 중 어느 것인지 불분명하다. Final post-processing이 이 deadline에 포함되지 않는다는 점도 명시적이지 않다.

**필요한 수정:** 두 timestamp를 행위자와 관찰 가능한 사건으로 정의한다. 예를 들면 다음과 같은 timeline을 제시할 수 있다.

```text
capture request accepted and timeout clock started
-> frames and metadata collected
-> Draft waits for and obtains the worker
-> Draft encoded, stored, and/or published
-> timeout obligation completed
```

어떤 Draft 사건이 제품 deadline을 종료하는지 정확히 밝힌다. 실제 계약이 그렇다면 final post-processing은 이 deadline에서 제외된다고 명시한다.

### 7. deadline의 중첩만으로 backlog가 누적되는 것은 아니다

**위치:** `2_2_parallel_capture.tex:9-11`

현재 표현은 parallel capture가 자동으로 queue 증가를 일으키는 것처럼 읽힐 수 있다. Backlog는 capture가 들어오는 속도가 하나의 Draft worker가 sequence를 처리하는 속도보다 빠를 때 누적된다. `its own processing time`도 queueing을 포함하는지 불분명하다.

**필요한 수정:** arrival rate와 service rate의 조건을 명시한다. 의도한 의미가 순수 Draft 실행시간이라면 `own processing time`을 `Draft execution duration`으로 좁힌다.

### 8. Figure 1의 queueing-delay 용어가 이후 정의와 일치하지 않는다

**위치:** `2_2_parallel_capture.tex:11-17`, `figures/fig_draft_overlap.tex:20-26`, `figures/fig_draft_overlap.tex:54-58`, `figures/fig_draft_overlap.tex:74-81`

그림은 빗금으로 표시된 worker 대기 구간만 Draft queueing delay라고 부른다. 반면 이후 문제 정의에서는 capture acceptance부터 Draft worker 시작까지의 전체 경과시간을 queueing delay로 사용하는데, 여기에는 frame 및 metadata collection도 포함된다. 캡션에서도 이 timeline이 실측인지 개념도인지 알 수 없다.

**필요한 수정:** 전체 pre-Draft delay와 그 하위 요소인 collection 및 worker waiting을 구분한다. 용어를 이후 수식과 일치시킨다. 동일한 Draft 실행시간에도 capture 간 대기가 누적되어 후속 capture가 timeout에 도달한다는 점을 캡션에서 설명한다.

### 9. Draft pipeline 설명이 내부적으로 충돌해 보인다

**위치:** `2_3_draft_sequence.tex:5-8`, `2_3_draft_sequence.tex:14-18`, `figures/fig_camera_pipeline.tex:42-43`, `figures/fig_camera_pipeline.tex:70-77`

초기 정의에서는 Draft Sequence가 대표 frame 하나를 선택하여 저장한다고 설명하지만, 연구 대상 확장은 lightweight multi-frame processing을 수행한다. 또한 `In parallel`은 시간적으로 동시 실행되는 것처럼 읽히지만, 뒤의 문단과 그림에서는 final processing을 application이 background에 진입할 때까지 미룬다. 그림만 보면 모든 capture mode가 final processing을 background까지 미루는 것으로 오해할 수도 있다.

**필요한 수정:** baseline Draft와 확장된 Draft를 구분하거나, Draft 생성을 여러 입력 frame까지 포함할 수 있는 일반적인 표현으로 정의한다. 실제로 동시에 실행되는 것이 아니라면 두 branch를 logical path라고 표현한다. Figure 2가 모든 mode가 아니라 background-deferred target configuration을 나타낸다고 범위를 한정한다.

### 10. 하나의 Draft Sequence 내부 stage의 순서와 역할이 보이지 않는다

**위치:** `2_3_draft_sequence.tex:13-23`

현재 `ordered single-worker execution`은 capture 사이의 실행 순서만 설명한다. 하나의 Draft Sequence 안에서 각 stage가 어떤 순서로 실행되는지는 보여주지 않는다. 따라서 이후에 등장하는 complete remaining suffix 기반 admission 요구가 충분한 준비 없이 갑자기 제시된다.

**필요한 수정:** 익명화된 대표 sequence를 추가하고 optional work와 mandatory work를 구분한다. 예를 들면 다음과 같다.

```text
optional M -> intermediate Draft processing -> optional S -> mandatory encode-and-save
```

M과 M+S가 동일한 mandatory completion tail 위에서 선택되는 optional configuration임을 밝힌다.

### 11. single-worker 근거만으로 bounded concurrency 대안을 충분히 반박하지 못한다

**위치:** `2_3_draft_sequence.tex:20-23`

Concurrency가 compute와 memory 수요를 증가시킨다는 사실만으로는 two-worker와 ordered commit buffer를 사용하는 대안을 배제할 수 없다. 리뷰어는 admission과 pacing보다 worker를 제한적으로 추가하는 방식이 단순한 대안이라고 생각할 수 있다.

**필요한 수정:** single worker가 의도적인 production backpressure 선택임을 설명한다. Capture-order publication 및 storage, 순서가 뒤바뀐 결과를 보관하는 memory 비용, preview 및 capture와의 자원 경쟁을 포함한다. Draft의 병렬 실행이 이론적으로 불가능하다고 주장하기보다 production trade-off로 제시한다.

### 12. M의 배포 상태와 thermal guard의 적용 범위가 불분명하다

**위치:** `2_3_draft_sequence.tex:17`, `2_4_static_safeguards.tex:6`, `2_4_static_safeguards.tex:11`

`We have investigated extending`은 M이 아직 초기 아이디어인 것처럼 들리지만, 2.4절에서는 deployed guard를 우회한 뒤 구현된 workload를 평가한다. M이 prototype인지, production에서 활성화된 기능인지, release evaluation 중인 기능인지 알기 어렵다. `disables all Draft image-processing`은 mandatory encoding과 recovery Draft까지 중단하는 것처럼 읽힌다.

**필요한 수정:** 구현 근거가 뒷받침하는 범위에서 S는 기존 production baseline이고 M은 구현되어 평가 중인 prototype 또는 candidate라고 구분한다. Guard의 적용 범위를 optional Draft effect stage로 한정하고 mandatory completion path는 계속 실행된다고 밝힌다.

### 13. Overheat Level과 30-capture 설정의 근거가 부족하다

**위치:** `2_4_static_safeguards.tex:6-7`, `2_4_static_safeguards.tex:13-16`

Level 0--6이 vendor-specific ordinal scale인지, 높은 값이 무엇을 의미하는지 정의되지 않는다. `Level 4 is readily reached`도 실제 빈도나 범위가 한정된 validation 관찰 없이 강하게 들린다. 한 장치에서 관찰된 12개의 pending Draft Sequence와 다른 장치의 30-capture burst가 어떻게 대응하는지도 정량적으로 설명되지 않는다.

**필요한 수정:** Overheat Level의 scale과 방향을 정의하고 Level 4 관련 관찰의 범위를 한정한다. 30-capture trace가 만든 pending count 또는 queueing delay를 제시하고, 이전 incident와 비교 가능한 이유 및 모든 level에서 이 burst 길이를 사용한 이유를 설명한다.

### 14. `misclassifies in both directions`는 현재 근거보다 강하다

**위치:** `2_4_static_safeguards.tex:21-26`

실패 전까지 15회의 실행이 성공했다는 사실만으로 보수적인 configuration-level release guard가 false positive라고 단정할 수는 없다. 현재 evidence는 관찰된 trace 초반에 성공 가능한 실행 기회를 guard가 포기한다는 점은 보여주지만, 해당 조건이 반복적으로 안전하다는 점까지 증명하지는 않는다.

**필요한 수정:** 반복 근거가 없다면 `the guard suppresses early executions that completed within the deadline in this trace`와 같이 관찰된 실행 기회로 주장을 제한한다. 더 넓은 evidence가 없다면 `supported operating range`도 `tested conditions on the measured device`로 낮춘다.

### 15. Shot-to-Shot 열이 정의되지도 분석되지도 않는다

**위치:** `tables/tab_timeout_index.tex:50-64`, `2_4_static_safeguards.tex:17`, `2_4_static_safeguards.tex:21-26`

표에는 367--702 ms의 Shot-to-Shot 값이 있지만, PDF만으로는 어떤 configuration과 집계 방식을 사용한 값인지 알 수 없다. Arrival rate는 backlog에 직접 영향을 주기 때문에 이 열은 부수적인 정보가 아니라 잠재적으로 중요한 설명 변수이다.

**필요한 수정:** 캡션 또는 table note에서 측정 조건과 통계량을 정의하고, 변화한 arrival interval이 Draft service time과 어떻게 상호작용하는지 설명한다. 본문에서 사용하지 않는 정보라면 이 열을 제거한다.

### 16. 현재 결과는 pacing보다 admission의 필요성을 더 직접적으로 보여준다

**위치:** `2_4_static_safeguards.tex:28-32`

표는 thermal-only cutoff가 capture별 상황을 충분히 구분하지 못한다는 점을 보여준다. 그러나 표만으로 capture pacing이 유일하게 필요한 다음 단계라고 증명되지는 않는다. 리뷰어는 late capture에서 M을 skip하거나 다차원 static policy를 사용하면 되지 않는지 질문할 수 있다.

**필요한 수정:** Admission은 queueing으로 이미 소모된 deadline budget을 회복할 수 없고 mandatory completion tail도 실행 불가능해질 수 있다는 점을 설명한다. 대안을 충분히 배제하지 않았다면 `require`보다 `motivate`를 사용한다. `captureAvailable`을 늦추면 shot-to-shot interval이 증가할 수 있다는 pacing 비용도 즉시 함께 제시한다.

### 17. 2.1절은 release 중요성에 비해 사용자에게 발생하는 영향을 충분히 설명하지 않는다

**위치:** `2_1_release_process.tex:4-14`

`one of the highest-priority KPIs`는 timeout이 실제 capture에 어떤 영향을 주는지 설명하지 않아 홍보성 표현처럼 보일 수 있다. 일반적인 release process 설명은 이해되지만, 실패의 구체적인 결과보다 더 많은 공간을 차지한다.

**필요한 수정:** 프로젝트 evidence가 뒷받침하는 범위에서 missing result, failed capture, subsequent capture failure와 같은 구체적인 결과를 한 문장으로 연결한다. 최상급 KPI 표현보다 hard release gate라는 운영 사실을 강조한다. Daily validation이 모든 지원 조합을 의미하는지 선별된 test matrix를 의미하는지도 실제 범위에 맞게 한정한다.

## 교수님이 요청한 순서를 유지하는 수정 방향

교수님이 요청한 서술 순서는 다음과 같다.

```text
산업 문제
-> 산업 문제를 악화시킨 parallel capture의 등장
-> Draft Sequence의 상세 설명
```

이 순서는 그대로 유지할 수 있다. 이해 문제는 progressive disclosure로 해결한다. 2.1--2.2절에서는 Draft Sequence를 deadline과 관련된 black box로 취급하고, 2.3절에서 내부 구조와 production 제약을 상세히 설명한다.

### 2.1절: 산업 문제를 제시하고 Draft completion을 최소한으로 정의한다

2.1절에서는 다음을 확립해야 한다.

1. Capture Timeout이 제품 및 release 문제인 이유
2. Timeout clock의 정확한 시작과 종료 사건
3. Draft image가 이 deadline path에서 제공되는 early result라는 사실
4. Parallel capture가 deadline을 가진 request의 arrival pattern을 바꾼다는 예고

2.1절의 마지막에는 다음과 같은 연결 문장을 사용할 수 있다.

> Under serial capture admission, the application waits for the preceding Draft image before starting another capture. Parallel capture was introduced to shorten this wait, but it also changed how multiple capture requests compete for the fixed deadline.

이 문장은 Draft 내부를 미리 설명하지 않으면서 2.2절의 필요성을 만든다.

### 2.2절: Parallel capture를 산업 문제의 악화 요인으로 제시한다

먼저 parallel capture의 본래 목적을 설명한다.

> Parallel capture was introduced to reduce the shot-to-shot interval by allowing the application to start a new capture before the preceding Draft image becomes available.

그다음 이벤트 순서를 운영 관점에서 정의한다.

> In this product-specific protocol, the HAL issues `captureAvailable` to indicate that the application may submit another capture request. Once the request is accepted, a new Capture Timeout clock starts even if the preceding capture has not completed its Draft Sequence.

Deadline의 중첩 자체가 아니라 backlog가 누적되는 조건을 명시한다.

> Draft Sequences, however, are processed in capture order by a single worker. When captures are admitted faster than this worker completes them, later captures spend an increasing portion of their deadline waiting for earlier Draft Sequences.

2.2절 마지막에서는 내부 설명이 다음 절에 의도적으로 배치되었음을 알려야 한다.

> This cross-shot contention arises from two production properties: ordered single-worker Draft execution and the growing processing cost of each Draft Sequence. Section~\ref{sec:draft-background} explains these properties in detail.

이렇게 하면 필요한 설명이 빠진 것이 아니라 다음 절에서 원인을 분석하기 위해 의도적으로 미뤄진 것으로 읽힌다.

### 2.3절: Draft path가 직렬 실행되고 점점 무거워진 이유를 설명한다

2.3절은 2.2절에서 생긴 질문에 다음 순서로 답하는 것이 좋다.

1. Draft Sequence는 무엇을 만들며 왜 reliability-critical한가?
2. Production에서는 왜 single-worker ordered execution을 사용하는가?
3. 하나의 sequence에는 어떤 stage가 있고 각각 optional인지 mandatory인지?
4. M과 S의 추가가 capture별 service demand를 어떻게 증가시켰는가?
5. 이 service demand가 parallel capture의 빠른 arrival과 결합해 어떻게 backlog를 만드는가?

현재의 서술 순서가 역사적 도입 순서로 오해되지 않도록 2.3절을 다음 문장으로 시작할 수 있다.

> The Draft Sequence was introduced together with the final post-processing pipeline; parallel capture did not create this path, but allowed multiple active capture deadlines to compete for its single worker.

Draft path와 final path를 설명한 뒤, 현재의 **Ordered single-worker execution** 문단을 **Increasing Draft workload**보다 먼저 배치하는 것이 좋다. Production 설계의 이유도 다음과 같이 강화할 수 있다.

> The framework deliberately executes Draft Sequences on one worker in capture order. This design preserves ordered publication and storage while bounding active Draft compute and memory demand. A concurrent design would require an out-of-order result buffer and would make multiple Draft workloads compete with preview and capture processing.

그다음 연구 대상 workload를 실행 순서에 맞게 정의한다.

> A Draft Sequence consists of optional image-processing stages followed by mandatory encoding and storage. In the target configuration, the sequence may execute the lightweight multi-frame stage M, the existing single-frame stage S, and the mandatory completion tail.

2.2절과 2.3절의 인과관계는 다음 문장처럼 명시적으로 종합한다.

> Parallel capture increases the rate at which Draft work arrives, whereas the addition of M and S increases the service demand of each capture. Their combination causes queueing delay to accumulate across a burst, leaving later captures with less budget for their own Draft processing.

이 연결이 2.2절과 2.3절의 핵심이다. Parallel capture는 arrival을 증가시키고, Draft 확장은 service demand를 증가시킨다.

### 2.3절에서 2.4절로의 연결

2.3절 마지막에서 기존 production 대응과 그 한계를 예고한다.

> Production systems have traditionally contained this risk using static thermal and queue-length safeguards. However, these safeguards do not account for the capture-specific combination of accumulated waiting time and remaining Draft cost.

이 문장이 있으면 2.4절의 static thermal guard가 갑작스럽게 등장하지 않는다.

## 권장 수정 우선순위

1. M/S/B/F 기호와 수치 충돌을 해결한다.
2. 실험 evidence chain을 완성하고 절차를 문서화한다.
3. 교수님이 요청한 절 순서를 유지하면서 black-box에서 white-box로 이어지는 transition을 추가한다.
4. Capture Timeout과 `captureAvailable`의 정확한 timeline을 정의한다.
5. Draft 내부 sequence, single-worker 제약, workload 증가를 명확히 한다.
6. 근거보다 강한 일반화를 낮추고 pacing의 trade-off를 함께 제시한다.
