import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
import json,time,hashlib,platform,importlib.metadata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV,calibration_curve
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,log_loss,precision_recall_curve,precision_score,recall_score,f1_score,confusion_matrix

from datetime import datetime
RUN=datetime.now().strftime('%Y%m%d_%H%M%S_%f')
I=ROOT/'docs'; T=ROOT/'outputs/tables/ml_phong'/RUN; F=ROOT/'outputs/figures/ml_phong'/RUN; M=ROOT/'outputs/models/ml_phong'/RUN
for p in [T,F,M,ROOT/'docs']: p.mkdir(parents=True,exist_ok=True)
if (T/'selected_config.json').exists(): raise RuntimeError('Completed run exists. Use a new independent folder for another experiment.')
features=pd.read_csv(I/'predictor_list.csv').feature.tolist()
df=pd.read_csv(ROOT/'data/processed/research_data_weather_price_holiday_assume_utc.csv')
manifest=pd.read_csv(ROOT/'outputs/tables/ml_preparation/split_manifest.csv')
assert df.order_id.is_unique and manifest.order_id.is_unique
assert len(features)==21 and len(set(features))==21
selected=manifest[manifest.split.isin(['train','validation_a','validation_b','test'])][['order_id','split']]
d=selected.merge(df,on='order_id',how='left',validate='one_to_one',indicator=True)
assert d['_merge'].eq('both').all()
expected={'train':(57449,3720),'validation_a':(7661,387),'validation_b':(3115,180),'test':(9445,504)}
sets={}
for s,(n,pos) in expected.items():
 z=d[d.split.eq(s)].copy(); assert len(z)==n and z.is_late.notna().all() and z.is_late.isin([0,1]).all() and int(z.is_late.sum())==pos
 sets[s]=z
pd.DataFrame([{'split':s,'n':len(z),'late':int(z.is_late.sum())} for s,z in sets.items()]).to_csv(T/'input_audit.csv',index=False)
cat=['customer_state','purchase_weekday']; num=[f for f in features if f not in cat]
for s,z in sets.items():
 for c in cat: z[c]=z[c].map(lambda v:str(v) if pd.notna(v) else np.nan)
 for c in num: z[c]=pd.to_numeric(z[c],errors='raise').replace([np.inf,-np.inf],np.nan)
train=sets['train']; A=sets['validation_a']; B=sets['validation_b']
pd.DataFrame({'feature':features,'missing_train':[train[c].isna().sum() for c in features],'unique_train':[train[c].nunique() for c in features]}).to_csv(T/'feature_audit.csv',index=False)
assert not train[features].isna().all().any(), 'Entirely missing training feature requires review'
def pipeline(model,scale):
 numeric=[('imputer',SimpleImputer(strategy='median'))]
 if scale:numeric.append(('scaler',StandardScaler()))
 prep=ColumnTransformer([('numeric',Pipeline(numeric),num),('category',Pipeline([('imputer',SimpleImputer(strategy='constant',fill_value='missing')),('encoder',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cat)],sparse_threshold=0)
 return Pipeline([('preprocessing',prep),('classifier',model)])
def factory(name):
 if name=='LogisticRegression':
  return LogisticRegression(max_iter=3000,C=1,solver='lbfgs',class_weight=None,random_state=42)
 if name=='RandomForest':
  return RandomForestClassifier(n_estimators=300,min_samples_leaf=2,class_weight=None,random_state=42,n_jobs=4)
 raise ValueError(name)
def metrics(y,p,threshold=None):
 r={'n':len(y),'late':int(np.sum(y)),'prevalence':float(np.mean(y)),'AP':average_precision_score(y,p),'ROC_AUC':roc_auc_score(y,p),'Brier':brier_score_loss(y,p),'LogLoss':log_loss(y,p,labels=[0,1])}
 if threshold is not None:
  pred=p>=threshold; tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
  r.update(threshold=float(threshold),Precision=precision_score(y,pred,zero_division=0),Recall=recall_score(y,pred),F1=f1_score(y,pred),alert_rate=float(pred.mean()),TN=int(tn),FP=int(fp),FN=int(fn),TP=int(tp))
 return r
def threshold(y,p):
 precision,recall,ts=precision_recall_curve(y,p); idx=np.flatnonzero(recall[:-1]>=.70)
 # Among equal precision choose higher threshold, hence lower alert rate.
 best=max(idx,key=lambda k:(precision[k],ts[k]));return float(ts[best])
def predictions(z,p,name,kind,t=None):
 return pd.DataFrame({'order_id':z.order_id.to_numpy(),'split':z.split.to_numpy(),'model':name,'y_true':z.is_late.astype(int).to_numpy(),'probability':p,'prediction':np.nan if t is None else (p>=t).astype(int),'threshold':np.nan if t is None else t,'probability_type':kind})
# Task 15 only: fit Train and evaluate Validation A. B/Test are not scored.
rows=[]; predictions_a=[]; logs=[]
for name in ['LogisticRegression','RandomForest']:
 print('Training '+name,flush=True)
 model=pipeline(factory(name),name=='LogisticRegression')
 start=time.perf_counter(); model.fit(train[features],train.is_late.astype(int)); elapsed=time.perf_counter()-start
 probabilities=model.predict_proba(A[features])[:,1]
 rows.append(dict(model=name,split='validation_a',probability_type='raw',**metrics(A.is_late,probabilities)))
 predictions_a.append(predictions(A,probabilities,name,'raw'))
 logs.append(dict(model=name,seed=42,training_seconds=elapsed,parameters=model.named_steps['classifier'].get_params()))
 joblib.dump(model,M/(name+'.joblib'))
 precision,recall,_=precision_recall_curve(A.is_late,probabilities)
 plt.plot(recall,precision,label=name)
pd.DataFrame(rows).to_csv(T/'validation_a_metrics.csv',index=False)
pd.concat(predictions_a,ignore_index=True).to_csv(T/'validation_predictions.csv',index=False)
(T/'experiment_log.json').write_text(json.dumps(logs,indent=2,default=str),encoding='utf-8')
versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','joblib','matplotlib']}
(T/'package_versions.json').write_text(json.dumps(versions,indent=2),encoding='utf-8')
paths=[ROOT/'data/processed/research_data_weather_price_holiday_assume_utc.csv',ROOT/'docs/predictor_list.csv',ROOT/'outputs/tables/ml_preparation/split_manifest.csv']
(T/'input_hashes.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2),encoding='utf-8')
plt.axhline(A.is_late.mean(),ls='--',color='gray',label='Validation A prevalence')
plt.xlabel('Recall');plt.ylabel('Precision');plt.legend();plt.tight_layout();plt.savefig(F/'validation_a_pr_curve.png',dpi=160)
print(pd.DataFrame(rows).to_string(index=False))
print('Results: '+str(T))
print('Task 15 complete. Compare with Viet models before weighting/calibration/test.')
