
import streamlit as st
from config import load_google_llm, newsContext
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from firebase_admin import credentials, firestore
import firebase_admin
import os

# -------------------------------
# Firebase Setup
# -------------------------------
script_dir = os.path.dirname(__file__)
key_path = os.path.join(script_dir, "serviceAccountKey.json")

if not firebase_admin._apps:  # Prevent reinitialization
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -------------------------------
# LLM Setup
# -------------------------------
llm = load_google_llm()

# -------------------------------
# Pydantic Model
# -------------------------------
class News(BaseModel):
    title: str
    article: str
    ai_summary: str
    sentiment_analysis: str
    key_topics: str
    credibility_assesment: str
    pidgin_version: str

parser = PydanticOutputParser(pydantic_object=News)

# -------------------------------
# Streamlit App
# -------------------------------
st.set_page_config(page_title="AI News Assistant", page_icon="📰", layout="wide")
st.title("📰 DeepSeedAI News Analyzer")

# User input (only country now)
st.sidebar.header("⚙️ Settings")
query = st.sidebar.text_input("Enter a country:")

if st.sidebar.button("Analyze News"):
    st.write(f"🔎 Fetching news for **{query}** ...")

    # Fetch articles using your custom tool
    my_tool = newsContext(query)

    # Prompt Template
    prompt_template = PromptTemplate.from_template(
        """
        You are a news master that receives news articles: {context},
        generate a summary in 2 sentences max, and a pidgin version together
        with the other information in the following JSON format:
        {{
            "title": string,
            "article": string,
            "ai_summary": string,
            "sentiment_analysis": string,
            "key_topics": string,
            "credibility_assesment": string,
            "pidgin_version": string
        }}
        """
    )

    prompt = prompt_template.format(context=my_tool)

    # Invoke LLM
    response = llm.invoke(prompt)

    try:
        parsed_result = parser.parse(response)

        # Display results
        st.subheader("📌 AI Generated News Analysis")
        st.write(f"**📰 Title:** {parsed_result.title}")
        st.write(f"**📄 Article:** {parsed_result.article}")
        st.write(f"**📝 AI Summary:** {parsed_result.ai_summary}")
        st.write(f"**😊 Sentiment Analysis:** {parsed_result.sentiment_analysis}")
        st.write(f"**🔑 Key Topics:** {parsed_result.key_topics}")
        st.write(f"**✅ Credibility Assessment:** {parsed_result.credibility_assesment}")
        st.write(f"**🌍 Pidgin Version:** {parsed_result.pidgin_version}")

        # Save to Firestore
        try:
            news_data = parsed_result.dict()
            doc_ref = db.collection("news_articles").add(news_data)
            # st.success(f"✅ Stored in Firestore with ID: {doc_ref[1].id}")
        except Exception as e:
            st.error(f"⚠️ Error storing data in Firestore: {e}")

    except Exception as e:
        st.error("⚠️ Parsing failed! Showing raw response below:")
        st.code(response, language="json")
        st.exception(e)
