from flask import Flask, request, jsonify, render_template
import json
import numpy as np
import tensorflow as tf
import pickle

app = Flask(__name__)

# Load trained model and preprocessors
model = tf.keras.models.load_model("chatbot_model.h5")

with open("tokenizer.pkl", "rb") as file:
    tokenizer = pickle.load(file)

with open("label_encoder.pkl", "rb") as file:
    encoder = pickle.load(file)

with open("data.json", "r") as file:
    data = json.load(file)

@app.route("/")
def home():
    return render_template("chat.html")  # Ensure chat.html is inside the "templates" folder

@app.route("/get", methods=["POST"])
def chatbot_response():
    user_input = request.form["msg"]  # Get user message from form data
    
    # Convert user input to model format
    input_seq = tokenizer.texts_to_sequences([user_input])
    input_seq = tf.keras.preprocessing.sequence.pad_sequences(input_seq, maxlen=20)

    # Get prediction
    predictions = model.predict(input_seq)
    response_index = np.argmax(predictions)
    
    try:
        intent_tag = encoder.inverse_transform([response_index])[0]
    except ValueError:
        return jsonify("I'm sorry, I don't understand.")

    # Retrieve response
    for intent in data["intents"]:
        if intent["tag"] == intent_tag:
            response = np.random.choice(intent["responses"])
            return jsonify(response)

    return jsonify("I'm sorry, I don't understand.")

if __name__ == "__main__":
    app.run(debug=True)
