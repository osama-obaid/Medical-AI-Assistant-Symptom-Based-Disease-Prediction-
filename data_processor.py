import pandas as pd
import pickle
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import os

# data_test_train.py
training = pd.read_csv('data/Training.csv')
testing = pd.read_csv('data/Testing.csv')

# تجهيز البيانات
cols = training.columns[:-1]
X = training[cols]
y = training['prognosis']

print(cols)

# تحويل النصوص إلى أرقام
le = preprocessing.LabelEncoder()
y_encoded = le.fit_transform(y)

# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# تدريب DecisionTree
clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)

# إنشاء مجلد models إذا مش موجود
os.makedirs("models", exist_ok=True)

# حفظ الموديل والمحول
with open("models/decision_tree.pkl", "wb") as f:
    pickle.dump(clf, f)

with open("models/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print("✅ Training complete. Models saved in 'models/' folder.")








