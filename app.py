from flask import Flask, jsonify, request, render_template, redirect, url_for
import pandas as pd
from path_finder.shortest_path import main  # Import your shortest path function
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import threading
import requests

app = Flask(__name__)

# Configure the Generative AI model
genai.configure(api_key="YOUR_API_KEY_HERE")

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 0,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

convo = model.start_chat(
    history=[{"role": "user", "parts": ["hello"]}, {"role": "model", "parts": ["Hello! How can I help you today?"]}]
)

travel_keywords = ["hi", "hello", "travel", "trip", "flight", "bus", "train", "route", "destination", "journey", "airport", "hotel"]

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_speech_input(prompt_text):
    speak(prompt_text)
    with sr.Microphone() as source:
        print(f"{prompt_text}...")
        audio = recognizer.listen(source)
        try:
            input_text = recognizer.recognize_google(audio)
            print(f"You said: {input_text}")
            return input_text
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Please try again.")
            return get_speech_input(prompt_text)
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            speak("Sorry, I'm having trouble processing your request.")
            return None

def process_route_search():
    start_place = get_speech_input("Please say the starting location")
    if not start_place:
        return

    destination_place = get_speech_input("Please say the destination location")
    if not destination_place:
        return

    # Prepare data for the POST request
    data = {"start": start_place, "destination": destination_place}

    # Send the data to the Flask app's search route
    response = requests.post(FLASK_APP_URL, data=data)

    if response.status_code == 200:
        print("Route details:")
        print(response.text)
        speak("Here are the details for your route.")
    else:
        print(f"Failed to get route details. Status code: {response.status_code}")
        speak("Sorry, I couldn't fetch the route details.")

def start_chatbot_listener():
    while True:
        user_input = get_speech_input("How can I assist you with your travel plans today?")
        if user_input.lower() == "exit":
            speak("Bye! Have a great day.")
            break
        elif any(keyword in user_input.lower() for keyword in travel_keywords):
            convo.send_message(user_input)
            response = convo.last.text
            speak(response)
        else:
            speak("I'm sorry, I can only answer questions related to travel and transportation.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/route')
def route():
    return render_template('route.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/search', methods=['POST'])
def search():
    start = request.form.get('start')
    destination = request.form.get('destination')
    search_time = "8:00 AM"

    if not start or not destination:
        return redirect(url_for('home', error='Missing input values'))

    available_routes, detailed_options, output = main(start, destination, search_time)

    return render_template(
        'route.html',
        start=start,
        destination=destination,
        available_routes=available_routes,
        detailed_options=detailed_options,
        output=output
    )

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    response = ""

    if user_input.lower() == "exit":
        response = "Bye! Have a great day."
    elif any(keyword in user_input.lower() for keyword in travel_keywords):
        convo.send_message(user_input)
        response = convo.last.text
    else:
        response = "I'm sorry, I can only answer questions related to travel and transportation."

    return jsonify({"response": response})

if __name__ == '__main__':
    FLASK_APP_URL = "http://127.0.0.1:5000/search"
    
    # Start the chatbot listener in a separate thread
    chatbot_thread = threading.Thread(target=start_chatbot_listener)
    chatbot_thread.daemon = True
    chatbot_thread.start()

    # Run the Flask app
    app.run(debug=True)
