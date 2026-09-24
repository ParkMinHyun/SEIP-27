"""Python port of CaptureAvailablePacer + CaptureAvailablePacingSession, at the
two formula variants the four workbooks were actually recorded with.

Structure follows ML@bb27a0f, which differs from the current implementation in
two ways that matter here: the per-draft reserve is the session's running
maximum wall (44a9a32 replaced it with an expectedMaximum), and there is no
delay cap (27d2967 added one).  Do not use this port to describe the current
system; it exists to replay the collection.

Which delay form a workbook used is decided by measurement, not by its file
name -- see compute_pacing_delay_ms and val_pacer.py.  Both forms reproduce the
recorded appliedDelayMs exactly on the workbooks they belong to, so the split is
not a fitted parameter.

The pacing side of DraftSequenceExecutionPredictor is ported here too, since
port.py covers the admission path only.
"""
import math
from collections import deque

DECAY, PRUNE = 0.90, 1e-6
PACING_WINDOW_DRAFT_COUNT = 2.0


class RWD:
    """RecencyWeightedDistribution: decay-weighted samples, mean() and expectedMaximum()."""

    def __init__(self):
        self.s = []

    def empty(self):
        return not self.s

    def add(self, x):
        self.s.append([x, 1.0])
        self.s.sort(key=lambda v: v[0])

    def decay(self):
        for v in self.s:
            v[1] *= DECAY
        self.s = [v for v in self.s if v[1] >= PRUNE]

    def mean(self):
        if not self.s:
            return 0.0
        w = sum(v[1] for v in self.s)
        return sum(v[0] * v[1] for v in self.s) / w if w > 0 else 0.0

    def expected_max(self):
        if not self.s:
            return 0.0
        w = sum(v[1] for v in self.s)
        w2 = sum(v[1] ** 2 for v in self.s)
        if w <= 0 or w2 <= 0:
            return 0.0
        n = w * w / w2
        tgt = w * (1.0 - 1.0 / (n + 1.0))
        c = 0.0
        for sc, wt in self.s:
            c += wt
            if c >= tgt:
                return sc
        return self.s[-1][0]


class Overhead:
    """DraftSequenceDurationOverhead: recency-weighted mean of non-node time."""

    def __init__(self):
        self.d = RWD()
        self.learned = 0.0

    def estimate(self):
        return self.learned

    def observe(self, node_processing_ms, draft_duration_ms):
        if draft_duration_ms <= 0 or node_processing_ms <= 0:
            return
        self.d.decay()
        self.d.add(max(0.0, float(draft_duration_ms - node_processing_ms)))
        self.learned = self.d.mean()


class PacingEstimator:
    """The four DraftSequenceExecutionPredictor methods the pacer calls.

    `base` is the per-workload point estimate table; pass the admission port's
    Predictor to share one model, or drive it standalone with observe().
    """

    def __init__(self, predictor=None):
        self.pred = predictor
        self.overhead = Overhead()

    def workload_sequence_ms(self, seq):
        if self.pred is None:
            return 0.0
        return sum(self.pred.est(seq).values())

    def overhead_ms(self):
        return self.overhead.estimate()

    def draft_sequence_ms(self, seq):
        return self.workload_sequence_ms(seq) + self.overhead.estimate()

    def demoted_ms(self, planned_seq, draft_seq):
        if planned_seq == draft_seq:
            return 0.0
        return max(0.0, self.workload_sequence_ms(planned_seq) - self.workload_sequence_ms(draft_seq))


class Snapshot:
    __slots__ = ('budget', 'workload_ms', 'overhead_ms', 'reserved_ms', 'key')

    def __init__(self, budget, workload_ms, overhead_ms, reserved_ms, key):
        self.budget = budget
        self.workload_ms = workload_ms
        self.overhead_ms = overhead_ms
        self.reserved_ms = reserved_ms
        self.key = key


class Decision:
    __slots__ = ('delay', 'computed_delay', 'backlog', 'growth', 'queued', 'queued_work',
                 't', 'ttd', 'snapshot')

    def __init__(self, delay, backlog, growth, queued, queued_work, ttd, t, snapshot):
        self.delay, self.backlog, self.growth = delay, backlog, growth
        self.computed_delay = delay
        self.queued, self.queued_work, self.ttd, self.t = queued, queued_work, ttd, t
        self.snapshot = snapshot


class PacingSession:
    def __init__(self, created):
        self.created = created
        self.snapshot = None
        self.pending = deque()
        self.max_draft_ms = 0
        self.walls = RWD()          # 44a9a32: reserve base is walls.expected_max()
        self.backlog_end = 0
        self.backlog_deadline = None
        self.growths = RWD()
        self.last_backlog = None

    @property
    def queued(self):
        return len(self.pending)

    @property
    def queued_work(self):
        return sum(d.snapshot.workload_ms for d in self.pending)

    def queue(self, d):
        self.pending.append(d)
        work = d.snapshot.workload_ms + d.snapshot.overhead_ms
        self.backlog_end = max(d.t + d.delay, self.backlog_end) + math.ceil(work)

    def dequeue(self, snapshot):
        if snapshot is not None:
            self.snapshot = snapshot
        return self.pending.popleft() if self.pending else None

    def rebase(self, now, overhead_ms, est_ws):
        work = sum(est_ws(d.snapshot.key) + overhead_ms for d in self.pending)
        self.backlog_end = now + math.ceil(work)

    def update_max(self, dur):
        if dur > 0:
            self.max_draft_ms = max(self.max_draft_ms, dur)
            self.walls.decay()
            self.walls.add(float(dur))

    def reserve_base(self, stat):
        return self.max_draft_ms if stat == 'max' else self.walls.expected_max()

    def backlog_at(self, now):
        return max(self.backlog_end - now, 0)

    def observe_growth(self, backlog):
        if self.last_backlog is not None:
            self.growths.decay()
            self.growths.add(float(backlog - self.last_backlog))
        self.last_backlog = backlog
        return max(self.growths.mean(), 0.0)

    def ttd_at(self, now, timeout_ms):
        if self.backlog_deadline is None:
            return timeout_ms
        return min(max(self.backlog_deadline - now, 0), timeout_ms)


def compute_pacing_delay_ms(backlog_ms, growth_ms, ttd_ms, reserved_ms, halve_growth=False):
    """computePacingDelayMs.  The clamp at zero happens once, at the end.

    `halve_growth` selects the pre-8d5e55d form, where the growth term is halved
    together with the deficit instead of being added after the split.  Which form
    a workbook was recorded with is determined empirically in val_pacer.py, not
    from the file name: the 0906-named workbooks reproduce only under the halved
    form and the 0829-named one only under the separate form, which is the
    opposite of what the names suggest.
    """
    est_completion = backlog_ms + reserved_ms * PACING_WINDOW_DRAFT_COUNT
    deficit = est_completion - max(ttd_ms, 0)
    if halve_growth:
        return max(math.ceil((deficit + growth_ms) / PACING_WINDOW_DRAFT_COUNT), 0)
    return max(math.ceil(deficit / PACING_WINDOW_DRAFT_COUNT + growth_ms), 0)


class Pacer:
    """Hooks mirror the Kotlin: decide_delay / start_draft / end_draft / skip_draft
    / set_deadline / clear.  `resolve` maps a planned key to the demoted shape."""

    def __init__(self, est, resolve=lambda k: k, timeout_ms=None, halve_growth=False,
                 reserve_stat='max'):
        """`reserve_stat` is 'max' (session running maximum, up to bb27a0f) or
        'expmax' (recency-weighted expectedMaximum, from 44a9a32)."""
        self.est = est
        self.resolve = resolve
        self.timeout_ms = timeout_ms
        self.halve_growth = halve_growth
        self.reserve_stat = reserve_stat
        self.session = None

    def decide_delay(self, now, timeout_ms=None, ttd_override=None, delay_override=None):
        """`ttd_override` feeds the recorded timeToDeadlineMs instead of the
        session's own clock.  Validation uses it to isolate the bookkeeping from
        which capture deadline the live pacer happened to hold."""
        if self.session is None:
            self.session = PacingSession(now)
        s = self.session
        if s.snapshot is None:
            return None
        ttd = (ttd_override if ttd_override is not None
               else s.ttd_at(now, timeout_ms if timeout_ms is not None else self.timeout_ms))
        backlog = s.backlog_at(now)
        growth = s.observe_growth(backlog)
        delay = compute_pacing_delay_ms(backlog, growth, ttd, s.snapshot.reserved_ms,
                                        self.halve_growth)
        d = Decision(delay, backlog, growth, s.queued, s.queued_work, ttd, now, s.snapshot)
        if delay_override is not None:
            # clock advances on the delay that was really applied; `computed_delay`
            # keeps this port's own answer so the two can be compared without the
            # difference feeding back into the backlog.
            d.delay = delay_override
        s.queue(d)
        return d

    def start_draft(self, planned_key, budget_ms):
        s = self.session
        if s is None:
            return None
        if planned_key is None:
            return s.dequeue(None)
        draft_key = self.resolve(planned_key)
        reserved = max(s.reserve_base(self.reserve_stat) - self.est.demoted_ms(planned_key, draft_key),
                       self.est.draft_sequence_ms(draft_key))
        return s.dequeue(Snapshot(budget_ms, self.est.workload_sequence_ms(draft_key),
                                  self.est.overhead_ms(), reserved, draft_key))

    def end_draft(self, now, duration_ms):
        s = self.session
        if s is None:
            return
        s.update_max(duration_ms)
        s.rebase(now, self.est.overhead_ms(), self.est.workload_sequence_ms)

    def skip_draft(self):
        if self.session is not None:
            self.session.dequeue(None)

    def set_deadline(self, deadline_uptime_ms):
        if self.session is not None:
            self.session.backlog_deadline = deadline_uptime_ms

    def clear(self):
        self.session = None
