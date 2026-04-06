import pickle
from pathlib import Path
p = Path('model/gbr_model_F2B.pkl')
with p.open('rb') as f:
    m = pickle.load(f)
print(type(m))
print(getattr(m, 'n_features_in_', None))
print(getattr(m, 'feature_names_in_', None))
print(m.get_params())
