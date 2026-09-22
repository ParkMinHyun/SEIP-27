import pandas as pd, warnings, os, pickle
warnings.filterwarnings('ignore')
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC={('S26U','12MP'):'data/S26_Ultra/SM-S948U_metrics_12MP_normal_0906.xlsx',
     ('S26U','24MP'):'data/S26_Ultra/SM-S948U_metrics_24MP_memory_0906.xlsx',
     ('S26','12MP'):'data/S26/SM-S942B_metrics_12MP_normal_0906.xlsx',
     ('S26','24MP'):'data/S26/SM-S942B_metrics_24MP_memory_0829.xlsx'}
SHEETS=['AdmissionReplay','PacingReplay','CaseStudyTrace','RQ1Runs','Capture','DynamicFunctionNode','SecDualBokehNode','SecFilterNode','SecImageCodecNode','WatermarkNode']
out={}
for k,rel in SRC.items():
    x=pd.read_excel(os.path.join(ROOT,rel),sheet_name=SHEETS)
    out[k]=x
    print(k,{s:len(v) for s,v in x.items()})
pickle.dump(out,open(os.path.join(os.path.dirname(__file__),'wb.pkl'),'wb'))
