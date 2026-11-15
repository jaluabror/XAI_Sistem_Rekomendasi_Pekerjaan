import pandas as pd
import numpy as np
from interpret.glassbox import ExplainableBoostingClassifier
import shap
import sklearn

print("SETUP BERHASIL!")
print(f"Python version : {__import__('sys').version.split()[0]}")
print(f"Interpret version : {__import__('interpret').__version__}")
print(f"SHAP version      : {shap.__version__}")
print(f"Scikit-learn version : {sklearn.__version__}")