import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.metrics import confusion_matrix, accuracy_score
import os
import pickle

df = pd.read_csv(r"D:\complete_data!!!!.csv")
plt.rcParams["figure.figsize"] = (20, 5)
plt.rcParams["figure.dpi"] = 100

subset1 = df[df['label'] == "Forehand"]
subset2 = df[df['label'] == "Backhand"]
subset3 = df[df['label'] == "Idle"]

s1_train, s1_test = train_test_split(subset1, test_size=0.35, random_state=5)
s2_train, s2_test = train_test_split(subset2, test_size=0.25, random_state=5)
s3_train, s3_test = train_test_split(subset3, test_size=0.25, random_state=5)

s1_train.reset_index(drop=True, inplace=True)
s2_train.reset_index(drop=True, inplace=True)
s3_train.reset_index(drop=True, inplace=True)
s1_test.reset_index(drop=True, inplace=True)
s2_test.reset_index(drop=True, inplace=True)
s3_test.reset_index(drop=True, inplace=True)

X_train = pd.concat([s1_train, s2_train, s3_train], ignore_index=True)
X_test = pd.concat([s1_test, s2_test, s3_test], ignore_index=True)

test_data_path = r"E:\IDEA_LAB\data\test_data.csv"
X_test.to_csv(test_data_path, index=False)

std_scaler = StandardScaler()
robust_scaler = RobustScaler()
minmax_scaler = MinMaxScaler()

numerical_cols = ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']

X_train[numerical_cols] = std_scaler.fit_transform(X_train[numerical_cols])
X_test[numerical_cols] = std_scaler.transform(X_test[numerical_cols])


stack_model = StackingClassifier(
    estimators=[
        ('rf', RandomForestClassifier(n_estimators=10, random_state=5)),
        ('svc', SVC(kernel='linear', probability=True, random_state=5)),
        ('knn', KNeighborsClassifier(n_neighbors=3)),
        ('lr', LogisticRegression(max_iter=100, random_state=5))
    ],
    final_estimator=LogisticRegression(max_iter=1000, random_state=5))

stack_model.fit(X_train[numerical_cols], X_train['label'])

print("Accuracy Score:",stack_model.score(X_test[numerical_cols], X_test['label'])*100,"%")

preds = stack_model.predict(X_test[numerical_cols])
conf_matrix = confusion_matrix(X_test['label'], preds)
# plt.imshow(conf_matrix, cmap='Blues', interpolation='nearest')
# plt.title('Confusion Matrix')

plt.figure(figsize=(5, 5))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=stack_model.classes_, yticklabels=stack_model.classes_)
plt.show()

acc = accuracy_score(X_test['label'], preds)
print("Accuracy:", acc * 100, "%")

model_path = r"E:\IDEA_LAB\src\model\tennis_stroke_classifier.pkl"

with open(model_path, 'wb') as f:
    pickle.dump(stack_model, f)

model_path = r"E:\IDEA_LAB\src\model\scaler.pkl"

with open(model_path, 'wb') as f:
    pickle.dump(std_scaler, f)