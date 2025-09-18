📰 DeepSeedAI News Analyzer

An AI-powered news assistant built with Streamlit, LangChain, and Firebase Firestore that fetches and analyzes news articles by country. The system provides AI-generated summaries, sentiment analysis, key topics, credibility checks, and even a Pidgin English translation to make news more accessible.

🚀 Features

🔎 Country-based News Fetching – Enter a country name to fetch relevant articles

📝 AI Summary – Concise 2-sentence summary of the article

😊 Sentiment Analysis – Positive / Negative / Neutral classification

🔑 Key Topics Extraction – 3–5 important topics detected

✅ Credibility Assessment – Quick trustworthiness check

🌍 Pidgin English Translation – Localized version of the news

💾 Firestore Integration – Automatically stores results for future access

🛠️ Tech Stack

Frontend: Streamlit

AI/LLM: LangChain
 + Google LLM

Data Storage: Firebase Firestore

Validation: Pydantic


⚙️ Installation

Clone the repository

git clone https://github.com/<your-username>/DeepSeedAI-News-Analyzer.git
cd DeepSeedAI-News-Analyzer


Create a virtual environment

python -m venv venv
source langtest_env/bin/activate   # Mac/Linux
langtest_env\Scripts\activate      # Windows


Install dependencies

pip install -r requirements.txt


Setup Firebase

Create a Firebase project in Firebase Console

Enable Firestore Database

Download the serviceAccountKey.json file and place it in the project root

Run the app

streamlit run app.py

📊 Usage

Open the Streamlit app in your browser

Enter a country name in the sidebar

Click Analyze News

View AI-generated results including summary, sentiment, key topics, credibility score, and pidgin version

Data will be saved automatically to Firestore

🔮 Future Improvements

🌐 Add support for real-time news APIs

🗣️ Extend translation support to multiple languages

🔍 Integrate fact-checking APIs for credibility scoring

📱 Build a mobile-friendly UI

🤝 Contributing

Contributions are welcome!

Fork the repo

Create a feature branch

Submit a pull request