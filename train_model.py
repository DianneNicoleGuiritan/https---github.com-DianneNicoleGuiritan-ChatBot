import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import pickle

# Step 1: Load dataset properly
with open("data.json", "r") as file:
    data = json.load(file)

# Debugging: Check the data type
print("Loaded data type:", type(data))  
if not isinstance(data, dict) or "intents" not in data:
    raise ValueError("Error: data.json does not have the expected format!")

# Extracting the list of intents
intents = data["intents"]

# Extract questions and answers
questions = []
answers = []

for intent in intents:
    for pattern in intent["patterns"]:
        questions.append(pattern)
        answers.append(intent["tag"])  # Using tag instead of response

print(f"✅ Total questions: {len(questions)}")
print(f"✅ Unique intents: {len(set(answers))}")

# Step 2: Tokenize text
tokenizer = Tokenizer()
tokenizer.fit_on_texts(questions)
X_train = tokenizer.texts_to_sequences(questions)
X_train = pad_sequences(X_train, maxlen=20)  # Padding to uniform length

# Save tokenizer for later use in `app.py`
with open("tokenizer.pkl", "wb") as file:
    pickle.dump(tokenizer, file)

print("✅ Tokenizer saved successfully!")

# Step 3: Encode answers
encoder = LabelEncoder()
y_train = encoder.fit_transform(answers)
y_train = tf.keras.utils.to_categorical(y_train)  # Convert to one-hot encoding

# Save LabelEncoder for `app.py`
with open("label_encoder.pkl", "wb") as file:
    pickle.dump(encoder, file)

print("✅ LabelEncoder saved successfully!")

# Step 4: Create the model
model = tf.keras.models.Sequential([
    tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=10, input_length=20),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(10, activation="relu"),
    tf.keras.layers.Dense(len(set(answers)), activation="softmax")
])

model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

# Step 5: Train the model
print("🚀 Training model...")
model.fit(X_train, y_train, epochs=50, batch_size=8)

# Step 6: Save the trained model
model.save("chatbot_model.h5")
print("✅ Model saved successfully!")
