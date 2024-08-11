import google.generativeai as genai
import speech_recognition as sr
import pyttsx3

# Configure the Generative AI model
genai.configure(api_key="AIzaSyDdBoRTFCKuyBeT1fN7hyMx8pyeLG_W_mA")

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 0,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

convo = model.start_chat(history=[
    {
        "role": "user",
        "parts": ["hello"]
    },
    {
        "role": "model",
        "parts": ["Hello! How can I help you today?"]
    }
])

travel_keywords = ["hi","hello","travel", "trip", "flight", "bus", "train", "route", "destination", "journey", "airport", "hotel"]

# Initialize the speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

print("Hello, how can I help you? (Say 'exit' to end the conversation)")
speak("Hello, how can I help you? Say 'exit' to end the conversation.")

while True:
    try:
        # Capture the user's speech input
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            user_input = recognizer.recognize_google(audio)
            print("You:", user_input)
        
        if user_input.lower() == "exit":
            print("Bot: Bye! Have a great day.")
            speak("Bye! Have a great day.")
            break
        
        if any(keyword in user_input.lower() for keyword in travel_keywords):
            convo.send_message(user_input)
            response = convo.last.text
            print("Bot:", response)
            speak(response)
        else:
            apology = "I'm sorry, I can only answer questions related to travel and transportation."
            print("Bot:", apology)
            speak(apology)
    
    except sr.UnknownValueError:
        print("Bot: Sorry, I didn't catch that. Please try again.")
        speak("Sorry, I didn't catch that. Please try again.")
    
    except sr.RequestError as e:
        print(f"Bot: Could not request results; {e}")
        speak("Sorry, I'm having trouble processing your request.")

