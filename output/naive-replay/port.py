"""Python port of DraftSequenceExecutionPredictor (ML@b6712a0 working tree),
admission path only: per-key base x shared condition, sequence residual with
recency-weighted expectedMaximum.  Plus node-level trace loading.
"""
import math, pickle, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DECAY, PRUNE = 0.90, 1e-6
NODE_SHEETS = ['DynamicFunctionNode', 'SecDualBokehNode', 'SecFilterNode', 'SecImageCodecNode', 'WatermarkNode']
OPTIONAL = {'BOKEH()', 'FILTER()', 'DECODING()', 'WATERMARK(watermarkType=OVERLAY)'}
GROUP = {'BOKEH()': 'PORTRAIT', 'DECODING()': 'DECORATION', 'FILTER()': 'DECORATION',
         'WATERMARK(watermarkType=OVERLAY)': 'DECORATION'}


class RWD:
    def __init__(self):
        self.s = []  # [score, weight]

    def empty(self):
        return not self.s

    def add(self, x):
        self.s.append([x, 1.0])
        self.s.sort(key=lambda v: v[0])

    def decay(self):
        for v in self.s:
            v[1] *= DECAY
        self.s = [v for v in self.s if v[1] >= PRUNE]

    def expected_max(self):
        if not self.s:
            return 0.0
        w = sum(v[1] for v in self.s)
        w2 = sum(v[1] ** 2 for v in self.s)
        if w <= 0 or w2 <= 0:
            return 0.0
        n = w * w / w2
        frac = 1.0 - 1.0 / (n + 1.0)
        tgt = w * frac
        c = 0.0
        for sc, wt in self.s:
            c += wt
            if c >= tgt:
                return sc
        return self.s[-1][0]


class Predictor:
    def __init__(self):
        self.base = {}      # key -> [n, mean]
        self.gamma = 1.0
        self.rseq = {}
        self.rglob = RWD()

    def est(self, keys):
        g = self.gamma
        return {k: (self.base[k][1] * g if k in self.base else 0.0) for k in keys}

    def decide(self, seq):
        pm = self.est(seq)
        P = sum(pm[k] for k in seq)
        r = self.rseq.get(seq)
        src = r if (r is not None and not r.empty()) else self.rglob
        U = P * math.exp(src.expected_max())
        return P, U, pm

    def learn(self, durs, decisions):
        durs = {k: v for k, v in durs.items() if v > 0}
        # residual
        scores, seen = [], set()
        for seq, pm in decisions:
            meas = tuple(k for k in seq if k in durs)
            pred = sum(pm.get(k, 0.0) for k in meas)
            if pred <= 0:
                continue
            act = sum(max(pm.get(k, 0.0), float(durs[k])) for k in meas)
            if meas in seen:
                continue
            seen.add(meas)
            scores.append((meas, max(0.0, math.log(act / pred))))
        if scores:
            self.rglob.decay()
            for k in list(self.rseq):
                self.rseq[k].decay()
                if self.rseq[k].empty():
                    del self.rseq[k]
            for meas, sc in scores:
                self.rglob.add(sc)
                self.rseq.setdefault(meas, RWD()).add(sc)
        # trend
        g0 = self.gamma
        samples = []
        for k, d in durs.items():
            if k in self.base and self.base[k][1] > 0:
                samples.append(d / self.base[k][1])
            b = self.base.setdefault(k, [0, 0.0])
            x = d / g0
            if x > 0:
                b[0] += 1
                b[1] += (x - b[1]) / b[0]
        if samples:
            med = float(np.median(samples))
            if med > 0:
                self.gamma = med


def load_nodes(x):
    N = pd.concat([x[s].assign(sheet=s) for s in NODE_SHEETS], ignore_index=True)
    return N.sort_values(['captureIndex', 'nodeOrder']).reset_index(drop=True)


def parse_seq(s):
    # keys are separated by '>' but keys may contain no '>' themselves
    return tuple(s.split('>')) if isinstance(s, str) and s else tuple()
