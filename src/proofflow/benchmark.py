"""Repeatable synthetic-ML benchmark. This model is NOT used to approve payments."""
import argparse
import json
from pathlib import Path
from .ml import synthetic_invoices, split_data, build_pipeline

def evaluate(n=1500, seed=42):
    from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss, precision_recall_fscore_support
    data = synthetic_invoices(n=n,seed=seed)
    X_train, X_test, y_train, y_test = split_data(data)
    model = build_pipeline().fit(X_train,y_train)
    probability = model.predict_proba(X_test)[:,1]
    pred = (probability >= 0.5).astype(int)
    precision, recall, f1,_ = precision_recall_fscore_support(y_test,pred,average="binary",zero_division=0)
    return {"dataset":"synthetic_only","seed":seed,"train_rows":len(X_train),"test_rows":len(X_test),"roc_auc":round(float(roc_auc_score(y_test,probability)),4),"average_precision":round(float(average_precision_score(y_test,probability)),4),"brier":round(float(brier_score_loss(y_test,probability)),4),"precision":round(float(precision),4),"recall":round(float(recall),4),"f1":round(float(f1),4)}

def main():
    parser = argparse.ArgumentParser(description="Evaluate synthetic invoice review classification")
    parser.add_argument("--out",default="artifacts/benchmark.json")
    args = parser.parse_args()
    metrics = evaluate()
    target = Path(args.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(metrics,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(metrics,indent=2))

if __name__ == '__main__':
    main()
