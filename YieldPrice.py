import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
import pickle

# Load the dataset
data = pd.read_csv('C:/Users/jvr/Desktop/project/corrected_crop_data1.csv')

print("Columns in the dataset:", data.columns.tolist())

X = data[['Crop', 'Total Rainfall', 'Max. Temp', 'Min Temp', 'District']]
y = data['Total Yield']
categorical_features = ['Crop', 'District']
numerical_features = ['Total Rainfall', 'Max. Temp', 'Min Temp']

class InteractionTermsTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['Rainfall_Temp_Interaction'] = X['Total Rainfall'] * X['Max. Temp']
        return X


preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numerical_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

pipeline = Pipeline(steps=[
    ('interaction_terms', InteractionTermsTransformer()),
    ('preprocessor', preprocessor),
    ('regressor', GradientBoostingRegressor(random_state=42))
])


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

param_dist = {
    'regressor__n_estimators': [100, 200, 300],
    'regressor__max_depth': [3, 5, 7],
    'regressor__learning_rate': [0.01, 0.1, 0.2]
}

random_search = RandomizedSearchCV(pipeline, param_distributions=param_dist, n_iter=10, 
                                   cv=5, verbose=1, n_jobs=-1, random_state=42)

random_search.fit(X_train, y_train)

best_model = random_search.best_estimator_

y_pred = best_model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f'RMSE: {rmse}')

pickle.dump(best_model, open('YieldPrice_optimized1.pkl', 'wb'))
