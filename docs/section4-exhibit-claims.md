# Section 4 exhibit claims

2026-09-16 작성. Section 4를 쓰기 **전에**, 본문은 보지 않고 `tables/`와 `figures/`의
exhibit만 읽어서 "이 표/그림에서 논문이 반드시 말해야 하는 것"을 exhibit별로 3~5개씩 뽑은
목록이다. **초안 문장이 아니다** — 각 항목은 (a) 한국어 한 줄 주장, (b) 그 주장을 떠받치는
셀과 숫자, (c) manuscript에 넣을 영문 초안 문장, (d) 그 문장과 반드시 같이 가야 하는 단서로
이루어져 있다. 내일 4장을 쓸 때 이 순서대로 문단을 만들면 된다.

여기 있는 모든 숫자는 exhibit 소스(`.tex`)에서 직접 읽었거나 `docs/exhibits.md` /
`docs/rq-evidence.md` / `data/`에서 확인한 값이고, 독립적인 숫자 검증 패스와 AGENTS.md
규칙 검증 패스를 각각 따로 거쳤다. **검증 과정에서 exhibit 자체의 결함이 여러 건 나왔다 —
문서 맨 끝 [남은 결정 사항](#남은-결정-사항)을 먼저 읽고 시작할 것.** 특히 RQ1의 `N` 열,
RQ2의 Survived 분모, RQ3의 unsafe admit 5 vs 8은 **문장을 쓰기 전에** 결론이 나야 한다.

---

## 전체 서사 (Section 4 한 줄 흐름)

AGENTS.md가 고정한 위계 — *안전 제약 하에서의 기능 활성화*이지 timeout 완화가 아니다 —
를 네 RQ가 순서대로 검증하는 구조로 읽히게 한다.

1. **4.1 Setup** — 이 비교가 성립하는 조건을 깐다. 두 기기 모두 production static thermal
   guard를 **끄고** 돌렸고(그래서 Baseline이 실제로 실패할 수 있다), Exynos S26의 parallel
   capture 제한도 해제했으며(그래서 S26 14개 셀이 존재한다), ADB loop가 요청률을 포화시킨
   regime이고, 발열은 시작 레벨만 맞춘 뒤 개입 없이 흘러간다. 관측 창은 최대 30장.
2. **4.2 RQ1** — 제약이 지켜졌다. 28개 셀 전부에서 분석 대상 run이 30장을 timeout 없이
   완주했고, 같은 셀의 가드 우회 M+S 구성은 26/28 셀에서 timeout에 도달했다. 동시에 레벨4
   이상 12개 셀 — 배포된 가드라면 optional stage를 전부 껐을 구간 — 에서 M을 런당 5.2~22.2장
   실행했다. **정적 게이팅은 안전한 촬영과 위험한 촬영을 구분하지 못한다**가 한 표 안에서
   양방향으로 보인다.
3. **4.3 RQ2** — 그 결과가 두 모듈 **모두** 있어야 나온다. 그리고 더 중요한 건: admission
   단독은 마감을 지키되 **하필 우리가 켜려는 M을 그 비용으로 쓴다**(M 29.0→29.3%). pacing은
   그걸 되사오는 모듈이다. 이게 "완화"가 아니라 "활성화" 논문이라는 증거.
4. **4.4 RQ3** — 그 되사오기가 아무렇게나 된 게 아니다. admission 판정은 양방향으로 정확하고
   (feasible의 97.3% admit, unsafe의 97.2% skip), 틀린 5건은 개별로 해부해서 전부 설명된다 —
   그리고 그 5건이 틀린 이유가 **발열 신호로는 안 보이는 core 경합**이라는 점이 2.4의 주장을
   측정으로 되갚는다.
5. **4.5 RQ4** — 지연 쪽도 마찬가지로 표적이 맞다. backlog가 없을 땐 556건 전부 지연 0,
   backlog가 예산의 절반을 넘으면 83.4% 개입. 그리고 실제로 마감이 얇게 끝난 촬영일수록
   pacing이 걸려 있었다(<5%에서 95.7%).
6. **4.6 Case study** — 두 모듈이 한 타임라인 위에서 어떻게 번갈아 작동하는지를 한 번
   보여준다. peer **중앙값** 대비 5개 지표 전부 나쁜 쪽인 run이다(단 "최악"은 아니다).

독자가 마지막에 믿어야 하는 것: *이 기능은 레벨4 이상에서도 켤 수 있다. 정적 가드는 그걸
할 수 없고, 런타임 조정은 할 수 있으며, 그 대가는 회수 가능한 fidelity 손실과 회수 불가능한
지연으로 명시적으로 나뉘어 관리된다.* — Section 4는 이 정책을
**deadline-constrained, responsiveness-dominant trade-off**라고 **이름으로** 불러야 한다
(AGENTS.md 요구사항이고, 현재 이 문구는 `3_1_overview.tex`에만 1회 등장하고 4장 어디에도 없다).

---

## tab_setup

### 이 exhibit의 역할
뒤에 나올 모든 주장의 **사용 허가증**이다. Baseline이 실패할 수 있었다는 것, 수치가 나온
regime이 포화 상태이고 발열이 통제되지 않았다는 것, "timeout 없음"이 30장 horizon 안에서의
진술이라는 것 — 셋 다 이 표(+4.1 prose)가 세워주지 않으면 뒤가 전부 무너진다.

### 읽는 법 (writer가 틀리기 쉬운 것)
- **RAM 이하 모든 행이 두 device 열을 `\multicolumn`으로 가로지른다**(L20–31). 즉 표는 "두
  기기가 SoC만 다르고 프로토콜은 동일하다"고 암묵적으로 주장한다. 이 주장이 성립하는 유일한
  이유가 `4_1_setup.tex` L10의 Exynos 제한 해제다 — 그 문장이 prose에 있어야 하는 이유.
- `Capture conditions` 행은 **수집된 4개 조합 중 2개**다. "모든 조합"이라고 쓰면 안 되고,
  4.1이 이미 쓰는 "low- and high-load endpoints"가 정답.
- **`24MP`는 요청 모드다.** 레벨5 이상에서 production stack이 12MP로 fallback한다
  (`4_1_setup.tex` L17). 워크북 `sizeBucket`으로 확인: 두 24MP 블록 모두 Lv0–Lv4는 MP24,
  **Lv5·Lv6은 100% MP12**. 즉 24MP Lv5/Lv6 행은 24MP 촬영이 아니다.
- `Starting overheat level 0--6`은 **시작값만**이다. 표는 발열 변수 하나를 통제할 뿐 발열
  궤적을 통제하지 않는다.
- `Run horizon: Up to 30`의 "Up to"가 일을 한다. full controller는 전부 30장 완주지만
  Baseline run은 timeout 시점에서 끝난다 — RQ1의 onset 숫자가 존재하는 이유가 그것.
- 표에 run 수, guard bypass, Exynos 제한 해제는 **하나도 없다**. 전부 prose 전용.
- RQ2는 이 표의 4개 조합 중 **3개 패널만** 쓴다(S26 24MP memory 패널 없음). "2×2 완전 설계"로
  읽히게 쓰면 안 된다.

### 반드시 말해야 하는 것

1. **평가 바이너리는 두 기기 모두에서 production static thermal guard를 끄고, Exynos S26의
   parallel capture 제한도 해제한 상태다 — 그래서 Baseline은 "무제어 arm"이지 "출하 정책"이
   아니고, 표의 skip과 delay는 전부 controller 정책에서 나온 것이다.**
   - 근거: `4_1_setup.tex` L9(두 기기 guard 우회), L10(Exynos 제한 해제 — S26 14개 셀은 이
     해제 없이는 존재하지 않는다), L11–12(네 configuration이 동일한 production-based capture
     구현 공유). 가드 정의는 `2_4_static_safeguards.tex` L8 "skips optional stages at level 4
     or higher". 레벨4 이상 12개 셀은 전부 Baseline 0/10이고(전체로는 28셀 중 17셀이 0/10),
     그 12셀의 최이른 onset은 8·8·7 / 3·4·3 / 9·9·9 / 6·5·6이다.
   - 영문 초안: "The evaluation binaries bypass the production static thermal guard on both
     devices and disable the Exynos-based Galaxy S26's parallel-capture restriction, and every
     controller configuration shares the same production-based capture implementation, so the
     Baseline column measures a deliberately uncontrolled arm rather than the deployed policy,
     and any skipped optional stage or applied pacing delay originates from the controller
     configuration alone."
   - 반드시 함께: 이건 **의도적 실험 변경**이지 출하 빌드에 대한 주장이 아니다. 그리고
     Baseline 열과 controller 열은 **같은 회차가 아니다** — Baseline은 이전 campaign을 그대로
     들고 온 값이고 M/S/Activated/d는 0906·0829 render에서 갱신됐다. 발열 궤적이 통제되지
     않으므로 두 arm은 "matched pair"가 아니라 "순차 수집분"이다. 이 문장이 없으면
     "differ only in controller policy"가 프로토콜이 통제하는 범위를 넘어선다.
   - 왜 Top: 이 문장이 없으면 리뷰어는 Baseline 26/28 실패를 "출하 제품이 26셀에서 터진다"로
     읽거나, 레벨4 이상에서 M·S가 0이 아닌 걸 보고 "arm이 비교 불가"라 결론짓고 RQ1·RQ2를
     한꺼번에 버린다.

2. **ADB loop가 capture opportunity가 열리는 즉시 셔터를 넣어 요청률을 포화시킨 regime이고,
   발열은 시작 레벨만 맞춘 뒤 개입 없이 흘러간다. 이건 우리 pacing 수치의 상한 조건이다 —
   실사용 cadence였다면 두 모듈이 다룰 backlog가 더 작았을 것이다.**
   - 근거: `tab_setup` L30(ADB loop), L28(시작 레벨 0–6), L29(에어컨 사무실, 정지 피사체),
     L27(AnTuTu 11.1.4). `4_1_setup.tex` L20–22(발열 비통제), L23–24(포화). 방향 진술은
     `4_7_threats.tex` L14에만 있는데 **현재 build에서 주석 처리돼 있다.**
   - 영문 초안: "The ADB loop issues each shutter request as soon as the framework exposes the
     next capture opportunity, so the reported behavior characterizes the saturated arrival
     regime the single Draft worker faces rather than ordinary user cadence; a slower cadence
     would leave less Draft backlog for either module to act on, and thermal state is set only
     at the start of a run and then evolves without intervention."
   - 반드시 함께: 방향만 말하고 크기는 말하지 말 것. "배포에서는 지연이 더 작을 것"은 검증되지
     않은 외삽이고, AGENTS.md는 closed loop에서 기록 지연을 스케일하는 것을 금지한다. 반대로
     포화를 "그러니 우리 안전 결과는 보수적이다"로 팔아서도 안 된다 — 발열 궤적이 통제되지
     않았으므로 이 모집단은 측정된 모집단이지 bounding 모집단이 아니다. 용어: "the single
     **D**raft worker" (Section 3 소문자 예외는 4장에 미치지 않는다).
   - 왜 Top: 큐잉 결과에 대해 산업계 리뷰어가 던지는 첫 질문인데, 지금 그 답이 build에서 빠진
     파일에 들어 있다.

3. **관측 창은 셀당 run 10개 × 최대 30장이고(Baseline run은 timeout 시점에서 종료), Baseline
   최초 timeout이 21·22·23·24·26·26·28번째 촬영에서 처음 나온 셀이 7개다 — 20장 horizon이었다면
   그 7개는 전부 "무발생"으로 보고됐을 것이다. 동시에 28셀 전부의 10/10 (--)은 "30장 안에서
   관측되지 않았다"는 뜻이지 보장이 아니다.**
   - 근거: `tab_setup` L31. 20장 이후 onset 7개 셀 = 24(S26U 12MP Lv2), 26(S26U 24MP Lv0),
     28(S26 12MP Lv0), 26(S26 12MP Lv1), 22(S26 12MP Lv2), 23(S26 24MP Lv0), 21(S26 24MP Lv1).
     다음으로 큰 onset이 19·19이므로 "7개"는 정확한 값. Baseline이 완전 절단된 셀은 S26U 12MP
     Lv0·Lv1 두 개. 30장 선택 근거는 `2_4_static_safeguards.tex` L21(레벨4 검증 실패가 20번째
     근처) — AGENTS.md가 2.4에 고정한 문장이므로 **4장은 `\ref{sec:guard-limit}`로 참조만** 하고
     일화를 되풀이하지 말 것.
   - 영문 초안: "Each cell comprises ten runs of up to 30 consecutive capture requests, and that
     horizon bounds both columns: seven of the 28 cells record their earliest baseline timeout
     only after the twentieth capture, so a shorter horizon would have reported them as
     failure-free, and the two cells in which every baseline run survives are censored at 30
     rather than shown to be safe."
   - 반드시 함께: 이 문장이 headline을 보장으로 만들지 못하게 막는 장치다. 괄호 안 onset은
     10회 중 **최솟값**이지 대표값이 아니다(`docs/exhibits.md` 2026-08-11 revision). 그리고
     이 7개 중 S26 12MP Lv0·Lv1 두 셀은 provenance 기록과 충돌한다(아래 블로커 참조) — 기록이
     맞으면 5개가 된다.
   - 왜 Top: "모든 조건에서 timeout 없음"이라는 headline에 리뷰어가 곧바로 던질 "얼마나 긴
     창에서?"에 대한 답이자, 동시에 그 headline이 보장으로 읽히는 걸 막는 한 문장.

4. **N=10은 사후에 맞춘 값이고 — 그것도 S26 Ultra 블록만 — 제외된 timeout 라벨 기록은 실제
   Capture Timeout 결과가 아니라 무효 측정이다. 프로토콜에 그대로 밝힐 것.**
   - 근거: `data/U_ablation_sampling/README.md` L9–11(Full arm 셀당 10~14 run → 셀 중심에서 먼
     run부터 제거해 10으로), L15–16(12MP Lv2–Lv6 이전 N = 13,12,14,14,11; 24MP Lv1·Lv3 = 11,11),
     L18–19(총 16 run 제거: 12MP 14, 24MP 2). 선정 지표에 `msExecPercent`, `slackP5Ms` 같은
     **결과량**이 들어간다(L28, L30) — 그래서 `docs/rq-evidence.md` §9 item 6이 "사전 규정된
     제외가 아니라 사후 balancing으로, 편향 방향과 함께" 제시하라고 요구한다. 무효 측정 규칙은
     `docs/rq-evidence.md` L424–431.
   - 영문 초안: "In the Galaxy S26 Ultra arm each cell reports a balanced ten runs, obtained
     after collection by trimming over-sized cells along a composite deviation score that
     includes outcome quantities; sixteen runs were removed in total. Records carrying a timeout
     label that were excluded from the collection are known invalid measurements rather than
     Capture Timeout outcomes."
   - 반드시 함께: **"outcome filtering"·"survival-conditioned"라는 표현은 금지**(AGENTS.md).
     그리고 **이 balancing은 S26 Ultra 14개 셀에만 문서화돼 있다** — S26 14개 셀의 N=10 근거는
     기록되지 않았고 provenance note는 오히려 5~11의 불균형 N을 적고 있다. 28셀 전체에 대해
     "balanced ten runs"라고 쓰면 검증 불가능한 provenance 주장이 된다. 제외 사유도 컬렉션마다
     다르다: 0803 Ultra는 측정 결함, 0906/0829는 `runStatus=CAPTURE_TIMEOUT` 9 run이 **operator
     test capture**(2026-09-08 저자 확인)다. 하나로 뭉뚱그리지 말 것.
   - 왜 Top: 리뷰어가 사후 balancing을 논문이 아니라 artifact에서 발견하면 RQ1 표 전체를
     의심한다. 두 절로 밝히면 비용이 0이다.

### 말하면 안 되는 것
- "모든 촬영 조합/모든 조건을 평가했다" — 수집된 4개 조합 중 2개다.
- "발열 조건을 통제했다" — 시작 레벨만 설정했고 궤적은 방치했다.
- "24MP 셀은 24MP 촬영이다" — 요청 모드이고 Lv5 이상은 12MP fallback이다.
- "cross-device / cross-model 효과가 있다" — 2개 모델뿐이다. controller가 per-model profile을
  갖지 않는다는 건 개연성 논거이지 증거가 아니다.
- 30장 horizon을 근거로 한 bounded-margin / guaranteed-deadline 진술. horizon은 관측을 한정할
  뿐 31번째 촬영이나 최악의 경우에 대해 아무것도 확립하지 않는다.
- guard bypass와 Exynos 제한 해제를 "controller가 대체한 기능"으로 쓰는 것. 대체 주장은 thermal
  guard에 대해서만 증명됐다.
- Section 3 소문자 예외를 4장에 끌고 오는 것. 현재 `4_1_setup.tex` L7이
  "The draft sequence's..."로 소문자다 — 4장에서는 `Draft Sequence`.
- ADB loop를 "사용자 행동 근사"로 묘사하거나 셔터 속도 비교를 되살리는 것(2026-08-21에 저자가
  수사로 판단해 뺀 문구).

---

## tab_rq1_end_to_end_summary

### 이 exhibit의 역할
안전 제약이 **기능을 켠 모든 곳에서** 지켜졌음을 보이는 표이자, 같은 grid에서 가드 우회 구성이
26/28 셀에서 실패했음을 보이는 표. RQ2·RQ3·RQ4는 전부 "이 행이 어떻게 만들어졌는가"의 해설이다.

### 읽는 법 (writer가 틀리기 쉬운 것)
- 두 생존 열 형식 `x/10 (k)`: x = 30장 완주 run 수, **k = 그 셀 시행 중 가장 이른 최초 timeout
  촬영 index**(대표값 아님). `10/10 (--)` = 전원 생존·onset 미관측.
- `Baseline`은 **가드를 우회한 M+S 구성**이지 배포 정책이 아니다. S26 Ultra 절반은 문자 그대로
  `tab_timeout_index`의 M+S 열과 동일한 Section 2 동기 campaign이다(normal 12MP
  `--,--,24,13,8,8,7` / memory 24MP `26,19,14,5,3,4,3`). **새로 짝지어 수집한 arm이 아니다.**
- **`@5`/`@30`은 prefix horizon**이다. `M@5 = 5.0`은 "처음 5장 중 5장에서 실행"이고 `@30`은
  30장 전체 누적 평균이다(@5 이후 25장이 아님).
- **단위 함정 1**: M·S·Activated는 **런당 개수**이지 퍼센트가 아니다(AGENTS.md). RQ2는 분모가
  *요청된* 촬영이라 퍼센트를 쓴다. 절대 통일하지 말 것.
- **단위 함정 2 (가장 자주 틀림)**: `Activated`의 분모는 5/30이 아니라 **4/29**다. k장 prefix는
  최대 k−1개의 transition만 담는다. 산술로 증명 가능: `0.1/4 = 2.5%`,
  `1.8/4 = 45.0%`, `12.2/29 = 42.07%`가 워크북의 퍼센트 필드와 일치한다.
- **단위 함정 3**: `d P50`은 **양수 지연 transition만** 모은 중앙값이다. `--`는 "양수 지연이
  하나도 없었다"이지 "0 ms 지연"이 아니다. @5 셀 중 일부는 **이벤트 1개짜리 중앙값**이다
  (S26 12MP Lv4의 31 ms, S26 24MP Lv4의 31 ms).

### 반드시 말해야 하는 것

1. **28개 셀(2기기 × 2컨디션 × 시작레벨 0–6) 전부에서 분석 대상 full-controller run이 30장
   horizon을 Capture Timeout 없이 완주했다. 같은 28셀 중 26셀에서는 가드를 우회한 M+S 구성이
   timeout에 도달했고, 가장 이른 onset은 3번째 촬영이다.**
   - 근거: 6열 전 28행 `10/10 (--)`. 5열 Baseline은 S26U 12MP Lv0·Lv1만 `10/10 (--)`이고 나머지
     26행이 onset을 달고 있으며, **17행은 생존 run 0**이다. 최이른 onset 3 = S26U 24MP Lv4·Lv6.
     S26 Ultra Baseline 행은 `tab_timeout_index`의 M+S 열 14셀과 완전 일치.
   - 영문 초안: "Every analyzed full-controller run completed its 30-capture horizon without a
     Capture Timeout, in all 28 (device, condition, starting overheat level) cells; the
     guard-bypassed M+S configuration reached Capture Timeout in 26 of the same 28 cells, the
     earliest onset being capture 3."
   - 반드시 함께: (i) **Baseline은 짝지어 수집한 arm이 아니라 failure reference**이고 S26 Ultra
     부분은 Table~\ref{tab:timeout_index}가 이미 보고한 같은 campaign이다 — 그렇게 밝히고, 이미
     본 표를 다시 서술하는 데 prose를 쓰지 말 것. (ii) **셀 단위 수치만** 쓸 것("26 of 28 cells",
     "17 cells with no surviving run"). N이 확정되기 전에는 pooled run/capture 총계를 쓰지 말 것.
     (iii) 제외 문장 필수: timeout 라벨 기록은 알려진 무효 측정이며, "timeout 난 run을 뺐다"나
     "survival-conditioned"로 쓰면 안 된다. (iv) **Baseline onset index와 controller 측 개입 시점
     사이의 부호 있는 차이를 만들지 말 것**(`docs/rq-evidence.md` Part 2 §4.2: admission과 pacing이
     서로의 이후 궤적을 바꾸고, capture index가 timestamp 순서를 함의하지 않는다). 리뷰어가 두
     숫자를 나란히 두면 빼기를 한다.
   - 왜 Top: AGENTS.md 위계의 "배포 블로커"가 해결됐다는 진술이다. 분모와 제외 단서를 달고 한
     문장으로 나오지 않으면 RQ2~RQ4를 읽을 이유가 없고, 산업계 리뷰어는 실패를 버려서 깨끗한
     결과를 얻었다고 가정한다.

2. **레벨4 이상 12개 셀에서 배포된 가드는 (그 레벨이 유지되는 동안) 정의상 M=0, S=0이다.
   컨트롤러는 같은 셀에서 M을 런당 5.2~22.2장 실행하면서 분석된 run 전부 timeout 0이다.
   거꾸로 레벨4 미만 16셀 중 14셀에서는, 가드가 전부 허용하는 바로 그 구성이 timeout을 냈다 —
   정적 게이팅은 안전한 촬영과 위험한 촬영을 구분하지 못한다.**
   - 근거: 가드 정의 `2_4_static_safeguards.tex` L8. Lv4–Lv6 12행의 M@30 = 17.4/13.6/10.9,
     13.4/5.2/7.5, 16.8/13.7/12.4, 22.2/7.2/6.5 → 5.2~22.2. 같은 12행 Baseline 전부 0/10.
     레벨4 미만 16행 중 Baseline이 `10/10 (--)`인 건 S26U 12MP Lv0·Lv1 둘뿐 → 14셀 실패.
   - 영문 초안: "The deployed thermal guard skips optional stages at level 4 or higher, so on the
     twelve cells that start at level 4-6 it yields M = 0 and S = 0 for as long as the level
     holds — a consequence of its definition rather than a separately measured arm. The
     controller instead executes the lightweight multi-frame Draft stage on 5.2 to 22.2 of a
     run's 30 captures with no Capture Timeout in any analyzed run. Below level 4 the guard
     permits every optional stage while the level holds, and that permitted configuration
     reached Capture Timeout in 14 of those 16 cells."
   - 반드시 함께: (i) 가드의 M=0/S=0은 **정의에서 따라 나오는 추론**이지 측정된 arm이 아니다 —
     현재 주석 처리된 `4_2_rq1_effectiveness.tex` 초안이 이미 그렇게 쓰고 있다. (ii) **양쪽에
     동일하게 hedge할 것.** 발열이 run 중에 변하므로, Lv0에서 시작해 15번째 촬영에서 레벨4에
     도달한 Baseline run은 더 이상 "가드가 허용하는 구성"이 아니다. Lv4+ 쪽에만 "for as long as
     the level holds"를 붙이고 Lv<4 쪽을 단정하면, 논문에서 가장 강한 anti-guard 주장이 바로 그
     hedge만큼 과장된다. (iii) **S@30 범위(7.8~28.7)는 상단이 분쟁 셀**이니 당장은 M 범위만 쓰거나
     "S@30 as low as 7.8 of 30"으로 쓸 것. (iv) 24MP fallback 문장을 **이 지점에서 한 번** 넣을
     것: 24MP는 요청 모드이고 Lv5·Lv6 행은 전량 12MP 실행이다.
   - 왜 Top: 논문의 실제 기여 주장이다 — timeout 완화가 아니라 기능 활성화. 그리고 AGENTS.md
     위계의 두 절반이 한 grid 안에서 만나는 유일한 지점이다. 이게 없으면 RQ1은 "우리가 더 낫다"
     표로 읽힌다.

3. **사용자가 체감하는 처음 5장 구간에서는 28행 전부 M@5 ≥ 4.5, S@5 ≥ 4.6이고 23행이 5.0/5.0 —
   기능을 거의 그대로 내준다. pacing은 가능한 4번의 전이 중 최대 1.8회, 14행에서는 0.0회로
   **드물게만** 개입한다.**
   - 근거: M@5 최솟값 4.5(S26U 24MP Lv6), S@5 최솟값 4.6(동). 5.0/5.0이 아닌 셀은 5개뿐이고
     전부 S26 Ultra 행(12MP Lv6 4.7/4.8; 24MP Lv3 4.7/4.7, Lv4 4.7/5.0, Lv5 4.8/5.0,
     Lv6 4.5/4.6) → 23/28행이 5.0/5.0. Activated@5 최대 1.8/4(S26U 24MP Lv6), 0.0인 행 14개
     (전부 `d P50@5 = --`와 짝).
   - 영문 초안: "Over the first five captures the controller retains the feature almost intact and
     intervenes rarely: M@5 is at least 4.5 of 5 and S@5 at least 4.6 of 5 in every one of the
     28 cells, 23 of them at the full 5.0/5.0, while Activated@5 never exceeds 1.8 of the 4
     eligible transitions and is 0.0 in 14 cells."
   - 반드시 함께: **"작게 개입한다"가 아니라 "드물게 개입한다"다.** 크기로는 표가 반대를 말한다 —
     `d P50@5`는 737/685/616/547 ms에 이르고, 이는 `@30` 전체 최댓값 538 ms보다 크다. 다만 그
     @5 중앙값들은 셀당 양수 이벤트가 0~23개뿐(두 셀은 이벤트 1개)이므로 **크기 논거를 이 열
     위에 세우지 말 것**. 그러니 "초반 지연의 크기에 대해서는 아무 결과도 주장하지 않는다"를
     명시하고, 빈도(Activated@5 / 4)와 유지율(M@5, S@5 / 5)로만 말한다. 그리고 이건 **실현된
     동작**이지 설계가 초반 5장을 우대한다는 뜻이 아니다 — 그런 규칙은 구현에 없다. 응답성 비용은
     AGENTS.md가 정한 "user-perceived"로, 절대 "visible"로 쓰지 말 것.
   - 왜 Top: 저자 본인의 usability 논거이자, 저자 초안이 정확히 절반 틀린 지점. 그리고 정적
     가드에 대한 가장 깔끔한 반례다 — 레벨4 이상 12셀에서 가드는 M@5 = 0, 컨트롤러는 4.5~5.0.

4. **28행 전부에서 S@30 ≥ M@30이고 격차는 최대 15.6장이다(S26U 12MP Lv6: M 10.9 vs S 26.5).
   컨트롤러는 두 optional stage를 한꺼번에 끄는 게 아니라 M을 먼저·더 자주 건너뛰고 S를 더
   오래 유지한다 — 레벨4에서 둘을 동시에 끄는 정적 가드와 갈라지는 지점이다.**
   - 근거: 28행 전부 S@30 ≥ M@30, 둘이 같은 건 양쪽이 30.0으로 포화한 5개 셀뿐. 큰 격차:
     15.6(S26U 12MP Lv6), 14.7(Lv5), 11.3(Lv4), 10.6(S26U 24MP Lv5), 10.0(S26 12MP Lv5).
     보조(표 아님, 워크북): 포함된 timeout-free 228 run / 6,840장에서 두 stage 모두 실행 4,031,
     S만 1,408, M만 20, **둘 다 없음 1,381(20.2%)**.
   - 영문 초안: "Retention is asymmetric across the two optional stages: S@30 is at least M@30 in
     every one of the 28 cells and the gap reaches 15.6 captures per run, so the controller skips
     the lightweight multi-frame Draft stage more often than the deployed single-frame stages
     rather than suppressing both together — which is what separates its behavior from the
     level-4 guard's."
   - 반드시 함께: (i) **"expensive"/"cheaper"라고 쓰지 말 것.** 표는 stage 소요시간을 하나도
     인쇄하지 않고, `2_4_static_safeguards.tex` L7이 기록한 동기 사건은 오히려 **단일프레임
     stage**가 timeout을 낸 사례다. (ii) 순서 규칙을 주장하지 말 것 — Section 3.3은 우선순위
     규칙을 주장하지 않는다. 설명이 필요하면 구조적 사실로만: multi-frame stage가 configured
     stage sequence의 첫 번째라 가장 긴 suffix에 대해 검사된다. (iii) **회수 가능성 단서를 여기
     반드시 붙일 것** — 지연은 shot-to-shot latency를 늘리고 회수되지 않지만, 건너뛴 stage의
     fidelity 비용은 final image가 Draft image를 대체할 때 끝난다. 이게 없으면 비대칭이 "공짜
     점심"으로 읽히고, AGENTS.md가 그걸 명시적으로 금지한다. (iv) 6,840장 중 1,381장(20.2%)은
     **두 stage 다 빠졌다** — graceful degradation에 바닥이 있다는 걸 직접 말하는 게 리뷰어가
     계산해내는 것보다 낫다. 그리고 그게 RQ3를 세팅한다: 문제는 "저하됐는가"가 아니라 "옳은
     촬영을 저하시켰는가"다.
   - 왜 Top: 결과를 on/off가 아니라 graceful degradation 이야기로 만들고, RQ3로 가는 다리가 된다.
     "timeout 안 났다" 다음 리뷰어의 질문은 "뭘 포기했고, 포기할 걸 포기한 게 맞나"다.

5. **개입 강도는 시작 레벨을 따라 단조 증가하지 않는다. 촬영 해상도가 전 구간 동일한 12MP
   블록에서, S26 Ultra는 M@30이 30.0 → 10.9로 내려가는 동안 Activated@30이 0.0 → 12.2(Lv5 정점)
   → 9.9로 움직인다. 두 레버가 같은 마감 압력을 나눠 받는다는 설계 방향과 일치하는 관측이며,
   기여도 분해는 RQ2 몫이다.**
   - 근거: S26U 12MP Activated@30 = 0.0/0.2/3.6/10.4/11.0/12.2/9.9, 같은 구간 M@30 = 30.0/29.4/
     27.1/25.6/17.4/13.6/10.9, d P50@30 = --/127/262/284/437/470/521(Lv0은 양수 지연 없음).
     S26 12MP Activated@30 = 2.6/3.7/5.3/11.8/15.4/12.7/15.1 — Lv4에서 한 번 꺾인다. "발열이
     오를수록 pacing이 는다"는 단순 읽기는 표 안에서 이미 반박된다.
   - 영문 초안: "Intervention does not rise monotonically with the starting overheat level. Within
     the 12MP blocks, where the captured resolution is the same at every level, Activated@30
     turns over — rising to a peak of 12.2 at level 5 and falling to 9.9 at level 6 on the S26
     Ultra while M@30 falls from 30.0 to 10.9. The two levers co-vary in the direction the design
     intends; Table~\ref{tab:rq2_ablation} owns the per-component contribution."
   - 반드시 함께: **24MP 블록의 Lv4 → Lv5 전이를 이 논거의 근거로 쓰지 말 것.** 그 지점이 바로
     production stack의 12MP fallback 경계라서, M·S·Activated가 동시에 떨어지는 것이 워크로드
     자체가 바뀐 것과 구분되지 않는다(워크북 `sizeBucket`: 두 24MP 블록 모두 Lv0–Lv4 MP24,
     Lv5·Lv6 전량 MP12). 그리고 이건 단일 closed-loop arm에서의 셀 간 공변이지 통제된 비교가
     아니다 — "signature of two levers absorbing the same pressure" 같은 메커니즘 단정 대신
     "co-vary in the direction the design intends"로 쓸 것.
   - 왜 Top: 저자의 세 번째 bullet을 방어 가능하게 만든 형태이자, grid에 대한 명백한 오독
     — "개입이 레벨에 따라 늘어야 하는데 24MP 블록은 컨트롤러가 포기한 것처럼 보인다" — 을
     미리 막는다. RQ2에 동기를 넘겨주기도 한다.

### 말하면 안 되는 것
- "controller가 Capture Timeout을 보장/방지한다", "deadline margin이 bounded다".
  지지되는 건 "분석된 run 중 관측되지 않았다"뿐.
- RQ1 모집단을 survival-conditioned로 묘사하거나 "timeout 난 run을 제거했다"로 쓰는 것.
- Baseline 열을 "the deployed static guard"나 "production"이라 부르는 것.
- 괄호 안 onset을 "무제어 run이 보통 실패하는 지점"으로 읽는 것 — 10회 중 최솟값이다.
- M·S·Activated를 퍼센트로 바꾸는 것, 또는 분모를 밝히지 않고 RQ2 퍼센트와 수치 비교하는 것.
  **주의: 예전에 허용됐던 "RQ2 rate × 30 = RQ1 count" 교차검증은 이제 안전하지 않다** — 그
  등식은 "어떤 run도 30장 전에 끝나지 않는다"에 의존했는데, 현재 컬렉션에서는
  `complete30ShotRunCount < includedRunCount`인 셀이 여럿이다.
- `Activated`를 5나 30에 대고 읽는 것. 분모는 4와 29다.
- `d P50`을 "촬영당 평균 지연"으로 읽는 것. 활성화 조건부이고 일부 셀은 이벤트 1~3개다.
- 건너뛴 optional stage를 masked/hidden/invisible/free로 묘사하는 것. 응답성 비용에
  "visible" 대신 "user-perceived".
- RQ1이 각 control loop의 기여를 보여준다고 주장하는 것 — ablation arm이 없다.
- 용어: `burst`(→ run / consecutive captures), `node`(→ optional stage),
  `Draft path`(→ the Draft pipeline / Draft Sequence), `final processing`,
  `optional Draft work`·`optional Draft stage`(→ optional stage),
  `lightweight multi-frame Draft composition`(→ the Draft Sequence's lightweight multi-frame
  composition, 또는 the lightweight multi-frame Draft stage). 4장은 Section 3 소문자 예외 밖.

---

## tab_rq2_ablation

### 이 exhibit의 역할
논문에서 컨트롤러를 **분해하는 유일한 표**. 두 모듈이 중복이 아니라 상보적임을 보이는 것,
그리고 더 중요하게는 **안전만 사는 레버(admission 단독)가 이미 존재하며 그 비용이 하필 논문이
켜려는 기능이라는 것**을 측정으로 보이는 것.

### 읽는 법 (writer가 틀리기 쉬운 것)
- **분모 함정 1**: `Captures`·`M`·`S` 세 열이 분모를 공유한다 — **30 × N 요청 촬영**. "정시에
  완료된" 촬영 기준이므로, 절단된 run의 timeout 촬영과 도달하지 못한 촬영은 전부 0점이고
  **실행됐지만 마감을 넘긴 촬영도 0점**이다(audit: 도달 143 vs 정시 133, 113 vs 101, 271 vs 258).
- **분모 함정 2**: `Activated`는 그 분모를 쓰지 않는다. 관측된 transition(도달 촬영 − run 수)이
  분모다: Full은 290/319/290, Pacing only는 133/101/257. 37.9%는 110/290이지 300의 37.9%가 아니다.
- **분모 함정 3**: `d P50`은 0 지연 transition을 제외한 조건부 중앙값이다.
- **동일 3연속 값**: `No control`과 `Pacing only`에서 `Captures = M = S`가 정확히 같다
  (29.0×3, 44.3×3, 24.3×3, 28.1×3, 42.3×3, 61.4×3). **admission이 꺼져 있어 정시에 완료된 촬영은
  전부 두 stage를 실행했기 때문**이다. 즉 그 두 구성에서 M·S 열은 품질 지표의 머리를 쓴
  **정시 완료율**이다.
- **Full 행은 RQ1의 Lv4 행과 같은 모집단이다.** 12개 Full 셀이 전부 RQ1을 재현한다
  (58.0×30=17.4, 95.7×30=28.7, 37.9×29=11.0, …). RQ2의 Full 행은 RQ1의 독립 확증이 아니다.
- **컬렉션 분할**: `Pacing only`와 `Full`만 2026-09-07에 갱신됐고 `No control`·`Admission only`는
  이전 출처를 유지한다. 그 두 그룹을 가로지르는 비교는 전부 컬렉션을 가로지른다.
- **제외 비대칭**: `Pacing only`의 Capture Timeout run은 그 arm의 측정 결과이므로 유지되고,
  `Full`의 timeout 라벨 기록은 무효 측정으로 제외된다. **이 표에는 timeout이 난 arm이 인쇄돼
  있으므로**, 옆에 붙는 "no valid analyzed run timed out"은 반드시 full controller로 한정해야 한다.

### 반드시 말해야 하는 것

1. **세 조건 전부에서 요청한 30장을 전부 "정시에" 완료한 구성은 admission+pacing 둘 다 켠
   경우뿐이고, 유효한 분석 대상 full-controller run 중 timeout이 난 것은 없다. 단 Admission only는
   가장 쉬운 조건에서는 혼자서도 10/10이므로, "둘 다 필요하다"는 어려운 두 조건과 stage
   유지율에서 성립하는 주장이다.**
   - 근거: `No control` 0/10 / Captures 29.0, 24.3, 42.3. `Pacing only` 0/10, 0/10, 1/10 /
     44.3, 28.1, 61.4. `Admission only` 10/10, 8/10, 7/10 / 100.0, 87.3, 90.7.
     `Full` 10/10 ×3 / 100.0 ×3. **실제 Full 모집단은 10/10, 11/11, 10/10 = 31 run 중 31**이고,
     `Pacing only`의 참 분모는 10, 12, 14다(표의 Survived 분모가 틀렸다 — 블로커 참조).
   - 영문 초안: "With both modules enabled, every requested capture completed within its deadline
     in all three panels and no valid analyzed run of the full controller timed out.
     \emph{No control} completed 29.0\%, 24.3\% and 42.3\% of requested captures, \emph{Pacing
     only} 44.3\%, 28.1\% and 61.4\%, and \emph{Admission only} 100.0\%, 87.3\% and 90.7\% —
     meeting the horizon on the easiest condition alone but not on the other two."
   - 반드시 함께: (i) "deadline-safe"라는 **속성 주장**이 아니라 관측 진술로 쓸 것. (ii)
     "no valid analyzed run timed out"을 **full controller로 한정**하지 않으면 바로 위 표의
     `Pacing only` 행과 모순된다. 제외 비대칭을 한 번 밝힐 것. (iii) `Survived`는 "30장 완주 +
     Capture Timeout 없음"이므로 두 실패 모드를 합친 값이다 — `Admission only`의 8/10, 7/10을
     "2건·3건이 timeout 났다"로 옮길 수 없다. 그리고 watchdog run이 survived에 포함된다.
     (iv) 분모가 고쳐지기 전에는 "10/10 in every panel"을 쓰지 말 것.
   - 왜 Top: ablation이 존재하는 이유 전체이고, 리뷰어가 "작동하는 모듈 하나 + 장식 하나"가
     아님을 확인할 수 있는 유일한 지점.

2. **Admission only는 마감 압박을 optional stage로 갚는데, 그 비용이 하필 우리가 켜려는 M에
   집중된다: 정시 완료가 29.0 → 100.0%로 오르는 동안 M은 29.0 → 29.3%에 머물고, 같은 구간에서
   S는 29.0 → 33.7%로 움직인다. pacing을 켜면 정시 완료 100.0%를 유지한 채 M이 58.0%가 된다.**
   - 근거: 패널별 `No control` → `Admission only` → `Full`.
     S26U 12MP: Captures 29.0 → 100.0 → 100.0, M 29.0 → 29.3 → **58.0**, S 29.0 → 33.7 → **95.7**.
     S26U 24MP: 24.3 → 87.3 → 100.0, M 24.3 → 24.3 → **44.5**, S 24.3 → 51.0 → **77.0**.
     S26 12MP: 42.3 → 90.7 → 100.0, M 42.3 → 44.3 → **56.0**, S 42.3 → 51.3 → **74.7**.
     pacing 추가분: M +28.7, +20.2, +11.7 / S +62.0, +26.0, +23.4 percentage point.
     Admission only의 절대 수치(확인됨): S26U 12MP N=10, 정시 300/300, M 88/300, S 101/300;
     S26U 24MP N=10, 262/300, M 73/300, S 153/300.
   - 영문 초안: "\emph{Admission only} recovers on-time completion by skipping optional stages, and
     the cost falls on the stage the paper exists to enable: on the S26 Ultra 12MP panel it raises
     completion from 29.0\% to 100.0\% of requested captures while $M$ stays at 29.3\%, whereas
     $S$ over the same step moves 29.0\% to 33.7\%. With both modules enabled the controller
     executes $M$ on 58.0\%, 44.5\% and 56.0\% of requested captures with all of them completed
     on time."
   - 반드시 함께: (i) `Admission only` → `Full` 단계는 **구성 변경인 동시에 컬렉션 변경**이다.
     "관측된 차이"로 쓰고 `4_7_threats.tex`에 한 문장을 둘 것. (ii) 인과 동사를 피할 것 —
     "pacing이 M을 되사왔다"는 closed loop에 matched counterfactual이 없다. (iii) **pacing이
     admission에 숫자 잔여를 넘긴다고 쓰지 말 것** — 모듈 간에 수치 상태는 전달되지 않는다
     (AGENTS.md; 역할 분담은 설계 의도). (iv) 회수 가능성 순서를 붙일 것.
   - 왜 Top: AGENTS.md가 요구하는 framing — 안전 제약 하의 기능 활성화 — 을 **측정**하는 유일한
     exhibit이다. "안전만 사는 레버는 이미 있고, 그게 기능을 비용으로 쓴다"가 "두 모듈 다 도움이
     된다"를 "두 번째 모듈이 기능을 배포 가능하게 만든다"로 바꾼다.

3. **No control / Pacing only의 M·S 칸은 품질 지표가 아니라 "정시 완료 비율" 그 자체다.
   S26 12MP에서 Pacing only의 M 61.4%가 Full의 56.0%보다 높아 보이지만, 그 61.4%는 요청 촬영의
   61.4%만 정시 완료했다는 뜻이고 Full은 100.0%다.**
   - 근거: 동일 3연속 값 6쌍(29.0/44.3/24.3/28.1/42.3/61.4). audit의 동일 분자로 확인:
     정시 133/101/258에 대해 M·S도 133/133, 101/101, 258/258. 도달 > 정시(143>133, 113>101,
     271>258)이므로 실행됐지만 늦은 촬영은 세 열 모두에서 0점.
   - 영문 초안: "In \emph{No control} and \emph{Pacing only} the Captures, $M$ and $S$ columns
     coincide by construction — admission is disabled, so every capture that met its deadline
     executed both optional stages — and those columns therefore report how far each run got
     rather than how many stages it retained. \emph{Pacing only}'s 61.4\% $M$ on the S26 panel is
     the same number as its 61.4\% completion, against 100.0\% for the full controller."
   - 반드시 함께: (i) 그 두 구성의 M·S 셀을 **인접 Captures 셀 없이 인용하지 말 것**.
     (ii) **"배달된 촬영 기준 M이 가장 높다"고 쓰면 안 된다** — 그 기준으로는 admission이 꺼진
     두 구성이 정의상 100%이고 Full이 가장 낮다. 검증 가능한 형태는: "정시 완료와 M을 동시에
     Full 이상으로 만드는 구성은 없다". (iii) Full이 S는 세 패널 전부 최고, M은 3중 2에서 최고 —
     둘 다 **요청 촬영 기준**임을 밝힐 것.
   - 왜 Top: 표에서 논문에 대해 쓰일 수 있는 유일한 셀이고, 61.4 대 56.0은 적대적 독자가 10초
     만에 찾는다. 분모와 함께 **먼저** 말하면 함정이 증거로 바뀐다.

4. **2.4와 3.1이 설계 논거로만 말한 두 레버의 한계가 ablation의 실패 양상과 일치한다(인과가
   아니라 일치): Admission only는 어려운 두 조건에서 8/10, 7/10에 그치고, Pacing only는
   0/10·0/12·1/14이며 정시 완료한 촬영에서는 두 stage를 모두 실행한 채로 끝난다.**
   - 근거: 위 셀들. 두 한계는 이미 manuscript에 있다 — `2_4_static_safeguards.tex` L32
     "Skipping optional stages shortens that capture's processing but cannot recover time already
     spent waiting", `3_1_overview.tex` L35–36. Pacing only의 절단: 도달 143·113·271장을 10·12·14
     run으로 나누면 run당 평균 14.3·9.4·19.4장.
   - 영문 초안: "The ablation's failure pattern is consistent with the two lever limits that
     Sections~\ref{sec:guard-limit} and~\ref{sec:objective} state as design arguments — admission
     shortens a capture's processing but cannot recover time already spent waiting, and pacing
     lengthens the next interval but cannot change work already in progress. \emph{Pacing only}
     survives 0, 0 and 1 run while executing both optional stages on every capture it completed
     on time."
   - 반드시 함께: (i) "because"를 쓰지 말 것 — exhibit은 결과만 기록한다. 메커니즘은
     Section 3이 공급한다. (ii) "every capture it **reaches**"가 아니라 "every capture it
     **completes on time**"이다. (iii) 14.3/9.4/19.4는 run당 평균이지 "run이 거기서 끝났다"가
     아니다(S26 패널에서 1 run은 30장을 완주했다). (iv) `eq:margin-recursion`은 회계 항등식이므로
     ablation을 제어법칙의 검증으로 제시하지 말 것.
   - 왜 Top: Section 4를 "결과 덤프"가 아니라 "Section 3의 검증"으로 읽히게 만들고, 리뷰어의
     당연한 질문 "그럼 admission만 쓰면 되지 않나?"를 미리 막는다.

5. **pacing 비용 두 칸은 구성 간 비교가 불가능하다 — 관측된 transition 자체가 133/101/257
   (Pacing only) 대 290/319/290(Full)으로, 두 패널에서는 run의 절반도 안 되는 앞부분만 잰
   값이다. 말할 수 있는 건 하나: 요청 30장을 전부 정시 완료하면서 실제로 걸린 지연의 중앙값이
   437 / 400 / 297 ms였다는 것.**
   - 근거: `Pacing only` 51.1%/242, 58.4%/483, 44.7%/387 대 `Full` 37.9%/437, 36.7%/400,
     53.1%/297 — **두 열 모두 패널마다 순서가 뒤집힌다**. S26U 12MP에서는 Full이 덜 자주 개입하지만
     중앙값이 1.8배 크고, S26 12MP에서는 더 자주 개입하지만 중앙값이 작다.
   - 영문 초안: "The two pacing-cost columns are not comparable across configurations:
     \emph{Pacing only}'s rates are measured over the prefix its runs survived — 133, 101 and 257
     observed transitions against 290, 319 and 290 for the full controller. The defensible
     statement is that the full controller completed every requested capture on time while the
     median of the delays it actually applied was 437, 400 and 297\,ms, a median taken over the
     transitions on which pacing engaged rather than over all captures."
   - 반드시 함께: (i) "촬영당 평균 지연 437 ms"로 읽히지 않게, 조건부 중앙값임을 **문장 안에**
     둘 것. (ii) **RQ2에는 적용된 지연에 대한 counterfactual이 없다** — "필요한 만큼만 걸었다",
     "과하지 않았다"로 미끄러지면 안 된다. 표적 관련 질문은 RQ4 몫이고, 거기서도 coverage는
     *놓친* 개입의 상한일 뿐 *불필요했던* 개입에 대해서는 말하지 않는다. (iii) 이 표에는 tail
     통계가 없으므로 최악 지연 주장 금지. (iv) `timeout > delay > admit`을 엄격한 사전식 최적
     ("최후의 수단으로만 지연")으로 번역하지 말 것 — 배포 정책은 그 corner solution이 아니다.
   - 왜 Top: 저자 본인의 bullet 중 표가 지지하지 않는 유일한 sub-claim이다. 초안대로 쓰면 두
     패널에서 자기를 반박하는 표 옆에 반증 가능한 문장을 놓게 된다.

### 말하면 안 되는 것
- "controller가 Capture Timeout을 방지/제거/보장한다", 10/10을 bounded-margin으로 승격.
- Full 모집단을 survival-conditioned로 묘사하거나 무효 측정의 결함 내용을 지어내는 것.
- "`Pacing only`가 M을 29.0%에서 44.3%로 올린다" 류의 문장. 생존 숫자다.
- `No control`/`Pacing only`의 M·S를 인접 Captures 없이 인용하는 것.
- "full controller가 delay를 더 잘 분산한다". 활성화율과 중앙값이 패널마다 반대로 움직인다.
- "전형적인 촬영이 437 ms 지연된다".
- `Activated`를 촬영 수에 대고 읽는 것(분모는 290/319/290).
- Full 행을 RQ1의 독립 확증으로 제시하는 것 — 같은 모집단, 다른 분모다. 한 번 그렇게 밝히고
  RQ2의 기여는 3자 대비로 한정할 것.
- `Admission only`가 "지연이 필요 없었다"거나 "pacing 비용을 아꼈다"고 쓰는 것 — 구성의 구조적
  귀결이지 측정이 아니다.
- RQ2 퍼센트를 run당 개수로 바꿔 RQ1과 "통일"하는 것.
- `Admission only`와 `Full`을 컬렉션 차이를 밝히지 않고 비교하는 것.
- 현재 주석 stub의 "over ten runs per condition and configuration" — 분모가 고쳐질 때까지 금지.

---

## tab_rq3_admission_quality + fig_rq3_unsafe_spike_anatomy

### 이 exhibit의 역할
admission 판정의 **양방향 채점표**(표)와 **틀린 5건에 대한 개별 해부**(그림). 표는 "지나치게
보수적이지도, 위험을 놓치지도 않는다"를 보이고, 그림은 남은 실패를 하나씩 설명하면서
"정적 발열 임계값으로는 이 순간들을 구분할 수 없다"는 2.4의 주장을 측정으로 되갚는다.

### 읽는 법 (writer가 틀리기 쉬운 것)
- **모집단**: 현재 표는 `Always-admit model audit` 절반만 인쇄한다. 그건 **pacing-only run에서
  나온 3,746건의 disjoint shadow pool**이다(12MP 882+882, 24MP 996+986). 143 full-controller run의
  **8,430건 enforced 결정이 아니다** — 그 블록은 2026-09-07에 exhibit에서 제거됐다.
  (주석 stub `4_4_rq3_admission.tex`는 아직 두 모집단을 다 언급한다.)
- **무엇을 잰 것인가**: audit build는 모든 optional stage를 **강제 실행**하고 watchdog을 **해제**한
  상태에서, shadow controller가 내렸을 판정(`afterModelAdmit`, session-sticky demotion 이전)만
  기록한다. 사후에 trace로 라벨을 붙인다 — 실현 비용 C가 결정 시점 예산 B에 들어가면 feasible,
  넘으면 unsafe.
- **단위 함정 (가장 크다)**: 퍼센트는 **자기 factual class 안에서**의 비율이다.
  `2.8% (5)`는 **unsafe 178건 중 5건**이지 3,746건 중 2.8%가 아니다(그건 0.13%).
  좌우 반쪽은 절대 합쳐지지 않는다. 행 분모는 인쇄돼 있지 않다 — feasible 847/847/942/932,
  unsafe 35/35/54/54, 그룹 합 882/882/996/986.
- **판정 단위**: 각 촬영은 **그룹당 최대 1건**의 결정을 낸다(Multi-frame = Bokeh 결정,
  Single-frame = Filter 결정). "모든 optional stage의 97.3%"가 아니라 "선택된 admission 결정의
  97.3%"다.
- **두 번째 함정**: B는 그 결정 시점의 Capture Timeout 마감까지 남은 시간이므로, audit 기록에서
  **C > B와 그 촬영이 timeout 난 것은 같은 사건**이다. 즉 **unsafe 178건 전부(admit 5 + skip 173)가
  이 recording에서 마감을 넘긴 촬영이다.** 그림의 역할은 "timeout이 안 났다"가 아니라
  "출하 빌드였다면 Capture Timeout으  로 나가지 않았을 것"이다.
- **그림 읽기**: bar는 1.0에 고정되고 plotted x = ratio − 1이며 tick label이 비율을 다시 적는다.
  y축은 아래에서 위로 `S2, S1, M3, M2, M1`이므로 y=5가 M1이다. y=2.5의 선이 multi-frame(M1–M3)과
  single-frame(S1–S2)을 가른다. 비교 기준은 **같은 run·같은 그룹의 직전 촬영**이고, 그 직전
  촬영은 그 자체로 safe admit이었다. `Busy cores`는 남은 stage 구간의 CPU ms / wall ms이지
  기기 core 개수가 아니다. **세 계열은 곱셈 관계이지만 인쇄된 비율끼리 정확히 나눠떨어지지는
  않는다**(1.41/0.60 = 2.35 vs 인쇄값 2.32) — stage wall time이 plotted latency의 97.5~99.0%만
  덮기 때문. "exactly"라고 쓰면 리뷰어가 나눗셈을 한다.
- 라벨 M1..S2는 **위치 기반**이고 그룹 안에서 성장률 내림차순이다 — 데이터가 바뀌면 이동한다.

### 반드시 말해야 하는 것

1. **admission 판정은 양방향으로 정확하다 — 사후 판정상 예산에 들어갔을 결정의 97.3%(3,470)를
   admit 판정하고, 예산을 넘겼을 결정의 97.2%(173)를 skip 판정한다. 3,746건 shadow audit 기준.**
   - 근거: Overall 행 97.3% (3,470) / 2.7% (98) / 2.8% (5) / 97.2% (173). 행별로
     12MP Multi 98.1%(831)/1.9%(16), 5.7%(2)/94.3%(33); 12MP Single 99.4%(842)/0.6%(5),
     **0.0%(0)**/100.0%(35); 24MP Multi 94.7%(892)/5.3%(50), 1.9%(1)/98.1%(53);
     24MP Single 97.1%(905)/2.9%(27), 3.7%(2)/96.3%(52). class 크기는 덧셈으로 복원:
     feasible 3,568, unsafe 178, 합 3,746.
   - 영문 초안: "Across 3,746 audited admission decisions — at most one per capture in each
     admission group — the shadow model is accurate in both directions: it admitted 97.3\%
     (3,470) of the decisions whose remaining sequence, executed in full, fit the budget read at
     that decision, and skipped 97.2\% (173) of those whose forced execution exceeded it. Every
     percentage is a share of its own factual class — 3,470 + 98 = 3,568 feasible and 5 + 173 =
     178 unsafe decisions — so 2.8\% is 5 of 178, and as a share of all audited decisions it is
     0.13\%."
   - 반드시 함께: (i) **shadow 판정이지 실행률이 아니다** — audit build는 모든 optional stage를
     강제 실행했고, 점수가 매겨진 건 session-sticky demotion 이전의 모델 권고다. 배포
     controller의 유지율로 제시하면 안 된다. (ii) 8,430건 enforced 결정과 **절대 같은 문장에
     넣지 말 것**(disjoint pool). (iii) **표본 선정은 outcome-neutral이 아니다**: 0803 성분이
     시작 발열 레벨 기준으로 뽑혔고, 24MP에서는 그 출처의 unsafe-admitted 모집단 전체가 규칙만으로
     제거된다. 따라서 **조건 간 unsafe-admit 비율 비교(5.7 vs 0.0 vs 1.9 vs 3.7)는 해석 불가**다.
     feasible-skip 열에는 이 편향이 없다. (iv) unsafe 절반은 **미해결 8-vs-5 불일치의 영향권**이다
     (블로커 참조). script 상수대로면 4.5%/95.5%가 된다. feasible 절반(97.3%/2.7%)은 두 소스가 일치.
     → **97.2%에 의존하는 문장은 5가 8로 바뀌어도 형태가 무너지지 않게 쓸 것.**
   - 왜 Top: RQ3에 대한 답 그 자체이고, admission이 단순히 보수적인 게 아님을 보이는 유일한
     지점이다. 한쪽 주장("위험한 일을 걸러낸다")은 전부 skip하는 모델도 만족시키므로 논문의
     전제를 무너뜨린다 — 리뷰어는 반대쪽 열을 먼저 본다.

2. **과보호도 하지 않는다: 예산에 들어갔을 결정 중 skip은 2.7%(98/3,568)뿐이고, 12MP normal에서는
   1,694건 중 21건이다. 나머지는 24MP memory pressure의 multi-frame(5.3%, 50건)에 몰려 있다.
   그리고 12MP Single-frame은 표에서 가장 강한 셀이다 — unsafe 35건 중 admit 0건, feasible
   847건 중 skip 5건.**
   - 근거: feasible-skip 열 1.9%(16), 0.6%(5), 5.3%(50), 2.9%(27), Overall 2.7%(98).
     12MP feasible class = 847 + 847 = 1,694, 그중 skip 16 + 5 = 21.
   - 영문 초안: "Admission is not buying its rejection record with over-conservatism: only 2.7\%
     (98 of 3,568) of the decisions whose remaining sequence would have fit were skipped — 21 of
     them in the 1,694 feasible decisions at 12MP normal — with the rest concentrated in the 24MP
     memory-pressure condition, where Multi-frame reaches 5.3\% (50)."
   - 반드시 함께: (i) "불필요한 skip"은 **사후에만** 그렇다 — 결정은 `eq:admission`의
     residual-calibrated 상한 추정 U 위에서 내려졌다. "controller가 불필요한 줄 알 수 있었던
     skip"이 아니다. (ii) 건너뛴 stage의 fidelity 비용은 실재하고, final image가 Draft image를
     대체할 때 끝난다 — masked/hidden/free 금지. (iii) 이 셀들을 RQ1/RQ2의 유지율을 "결정
     측면에서 설명한다"고 쓰면 안 된다 — disjoint pool이다. (iv) margin 중앙값(+1.2/+0.7/+2.6/
     +1.6%)을 인용한다면 **표에 없는 값**이라고 밝힐 것. overrun 중앙값(−3.0/−3.5/−3.2/−3.4%)은
     8-vs-5 불일치와 함께 움직이므로 확정 전에는 쓰지 말 것.
   - 왜 Top: 97.2%는 전부 skip하는 모델도 달성한다. false-positive 열이 안전 열에 의미를 준다.
     그리고 이게 RQ3를 "기능 활성화"라는 논문 목표에 묶는 지점이다.

3. **unsafe admit 5건은 전부 개별로 설명된다: 2건(M1, M2)은 모델 자신의 결정 집합에서도 예산
   초과라 watchdog만이 잡았을 사례이고(스테이지 1,460 ms 대 예산 1,202 ms / 1,648 대 889),
   나머지 3건은 모델 자신의 다른 stage skip을 반영하면 예산 안에 들어온다(833/844, 961/1,435,
   713/983). M1·M2는 진짜 모델 오류로 인정하고 쓰는 편이 나머지 3건을 믿게 만든다.**
   - 근거: 그림 우측 `prevented by` 주석 — y=5(M1) watchdog, y=4(M2) watchdog, y=3(M3) later
     single-frame skip, y=2(S1) earlier multi-frame skip, y=1(S2) earlier multi-frame skip.
     즉 **2 + 3이지 각 건이 둘 다가 아니다.** 정량치는 `docs/exhibits.md`
     #fig_rq3_unsafe_spike_anatomy.
   - 영문 초안: "Each of the five unsafe admits carries at least one safeguard the audit build had
     removed. Two are over budget even on the model's own decision set and are reached only by the
     watchdog, whose budget the audit still records: the deciding stage ran 1,460\,ms against a
     1,202\,ms watchdog budget on M1 and 1,648\,ms against 889\,ms on M2, so the watchdog would
     have abandoned the stage 258\,ms and 759\,ms before it finished. The other three fall back
     inside budget once the model's own skips in the same capture are honoured — 833 against 844
     on M3, 961 against 1,435 on S1, 713 against 983 on S2 — because a stage rejected after the
     decision removes cost while one rejected before it shortens the path and raises the budget."
   - 반드시 함께: (i) **방향을 뒤집지 말 것**: watchdog은 stage가 끝나기 **258 ms·759 ms 전에**
     잘랐을 것이다("258 ms 들어가서 잘랐다"가 아니라). (ii) **두 종류의 슬래시 쌍을 구분해서
     쓸 것** — 1460/1202는 *한 stage의 소요 대 그 stage의 watchdog 예산*, 833/844는 *남은 sequence
     비용 대 그 결정의 예산*이다. 같은 형식으로 나란히 두면 독자가 1,460과 833을 비교한다.
     (iii) **watchdog 차단은 공짜가 아니다** — `3_3_admission.tex`에 따르면 watchdog 만료 시
     framework는 보존된 원본 입력으로 encoding·saving을 진행하므로, 그 stage의 결과는 잃고 이미 쓴
     시간은 회수되지 않는다. "prevented by watchdog"이 깨끗한 구제로 읽히면 안 된다. (iv) **세 skip
     판정의 강도가 다르다**: M3는 11 ms 차이로 통과하고 S1은 474, S2는 270이다. 하나로 묶으면
     리뷰어가 찾아낼 가장 약한 사례를 숨기게 된다. (v) 5건에 대한 사후 설명이지 안전 속성이
     아니다. C_model은 상한, B_model은 하한이고 두 보정 모두 **이전 촬영들이 남긴 큐로는 전파되지
     않는다.** (vi) audit이 watchdog을 해제했으므로 **watchdog 자신의 비용에 대해서는 아무것도
     측정하지 못한다** — 예산 안에 끝났을 stage를 얼마나 자주 자르는지는 이 exhibit 밖이다.
     (RQ4 coverage 한계의 구조적 쌍둥이. 리뷰어의 다음 질문이 정확히 이것.)
   - 왜 Top: exhibit의 후반부이자 리뷰어의 명백한 수 — "결국 넘긴 일을 admit했으니 테스트가
     부실한 것 아니냐" — 에 대한 방어다. 5/5를 설명하면 실패 칸이 계층 방어의 증거가 된다.

4. **이 spike들은 일이 폭증한 게 아니라 core를 뺏긴 경우다 — 5건 중 4건에서. M1은 CPU time
   1.41배인데 latency 2.32배, busy core 0.60배. 게다가 이 순간들의 발열 레벨·thermal status는
   직전 (그 자체로 안전했던) 촬영과 동일했고 blocking GC는 0인 반면 run-queue wait과 context
   switch는 양방향으로 움직였다 — 즉 admission 시점에 읽을 수 있는 신호로는 이 결정들을 직전
   촬영과 구분할 수 없다.**
   - 근거: 그림 값 라벨(아래→위 S2, S1, M3, M2, M1) — M1 2.32/1.41/0.60, M2 1.95/1.15/0.59,
     M3 1.14/1.23/**1.08**, S1 1.60/1.24/0.76, S2 1.42/1.37/0.96.
   - 영문 초안: "On four of the five, the remaining stages were served by fewer cores rather than
     needing much more CPU: M1 needed 1.41x the preceding capture's CPU time and took 2.32x the
     wall time with busy cores at 0.60x, M2 1.15x / 1.95x / 0.59x, and S1 1.24x / 1.60x / 0.76x,
     while S2 was essentially flat in cores at 0.96x. Busy cores is CPU time per unit of wall time
     over the remaining stages, so the three quantities are one measurement and its two factors
     rather than an attribution."
   - 반드시 함께: (i) **M3는 예외이고 이름으로 밝혀야 한다** — busy core가 1.08배로 **늘었고**
     CPU time(1.23배)이 latency(1.14배)보다 더 자랐다. 진짜 추가수요 사례다. "5건 전부"라고 쓰면
     그림이 반박한다. (ii) "CPU가 안 늘었다"가 아니다 — 5건 전부 CPU time이 늘었다. 지지되는 건
     **M1·M2·S1에서 core 항이 지배한다**는 것. (iii) "절대 예측할 수 없다"는 exhibit이 감당 못
     하는 절대 진술이다. "admission 시점에 쓸 수 있는 신호로는 구분되지 않는다"로 쓸 것.
     (iv) "exactly"라고 쓰지 말 것(위 읽는 법 참조). (v) thermal/GC/run-queue 비교는 **8건
     regeneration에서 기록된 것**이고 exhibit은 5행을 인쇄한다 — manuscript에 넣기 전에 5건에서
     재검증할 것.
   - 왜 Top: RQ3가 논문의 framing 위계를 되갚는 지점이다. "정적 발열 게이팅은 안전한 촬영과
     위험한 촬영을 구분하지 못한다"를 2.4는 주장하고 여기서는 **런타임 모델이 실패한 바로 그
     5건 위에서** 측정한다. 이게 없으면 그림은 변명 목록이고, 있으면 런타임 제어의 논거가 된다.

5. **이 표는 shadow audit이다: optional stage 전부 강제 실행 + watchdog 해제 상태에서 모델의
   판단만 채점한 것. 그래서 여기 unsafe 178건은 전부 이 recording에서 마감을 넘긴 촬영이고,
   RQ1의 timeout-free 결과는 enforced full-controller arm에 한정된 진술임을 명시해야 한다.**
   - 근거: `4_4_rq3_admission.tex` L4·L10(disjoint pool, demotion·watchdog 미적용),
     `docs/rq-evidence.md` 5.2("C > B와 그 촬영이 timeout 난 것은 같은 사건"; 초과 결정
     154건 전부가 timeout 난 촬영에 속한다), 5.3(모델 오판이지 출하 빌드가 낼 Capture Timeout이
     아니다).
   - 영문 초안: "The audit scores the decision as it was made: every optional stage is forced to
     execute and the watchdog is disarmed, so an unsafe admit here is a model misjudgement
     measured to completion under a condition different from deployment — not a harder version of
     the same one — and not a Capture Timeout a shipped build would emit. Because the budget is
     the time left to the deadline, every decision in the unsafe class, admitted or skipped,
     belongs to a capture that overran its deadline in this recording; the timeout-free result
     belongs to the enforced full-controller arm and is reported in RQ1."
   - 반드시 함께: (i) **"배포보다 가혹한 조건"이라고 쓰지 말 것.** 그건 "그러니 우리 수치는 배포
     품질의 보수적 하한"이라는 framing인데, 성립하지 않는다. 방어 가능한 형태는 **방향성**이다:
     일을 빼면 C가 내려가고 B가 올라가므로 **feasible 라벨은 강건**하고(97.3%는 audit 조건 때문에
     부풀지 않는다) **unsafe 라벨이 취약**하다 — 5건 중 3건의 B 판정이 정확히 그걸 보인다.
     (ii) 0729-only pool의 netted 수치(3 of 13, 23.1%)를 pooled 수치(4, 11.4%)와 짝지어
     "X에서 Y로"라고 쓰지 말 것 — 다른 모집단이고 pooled set 위에서 재계산되지 않았다.
   - 왜 Top: 나머지 RQ3 숫자 전부가 오독되는 걸 막는 문장이고, prose를 줄일 때 가장 먼저
     사라지는 문장이다. 이게 없으면 리뷰어는 "unsafe admit 5건"을 출하된 timeout 5건으로 읽거나
     97.3%를 배포 controller의 admit 비율로 읽는다 — 둘 다 이 절에 치명적이다.

### 말하면 안 되는 것
- "5건 모두 timeout이 안 났다" / "audit에서 timeout이 없었다". audit에서 unsafe 178건은 **전부**
  마감을 넘겼다. 방어 가능한 형태는 "출하 빌드에서 Capture Timeout으로 나가지 않았을 것".
- 97.3% / 97.2% / 2.8%를 배포 controller의 동작으로 제시하거나, 8,430건·143 run과 같은 문장에
  모집단 이름 없이 넣는 것.
- "결정의 2.8%가 unsafe admit이었다" — 분모가 3,746이 아니다.
- 97.2%나 5/5 정리를 bounded-margin / guaranteed-deadline / "admission is safe"로 승격.
- audit 조건을 "배포 품질의 보수적 하한"으로 쓰는 것.
- audit pool을 무작위/대표 표본으로 제시하는 것, 조건 간 unsafe-admit 비율을 비교하는 것.
- watchdog이 Capture Timeout을 "막았음을 증명한다"고 쓰는 것. 출하된 containment로만 보고할 것.
- `node` / `per-node watchdog` / `node-time admission`. manuscript는 그냥 "the watchdog"이고
  (`3_3_admission.tex`, `4_4`, `4_7`이 이미 "the watchdog of Section~\ref{sec:admission}"),
  나머지는 `optional stage` / `admission at each optional stage` / `the remaining stages of the
  Draft Sequence`. **`per-stage watchdog`이라는 제3의 이름을 새로 만들지 말 것.**
- `optional-work group` — manuscript 용어는 admission group, 또는 Multi-frame / Single-frame 그룹.
- 제거된 enforced 절반의 수치(93.6%, 87.5%, 99.6%, 98.0%, 59.9%)를 실행률로 재사용하는 것.
- 그림의 세 bar를 가산적으로 읽거나 latency 변화의 합으로 읽는 것.
- 표 머리글 `Feasible work` / `Unsafe work`는 exhibit 자신의 문구라 그대로 두지만, **prose는
  그걸 물려받지 않는다** — "the decisions the trace labelled feasible"로 쓰고, 결정 단위에
  작용하는 동사는 언제나 stage를 취한다(admits / skips / retains / executes optional stages).
- `docs/rq-evidence.md`의 `within-burst variation`을 그대로 옮기는 것 →
  "variation within the same run of consecutive captures".

---

## tab_rq4_pacing_sizing

> **파일 이름은 주소이지 설명이 아니다.** 2026-09-08 reframing 이후 RQ4는 지연의 *크기가
> 적절한지*를 묻지 않는다. 지금 묻는 것은 (a) 실제로 존재하는 Draft backlog에 비례해 pacing이
> 개입하는가, (b) 마감 여유가 얇게 끝난 촬영에 대해 작동하고 있었는가다. `sizing`이라는 이름에
> 기대어 크기 주장을 되살리지 말 것.

### 이 exhibit의 역할
reframed RQ4에 답하는 유일한 exhibit이고 **RQ4는 그림을 싣지 않는다**. 패널 (b)가 pacing 규칙과
독립적인 내용을 담은 절반이므로, prose는 (b)에 기대고 (a)는 "배포된 응답의 기술"이라고 드러내
놓고 라벨링해야 한다.

### 읽는 법 (writer가 틀리기 쉬운 것)
- **범위 함정 (가장 크다)**: 표에 조건·기기 라벨이 **하나도 없다**. 이건 **12MP normal 전용**이다 —
  (a) 패널 n 합이 556+894+912+688 = 3,050이고, 이는 116 run을 두 기기에 걸쳐 pool한 12MP gating
  결정 수다. `data/rq4/*.csv`에는 값이 다른 24MP 블록이 나란히 있다(>=50 활성화 79.1%,
  slack<5 coverage 90.2%). 전 조건 합은 6,119. **setup 문장이 모집단을 못 박지 않으면 독자는
  CSV의 24MP 행을 표로 읽는다.**
- **패널 (a) 행은 서로 배타적**이고 합이 3,050이다. **패널 (b) 행은 포함관계**다 —
  `<5`(139) ⊂ `<10`(392) ⊂ `<20`(869). **(b)를 절대 더하지 말 것.**
- **B가 무엇인가**: 완주한 trace에서 재구성한 **측정된** Draft backlog이지 controller 자신의
  추정(`controllerBacklogMs`, 더 낮게 나온다)이 아니다. 분모는 **남은 window T가 아니라 고정
  예산**이다. 결과: **밴드는 부하를 재지 위험을 재지 않는다.** 남은 window를 모르기 때문이고,
  그게 정확히 가장 무거운 밴드의 16.6%가 지연을 안 받은 이유다.
- **Slack이 무엇인가**: (b)의 행은 각 결정이 내보낸 촬영의 **실현된** timeout slack이다 —
  개입 *이후에* 측정된 결과이지 controller가 읽은 상태가 아니다.
- **d/B 분모**: 그 그룹의 **paced 결정 수**다(688이 아니라 574, 139가 아니라 133). `<10` 밴드가
  `--`인 건 paced 결정이 0이기 때문. 예전에 이걸 알려주던 표 주석이 삭제됐으므로 **이제 prose가
  유일한 전달자**다.
- **세 개의 시계를 한 문장에 섞지 말 것**: (i) controller가 실제로 읽은 결정 시점 상태
  (`timeToDeadlineMs`, 예약 시간, deficit, `controllerBacklogMs`), (ii) 결정 시점에 고정되지만
  사후 재구성된 값(= 인쇄된 밴드 자체), (iii) 순수 결과(`timeoutSlackPercent`).
- 용어: 이 양은 manuscript 전체에서 **`backlog`**다. `queued Draft work`는 2026-09-08에 폐기되어
  live 파일에서 전부 치환됐다(`_4_experiments.tex` L19, `3_4_pacing.tex` 7회, 패널 라벨
  "(a) Draft backlog B at the decision"). 되살리지 말 것.

### 반드시 말해야 하는 것

1. **마감 여유가 얇게 끝난 촬영일수록 pacing이 걸려 있었다 — 예산의 5% 미만으로 끝난 139건 중
   95.7%(133), 10% 미만 392건 중 92.3%(362), 20% 미만 869건 중 85.4%(742). 세 행은 포함관계다.**
   - 근거: 패널 (b) 세 행. `data/rq4/thin_margin_coverage.csv`의
     `12MP normal,slack<20/<10/<5`와 일치.
   - 영문 초안: "Where the realized deadline margin still ran thin, pacing was acting: of the
     captures whose Draft Sequence completed within 5\% of the budget, 95.7\% (133 of 139) carried
     a paced decision, and the share rises as the margin tightens across the three nested rows —
     92.3\% (362 of 392) within 10\% and 85.4\% (742 of 869) within 20\%."
   - 반드시 함께: (i) **필수 한계**: coverage는 실현 margin, 즉 개입 *이후에* 측정된 결과로
     라벨링된 값이다. 따라서 **놓친 개입의 상한**을 줄 뿐 **불필요했던 개입에 대해서는 아무 말도
     하지 않는다** — closed loop에는 "같은 촬영을 지연 없이 내보냈다면"의 반사실이 없다. 그걸
     확립하려면 새 matched run이나 검증된 closed-loop simulator가 필요하다. (ii) **동사 주의**:
     지연이 촬영 i를 지킨 것인지 다음 capture 기회를 지킨 것인지가 **아직 미해결**이다
     (블로커 참조). 확정 전까지는 "pacing was acting on" / "carried a paced decision"만 쓰고,
     **"released by a paced callback" / "protected" / "saved"는 금지**. (iii) 주어를
     "the controller"로 쓰지 말 것 — 그건 admission을 포함하는 이름이고, 이 패널은
     `appliedDelayMs > 0`만 센다(admission 관련 열은 RQ3 주제라 삭제됐다). (iv) 세 행은 중첩이므로
     합산 금지.
   - 왜 Top: controller가 계산하지 않는 양에 대고 진술된 **유일한 절반**이다. 패널 (a)는 pacing
     규칙의 지배항을 공유하므로 "모듈이 중요한 곳에서 작동했는가"에 스스로 답할 수 없다.
     2026-09-08 reframing이 존재하는 이유가 정확히 RQ4에게 이 주장을 시키기 위해서다.

2. **Draft backlog가 늘수록 pacing 개입도 단조 증가한다: 0.0%(0/556) → 8.2%(73/894) →
   45.0%(410/912) → 83.4%(574/688). 예산의 10% 미만으로 한가할 땐 556건 전부 지연 0 — 없어도 될
   때는 한 푼도 물리지 않는다.**
   - 근거: 패널 (a) 네 행. `data/rq4/pressure_response.csv`와 일치. `<10` 밴드에서 관측된 최소
     실현 여유는 예산의 35.1%(표에 없음).
   - 영문 초안: "Pacing activation tracks the Draft backlog actually present: it rises from 0.0\%
     of the 556 decisions taken while the backlog stayed under a tenth of the budget, through
     8.2\% (73 of 894) and 45.0\% (410 of 912), to 83.4\% (574 of 688) of those taken while at
     least half the budget was already queued; the ordering holds on each device read alone,
     where the lowest band activates on 0.0\% of decisions on both."
   - 반드시 함께: (i) **필수 한계**: 밴드 축이 측정된 backlog를 쓰긴 하지만 여전히
     `eq:pacing`의 지배항을 공유하므로, **이 네 행은 배포된 응답을 *기술*할 뿐 독립적으로
     *검증*하지 않는다.** 같은 문단 안에서 밝힐 것. (ii) 밴드는 고정 예산 대비 비율이므로 **부하를
     정렬하지 위험을 정렬하지 않는다** — 이게 4번 항목을 세팅한다. (iii) 35.1%는 **관측값이지
     하한이 아니다.** "no capture finished with less than 35.1%"처럼 전칭으로 쓰면 bounded-margin
     주장이 된다.
   - 왜 Top: `_4_experiments.tex`가 지금 적어놓은 RQ4 질문의 전반부이고, **0.0% / 556**이
     responsiveness-dominant trade-off의 응답성 절반을 보여주는 가장 깨끗한 숫자다. 무거운 밴드만
     본 리뷰어는 일괄 지연을 가정하는데, 0 행이 그걸 한 절로 반박한다.

3. **delay는 backlog 대비 **중앙값 기준** 작고, 압력이 커질수록 비중이 오히려 준다: 29.1% →
   13.0% → 8.3%(각각 paced 73/410/574 기준). 절대 지연도 같이 준다(419 → 377 → 348 ms) —
   분자와 분모가 반대로 움직이므로 비율 하락이 분모 팽창의 착시가 아니다. 큐를 비우려는 게
   아니라 도착률을 깎는 것이고, 적용된 453.3초 중 99.6%가 draft work가 남아 있는 동안 흘렀다.**
   - 근거: 패널 (a) `d/B P50` 29.1/13.0/8.3, 패널 (b) 10.1/10.7/11.2(paced 742/362/133 기준).
     `data/rq4/pressure_response.csv`, `thin_margin_coverage.csv`와 일치. 밴드별 절대 지연
     중앙값은 같은 CSV의 `delayP50Ms` 419 / 377 / 348 ms. 전체 1,057 paced 결정 기준 총 적용
     지연 453.3 s, 지연이 backlog를 넘은 결정 2건, 비중첩분 2.0 s = 0.4%(2자리로는 0.45%이므로
     "2.0 s of 453.3 s"와 "0.4%"를 나란히 두어 독자가 나눠보게 하지 말 것).
   - 영문 초안: "The delay is a small and shrinking share of the load it responds to at the median:
     29.1\% of the measured Draft backlog on the lightest band that paced at all, falling to
     13.0\% and then 8.3\% as the backlog grows — each median taken over that band's paced
     decisions (73, 410 and 574) and not over $n$ — and on the nested thin-margin rows it holds at
     10.1\% to 11.2\%. All but 0.4\% of the 453.3\,s of delay applied over the condition elapsed
     while Draft work was still outstanding, so pacing trims the rate at which captures arrive
     rather than draining what is already queued."
   - 반드시 함께: (i) **"적절한 크기"·"correct"·"minimum"·"optimal"로 쓰지 말고, \(d^{*}\)나
     reservation-to-\(T\) 비교를 되살리지 말 것** — 2026-09-08에 폐기된 주장군이다. (ii)
     **"bounded"라는 단어는 사실이 아니다.** 인쇄된 값은 전부 P50이고 **d/B에는 천장이 없다** —
     12MP의 1,057 paced 결정에서 P50 10.5%, P90 27.5%, P99 45.6%, **최댓값 155.1%**이고 2건은
     100%를 넘는다(그 2건이 바로 아래 work-conservation 절이 말하는 2건이다). 즉 "bounded"라고
     쓰면 자기 반례를 같은 문단에 인쇄하는 셈이고, bounded-margin 금지 규칙과도 충돌한다.
     → "small and shrinking **at the median**"으로 쓰고, **비례성 문장에는 항상 "중앙값이지
     상한이 아니다"를 붙일 것**. (iii) d 자체가 controller의 backlog 추정에서
     계산되므로 d/B는 자기 지배 입력의 재구성에 행동을 견주는 값이다 — **비용 readout이지 독립
     결과가 아니다.** (iv) **"it never idles the worker"라고 쓰지 말 것** — 1,057건 중 2건에서
     지연이 backlog를 넘었다. 주석 초안 `4_5_rq4_pacing.tex` L13이 이 문구를 쓰고 있으니 주석
     해제 전에 고칠 것. (v) 스케일 연구(0.5×, 0.75×)나 계수 sweep을 보고하거나 암시하지 말 것.
   - 왜 Top: 응답성 비용 readout이고 논문 어디에도 인쇄되지 않는다 — RQ1·RQ2는 절대 d를 찍고
     d/B는 아무도 안 찍는다. 그리고 저자 bullet이 폐기된 sizing 주장으로 넘어가는 지점이라,
     방어 가능한 문구를 미리 확정해두면 재작성을 아낀다.

4. **가장 무거운 밴드에서 지연이 안 걸린 16.6%(114/688)는 모듈이 실행에 실패한 게 아니라
   controller 자신의 테스트가 deficit ≤ 0을 반환한 경우다(114/114, 중앙값 −496 ms). 남은 window가
   278 ms 길고, 곧 돌 sequence 예약이 193 ms 작고, backlog 추정이 592 ms 낮았다. 결과도 같은
   방향이다 — 중앙 여유 19.3% 대 10.9%, 5% 미만이 114건 중 2건 대 574건 중 99건.**
   - 근거: 688 − 574 = 114, 114/688 = 16.57% → **16.6%**(100 − 83.4와 일치).
     paced 대비 unpaced 중앙값: `timeToDeadlineMs` 6,033 vs 5,755 ms,
     `draftSequenceReservedDurationMs` 861 vs 1,054 ms, `controllerBacklogMs` 3,618 vs 4,210 ms.
     메커니즘(결정 시점 필드 기준): 발열 Lv5–6에서는 직전 촬영이 이미 demote된 비율이
     **75.0% 대 43.5%**이고 예약이 843 ms 대 1,092 ms인 반면, Lv3–4에서는 직전 demote가 **5.2%**뿐이고
     남은 window가 더 길며 backlog 추정이 더 낮다.
   - 영문 초안: "The 16.6\% of the heaviest band that drew no delay are not interventions the
     module failed to run: all 114 recorded a non-positive projected deficit, so its own test
     declined. At overheat levels 5 and 6 the preceding capture was already demoted on 75.0\% of
     the unpaced group against 43.5\% of the paced peers and the reserve for the sequence about to
     run fell to 843\,ms against 1,092\,ms, while at levels 3 and 4 only 5.2\% were already
     demoted and what separates them is a longer remaining window and a lower backlog estimate. A
     large Draft backlog is therefore not by itself a high-risk state: the band measures the queue
     and not the window that remains."
   - 반드시 함께: (i) **"저발열"이라는 라벨은 틀렸다** — 양쪽 중앙 발열 레벨이 모두 4이고, 114건
     중 36건(31.6%)이 레벨 6이다. (ii) **"놓친 게 아니다"를 전칭으로 쓰지 말 것**: 114건 중 2건은
     여전히 5% 미만으로 끝났고, controller 추정 대신 측정 backlog를 넣으면 **28건이 trigger를
     넘는다**(그 28건은 중앙 13.8%, 최소 0.24%). **이 자기비판을 여기서 먼저 말하는 게 싸다.**
     (iii) 19.3% 대 10.9% 비교는 무작위 배정이 아닌 두 집단의 **연관**이지, 각 기각이 옳았다는
     증거가 아니다. (iv) 통합 skip 비율(40.4% 대 39.4%)로 이 집단을 설명하지 말 것 — 발열 레벨별로
     반대 방향의 두 경향을 숨긴다. (v) **58/56 같은 레벨별 개수는 `docs/exhibits.md`에 기록되기
     전까지 인쇄하지 말 것**(블로커 참조).
   - 왜 Top: 이 밴드는 적대적 질문을 정확히 하나 부른다 — "최악 사례의 6분의 1을 놓쳤네요".
     이게 그 답이고, 동시에 논문에서 가장 정직한 자기비판(114건 중 28건이 추정 미달에 업혀
     갔다)을 여기서 밝히면 싸고 리뷰어가 먼저 찾으면 비싸다.

5. **가장 아슬아슬했던 관측은 예산의 0.16%, 11 ms이고 3,050건 중 11건이 1% 미만이었다 — 전부
   포화 상태(backlog 27–71%, 큐 대기 28–72%, 발열 Lv4 이상)였고 10건에는 pacing이나 optional
   stage skip이 걸려 있었다. Slack<5%에서 지연이 없던 6건 중 5건은 admission이 그 촬영에서
   optional stage를 건너뛰도록 권고한 경우(실현 여유 17–230 ms)이고, 나머지 1건이 두 모듈
   어느 쪽도 손대지 않은 11 ms짜리다.**
   - 근거: `scripts/rq4_pacing_sizing_metrics.py`의 tail 출력(12MP normal). 예외 1건에 대해
     직전 세 촬영에 654·663·288 ms의 pacing이 적용됐고 admission은 다음 촬영부터 optional stage를
     건너뛰었다. 139 − 133 = 6 = 4.3%.
   - 영문 초안: "The tightest realized margin in the analyzed population was 0.16\% of the budget,
     or 11\,ms, and eleven of the 3,050 decisions finished under 1\%; all eleven were saturated
     states — 27 to 71\% of the budget already queued as Draft backlog, a 28 to 72\% queue wait
     before the capture's own Draft Sequence started, and overheat level 4 or above — and ten of
     the eleven met pacing, a skipped optional stage, or both. Realized slack is an outcome and
     not a bound."
   - 반드시 함께: (i) **숫자를 맨몸으로 두지 말 것.** 포화 맥락 + 제어 동작이 걸려 있었다는 사실 +
     주장 한계가 같은 호흡에 와야 한다. 아니면 "운 좋게 넘어갔다"로 읽힌다. (ii) **24MP를 pool하지
     말 것** — pool하면 0.06%, 4 ms, 6,119건 중 18건이 되고 AGENTS.md는 RQ4를 12MP normal로
     한정한다. 폐기된 컬렉션의 0.11% / 8 ms도 쓰지 말 것. (iii) 실현 slack은 결과이지 하한이
     아니다. baseline 반사실은 RQ1 몫. (iv) 그 5건의 skip이 아꼈다는 220–377 ms는 **같은 기기·같은
     발열 등급의 중앙값 대비 추정치**이지 그 촬영의 대안을 측정한 값이 아니다 — 추정이라고 쓰거나
     빼라. (v) **"예측 실패"가 아니다**: 6건 전부 deficit ≤ 0이었고, 측정 backlog를 대입해도
     **1건만** trigger를 넘는다(추정 미달 이야기는 114건 쪽이지 6건 쪽이 아니다). 그리고
     **"추후" admission skip이 아니다** — 5건은 그 촬영 **자체**에서 skip이 권고됐고, "추후"는
     나머지 1건에만 해당한다. (vi) 이 주장은 **prose 소유**다 — reframed 표는 margin 열을
     의도적으로 인쇄하지 않는다.
   - 왜 Top: "얼마나 가까이 갔었나"는 timeout 방지 주장에 대해 산업계 리뷰어가 던지는 첫
     질문이고, AGENTS.md가 어딘가에는 남기라고 요구한다. 표가 margin 열을 안 찍으므로 **prose가
     유일한 자리**다 — 여기 안 쓰면 그냥 빠진다.

### 추가로 반드시 있어야 하는 문장 (항목이라기보다 필수 구성)
- **모집단 못 박기**: "3,050 gating pacing decisions over the 116 full-controller runs of the
  12MP normal condition, pooled over the two devices." 전 컬렉션의 6,119 / 232는 나오면 안 된다.
- **제외 매니페스트**: `runStatus`가 CAPTURE_TIMEOUT인 9 run은 **operator test capture**로 제외됐다
  (2026-09-08 저자 확인). 기록된 pacing 결정이나 재구성된 backlog가 없는 행도 결정 단위로 제외.
  무효 측정으로 제시하고, survival-conditioned로 부르지 말 것.
- **sweep이 없는 이유를 긍정문으로**: AGENTS.md는 closed-loop 단서가 **RQ4의 prose에 속한다**고
  명시한다(Section 3.4에서는 2026-08-20에 제거됨). 같은 trace에서 기록 지연에 0.5나 0.75를 곱하는
  건 유효한 반사실이 아니고, 방어 가능한 스케일 연구에는 새 matched run이나 검증된 closed-loop
  replay/simulator가 필요하다. 계수가 왜 1/2인지 묻는 리뷰어에 대한 유일한 답이기도 하다.
- **자제의 readout**: 지연도 optional stage skip도 없었던 **1,367건(3,050건의 44.8%)**의 실현
  여유가 5퍼센타일에서 **24.7%**다(중앙값 66.5%). "개입하지 않은 것이 태만이 아니었다"를 가장
  강하게 말하는 값이고, 패널 (b) coverage 옆에 놓여야 한다. ⚠ **단서 필수**: 이 집단의
  *최솟값*은 0.157%다 — 항목 5의 그 11 ms 촬영이 바로 여기 속한다. 5퍼센타일에서 편안했다는
  진술이지 바닥이 아니다.
- **패널 (b)도 기기별로 단조이고, 미개입 6건이 전부 한 기기에 몰려 있다**: slack<5에서 S26
  94.3%(100/106), S26 Ultra 100.0%(33/33). 즉 **지연이 없던 6건은 전부 S26**이다. "두 기기를
  pool했다"는 반론을, 실제로 주장을 지고 있는 절반(패널 b)에서 무디게 만든다.
- **큐 수준**: backlog는 중앙 run에서 예산의 **59.4%**까지 올라갔고 116 run 중 3개에서 80%를
  넘었다. (재현값은 59.45%이므로 59.4 / 59.5 / "about 59%" 중 확정할 것. 그리고 관측 최댓값
  85.0%를 "bounded in every run we measured"로 쓰지 말 것 — 현재 주석 초안 L16의 문구.)
- **정의 두 개**(표 주석이 삭제되면서 prose로 옮겨진 load-bearing 문장): `d/B`의 분모는 옆 칸의
  paced 수이지 n이 아니다. `B`는 trace 재구성값이지 `eq:backlog`의 controller 추정 \(\hat B\)가
  아니다. 그리고 패널 (b)는 중첩이다.

### 말하면 안 되는 것
- 지연이 적절히 사이징됐다 / 옳다 / 최소다 / 최적이다. \(d^{*}\)나 reservation-to-\(T\) 비교.
- \(d^{*}\)를 "required / physically required / minimum / optimal delay"라 부르는 것
  (→ the retrospective matched-policy target; reframed RQ4는 이걸 부를 일이 없다).
- 실현 margin이 bounded다 / 마감을 보장한다 / 얇았던 촬영이 baseline에서는 timeout이었을 것이다
  (마지막은 RQ1 질문이다).
- pacing이 특정 촬영을 "protected"·"saved"했다고 쓰는 것(attribution 미해결).
- 패널 (a)를 선택성의 독립 검증으로 제시하는 것.
- 24MP를 thin-margin tail이나 어떤 RQ4 셀에든 pool하는 것. 0.11% / 8 ms / 3,781건 인용.
- 11 ms를 맨몸으로 두는 것.
- 스케일 연구·계수 sweep, 또는 타 도메인에서 가져온 pacing 기법과의 비교(저자가 명시적으로
  요청하지 않는 한).
- 114건을 "misses"라 부르거나 저발열 집단이라 부르는 것. 통합 skip 비율로 설명하는 것.
- 패널 (b) 행을 더하거나 배타적 그룹으로 취급하는 것.
- n을 d/B의 분모로 읽게 두는 것. B를 controller 추정이라 부르는 것.
- 99.3% "Either" coverage를 pacing 수치처럼 들여오는 것(admission이 섞여 있고, 그래서 열이
  삭제됐다). 쓰려면 admission을 명시할 것.
- 용어: `queued Draft work` → **backlog**. `burst` → queue-local / since the queue was last empty.
  (※ "since the queue last drained"나 "following a queue drain"도 금지 — 첫 연속 촬영 구간을
  오기술한다.) `node`, `Draft path`, `final processing`, `optional Draft work` 금지.

---

## tab_casestudy_selection + fig_casestudy_12mp

> ⚠ **먼저 확정할 것**: 디스크의 `.tex`와 `data/case_study/*.csv`는 **2026-08-03 컬렉션**이다
> (`data/U_ablation_sampling/48U_metrics_12MP_normal_0803_1.xlsx`의 runKey `1:30` — 30개
> `appliedDelayMs` 벡터로 동정됨). 반면 `docs/exhibits.md#fig_casestudy_12mp`는 **2026-09-06
> refresh**(run 28, M 1–14, S 전 30장, 19번째에서 792 ms 정점, backlog 정점 68.2%, Slack 최소
> 3.10%, 음영 없음)를 기술하면서 스스로 "never landed"라고 적고 있다. **아래 숫자는 전부 현재
> 컴파일되는 on-disk 버전 기준.** refresh가 반영되면 서사가 통째로 바뀐다 — run 28은 S를 아예
> demote하지 않으므로 두 레버가 얽히는 두 번째 episode가 사라진다.

### 이 exhibit의 역할
Section 4에서 독자가 admission과 pacing을 **같은 타임라인 위에서** 보는 유일한 자리. 통계를
보태는 게 아니라(그건 RQ1~RQ4가 한다) 조정 메커니즘을 촬영 단위로 보여주는 것이 일이다.

### 읽는 법 (writer가 틀리기 쉬운 것)
- 표 (a)는 데이터 없는 근거 3행. (b)는 5지표 × (This run / peer 중앙값 / peer [min–max] / 판정),
  peer는 조건 고정 n=10. **헤더가 "vs. med."다 — "vs. worst"가 아니다.**
- **단위 함정 1**: 표의 M·S는 RQ1 관례를 따라 **런당 "촬영 수"**(8, 22)로 찍힌다. 원 CSV 필드는
  퍼센트(26.7 → 8, 73.3 → 22)다. 그리고 **stage 인스턴스 수가 아니다** — `S`는
  `2_4_static_safeguards.tex`가 정의하듯 **단일프레임 stage들을 통칭**하고, 실행된 sequence key를
  보면 S 하나가 DECODING·FILTER·DECODING·WATERMARK **4개 인스턴스**다. 그래서 **"60개 optional
  stage 기회 중 30개"라는 분모를 쓰면 안 된다**(그건 지어낸 값이다). 총계가 필요하면
  "capture-level 기회 60개 중 30개"라고 명시할 것.
- **단위 함정 2**: "Pacing activated 55.2%"는 그 run의 **29개 transition 중 16개**이지 30장 중
  16장이 아니다(워크북 `transitionCount 29 / pacedTransitionCount 16`).
- **단위 함정 3**: 그림 (2)의 queue depth는 **realQueueDepth + 1**이다 — 커밋된 CSV가 서비스 중인
  Draft까지 세기 때문이고(`scripts/export_casestudy.py`가 그렇게 문서화하고 파일 재작성을 거부),
  30개 촬영 중 26개에서 +1이다(1·5·16·30번만 같다 — 그때는 실행 중인 게 없다). 즉 정점 6은
  **대기 5 + 실행 중 1**이다. `docs/exhibits.md`가 말하는 `realQueueDepth`는 착지하지 않은
  refresh 기준.
- **capture 2는 대치값이다.** runId 30의 `realBacklogMs`와 `realQueueDepth`가 2번째에서 비어
  있는데 커밋된 `12mp_normal_backlog.csv`는 650 ms / depth 1을 찍는다(export script가 이 사실을
  문서화하고 재생성을 거부). **backlog 상승 속도를 말하는 문장은 3번째(1,113 ms)부터 시작할 것.**
- **지연 막대의 인덱스는 미해결이다.** `\(d_i\)`가 다음 capture 기회에 적용된다는 것이 AGENTS.md의
  기호 규약이지만, 이 워크북의 두 필드는 반대쪽을 가리킨다 — `delayAppliesBeforeShotIndex`가 30행
  전부에서 자기 shot index와 같고, `shotToShotTimeMs − appliedDelayMs`가 29개 transition 전부에서
  `shotToShotWithoutRecordedPacingMs`와 잔차 0으로 일치한다. **확정 전까지 "i번째 지연이 i+1에
  나타난다" 형태의 문장을 쓰지 말 것.**
- 그림 (1) stage strip: lane 2 = M, lane 1 = S(export script 주석과 figure의 ytick이 일치 — 뒤집힌
  것 아님). 채운 사각형 = 실행, 빈 사각형 = admission skip.
- 그림 (4): Backlog와 Slack 모두 ms를 70으로 나눠 예산 대비 %로 그린다. **0% 점선은 Slack의
  실패 경계일 뿐 Backlog의 경계가 아니다.** 두 곡선은 예산을 분할하지 않는다(합이 45.5~73.2%).
  두 곡선이 거의 같아지는 지점은 **28번(33.3% vs 33.5%) 하나뿐**이고, 4~5번 사이의 역전에는
  근접 쌍이 없다. 어느 쪽이든 **주석하거나 서술하지 말 것**(`docs/exhibits.md` 금지 규칙).
- 음영 8–12는 가드 우회 baseline의 first-timeout window다. 8은 최이른 baseline onset
  (`tab_timeout_index`·`tab_rq1`이 인쇄), **12는 RQ1에서 제거된 Kaplan–Meier 중앙값**으로 현재
  manuscript 어디에도 출처가 없다. `docs/exhibits.md`는 이 밴드를 삭제하기로 기록했지만 `.tex`는
  아직 `\csTimeoutRange{8}{12}`를 네 번 그린다.
- **그려지지 않았지만 핵심**: `shotOverheatLevel`은 1–19번에서 4, 20–30번에서 5.
  `draftSequenceDurationMs` 중앙값은 1–8번 1,198 ms → 9–22번 758 ms → 23–30번 368 ms.
  `bokehAdmissionMarginMs`는 9번째에서 **−2.11 ms**. 셋 다 어느 exhibit에도 없다.

### 반드시 말해야 하는 것

1. **이 run은 표 (a)가 밝힌 대로 production guard가 optional stage를 막기 시작하는 overheat Lv4에서
   시작하고, 워크북상 30장 내내 Lv4~5다. 그 구간에서 controller는 M을 8장, S를 22장에서 실행하고
   30장을 완주했다 — "timeout을 막았다"가 아니라 "정적 guard가 막았을 기능을 켤 수 있게 했다"는
   얘기다. 그리고 Slack 최솟값 2.1%(8번째)는 절대 혼자 두지 않는다: 그 시점 backlog 43.3%, 해당
   촬영에 386 ms pacing, 5–8번 누적 1,629 ms, 9번부터 M skip.**
   - 근거: stage strip(M 1–8, S 1–22). 워크북 `shotOverheatLevel` 4(1–19) / 5(20–30).
     Slack 최소 150 ms = 2.142857%(8번, 워크북 자체 `timeoutSlackPercent`와 일치), 곡선은 0%
     점선에 닿지 않는다. 같은 촬영 backlog 3,033 ms = 43.33%, 적용 지연 386 ms,
     291+440+512+386 = 1,629 ms. 가드 정의 `2_4_static_safeguards.tex` L8. **이 run은 replay가
     아니라 실측이다** — `ReplayScope`의 `certificationStatus = FACTUAL_RECORDED_TARGET`,
     `targetPolicy = RECORDED_RUNTIME`, `actionEvidenceComplete = True`.
   - 영문 초안: "The plotted run starts at overheat level 4 — where panel~(a) records that the
     production guard begins suppressing optional stages — and stays at level 4 or 5 for all
     thirty captures. Within that range the controller executed the lightweight multi-frame Draft
     stage on 8 of the 30 captures and the single-frame stages on 22, and the run completed.
     Realized Slack reaches a minimum of 2.1\% of the budget at capture 8, where 43.3\% of the
     budget was already queued as Draft backlog, 386\,ms of pacing delay had been applied to that
     capture and 1,629\,ms over captures 5 to 8, and admission skipped the multi-frame stage from
     the next capture onward."
   - 반드시 함께: (i) **RQ1의 baseline 반사실을 이 문장에 섞지 말 것.** `0/10 (8)`과 `2.1%`가 한
     문장에 있으면 case study가 자기 통제 비교인 척하게 된다 — baseline은 **별도 문장에서
     `Table~\ref{tab:rq1_controller_behavior}` 상호참조로만**. 게다가 RQ1 baseline 모집단은 이
     case study 컬렉션이 아니다. (ii) 한 run의 최솟값은 **절대** bounded-margin이나
     guaranteed-deadline이 아니다. (iii) 가드가 모든 stage를 껐을 것이라고 **측정된 사실처럼**
     쓰지 말 것 — "run 전체가 가드가 optional stage를 억제하는 구간 안에 놓여 있다"로. 평가
     바이너리는 그 가드를 우회했다. (iv) **Capture Timeout 상수를 4장 어디에도 인쇄하지 말 것.**
     (v) "M 8장 + S 22장 = 60개 중 30개"를 쓰지 말 것 — 단위 함정 1 참조.
   - 왜 Top: AGENTS.md 위계상 case study의 본업이 여기다. 이 run은 이상적인 증인이다 — 정적
     가드라면 30장 연속 거절했을 것이고, 논문이 켜려는 바로 그 stage가 8장에서 실행됐다.
     **M의 숫자를 따로 말할 것**: 기능의 이름이 걸린 유일한 count이고(26.7%, 0906 peer 중앙값
     45.0% 대비), "optional stage 30개 유지"에 뭉뚱그리면 사라진다.

2. **이 run은 같은 조건 peer 10개의 **중앙값** 대비 5개 지표 전부 나쁜 쪽이다 — 다만 "최악"은
   아니다(peer 중 delay 최대 11.70 s, pacing 69.0%, Slack P5 4.6%). 그리고 "왜 이 run이냐"의
   실제 답은 조정 동작 다섯 가지를 모두 보인 유일한 세션이라는 **선정 필터**이므로 논문에
   밝혀야 한다.**
   - 근거: 표 (b) 5행 전부 "worse" 판정 — M 8 vs 14, S 22 vs 30, Pacing activated 55.2% vs
     31.0%, 누적 지연 5.21 s vs 4.17 s, Slack P5 5.2% vs 9.4%. **그러나 인쇄된 peer 범위 자체가
     "최악"을 반박한다**: 지연은 peer 최대 11.70 s, pacing은 69.0%, Slack P5는 peer 최소 4.6%,
     M 8은 peer 최솟값과 **동률**이다. 0803 peer로 재계산해도 같다(지연 최대 6,587 ms,
     paced 최대 62.1%, margin P5 최소 209.2 ms, M 최소 23.3%). 선정 필터는
     `scripts/export_casestudy.py`의 `evaluate()`: c1 30장 완주·timeout·watchdog 없음, c2 **첫
     optional-stage skip 이전에 pacing 활성화**, c3 두 skip이 서로 다른 촬영에서 순서대로(M 먼저
     S 나중), c4 skip 이후 pacing이 2장 이상 0으로 이완, c5 두 번째 skip 이전에 pacing 재활성화.
     docstring: "the unique session that survives the mechanism-coverage filter".
   - 영문 초안: "The plotted run is below the peer median on both stage-execution metrics and on
     Slack P5, and above it on both pacing costs, so it reads worse than the median on all five —
     though it is not the extreme of the peer range on any of them. We show the one session that
     exercises all of the controller's coordination behaviours."
   - 반드시 함께: (i) **"최악 케이스"라고 쓰면 표 자신의 peer 범위가 10초 만에 반박한다.**
     헤더도 "vs. med."다. (ii) **필터를 밝히지 않으면 항목 3이 순환 논증이 된다** — c2~c5가 바로
     그림이 "발견"했다고 주장할 동작이다. (iii) 표에 **셀 두 개가 깨져 있다**(블로커 참조).
     (iv) **0906 peer 집합에서는 10개 peer 전부가 S를 30장 실행한다.** 즉 그 행은 S를 8장
     건너뛴 run을 "아무도 S를 건너뛴 적 없는 모집단"에 대고 비교한다 — run의 속성처럼 보이지만
     실은 **컬렉션 차이**다. 따라서 "이 run만이 S를 skip한 유일한 run"이라고 쓰면 안 된다.
     (v) `docs/exhibits.md`는 이 필터가 0906 워크북에는 **아예 적용되지 않는다**고 적는다 —
     정직한 공개 문구가 컬렉션에 따라 달라진다.
   - 왜 Top: 단일 run 그림에 대한 리뷰어의 첫 반응이 "제일 좋은 걸 골랐겠지"다. 중앙값 대비
     전 지표 열세는 그 반응을 막는다. 하지만 "최악"으로 과장하면 표가 반박하고, 필터를 숨기면
     항목 3이 무너진다.

3. **위험 국면이 두 번 있고, 두 번 다 pacing 개입 → optional stage skip → 한 촬영 뒤 backlog
   감소·Slack 회복 순으로 관측된다(5→9→10번, 21→23→24번). 단 이 순서 자체가 케이스 선정
   조건이므로 "발견"이 아니라 "조정 동작을 모두 보이는 세션에서의 관찰"로 써야 한다.**
   - 근거: `12mp_normal_delay.csv` — 첫 양수 지연 5번째 291 ms, 5–12번
     291/440/512/386/372/455/554/696, 13–20번 0, 21번 12 ms → 24번 388 ms.
     stage: M 1–8 실행 / 9–30 skip, S 1–22 실행 / 23–30 skip
     (워크북 `recordedFirstPacingDelayShot 5`, `recordedFirstAdmissionSkipShot 9`와 일치).
     `margin.csv`: 5번 28.1%, **8번 최소 2.14%**, 15번 27.3%, 24번 5.06%, 30번 45.6%.
     `backlog.csv` 1차 차분(3번째부터): 4–5번 +672/+620 → 6–9번 +372/+65/+191/+323 →
     **10번째 첫 음수(−252)**; 21–23번 +272/+254/+58로 정점 63.8% → **24번째 −312**.
   - 영문 초안: "The run contains two pressure episodes and both are observed in the same order:
     pacing engaged at capture 5 and admission skipped the multi-frame stage from capture 9, and
     Draft backlog turned down at capture 10; pacing resumed at capture 21, admission skipped the
     single-frame stages from capture 23, and backlog turned down at capture 24 from its run peak
     of 63.8\%. Realized Slack recovers from 2.1\% to 27.3\% and from 5.1\% to 45.6\%."
   - 반드시 함께: (i) **인과 금지.** closed loop이므로 같은 촬영을 지연 없이 내보냈거나 skip 없이
     실행한 반사실이 없다. "backlog reverses within one capture of that skip"으로 쓰고
     **"pacing caused" / "admission restored" / "the skip cut backlog by X"는 금지.**
     (ii) **describes-not-tests 단서가 여기에도 붙는다**: 지연 막대는 controller 자신의 backlog
     추정에서 계산되고 backlog 곡선은 측정값이라 **규칙의 지배항을 공유한다** — 두 곡선의 시각적
     동조는 배포된 응답을 기술할 뿐 독립적으로 검증하지 않는다. (iii) **pacing 혼자 첫 국면을
     막지 못했다** — 지연이 네 번 걸린 뒤에도 backlog는 9번째까지 올랐고 Slack은 2.1%까지
     떨어졌다. 이 약화를 직접 쓰는 게 정직하다. (iv) **backlog 상승 문장은 3번째부터** 시작할 것
     (2번은 대치값). (v) **"i번째 지연이 i+1에 나타난다"고 쓰지 말 것**(읽는 법 참조).
     (vi) **두 국면에서 Slack 최저점의 위치가 다르다** — 첫 국면은 skip **직전**(8번), 두 번째는
     skip **직후**(24번). 완전히 같은 패턴이라고 쓰면 그림이 반박한다.
     (vii) **이 run에서 지연은 backlog에 단조가 아니다** — 최대 지연 696 ms가 12번째(backlog
     36.9%)이고, backlog 정점 63.8%인 23번째의 지연은 351 ms다. RQ4의 비례성 주장을 이 두 패널에
     그대로 옮기는 독자를 위해, **단일 run 관점의 한계**로 미리 말해둘 것(RQ4의 주장은 3,050건에
     대한 분포적 주장이다).
   - 왜 Top: 어떤 표도 못 하는 유일한 주장이다. 다만 순서 자체가 선정 기준이므로, **정직하게
     밝히면 "발견"에서 "예시"로 격하되지만 방어 가능해지고, 숨기면 리뷰어가 스크립트를 열었을 때
     절 전체가 무너진다.**

4. **admission이 바꾸는 건 큐에 쌓인 Draft Sequence "개수"가 아니라 한 Sequence가 실행하는
   Draft work의 "양"이다: 23→29번 사이 큐 깊이는 6(대기 5 + 실행 중 1)으로 그대로인데 backlog는
   63.8% → 31.8%로 줄고, 같은 구간 Sequence당 실측 실행 시간 중앙값은 1,198 → 758 → 368 ms로
   내려간다. 그리고 그 첫 skip은 **2.1 ms 차이로 내려진 결정**이다.**
   - 근거: `backlog.csv` — `queue_depth`가 23번과 29번 모두 6인 동안 `backlog_ms`가
     4,469 ms(63.84%) → 2,228 ms(31.83%). 워크북 `draftSequenceDurationMs` 중앙값
     1–8번 1,198 ms(범위 1,104–1,571) → 9–22번 758 ms(674–851) → 23–30번 367.5 ms(349–493).
     실행된 sequence key로 보면 23번 skip이 **DECODING·FILTER·DECODING·WATERMARK 4개 인스턴스를
     한꺼번에** 제거한다. 그리고 9번째 `bokehAdmissionMarginMs` = **−2.111 ms**(예측 상한
     1,219.1 ms 대 예산 1,217.0 ms).
   - 영문 초안: "Admission changes the Draft work each Draft Sequence carries rather than the
     number of Draft Sequences queued: between captures 23 and 29 the queue holds six Draft
     Sequences at both ends — five waiting and one in service — while Draft backlog falls from
     63.8\% to 31.8\% of the budget, and the measured per-Sequence Draft duration falls from a
     median of about 1.2\,s to 0.76\,s and then 0.37\,s across the two skips. The first of those
     skips was taken on 2.1\,ms of margin, the predicted upper bound exceeding the live budget by
     that amount."
   - 반드시 함께: (i) **인과 귀속 금지 + 이중 교란**: 20번째에 발열이 4 → 5로 오르고(두 번째
     국면 한가운데), 24–27번에 pacing이 388/283/189/66 ms를 동시에 걸고 있었다. admission 단독
     효과로 쓰지 말 것. (ii) duration 계열과 2.1 ms는 **워크북 측정값이고 그림이 인쇄하지 않는다** —
     측정 출처를 명시하거나 다섯 번째 패널로 내보낼 것. 그리고 phase 경계가 skip 자체이므로
     **효과 크기가 아니라 측정된 진행**으로 제시할 것. (iii) queue depth 관례(서비스 중 포함)를
     caption이나 패널 라벨에 적을 것. (iv) backlog는 **예측 drain 구간**이지 대기 시간의 합이
     아니므로 "backlog ÷ depth = Sequence당 시간"은 근사이지 산술이 아니다. (v) **여기서 용어가
     하중을 받는다**: 큐가 담는 건 Draft **Sequence**(개수), 줄어드는 게 Draft **work**(양),
     admission이 건너뛰는 단위가 Draft **stage**다. (vi) **S는 단일프레임 stage들의 통칭**이므로
     23번의 표시 하나가 4개 stage 인스턴스를 뜻한다고 밝힐 것.
   - ⚠ **narrative 위험 — demotion이 latch된다.** 9번째에 M이 skip된 뒤 남은 22장에서 한 번도
     돌아오지 않고, 23번째에 S가 skip된 뒤에도 마찬가지다. 워크북의 admission margin 열은 그
     전에 이미 양수로 돌아서는데도(`bokehAdmissionMarginMs` 10번 +377, 15번 +1,274;
     `filterAdmissionMarginMs` 25번 +182, 30번 +2,762) `bokehRecommendedAdmit` /
     `filterRecommendedAdmit`은 끝까지 False다. **그러므로 stage strip을 "admission이 매 촬영
     재평가해서 다시 admit한다"로 서술하면 안 된다 — 이 run에서 재admit은 한 번도 없다.**
     (margin 열이 이미 짧아진 sequence 기준으로 계산됐을 수 있으므로, 그게 "admit해도 안전했다"는
     증거는 아니다.) 저자 bullet 3("둘이 runtime 상황에 맞게 상호작용한다")이 정확히 이 함정으로
     걸어 들어간다 — 안전한 표현은 "admission이 각 optional stage 지점에서 live budget에 대해
     검사하고, 이 run에서는 두 번의 skip이 이후 계속 유지됐다"다.
   - 왜 Top: 논문 자신의 3단 어휘가 눈에 보이는 유일한 자리이고, backlog가 왜 꺾이는지를 독자가
     볼 수 있는 유일한 자리다. 그리고 **2.1 ms는 이 run에서 가장 인용 가치가 높은 숫자다** —
     정적 레벨4 가드는 30장 전부를 껐을 텐데, 런타임 검사는 **들어맞지 않는 첫 촬영을 2 ms
     차이로** 걸러냈다. 논문의 위계를 이보다 구체적으로 만드는 숫자가 없다.

5. **비용은 가시성이 아니라 회수 가능성으로 정렬한다: 5.21 s의 누적 지연은 shot-to-shot latency로
   나가 회수되지 않고, skip된 optional stage(M 22장 + S 8장)의 화질 비용은 final image가 Draft
   image를 대체할 때 끝난다 — 단 대상 모드의 post-processing은 앱이 백그라운드로 갈 때까지
   미뤄지므로 그 대체는 즉시가 아니다. 그리고 이건 한 기기·한 조건·한 run의 예시이지 일반성의
   근거가 아니다.**
   - 근거: 지연 패널 합 5,212 ms / 16개 paced transition(표의 "Cumulative applied delay 5.21 s").
     stage strip: M은 9–30번 22장에서, S는 23–30번 8장에서 skip.
   - 영문 초안: "The two costs the run pays are ranked by recoverability rather than by
     visibility: the 5.21\,s of cumulative applied delay lengthened shot-to-shot latency and is
     never recovered, whereas the fidelity cost of the skipped optional stages ends when the final
     image replaces the Draft image — and for this mode post-processing is deferred until the
     application backgrounds, so that replacement is not immediate and the Draft image is what the
     user sees for the whole foreground session. The run is one 30-capture session of one setting
     on one device under a saturating request rate; the population evidence is in RQ1 through RQ4."
   - 반드시 함께: (i) 건너뛴 stage를 masked/hidden/invisible/free로 묘사 금지 — 정적 레벨4 가드가
     충분했다고 인정하는 셈이 되어 논문의 전제가 녹는다. 응답성 비용은 "user-perceived".
     **회수 가능성 순서에는 반드시 "대체가 즉시가 아니다"라는 이유가 따라붙어야 한다** — 없으면
     그 순서가 곧 masked/free 읽기로 퇴화한다. (ii) 5.21 s를 작다/미미하다고 하지 말 것.
     (iii) **21.7 s 대비 24.0%를 쓰지 말 것** — `burstSpanMs` 21,717 ms는 5,212 ms의 지연을
     **포함**하므로 분모가 분자를 담고 있고(그래서 `docs/exhibits.md`가 표에서 뺐다), 게다가
     세션 평균 비용 비율이라 tail-latency 문제에 average-latency framing을 들여온다. 이 run의
     span은 자기 0803 peer 범위의 **최댓값**이기도 하다. (iv) **촬영당 지연 증가로 환산하지 말 것.**
     이유는 "`shotToShotTimeMs`가 `appliedDelayMs`를 안 따라간다"가 **아니다** — 실제로는
     `shotToShotTimeMs − appliedDelayMs`가 29개 전부에서 잔차 0으로 without-pacing 열과 일치한다.
     **진짜 이유는 closed loop이라 지연을 사실 trace에서 기계적으로 빼는 것이 AGENTS.md 금지
     사항이기 때문**이다 — 지연을 없애면 이후 backlog·admission·발열·실현 Draft 시간이 전부
     달라지고, 반사실에는 새 matched run이나 검증된 closed-loop replay가 필요하다.
     (v) `burstSpanMs`는 "30장 연속 촬영의 경과 시간"으로 번역할 것(`burst` 금지).
     (vi) **M과 S를 합치지 말 것** — 기능의 이름이 걸린 건 M 22장 skip이다.
   - 왜 Top: 모든 case study는 독자에게 "그래서 얼마 들었냐"를 계산하게 만들고, skip에 대한
     논문의 방어는 싸다가 아니라 **회수 가능성 순서**에 걸려 있다. 이 문장을 틀리면 2.3, 2.4,
     3.1을 동시에 반박한다.

### 또 하나 — 반드시 붙어야 하는 한계
- **coverage는 놓친 개입의 상한이지 불필요했던 개입에 대해서는 말하지 않는다.** 다섯 항목 전부가
  개입 → 회복 방향으로 읽힌다. 이 두 exhibit로는 16번의 paced transition이나 30번의 skip 중
  **어느 하나가 필요했는지** 보일 수 없다. closed loop에는 같은 촬영을 지연 없이 내보낸 반사실이
  없고, 만들려면 새 matched run이나 검증된 simulator가 필요하다. case study prose에서 한 번 말할 것.

### 말하면 안 되는 것
- **"최악의 run이다"** — 표 자신의 peer 범위가 반박한다. "중앙값 대비 5지표 전부 나쁜 쪽"이다.
- case study가 pacing이 Capture Timeout을 "막았음"을 보인다 / margin이 bounded다 / 마감이
  보장된다. 한 세션의 Slack 최솟값 2.1%일 뿐이고, 반사실은 RQ1 몫(그리고 **같은 문장에 넣지 말 것**).
- pacing-먼저 순서, M-먼저-S-나중 순서, 8장 이완, 두 번째 skip 전 재활성화를 **경험적 발견**으로
  제시하는 것. 넷 다 선정 기준 c2–c5다.
- **stage strip을 "매 촬영 재평가·재admit"으로 서술하는 것.** 이 run에서 skip은 latch된다.
- "i번째 지연이 i+1에 효과가 난다" — 인덱스 귀속이 미해결이고 워크북 필드는 반대쪽을 가리킨다.
- Backlog와 Slack 곡선의 교차점을 주석하거나 서술하는 것.
- 두 곡선이 예산을 분할한다거나 100%로 합쳐진다고 쓰는 것.
- Capture Timeout 상수를 4장 어디에든 인쇄하는 것(1% = 70 ms 환산도 밖으로).
- "60개 optional stage 기회 중 30개" — 지어낸 분모다. M·S는 **촬영 수**이고 S 하나가 4개 stage
  인스턴스다.
- "이 run만이 S를 skip한 유일한 run" / "모든 peer가 S를 30장 전부 실행했다" — peer 열과 그려진
  run이 서로 다른 컬렉션이라 **컬렉션 차이를 run 속성으로 파는 것**이 된다.
- baseline의 8번째를 "무제어 run이 보통 실패하는 지점"으로 쓰는 것 — 10회 중 최솟값이다.
- 누적 지연을 경과 시간으로 나눈 24.0%, 또는 transition당 180 ms, 또는 exporter의 without-pacing
  평균(569.1 ms 대 관측 748.9 ms)과의 차이. 마지막은 AGENTS.md가 명시적으로 금지한 뺄셈이다.
- "큐가 Draft work를 담는다", "admission이 큐를 줄였다", "admission이 Draft work를 건너뛰었다".
- pacing이 admission에 deficit의 수치 몫을 넘겼다고 설명하는 것.
- case study를 일반성의 증거로 세우거나 RQ4의 thin-margin tail(0.16% / 11 ms)과 비교하는 것 —
  다른 모집단이다.

---

## 저자 메모 검증

저자가 준 예시 bullet을 하나씩 채점한다. **"과장"과 "틀림"만 고치면 되고, "맞음"은 그대로
쓰되 분모/단서를 붙이면 된다.**

### (1) tab_rq1_end_to_end_summary

| 저자 bullet | 판정 | 고친 형태 |
|---|---|---|
| "모든 촬영 조합, 컨디션에서 timeout이 발생 안한다!!" | **맞음 + 범위 과장** | 인쇄된 셀 읽기로는 정확하다(28행 전부 `10/10 (--)`). 다만 "모든 촬영 조합"은 틀렸다 — 수집된 4개 해상도·메모리 조합 중 **2개**다. 그리고 현재형 단정은 보장으로 읽힌다. → "평가한 2기기 × 2컨디션 × 시작레벨 0–6, 28개 셀 전부에서 분석 대상 run이 30장 안에 Capture Timeout 없이 완주했다." 여기에 **제외 문장**(timeout 라벨 기록 = 무효 측정)과 **baseline 대비**(26/28 셀 실패)를 반드시 붙일 것. |
| "5장 이내에서 stage execution이 높고 pacing delay도 적게 걸려서 본 구현이 사용성에 최적화 되있다!" | **절반 맞고 절반 틀림** | *stage execution이 높고*: **맞고, 저자가 말한 것보다 강하다** — M@5 ≥ 4.5, S@5 ≥ 4.6이 28행 전부이고 23행이 5.0/5.0.  *pacing delay도 적게 걸려서*: **크기로 읽으면 틀렸다.** 표는 반대를 말한다 — `d P50@5`가 737/685/616/547 ms에 이르고 `@30` 전체 최댓값 538 ms보다 크다. 맞는 건 **빈도**다: Activated@5는 가능한 4번 중 최대 1.8, 14행에서 0.0.  *사용성에 최적화*: **과장.** 설계에 초반 5장을 우대하는 규칙이 없다 — 실현된 동작이지 최적화 목표가 아니다. → "초반 5장에서는 스테이지를 거의 다 실행하고 pacing은 드물게만 개입한다. 대신 개입할 때의 지연은 작지 않다." |
| "admission 및 pacing 개입에 따라 동적으로 변화한다" | **방향 맞음, 너무 모호** | 단조 증가 사례를 인용하되(S26U 12MP: M@30 30.0 → 10.9, d P50@30 127 → 521), **개입이 레벨에 단조가 아니라는 점**을 같이 말하는 게 더 강하다(S26U 24MP Activated@30이 11.0/10.2/10.8/11.0/10.6/8.5/8.5로 사실상 평평; S26 12MP는 Lv4에서 꺾임). ⚠ **24MP의 Lv4 → Lv5 전이를 예시로 쓰지 말 것** — 그 지점이 12MP fallback 경계라 워크로드 자체가 바뀐다. |

### (2) tab_rq2_ablation

| 저자 bullet | 판정 | 고친 형태 |
|---|---|---|
| "admission, pacing 둘 다 있어야 stage execution도 높고 timeout도 발생안하고 delay도 적절히 분산된다" | **3개 중 2개 생존, 1개 틀림** | *stage execution이 높고*: **분모 필요.** Full이 S는 세 패널 전부 최고이고 M은 3중 2에서 최고지만, **S26 12MP에서는 Pacing only의 M(61.4%)이 Full(56.0%)보다 높다.** 답은 인접 Captures 셀이다 — 61.4%는 요청 촬영의 61.4%만 정시 완료했다는 뜻이고 Full은 100.0%다. "배달 기준 M이 가장 높다"로 도망가면 **안 된다**(그 기준으로는 admission이 꺼진 구성이 정의상 100%).  *timeout도 발생안하고*: **사실로는 맞고 표현이 틀림.** "no valid analyzed run timed out" + full controller 한정 + 제외 비대칭 1회 명시. 그리고 Full 모집단은 10/10·11/11·10/10 = **31 run 중 31**이지 표에 찍힌 30 중 30이 아니다.  *delay도 적절히 분산된다*: **과장이고, 한 패널에서 표가 반박한다.** S26U 12MP는 Full이 **덜** 자주 개입하고 중앙값이 **1.8배 크다**(37.9%@437 vs 51.1%@242). 게다가 세 비교 전부 불공정하다 — Pacing only는 살아남은 앞부분(133/101/257 transition)에서만 측정됐다. |
| *(저자가 빠뜨린 것)* | — | **이 표에서 가장 값진 사실**: Admission only가 한 조건에서는 혼자 마감을 지키는데, 그 방법이 M을 No control 수준에 그대로 묶어두는 것이다(29.0 → 29.3 / 24.3 → 24.3 / 42.3 → 44.3). 같은 구간 S는 33.7 / 51.0 / 51.3으로 올라간다. **기능 활성화 논거가 측정된 지점이 여기다.** |

### (3) tab_rq3_admission_quality + fig_rq3_unsafe_spike_anatomy

| 저자 bullet | 판정 | 고친 형태 |
|---|---|---|
| "우리 admission 성능 좋다!" | **맞음, 덜 구체적** | 양방향이라는 게 핵심이다. → "feasible 판정의 97.3%(3,470)를 admit하고 unsafe 판정의 97.2%(173)를 skip한다 — 3,746건 shadow audit 기준." false-positive 분해(2.7%, 98건, 24MP multi-frame 5.3%에 집중)를 붙여 한쪽 주장으로 읽히지 않게 할 것. |
| "unsafe admit 파헤쳐 보니, 원래대로라면 watchdog 발생했을거고 이전/이후 stage 수행에서 stage skip 됐을거라 안전하다" | **접속이 틀림 + "안전하다"가 과장** | (1) **"그리고"가 아니라 "또는"이다.** 그림 주석은 M1·M2가 watchdog, M3·S1·S2가 earlier/later stage skip — **2 + 3**이지 각 건이 둘 다가 아니다. `docs/exhibits.md`는 "M1–M2는 watchdog으로만 커버되며, 자기 결정 집합에서도 예산 초과라 **진짜 모델 오류 2건**"이라고 못 박는다. **그 2건을 인정하고 쓰는 게 나머지 3건을 믿게 만든다.** (2) "안전하다"는 너무 강하다 — 지지되는 표현은 "출하 빌드에서 Capture Timeout으로 나가지 않았을 사례들"이고, 5건에 대한 사후 설명이지 보장이 아니다. 게다가 **watchdog 차단 자체가 비용**을 동반한다(stage 결과 상실, 이미 쓴 시간 미회수). (3) **"이전/이후"는 맞고 그대로 살릴 가치가 있다** — 비자명한 부분이다. 결정 *뒤에* 거부된 stage는 비용을 없애고, *앞에* 거부된 stage는 경로를 줄여 예산을 늘린다. |
| "core가 갑자기 줄고 cpu time이 느는건 절대 예측할 수 없다" | **두 번 과장** | (1) **5건 전부가 아니다.** busy core는 M1 0.60, M2 0.59, S1 0.76으로 떨어지고 S2는 0.96으로 평평하지만, **M3는 1.08로 올랐고** CPU time(1.23배)이 latency(1.14배)보다 더 자랐다 — 진짜 추가수요 사례다. "5건 중 4건"이라 쓰거나 M1/M2/S1을 이름으로 부를 것. (2) "절대 예측할 수 없다"는 exhibit이 감당 못 하는 절대 진술이다. 더 좁고 **논거로는 더 강한** 형태: 이 순간들의 발열 레벨·thermal status가 직전 (안전했던) 촬영과 **동일**했고 blocking GC는 0인 반면 run-queue wait과 context switch는 양방향으로 움직였다 → **admission 시점에 읽을 수 있는 신호로는 이 결정들을 직전 촬영과 구분할 수 없다.** (단, 이 통제 신호 비교는 8건 regeneration 기준이라 5건에서 재검증 필요.) |

### (4) tab_rq4_pacing_sizing

| 저자 bullet / 메모 카드 | 판정 | 고친 형태 |
|---|---|---|
| "위험도가 높아질 수록 pacing 개입이 늘어난다" | **방향 맞음, 단어 하나 틀림** | 활성화 경사는 실재하고 단조다(0.0 → 8.2 → 45.0 → 83.4%). 다만 패널 (a)의 축은 **위험도가 아니라 부하**다 — 고정 예산 대비 측정 backlog일 뿐, 그 촬영의 남은 window를 모른다. (남은 window T로 정규화하면 >=50 밴드가 688건이 아니라 1,138건이 되고 활성화는 83.4%가 아니라 78.0%가 된다.) → "pacing 개입은 실제로 쌓인 **Draft backlog**에 비례해 늘어난다"로 쓰고, 위험은 패널 (b)가 담당하게 할 것. + describes-not-tests 단서. |
| "pacing 크기는 backlog의 10% 정도 크기로 적절하다" | **직관은 절반 살고, 단어는 틀림** | (i) **"적절하다"는 2026-09-08에 폐기된 sizing 주장**이고 이 표로는 답할 수 없다 — 이 단어는 버려야 한다. (ii) 다만 **"10% 정도"라는 직관 자체는 서술적으로는 맞다**: 12MP의 paced 1,057건 전체에서 d/B 중앙값이 **10.5%**다. 단 그 값을 패널 (b)의 10.1~11.2%에서 읽으면 안 된다 — 거기는 다른 모집단(얇은 여유 집단)이고, 패널 (a)는 29.1 → 13.0 → 8.3%다. 그리고 **10.5%는 현재 repo 어느 파일에도 없다** — 인용하려면 같은 커밋에서 `docs/exhibits.md`에 기록해야 한다. → "delay는 backlog 대비 중앙값 기준 작고 압력이 커질수록 비중이 오히려 준다(29.1 → 13.0 → 8.3%, 절대 지연도 419 → 377 → 348 ms) — 큐를 비우는 게 아니라 도착률을 깎는다. 단 중앙값이지 상한이 아니다(P99 45.6%, 최댓값 155.1%)." 패널 (b)의 평평한 10~11%는 **별개의 두 번째 관측**이다: 얇은 여유에 대한 coverage는 **더 많이 쓰는 게 아니라 개입하는 것**에서 나온다. |
| "> 50 Paced 되지 않은 16.7%" | **숫자 0.1 틀림** | 114/688 = 16.57% → **16.6%**(100 − 83.4와 일치). 16.7%는 115/688이다. 밴드 라벨도 `>50`이 아니라 `>=50`. |
| "1. Backlog는 크지만 감당 가능 (저발열)" | **틀림** | **저발열이 아니다.** 양쪽 중앙 발열 레벨이 모두 4이고, 114건 중 36건(31.6%)이 **레벨 6**이다. 이 절반을 가르는 건 발열이 아니라 **더 긴 남은 window와 더 낮은 backlog 추정**이다. |
| "2. 직전 Admission skip으로 pacing 비용 ↓" | **맞음, 단 절반에만** | 레벨 5–6 부분집합에서만 성립한다: 직전 촬영이 이미 demote된 비율 **75.0% 대 43.5%**, 예약 **843 ms 대 1,092 ms**. 레벨 3–4 쪽은 직전 demote가 **5.2%**뿐이다. |
| "각각 50% 씩 담당 (58/56)" | **숫자는 실재·완전하지만 라벨이 어긋남** | 58 + 56 = 114는 맞고 **완전 분할**이다. 데이터에서 114를 58/56으로 정확히 가르는 분할은 **발열 레벨 분할 하나뿐**이다(Lv3 24, Lv4 34, Lv5 20, Lv6 36 → Lv3–4 = 58, Lv5–6 = 56). "(1) 저발열 / (2) 직전 admission skip"으로 가르면 **45/69**가 나온다. (단 "저자가 발열 분할을 의도했다"는 검증 불가이므로, "데이터에 존재하는 유일한 58/56 분할"이라고만 쓸 것.) ⚠ 레벨별 개수는 `docs/exhibits.md`에 기록되기 전까지 인쇄하지 말 것. |
| "Slack < 5%, Paced 되지 않은 4.3% (6)" | **맞음** | 139 − 133 = 6 = 4.3%. |
| "→ Pacing 예측 실패" | **6건 중 최대 1건** | 6건 **전부** deficit ≤ 0이었고, controller 추정 대신 측정 backlog를 넣어도 **1건만** trigger를 넘는다. 추정 미달 이야기는 **114건 쪽**(28/114)이지 이 6건이 아니다. |
| "→ 추후 admission이 skip" | **6건 중 1건만 "추후"** | 5건은 admission이 **그 촬영 자체에서** skip을 권고했고 실제로 해당 stage가 실행되지 않았다(실현 여유 17–230 ms). "추후"는 나머지 1건 — 두 모듈 어느 쪽도 손대지 않은 11 ms짜리 — 에만 해당한다. |
| "→ Timeout 발생 x" | **관측으로는 맞음, 보장으로 쓰면 안 됨** | 분석된 12MP 3,050건 중 timeout 0. 다만 보장/하한으로 표현 금지이고, 제외된 9 run(operator test capture)을 함께 밝힐 것. |

### (5) tab_casestudy_selection + fig_casestudy_12mp

| 저자 bullet | 판정 | 고친 형태 |
|---|---|---|
| "timeout window 전에 pacing이 개입했고 backlog 증가를 둔화 시켰다" | **절반 맞음, 세 위험** | *window 전 개입*: **사실이다**(첫 지연 5번째 291 ms, 음영은 8번째 시작). 위험 셋: (i) "첫 skip 이전에 pacing 활성화"는 **선정 기준 c2**라서 그림이 발견한 게 아니다 — 필터를 밝혀야 한다. (ii) 음영의 오른쪽 끝 **12는 RQ1에서 제거된 Kaplan–Meier 중앙값**이라 manuscript 어디에도 출처가 없다. (iii) **"5번째 지연이 미루는 6번째에서 증가가 꺾였다"는 메커니즘 문장을 쓰면 안 된다** — 지연 인덱스 귀속이 미해결이고, 이 워크북의 두 필드(`delayAppliesBeforeShotIndex`, `shotToShotWithoutRecordedPacingMs`)는 오히려 반대쪽을 가리킨다. *증가 둔화*: **지지되지만 인과로 쓰면 안 되고 "멈췄다"로 올리면 안 된다.** 차분은 4–5번 +672/+620에서 6–9번 +372/+65/+191/+323으로 떨어진다(**2번째 값은 대치값이라 3번째부터 시작할 것**). 그리고 backlog는 9번째까지 계속 **올랐고** Slack은 2.1%까지 떨어졌다. |
| "위험순간 admit skip을 통해 backlog도 줄이고 timeout margin도 늘리면서 위험에서 벗어났다" | **방향 맞음, 귀속 과장** | 촬영 번호는 정확하다(M skip 9번 → backlog 10번에 반전 → Slack 15번에 27.3%; S skip 23번 → backlog 24번 반전 → Slack 30번에 45.6%). 과장은 "admission 단독"이다 — 같은 구간에 pacing이 9–12번에 372/455/554/696 ms, 24–27번에 388/283/189/66 ms를 동시에 걸고 있었고, **20번째에 발열이 4 → 5로 오른다.** → "각 skip 한 촬영 안에 backlog가 반전되고, 그동안 pacing도 계속 걸려 있었다"(공동 귀속, 측정량, 보장 없음). "위험에서 벗어났다"를 안전 진술로 만들지 말 것. |
| "admission, pacing 둘이 runtime 상황에 맞게 상호작용한다" | **맞지만 표현 하나가 함정** | 저자가 가리키고 싶어 할 패턴 — 13–20번 8장 동안 pacing이 정확히 0으로 이완했다가 21번에 재개 — 이 **선정 기준 c4·c5**다. 더 큰 문제: **"runtime 상황에 맞게"가 "매 촬영 재평가한다"로 읽히는데, 이 run에서 skip은 latch된다** — 9번 M skip 이후 22장 내내, 23번 S skip 이후 끝까지 한 번도 재admit되지 않는다(워크북 margin 열은 그 전에 이미 양수로 돌아서는데도 recommend 플래그는 False 유지). 안전한 표현: "admission이 각 optional stage 지점에서 live budget에 대해 검사하고, 이 run에서는 두 번의 skip이 이후 유지됐다". 저자가 안 말한 더 강한 사실 추가: **23–29번에 queue depth가 6으로 고정인데 backlog는 반토막 난다** — 이게 상호작용을 "두 레버가 같은 일을 한다"가 아니라 **분업**으로 만든다. |
| *(저자가 빠뜨린 것 3개)* | — | (i) **run 전체가 overheat 4–5**, 즉 production 가드가 optional stage를 전부 막는 구간이라는 사실. 이게 case study를 timeout 완화가 아니라 **기능 활성화** framing에 묶는다(단 RQ1 baseline은 별도 문장의 상호참조로만). (ii) **9번째 skip이 2.1 ms 차이로 내려진 결정**이라는 것 — 정적 가드는 30장을 다 껐을 텐데 런타임 검사는 들어맞지 않는 첫 촬영을 2 ms 차이로 걸러냈다. 이 run에서 가장 인용 가치가 높다. (iii) **비용의 회수 가능성 순서.** |

### P1 — 일관성·출처

7. **`4_7_threats.tex`가 "one device … only for the Galaxy S26 Ultra"라고 쓰고 있다.**
   `tab_setup`은 2기기, `tab_rq1`은 두 기기 28셀, `tab_rq2`에 S26 패널, `4_5`는 "pooled over the
   two devices". git이 방향을 확정한다: 4.7은 `2583e14`(2026-08-25)가 마지막이고 S26은
   `1a7ed0a`(2026-08-31)에 추가됐다 — **4.7이 stale이고 2기기가 현재다.** 4.7을 되살리기 전에
   그 첫 문단을 "two device models, one per SoC vendor"로 고쳐야 한다.

8. **`4_7_threats.tex`가 현재 build에서 빠져 있다.** 그래서 **"The controller offers no formal
   deadline guarantee"와 evidence-adaptive-not-bounding 문장이 PDF 어디에도 없다.** AGENTS.md의
   never-bounded-margin 규칙을 생각하면, 그 문장이 자리를 찾기 전에는 RQ1 headline을 책임 있게
   쓸 수 없다. 나머지 셋도 갈 곳이 필요하다: 느린 cadence 한계와 study recording path 비용은
   4.1로, cross-device 한계는 결론이나 복구된 4.7로. (참고: `4_4_rq3_admission.tex` L5가 "the
   study recording path"를 이미 소개된 것처럼 참조한다.)

9. **case study가 어느 컬렉션으로 나가는가.** 디스크는 2026-08-03(run key 1:30), `docs`는
   2026-09-06 refresh(run 28)를 기술하며 "never landed"라고 적고 있다. **run 28은 S를 아예
   demote하지 않으므로 두 레버가 얽히는 두 번째 episode가 사라진다.** 그리고 refresh에는
   mechanism-coverage 필터가 적용되지 않아(같은 조건 peer 전부가 레벨4에서 S를 30장 실행)
   정직한 공개 문구 자체가 달라진다.

10. **case study 표에 결함이 세 개 있고, 유일한 기계 생성 backing artifact가 하필 틀린 행에서만
    표와 일치한다.** 문서가 이름을 대는 10개 peer run ID로 재계산하면 peer 중앙값 5개 중 4개가
    자릿수까지 재현되지만:
    - (a) **S peer 범위는 `[30--30]`이어야 한다**(표는 `[22--30]`). 원인은 pooling 관례가 아니라
      **갱신되지 않은 0803 행**이다 — `[22--30]`은 커밋된
      `data/case_study/12mp_normal_peer_comparison.csv`의 `filterExecutionPercent` 범위
      (73.3% → 22, 100% → 30)를 그대로 옮긴 값이다.
    - (b) **지연 peer 최댓값 9.70 s는 어느 컬렉션과도 맞지 않는다.** 0906 peer 최대는 11,702 ms
      (= 11.70 s), 0803 peer 최대는 6,587 ms(= 6.59 s)다. 9.70 s는 **출처 없음**.
    - (c) **0906 peer 집합에서는 10개 peer 전부가 S를 30장 실행한다.** 즉 S 행은 S를 8장 건너뛴
      run을 "아무도 건너뛴 적 없는 모집단"에 대고 비교한다 — **컬렉션 차이가 run 속성처럼
      보이는 것**이라 그대로 두면 잘못된 문장을 유도한다.
    - (d) 부수: peer 중앙값 M이 13.5장이라 정수 14로 찍혀 있다(확인 필요).
    → 세 개 다 **prose를 쓰기 전에 고쳐야 하는 항목**이지 open question이 아니다.

11. **case study 표 (b)의 provenance가 섞여 있다.** "This run" 열은 2026-09-07 저자 공급값으로
    고정, peer 열은 2026-09-06 워크북에서 재계산, 그려진 run은 2026-08-03 컬렉션이다. 그리고
    문서가 근거로 대는 `data/case_study/12mp_normal_author_supplied_this_run.csv`는 git 이력에
    존재한 적이 없다.

12. **\(d_i\)가 촬영 i를 지키는가, 다음 capture 기회를 지키는가 — RQ4와 case study 양쪽에
    걸린다.** ML clone(`@80cd230`)의 증거가 양쪽을 가리킨다 — `CaptureAvailableApmPolicy`는
    `captureAvailable` runnable을 `appliedDelayMs` 뒤로 미루고(=나중 촬영), 반면
    `CaptureMetricsExcelExporter`는 `delayAppliesBeforeShotIndex = shotIndex`로 "이 촬영의
    incoming transition에 속한다"고 적는다. AGENTS.md의 기호 규약은 "\(d_i\) applies to the next
    capture opportunity"다. **case study 워크북의 두 필드는 후자 쪽이다** —
    `delayAppliesBeforeShotIndex`가 30행 전부에서 자기 shot index와 같고,
    `shotToShotTimeMs − appliedDelayMs`가 29개 transition 전부에서
    `shotToShotWithoutRecordedPacingMs`와 잔차 0으로 일치한다.
    **확정 전까지: RQ4 패널 (b)의 동사는 "pacing was acting on" / "carried a paced decision"이고
    "released by" / "protected"는 금지. case study에서는 "i번째 지연이 i+1에 나타난다" 형태의
    문장 금지.** 확정하면 커밋 해시를 기록할 것.

13. **RQ3 exhibit 이름이 셋이다.** 파일 `tab_rq3_admission_quality.tex`, Notes 포인터와 docs
    heading `tab_rq3_admission_summary`, LaTeX label `tab:rq3_admission_audit`, AGENTS.md 맵은
    `tab_rq3_admission_summary.tex`. 한 커밋에서 정렬할 것(label은 유지 가능 — AGENTS.md가 label로
    인용하라고 하므로).

14. **RQ1 표에 label이 두 개**(`tab:rq1_preventive_alignment`, `tab:rq1_controller_behavior`).
    하나로 정리할 것.

14b. **이 문서가 인용한 숫자 중 상당수가 "참이지만 repo에서 읽을 수 없다".** 검증 패스가 직접
    재현해서 확인했지만 `.tex`·`docs/`·`data/` 어디에도 없는 값들이다 — RQ4의 기기별 활성화
    분할, 114건의 발열 히스토그램(24/34/20/36)과 대안 분할(45/69)과 Lv3–4 중앙값들,
    6건의 행별 slack과 flip 산술, d/B의 P90/P99/최댓값과 pooled 중앙값 10.5%,
    밴드별 절대 지연 419/377/348 ms, run별 backlog 정점(중앙 59.45%, 최대 85.03%),
    미개입 1,367건의 통계, case study의 `draftSequenceDurationMs` 계열과 2.1 ms margin과
    실행 sequence key. **AGENTS.md는 exhibit이 바뀌면 같은 커밋에서 `docs/exhibits.md`를
    고치라고 요구한다.** → 인용할 숫자를 정하고 그것들을 먼저 `docs/exhibits.md`에 기록하거나,
    아니면 주석 초안이 이미 쓰는 정성적 형태("the ordering holds on each device read alone")를
    유지할 것. **이게 이 세트에서 가장 큰 잔여 리스크다.**

### P2 — 쓰기 전에 정할 것

15. **`_4_experiments.tex`의 용어 두 곳.** L3 "preserving optional Draft processing" →
    "retaining optional stages"(AGENTS.md가 `optional Draft processing`을 drifted variant로 지목).
    L15 RQ3 문항의 "the remaining draft sequence" → **`Draft Sequence`**(Section 3 소문자 예외는
    4장에 미치지 않는다). 같은 L15가 **admit 방향만** 묻는데 exhibit은 양방향을 채점한다 —
    RQ 문항을 넓힐지 결정할 것. `4_1_setup.tex` L7도 소문자다.
    (※ `2_4_static_safeguards.tex`도 전반적으로 소문자다. 2장도 예외 밖이므로, 저자가 규칙을
    넓힌 건지 확인하고 **일괄 치환은 하지 말 것.**)

16. **RQ1이 deadline margin을 하나도 인쇄하지 않는데 괜찮은가.** Slack P5는 2026-08-11에
    제거됐고(값은 `docs/rq-evidence.md` Part 3 §2.2에 보존), AGENTS.md는 최소 margin 통계를
    RQ4의 12MP normal 모집단으로 한정한다. 산업계 리뷰어는 "얼마나 가까이 갔었나"를 **RQ4가
    아니라 RQ1에서** 묻는다. → RQ1 prose가 RQ4의 tail을 전방 참조할지 침묵할지 **결정**할 것
    (둘 다 방어 가능하지만 누락이 아니라 결정이어야 한다). ⚠ 워크북의 현재 `slackP5Percent`는
    제거된 열의 숫자와 **다르므로** 대체품으로 쓰면 안 된다.

17. **24MP fallback의 범위가 docs 안에서 어긋난다.** `4_1_setup.tex` L17은 "레벨5 이상"이라고
    하는데 `docs/exhibits.md#tab_setup`은 "run에서 그 해상도로 나오는 건 처음 1~2장뿐"이라고 —
    훨씬 넓고 레벨 조건이 아니다. 어느 쪽인지 확인 전에는 어느 문장도 쓰지 말 것.

18. **RQ2의 `No control` / `Admission only` 두 arm의 N과 provenance가 기록돼 있지 않다**
    (`docs/exhibits.md`는 "이전 출처를 유지"라고만 적는다). 다만 여섯 셀 중 넷은 in-repo
    워크북에서 N=10으로 정확히 재현됐다: No control S26U 12MP(87/87/87 of 300, 0/10),
    No control S26 12MP(127/127/127 of 300, 0/10), Admission only S26U 12MP(300 정시, M 88, S 101,
    10/10), Admission only S26U 24MP(262 정시, M 73, S 153, 8/10). **S26U 24MP No control 셀은
    in-repo 출처가 없다.**

19. **`No control`·`Admission only` 워크북에 양수 `transitionDelayMs`가 있다**(12MP admit-only:
    338 transition 중 179건). 표는 그 두 arm의 Activated를 0, d P50을 `--`로 찍는다. 그 필드가
    controller 적용 지연이 아닌 replay/shadow 값이거나(모든 워크북에 `PacingReplay` 시트가 있다),
    아니면 그 arm이 pacing-disabled가 아니었다는 뜻이다. **확정 전까지 그 두 arm의 pacing
    통계를 워크북에서 인용하지 말 것.**

20. **RQ2가 S26 24MP memory 패널을 갖지 않는다.** 수집됐다면 리뷰어가 왜 빠졌는지 묻고,
    수집되지 않았다면 4.1이나 RQ2 prose가 한 절로 밝혀야 한다.

21. **case study 보조 결정들**: 음영 8–12를 유지할지(12의 출처 문제), `draftSequenceDurationMs`를
    내보낼지(1,198 → 758 → 368 ms가 두 backlog 반전의 직접 설명이고 현재 어디에도 없다),
    queue depth 관례를 caption에 적을지(서비스 중 포함 vs `realQueueDepth`), 촬영별 발열을
    내보낼지(20번째의 4→5 전이가 두 번째 episode 한가운데에 있어 교란 요인이다).

22. **RQ4 자잘한 확정**: 표에 조건·기기 라벨이 없으므로 caption에 넣을지 setup 문장으로
    못 박을지; backlog 중앙 정점을 59.4 / 59.5 / "about 59%" 중 무엇으로 쓸지(재현값 59.45%);
    기기별 활성화 수치를 prose에 넣을지(넣으려면 `docs/exhibits.md`에 같은 커밋으로 기록해야
    한다).

23. **재생성 스크립트 정비.** `scripts/rq1_summary_counts.py`는 존재하지 않는 경로
    (`data/ablation_sampling/`)를 읽고 2026-09-07 이전 컬렉션을 재현한다 — **현재 RQ1 셀을
    재생성하는 스크립트가 없다.** `scripts/rq2_ablation_metrics.py`는 다른 기계의 절대 경로를
    하드코딩하고 3패널 refresh 이전 설계를 대상으로 한다. RQ3 쪽은 docs가 지시하는
    `scripts/rq2_audit_pool.py`(레벨 선정 규칙의 소유자)와 `scripts/rq2_admission_metrics.py`가
    **디스크에 없다** — 그래서 8-vs-5를 이 repo 안에서 해결할 수 없다. ML clone에 있는지 확인 필요.

24. **`docs/` 자체의 drift.** `docs/exhibits.md#tab_setup`은 camera software를 17.0.00.55로
    적는데 표는 2026-08-31부터 17.5.00.10이다. `docs/exhibits.md`의 RQ1 항목은 group header로
    "Draft stages retained"를 주장하는데 `.tex`는 "Draft stages executed"를 찍고, 같은 항목이
    2026-09-08에 삭제된 `tab:rq4_pacing_summary`를 참조한다(죽은 참조).
    `docs/rq-evidence.md` L2434–2438의 RQ1↔RQ2 교차검증 수치는 refresh 이전 컬렉션이다.
    AGENTS.md 규칙상 exhibit이 바뀌면 같은 커밋에서 `docs/exhibits.md`를 고쳐야 한다.
