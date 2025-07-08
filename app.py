import streamlit as st
import os
from dotenv import load_dotenv
import requests
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import threading
import re

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

audio_file = "speech.mp3"
speak_thread = None

# Preprocess user input
def preprocess_query(text):
    text = text.lower().strip()
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = text.replace("bodypain", "body pain")
    text = text.replace("legpain", "leg pain")
    text = text.replace("headache", "head ache")  # optional
    return text

# Text-to-speech
def speak_text(text):
    tts = gTTS(text)
    tts.save(audio_file)
    playsound(audio_file)

# Risk scoring
def get_risk_score(symptom_text):
    keywords = ["fever", "cough", "chest pain", "vomit", "bleeding"]
    score = sum(word in symptom_text.lower() for word in keywords)
    return min(score * 20, 100)

# Remedies for known symptoms
def get_remedies_and_treatments(symptom_text):
    symptom_text = symptom_text.lower()
    remedies = {}

    if "cough" in symptom_text:
        remedies["home_remedies"] = ["Turmeric milk", "Ginger honey tea", "Steam inhalation"]
        remedies["ayurvedic"] = ["Sitopaladi Churna", "Tulsi syrup"]
        remedies["allopathic"] = ["Dextromethorphan", "Paracetamol"]
        remedies["homeopathic"] = ["Drosera", "Bryonia"]

    elif "fever" in symptom_text:
        remedies["home_remedies"] = ["Wet cloth on forehead", "Tulsi ginger tea", "Rest and fluids"]
        remedies["ayurvedic"] = ["Giloy juice", "Sudarshan Vati"]
        remedies["allopathic"] = ["Paracetamol", "Ibuprofen"]
        remedies["homeopathic"] = ["Aconite", "Ferrum Phos"]

    elif "body pain" in symptom_text:
        remedies["home_remedies"] = ["Warm bath", "Turmeric milk", "Stretching and rest"]
        remedies["ayurvedic"] = ["Ashwagandha", "Bala oil massage"]
        remedies["allopathic"] = ["Paracetamol", "Ibuprofen"]
        remedies["homeopathic"] = ["Rhus tox", "Arnica"]

    return remedies

# Streamlit UI
st.set_page_config(page_title="AI Health Query Assistant")
st.title("🧠 AI Health Query Assistant")
st.subheader("Describe your symptoms or health-related question")

use_voice = st.toggle("🎙️ Use Voice Input")
user_query = ""

# Voice input
if use_voice:
    st.markdown("🎤 Speak now:")
    if st.button("🎙️ Record from Mic"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                user_query = recognizer.recognize_google(audio)
                st.success(f"🗣️ You said: {user_query}")
            except:
                st.error("⚠️ Could not recognize speech.")

# Text input fallback
if not user_query:
    raw_query = st.text_input("Or type your symptoms here")
    user_query = preprocess_query(raw_query)

# Main logic
if user_query:
    with st.spinner("Checking your query..."):
        try:
            # Optional: fallback on known symptoms
            fallback_keywords = ["fever", "pain", "sore throat", "vomit", "headache", "body pain", "cough"]
            if any(word in user_query for word in fallback_keywords):
                skip_validation = True
            else:
                skip_validation = False

            # Use LLM validation only if needed
            if not skip_validation:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                check_body = {
                    "model": "llama3-8b-8192",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Reply only Yes or No. Does this message describe a health symptom, illness, pain, or "
                                "any physical condition that might need treatment (e.g., 'body pain', 'fever', 'vomiting')?"
                            )
                        },
                        {"role": "user", "content": user_query}
                    ]
                }
                check_response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=check_body
                )
                decision = check_response.json()["choices"][0]["message"]["content"].strip().lower()
                if "no" in decision:
                    st.error("🚫 Not a health-related query. Please ask about symptoms or conditions.")
                    st.stop()

        except Exception as e:
            st.error(f"⚠️ Error while validating: {e}")
            st.stop()

    # Main AI response
    with st.spinner("Thinking..."):
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            body = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful AI health assistant. You're not a doctor. Provide guidance for symptoms "
                            "with suggestions for home remedies, Ayurvedic, Allopathic, and Homeopathic treatments. "
                            "Always recommend visiting a professional if symptoms are serious."
                        )
                    },
                    {"role": "user", "content": user_query}
                ]
            }

            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
            reply = res.json()["choices"][0]["message"]["content"]

            st.success("Here’s what I suggest:")
            st.write(reply)

            if st.button("🔈 Read Aloud"):
                speak_thread = threading.Thread(target=speak_text, args=(reply,))
                speak_thread.start()

            if st.button("🛑 Stop Speaking"):
                try:
                    os.system("taskkill /f /im wmplayer.exe")
                    os.remove(audio_file)
                    st.success("🔇 Stopped.")
                except:
                    st.warning("Could not stop or already stopped.")

            st.metric("🧪 Risk Estimate", f"{get_risk_score(user_query)}%")

            # Remedies display
            remedies = get_remedies_and_treatments(user_query)
            if remedies:
                st.markdown("### 🌿 Home Remedies & Medicines")

                st.subheader("🧪 Home Remedies")
                for item in remedies.get("home_remedies", []):
                    st.write(f"- {item}")

                st.subheader("🌱 Ayurvedic Medicines")
                for item in remedies.get("ayurvedic", []):
                    st.write(f"- {item}")

                st.subheader("💊 Allopathic Medicines")
                for item in remedies.get("allopathic", []):
                    st.write(f"- {item}")

                st.subheader("🏥 Homeopathic Medicines")
                for item in remedies.get("homeopathic", []):
                    st.write(f"- {item}")
            else:
                st.info("No remedies found for this query.")

            st.markdown("### 🆘 General First-Aid")
            st.info("💧 Stay hydrated, rest well, and consult a doctor if symptoms get worse.")

        except Exception as e:
            st.error(f"⚠️ Failed to fetch response: {e}")
