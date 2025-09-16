import streamlit as st
import os
from datetime import datetime
import json
from typing import Optional

try:
    from config import load_google_llm, newsContext
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI News Analyzer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .news-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Pydantic model
class News(BaseModel):
    title: str = Field(..., description="News article title")
    article: str = Field(..., description="Full article content")
    ai_summary: str = Field(..., description="AI-generated summary (max 2 sentences)")
    sentiment_analysis: str = Field(..., description="Sentiment: positive/negative/neutral")
    key_topics: str = Field(..., description="3-5 key topics from the article")
    credibility_assesment: str = Field(..., description="Credibility assessment")
    pidgin_version: str = Field(..., description="Pidgin language version of summary")

@st.cache_resource
def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        if not firebase_admin._apps:
            script_dir = os.path.dirname(__file__)
            key_path = os.path.join(script_dir, "serviceAccountKey.json")
            
            if os.path.exists(key_path):
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
            else:
                st.error("Firebase service account key not found!")
                return None
        
        return firestore.client()
    except Exception as e:
        st.error(f"Firebase initialization error: {e}")
        return None

@st.cache_resource
def initialize_llm():
    """Initialize the language model"""
    try:
        return load_google_llm()
    except Exception as e:
        st.error(f"LLM initialization error: {e}")
        return None

def get_sentiment_color(sentiment):
    """Return color based on sentiment"""
    sentiment_lower = sentiment.lower()
    if 'positive' in sentiment_lower:
        return '#28a745'
    elif 'negative' in sentiment_lower:
        return '#dc3545'
    else:
        return '#ffc107'

def analyze_news(city: str, country: str, llm, db) -> Optional[News]:
    """Analyze news for given city and country"""
    
    try:
        # Get news context
        with st.spinner(f"Fetching news for {city}, {country}..."):
            news_tool = newsContext(city)
        
        # Create prompt template
        prompt_template = PromptTemplate.from_template(
            """You are a professional news analyst. Analyze the following news articles: {context}

Generate a comprehensive analysis in the following JSON format:

{{
    "title": "string - Main headline or summary title",
    "article": "string - Full article content",
    "ai_summary": "string - Concise summary in maximum 2 sentences",
    "sentiment_analysis": "string - Overall sentiment (positive/negative/neutral) with brief explanation",
    "key_topics": "string - List 3-5 main topics separated by commas",
    "credibility_assesment": "string - Assessment of source credibility and reliability",
    "pidgin_version": "string - Summary translated to Nigerian Pidgin English"
}}

Ensure all fields are properly filled with relevant information."""
        )
        
        # Format prompt
        prompt = prompt_template.format(context=news_tool)
        
        # Get LLM response
        with st.spinner("Analyzing news with AI..."):
            response = llm.invoke(prompt)
        
        # Parse response
        parser = PydanticOutputParser(pydantic_object=News)
        parsed_result = parser.parse(response)
        
        # Store in Firestore
        if db:
            with st.spinner("Saving to database..."):
                news_data = parsed_result.dict()
                news_data['timestamp'] = datetime.now()
                news_data['city'] = city
                news_data['country'] = country
                
                doc_ref = db.collection("news_articles").add(news_data)
                st.success(f"✅ Analysis saved to database with ID: {doc_ref[1].id}")
        
        return parsed_result
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI News Analyzer</h1>
        <p>Get instant AI-powered analysis of news articles with sentiment, topics, and credibility assessment</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize services
    db = initialize_firebase()
    llm = initialize_llm()
    
    if not llm:
        st.error("❌ Could not initialize language model. Please check your configuration.")
        st.stop()
        #testing
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h3>🌍 Location Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        city = st.text_input(
            "City",
            placeholder="e.g., Lagos, London, New York",
            help="Enter the city you want to get news for"
        )
        
        country = st.text_input(
            "Country",
            placeholder="e.g., Nigeria, UK, USA",
            help="Enter the country for context"
        )
        
        st.markdown("""
        <div class="sidebar-section">
            <h3>📊 Analysis Features</h3>
            <ul>
                <li>✅ AI Summary (2 sentences max)</li>
                <li>✅ Sentiment Analysis</li>
                <li>✅ Key Topics Extraction</li>
                <li>✅ Credibility Assessment</li>
                <li>✅ Pidgin Translation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Database status
        db_status = "🟢 Connected" if db else "🔴 Not Connected"
        st.markdown(f"""
        <div class="sidebar-section">
            <h3>🔧 System Status</h3>
            <p><strong>Firebase:</strong> {db_status}</p>
            <p><strong>LLM:</strong> 🟢 Ready</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📰 News Analysis")
        
        if st.button("🚀 Analyze News", type="primary", use_container_width=True):
            if not city or not country:
                st.warning("⚠️ Please enter both city and country")
            else:
                # Analyze news
                result = analyze_news(city, country, llm, db)
                
                if result:
                    # Store result in session state
                    st.session_state.analysis_result = result
                    st.session_state.analysis_location = f"{city}, {country}"
    
    with col2:
        st.markdown("### 📈 Quick Stats")
        if db:
            try:
                # Get recent analyses count
                recent_docs = db.collection("news_articles").limit(10).get()
                st.metric("Recent Analyses", len(recent_docs))
            except:
                st.metric("Recent Analyses", "N/A")
        else:
            st.metric("Database", "Offline")
    
    # Display results
    if hasattr(st.session_state, 'analysis_result') and st.session_state.analysis_result:
        result = st.session_state.analysis_result
        location = st.session_state.analysis_location
        
        st.markdown(f"## 📊 Analysis Results for {location}")
        
        # Title and Summary
        st.markdown(f"""
        <div class="news-card">
            <h3>{result.title}</h3>
            <p><strong>AI Summary:</strong> {result.ai_summary}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_color = get_sentiment_color(result.sentiment_analysis)
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: {sentiment_color};">😊 Sentiment</h4>
                <p>{result.sentiment_analysis}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏷️ Key Topics</h4>
                <p>{result.key_topics}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>✅ Credibility</h4>
                <p>{result.credibility_assesment}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Expandable sections
        with st.expander("📄 Full Article"):
            st.text_area("Article Content", result.article, height=200, disabled=True)
        
        with st.expander("🗣️ Pidgin Version"):
            st.markdown(f"**Pidgin Summary:** {result.pidgin_version}")
        
        # Download option
        if st.button("📥 Download Analysis as JSON"):
            json_data = result.dict()
            json_data['location'] = location
            json_data['analysis_date'] = datetime.now().isoformat()
            
            st.download_button(
                label="Download JSON",
                data=json.dumps(json_data, indent=2),
                file_name=f"news_analysis_{city}_{country}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()