"""Part A: open-loop forecast replay at every recorded decision point.

For each admission point and each pacing decision recorded in the four
full-controller workbooks, compute what a naive estimator (statistic of the
last N completed draft-sequence durations in the same run) would have
forecast, and score it and the deployed controller's recorded forecast
against the realized quantity on the same trace.  No counterfactual state.
"""
import pickle, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
W = pickle.load(open(os.path.join(HERE, 'wb.pkl'), 'rb'))
NS = (1, 3, 5, 10)


def tf(s):
    return s.astype(str).str.strip().str.lower().isin(['true', '1', '1.0', 'yes'])


def short(k):
    return (k.fillna('').str.replace(r'\(.*?\)', '', regex=True)
            .str.replace('DYNAMIC_FUNCTION', 'DF').str.replace('DECODING', 'D')
            .str.replace('WATERMARK', 'W').str.replace('ENCODING', 'E')
            .str.replace('BOKEH', 'B').str.replace('FILTER', 'F'))


def drafts_of(x):
    t = x['CaseStudyTrace'].copy()
    runs = x['RQ1Runs']
    t['runStatus'] = t.runId.map(dict(zip(runs.runId, runs.runStatus)))
    t = t[t.runStatus.ne('CAPTURE_TIMEOUT')].copy()
    t['comp'] = short(t.executedWorkloadSequenceKey)
    t['dur'] = t.draftSequenceDurationMs.astype(float)
    return t.sort_values(['runId', 'runShotIndex'])


def history(dr, run_drafts, t_dec, N, comp=None):
    """Durations of the last N drafts of the run completed at or before t_dec."""
    h = run_drafts[run_drafts.draftEndUptimeMs <= t_dec]
    if comp is not None:
        h = h[h.comp == comp]
    return h.sort_values('draftEndUptimeMs').dur.values[-N:]


rows_adm, rows_pac = [], []
for (dev, cond), x in W.items():
    t = drafts_of(x)
    by_run = {r: g for r, g in t.groupby('runId')}
    cap2run = dict(zip(t.captureIndex, t.runId))
    cap = t.set_index('captureIndex')

    # ---------------- admission points ----------------
    a = x['AdmissionReplay']
    a = a[a.captureIndex.isin(cap.index) & a.admissionStage.isin(['Bokeh', 'Filter'])].copy()
    for _, r in a.iterrows():
        c = cap.loc[r.captureIndex]
        rd = by_run[c.runId]
        t_dec = r.nodeStartUptimeMs
        el = t_dec - c.draftStartUptimeMs
        G = c.draftEndUptimeMs - t_dec
        rec = dict(dev=dev, cond=cond, run=c.runId, shot=c.runShotIndex, cap=r.captureIndex,
                   stage=r.admissionStage, T=r.beforeBudgetMs, G=G, el=el,
                   Phat=r.beforeSequencePredictedDurationMs, U=r.beforeSequencePredictedUpperBoundMs,
                   admit=bool(tf(pd.Series([r.beforeEffectiveAdmit]))[0]),
                   reason=r.beforeAdmissionSkipReason, observed=bool(tf(pd.Series([r.beforeSuffixFullyObserved]))[0]),
                   node_dur=r.beforeNodeDurationMs, comp=c.comp, level=c.shotOverheatLevel,
                   planned=short(pd.Series([r.workloadSequenceKey]))[0])
        prior = rd[rd.draftEndUptimeMs <= t_dec].sort_values('draftEndUptimeMs')
        rec['hist_n'] = len(prior)
        rec['inflight_ahead'] = int(((rd.captureIndex < r.captureIndex) & (rd.draftEndUptimeMs > t_dec)).sum())
        for N in NS:
            h = prior.dur.values[-N:]
            rec[f'mean{N}'] = max(0.0, h.mean() - el) if len(h) else 0.0
            rec[f'max{N}'] = max(0.0, h.max() - el) if len(h) else 0.0
            rec[f'mix{N}'] = len(set(prior.comp.values[-N:])) > 1 if len(h) else False
            rec[f'mism{N}'] = (prior.comp.values[-N:] != c.comp).any() if len(h) else False
            hm = prior[prior.comp == c.comp].dur.values[-N:]
            rec[f'cmean{N}'] = max(0.0, hm.mean() - el) if len(hm) else rec[f'mean{N}']
            rec[f'cmean{N}_fallback'] = len(hm) == 0
            # age of freshest sample in captures (how many captures behind)
            rec['fresh_lag'] = int(r.captureIndex - prior.captureIndex.values[-1]) if len(prior) else np.nan
        rows_adm.append(rec)

    # ---------------- pacing decisions ----------------
    p = t[tf(t.pacingDecisionRecorded) & t.decisionUptimeMs.notna()]
    for _, r in p.iterrows():
        rd = by_run[r.runId]
        t_dec = r.decisionUptimeMs
        earlier = rd[rd.captureIndex < r.captureIndex]
        out = earlier[earlier.draftEndUptimeMs > t_dec]
        B_true = (out.draftEndUptimeMs.max() - t_dec) if len(out) else 0.0
        nxt = rd[(rd.captureIndex >= r.captureIndex) & (rd.captureIndex <= r.captureIndex + 1)]
        two = nxt.dur.sum() if len(nxt) == 2 else np.nan
        rec = dict(dev=dev, cond=cond, run=r.runId, shot=r.runShotIndex, cap=r.captureIndex,
                   T=r.timeToDeadlineMs, B_true=B_true, B_rec_true=r.realBacklogMs,
                   B_dep=r.controllerBacklogMs, C_dep=r.draftSequenceReservedDurationMs,
                   d_app=r.appliedDelayMs, d_formula=r.sharedDeficitFormulaDelayMs,
                   two_true=two, q_out=len(out), level=r.shotOverheatLevel,
                   margin=r.timeoutMarginMs)
        prior = rd[rd.draftEndUptimeMs <= t_dec].sort_values('draftEndUptimeMs')
        rec['hist_n'] = len(prior)
        for N in NS:
            h = prior.dur.values[-N:]
            for stat in ('mean', 'max'):
                m = (h.mean() if stat == 'mean' else h.max()) if len(h) else 0.0
                B = 0.0
                for _, o in out.iterrows():
                    if o.draftStartUptimeMs <= t_dec:
                        B += max(0.0, m - (t_dec - o.draftStartUptimeMs))
                    else:
                        B += m
                rec[f'B_{stat}{N}'] = B
                rec[f'C_{stat}{N}'] = m
        rows_pac.append(rec)

A = pd.DataFrame(rows_adm)
P = pd.DataFrame(rows_pac)
A.to_pickle(os.path.join(HERE, 'adm.pkl'))
P.to_pickle(os.path.join(HERE, 'pac.pkl'))
print(len(A), len(P))
print('B_true reconstruction check (ms):', (P.B_true - P.B_rec_true).abs().describe().round(2).to_dict())
