import itertools
import pandas as pd
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load the ground truth and predictions data
ground_truth = pd.read_csv('evaluations/gt_intent_class.csv')
predictions = pd.read_csv('evaluations/pred_intent_class.csv')

# Ensure the dataframes are sorted by the same 'id' column
ground_truth = ground_truth.sort_values('id')
predictions = predictions.sort_values('id')

# Check if the 'id' columns in both dataframes are identical
if not ground_truth['id'].equals(predictions['id']):
    raise ValueError("The 'id' columns in the ground truth and predictions are not identical.")

# Extract the 'intent' columns
y_true = ground_truth['intent']
y_pred = predictions['intent']

# Encode the labels
le = LabelEncoder()
y_true = le.fit_transform(y_true)
y_pred = le.transform(y_pred)

# Generate the confusion matrix
cm = confusion_matrix(y_true, y_pred)

# Plot the confusion matrix
plt.figure(figsize=(10,7))
plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('Confusion Matrix')
plt.colorbar()
tick_marks = range(len(le.classes_))
plt.xticks(tick_marks, le.classes_, rotation=45)
plt.yticks(tick_marks, le.classes_)

# Loop over the confusion matrix and display the counts
thresh = cm.max() / 2.
for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    plt.text(j, i, cm[i, j],
             horizontalalignment="center",
             color="white" if cm[i, j] > thresh else "black")

plt.tight_layout()
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show()

# Calculate the accuracy
accuracy = accuracy_score(y_true, y_pred)
print(f'Accuracy: {accuracy}')

# Calculate the precision
precision = precision_score(y_true, y_pred, average='weighted')
print(f'Precision: {precision}')

# Calculate the recall
recall = recall_score(y_true, y_pred, average='weighted')
print(f'Recall: {recall}')

# Calculate the F1 score
f1 = f1_score(y_true, y_pred, average='weighted')
print(f'F1 Score: {f1}')