import pickle, sys, random
import numpy as np, pandas as pd
from sim import prepare, run_arm
W = pickle.load(open('wb.pkl', 'rb'))
mode = sys.argv[1] if len(sys.argv) > 1 else 'early'
P = {}
for k, x in W.items():
    P[k], lp5, bg = prepare(x, mode)
    print(k, 'lead_p5', lp5, 'busy_gap', bg, 'runs', len(P[k]))
pickle.dump(P, open(f'prep_{mode}.pkl', 'wb'))
