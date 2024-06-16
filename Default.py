import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load the dataset
data_path = 'C:/Users/jvr/Desktop/project/m_loan_data.csv'
loan_data = pd.read_csv(data_path)

# Selecting features and target
X = loan_data.drop(columns=['Loan ID', 'Verdict'])
y = loan_data['Verdict']

# Identifying categorical and numerical columns
categorical_cols = X.select_dtypes(include=['object', 'bool']).columns
numerical_cols = X.select_dtypes(include=['float64', 'int64']).columns

# Creating transformers for numerical and categorical data
numerical_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

# Creating a preprocessor with ColumnTransformer to apply transformations
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_cols),
        ('cat', categorical_transformer, categorical_cols)
    ])

# Creating a pipeline with preprocessor and a gradient boosting classifier
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', GradientBoostingClassifier(random_state=0))
])

# Splitting the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Training the model
model.fit(X_train, y_train)

# Predicting the model
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)  # Get probabilities for each class

# Getting maximum probability (confidence score) for each prediction
confidence_scores = y_proba.max(axis=1)

# Serialize the model using pickle
model_filename = 'gradient_boosting_classifier.pkl'
with open(model_filename, 'wb') as file:
    pickle.dump(model, file)
    # Optionally, you might also want to save y_pred and confidence_scores if needed

# Load the model to make predictions or for further use
with open(model_filename, 'rb') as file:
    loaded_model = pickle.load(file)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(accuracy)
print(report)
# Print the confidence scores (you can save or use these as needed)
print(confidence_scores)
