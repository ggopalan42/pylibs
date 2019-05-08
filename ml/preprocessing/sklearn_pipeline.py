from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Imputer, StandardScaler


def standard_pipeline(imputer_strategy='median'):
    ''' Sets up a standard scikit-learn pipeline '''

    std_pipe = Pipeline([
            ('imputer', Imputer(strategy=imputer_strategy)),
            ('std_scaler', StandardScaler()),
    ])

    return std_pipe