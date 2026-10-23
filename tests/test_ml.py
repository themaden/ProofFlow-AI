from proofflow.ml import FEATURES, build_pipeline, split_data, synthetic_invoices
from sklearn.metrics import roc_auc_score

def test_reproducible_synthetic_data():
    assert synthetic_invoices(120, seed=5).equals(synthetic_invoices(120, seed=5))

def test_train_pipeline():
    df = synthetic_invoices(450)
    xtrain, xtest, ytrain, ytest = split_data(df)
    model = build_pipeline().fit(xtrain, ytrain)
    pred = model.predict_proba(xtest)[:,1]
    assert len(pred) == len(ytest)
    assert roc_auc_score(ytest, pred) >= .55

def test_all_features_present():
    assert all(name in synthetic_invoices(50) for name in FEATURES)
