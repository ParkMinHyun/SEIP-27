"""Cache the RQ3 always-admit audit workbooks (0729 PacingOnly + 0803 pacing_only)
for audit_rescore.py.  Writes audit_wb.pkl next to this file."""
import os, pickle, warnings
import pandas as pd
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(os.path.dirname(HERE))
ML = os.path.join(os.path.dirname(PAPER), 'ML')
BOOKS = {
    '12MP normal': [os.path.join(ML, 'data', '0729_RQ2', f'48U_metrics_12MP_normal_0729_PacingOnly_{i}.xlsx') for i in (1, 2)]
                   + [os.path.join(PAPER, 'data', 'U_ablation_sampling', '48U_metrics_12MP_normal_pacing_only_0803.xlsx')],
    '24MP memory': [os.path.join(ML, 'data', '0729_RQ2', f'48U_metrics_24MP_memory_0729_PacingOnly_{i}.xlsx') for i in (1, 2)]
                   + [os.path.join(PAPER, 'data', 'U_ablation_sampling', '48U_metrics_24MP_memory_pacing_only_0803.xlsx')],
}
SHEETS = ['AdmissionReplay', 'PacingReplay', 'Capture', 'DynamicFunctionNode', 'SecDualBokehNode',
          'SecFilterNode', 'SecImageCodecNode', 'WatermarkNode']
out = {}
for cond, paths in BOOKS.items():
    for p in paths:
        x = pd.read_excel(p, sheet_name=SHEETS)
        out[os.path.basename(p)] = dict(cond=cond, path=p, **x)
        print(os.path.basename(p), {s: len(v) for s, v in x.items()})
pickle.dump(out, open(os.path.join(HERE, 'audit_wb.pkl'), 'wb'))
