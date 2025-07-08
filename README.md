# 🧠 AI Health Query Assistant

An AI-powered assistant that responds to health-related queries using natural language processing and voice interaction. This project uses OpenAI’s GPT model via API to provide helpful responses to symptom-related questions — with a reminder that it's not a substitute for professional medical advice.

---

## 🚀 Features

- 🔍 **Health Query Input** (Text + Voice)
- 🗣️ **Text-to-Speech**: Reads answers aloud
- 🧑‍⚕️ **Medical Suggestion Mode**: Recommends seeing a doctor if symptoms are serious
- 🌿 **Home Remedies + Medicine Types**: Offers Ayurvedic, Allopathic, and Homeopathic suggestions
- ❌ **Query Validation**: Rejects non-medical questions with a polite warning
- 🎯 **Disease Risk Estimator (Mock Layer)**: A simple logic-based mock scoring system (can be extended with ML)

---

## 📌 Tech Stack

| Tool            | Purpose                               |
|-----------------|----------------------------------------|
| `Python`        | Backend logic                         |
| `Streamlit`     | Frontend UI                           |
| `OpenAI API`    | GPT model for natural conversation     |
| `SpeechRecognition` | Converts voice to text           |
| `pyttsx3`       | Converts response text to speech       |
| `dotenv`        | Securely load API keys                |

---

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/ai-health-query-assistant.git
cd ai-health-query-assistant
pip install -r requirements.txt
