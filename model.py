import pandas as pd
import re
import nltk
import pickle

from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Download stopwords (only first time)
nltk.download('stopwords')

# 🔹 Load stopwords ONCE (important fix)
stop_words = set(stopwords.words('english'))

# 🔹 STEP 1: Load Dataset
print("Loading dataset...")
data = pd.read_csv('fake_job_postings.csv')

# 🔹 STEP 2: Use only required columns
data = data[['description', 'fraudulent']]

# 🔹 STEP 3: Remove empty rows
data.dropna(inplace=True)

# 🔹 OPTIONAL: Use smaller data for faster testing (REMOVE later)
# data = data.sample(5000)

print("Dataset loaded successfully")

# 🔹 STEP 4: Text Cleaning Function (optimized)
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)   # remove special characters
    text = re.sub(r'\d', ' ', text)   # remove numbers
    words = text.split()
    words = [word for word in words if word not in stop_words]
    return " ".join(words)

print("Cleaning text... please wait")

# Apply cleaning
data['cleaned'] = data['description'].apply(clean_text)

print("Text cleaning done")

# 🔹 STEP 5: Feature Extraction (TF-IDF)
print("Applying TF-IDF...")

tfidf = TfidfVectorizer(max_features=5000)
X = tfidf.fit_transform(data['cleaned']).toarray()
y = data['fraudulent']

print("TF-IDF completed")

# 🔹 STEP 6: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 🔹 STEP 7: Train Model
print("Training model...")

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

print("Model training completed")

# 🔹 STEP 8: Evaluation
print("\nEvaluating model...")

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("\nAccuracy:", accuracy)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# 🔹 STEP 9: Save Model & Vectorizer
pickle.dump(model, open('model.pkl', 'wb'))
pickle.dump(tfidf, open('tfidf.pkl', 'wb'))

print("\nModel and TF-IDF saved successfully!")