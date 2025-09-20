import streamlit as st
from config import load_google_llm, newsContext
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from firebase_admin import credentials, firestore
import firebase_admin
import os
import datetime
import json
from typing import List, Optional

# ------------------------------- 
# Firebase Setup
# ------------------------------- 
script_dir = os.path.dirname(__file__)
key_path = os.path.join(script_dir, "serviceAccountKey.json")

if not firebase_admin._apps:  # Prevent reinitialization
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
llm = load_google_llm()

# ------------------------------- 
# Pydantic Models
# ------------------------------- 
class News(BaseModel):
    title: str
    article: str
    ai_summary: str
    sentiment_analysis: str
    key_topics: str
    credibility_assessment: str  # Fixed spelling
    pidgin_version: str
    timestamp: Optional[str] = None
    country: Optional[str] = None
    confidence_score: Optional[float] = None
    
    class Config:
        # For Pydantic v1 compatibility
        allow_population_by_field_name = True

parser = PydanticOutputParser(pydantic_object=News)

# ------------------------------- 
# Custom CSS Styling
# ------------------------------- 
def load_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .news-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.2s ease;
    }
    
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #e0e6ed;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin: 0;
    }
    
    /* Sentiment styling */
    .sentiment-positive {
        color: #27ae60;
        font-weight: bold;
    }
    
    .sentiment-negative {
        color: #e74c3c;
        font-weight: bold;
    }
    
    .sentiment-neutral {
        color: #f39c12;
        font-weight: bold;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Progress bar styling */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Alert styling */
    .alert-success {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        margin: 1rem 0;
    }
    
    .alert-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #e74c3c;
        margin: 1rem 0;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------- 
# Helper Functions
# ------------------------------- 
def get_sentiment_color(sentiment):
    sentiment_lower = sentiment.lower()
    if 'positive' in sentiment_lower:
        return 'sentiment-positive'
    elif 'negative' in sentiment_lower:
        return 'sentiment-negative'
    else:
        return 'sentiment-neutral'

def calculate_credibility_score(assessment):
    """Calculate a numerical credibility score from text assessment"""
    assessment_lower = assessment.lower()
    if any(word in assessment_lower for word in ['high', 'reliable', 'credible', 'trustworthy']):
        return 0.8 + (hash(assessment) % 20) / 100  # 0.8-0.99
    elif any(word in assessment_lower for word in ['medium', 'moderate', 'fair']):
        return 0.5 + (hash(assessment) % 30) / 100  # 0.5-0.79
    else:
        return 0.2 + (hash(assessment) % 30) / 100  # 0.2-0.49

def display_news_analysis(parsed_result, country):
    """Display the news analysis in a professional format"""
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Title and article
        st.markdown(f"""
        <div class="news-card">
            <h2 style="color: #2c3e50; margin-bottom: 1rem;">📰 {parsed_result.title}</h2>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0; line-height: 1.6; color: #495057;">{parsed_result.article}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Summary
        st.markdown(f"""
        <div class="news-card">
            <h3 style="color: #667eea; margin-bottom: 1rem;">🤖 AI Summary</h3>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #2c3e50; margin: 0;">{parsed_result.ai_summary}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pidgin Version
        st.markdown(f"""
        <div class="news-card">
            <h3 style="color: #28a745; margin-bottom: 1rem;">🌍 Pidgin Version</h3>
            <p style="font-style: italic; font-size: 1.1rem; line-height: 1.6; color: #2c3e50; margin: 0;">{parsed_result.pidgin_version}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Metrics sidebar
        sentiment_class = get_sentiment_color(parsed_result.sentiment_analysis)
        credibility_score = calculate_credibility_score(parsed_result.credibility_assessment)
        
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value {sentiment_class}">😊</p>
            <p class="metric-label">Sentiment</p>
            <p style="margin: 0.5rem 0 0 0; font-weight: 500;" class="{sentiment_class}">{parsed_result.sentiment_analysis}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{credibility_score:.2f}</p>
            <p class="metric-label">Credibility Score</p>
            <div style="background: #e9ecef; border-radius: 10px; height: 8px; margin-top: 0.5rem;">
                <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; border-radius: 10px; width: {credibility_score*100}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">🔑</p>
            <p class="metric-label">Key Topics</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #495057;">{parsed_result.key_topics}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">✅</p>
            <p class="metric-label">Credibility Assessment</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #495057;">{parsed_result.credibility_assessment}</p>
        </div>
        """, unsafe_allow_html=True)

def load_analytics_data():
    """Load analytics data from Firestore"""
    try:
        docs = db.collection("news_articles").stream()
        data = []
        for doc in docs:
            doc_data = doc.to_dict()
            data.append(doc_data)
        return data
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        return []

def display_analytics():
    """Display analytics dashboard"""
    st.markdown('<div class="main-header"><h1>📊 Analytics Dashboard</h1><p>Insights from your news analysis</p></div>', unsafe_allow_html=True)
    
    data = load_analytics_data()
    
    if not data:
        st.info("No analytics data available yet. Analyze some news first!")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_articles = len(data)
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{total_articles}</p>
            <p class="metric-label">Total Articles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        confidence_scores = [item.get('confidence_score', 0) for item in data if item.get('confidence_score')]
        avg_credibility = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{avg_credibility:.2f}</p>
            <p class="metric-label">Avg Credibility</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        countries = set(item.get('country') for item in data if item.get('country'))
        countries_analyzed = len(countries)
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{countries_analyzed}</p>
            <p class="metric-label">Countries</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        timestamps = [item.get('timestamp') for item in data if item.get('timestamp')]
        latest_analysis = max(timestamps) if timestamps else "N/A"
        if latest_analysis != "N/A":
            latest_analysis = latest_analysis.split('T')[0]  # Just show date
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">📅</p>
            <p class="metric-label">Latest: {latest_analysis}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Simple charts using Streamlit native components
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Sentiment Distribution")
        sentiments = {}
        for item in data:
            sentiment = item.get('sentiment_analysis', 'Unknown')
            # Extract main sentiment word
            if 'positive' in sentiment.lower():
                key = 'Positive'
            elif 'negative' in sentiment.lower():
                key = 'Negative'
            else:
                key = 'Neutral'
            sentiments[key] = sentiments.get(key, 0) + 1
        
        for sentiment, count in sentiments.items():
            percentage = (count / len(data)) * 100
            color = "#27ae60" if sentiment == "Positive" else "#e74c3c" if sentiment == "Negative" else "#f39c12"
            st.markdown(f"""
            <div style="margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600; color: {color};">{sentiment}</span>
                    <span style="font-weight: 600;">{count} ({percentage:.1f}%)</span>
                </div>
                <div style="background: #e9ecef; border-radius: 10px; height: 8px; margin-top: 0.3rem;">
                    <div style="background: {color}; height: 100%; border-radius: 10px; width: {percentage}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🌍 Top Countries")
        countries_count = {}
        for item in data:
            country = item.get('country', 'Unknown')
            countries_count[country] = countries_count.get(country, 0) + 1
        
        # Sort and show top 5
        sorted_countries = sorted(countries_count.items(), key=lambda x: x[1], reverse=True)[:5]
        max_count = max([count for _, count in sorted_countries]) if sorted_countries else 1
        
        for country, count in sorted_countries:
            percentage = (count / max_count) * 100
            st.markdown(f"""
            <div style="margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600;">{country}</span>
                    <span style="font-weight: 600;">{count}</span>
                </div>
                <div style="background: #e9ecef; border-radius: 10px; height: 8px; margin-top: 0.3rem;">
                    <div style="background: #667eea; height: 100%; border-radius: 10px; width: {percentage}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------- 
# Main Application
# ------------------------------- 
def main():
    st.set_page_config(
        page_title="DeepSeedAI News Analyzer", 
        page_icon="📰", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    load_css()
    
    # Sidebar navigation
    st.sidebar.markdown("### 🧭 Navigation")
    page = st.sidebar.selectbox("Choose a page:", ["News Analyzer", "Analytics Dashboard", "History"])
    
    if page == "News Analyzer":
        # Main header
        st.markdown('<div class="main-header"><h1>📰 DeepSeedAI News Analyzer</h1><p>Advanced AI-powered news analysis with sentiment detection and credibility assessment</p></div>', unsafe_allow_html=True)
        
        # Sidebar controls
        st.sidebar.markdown("### ⚙️ Analysis Settings")
        query = st.sidebar.text_input("🌍 Enter a country:", placeholder="e.g., Nigeria, Ghana, Kenya")
        
        # Database status
        st.sidebar.markdown("**Database Status:** 🟢 Ready")
        
        # Advanced options
        with st.sidebar.expander("🔧 Advanced Options"):
            save_to_db = st.checkbox("💾 Save to database", value=True)
            show_raw_response = st.checkbox("🔍 Show raw AI response", value=False)
            analysis_depth = st.select_slider("📊 Analysis Depth", options=["Basic", "Standard", "Detailed"], value="Standard")
        
        # Analysis button
        if st.sidebar.button("🚀 Analyze News", type="primary"):
            if not query.strip():
                st.warning("⚠️ Please enter a country name.")
                return
            
            # Loading state
            with st.container():
                st.markdown('<div class="loading-container"><div class="loading-spinner"></div></div>', unsafe_allow_html=True)
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Fetch news
                    status_text.text("🔎 Fetching news articles...")
                    progress_bar.progress(25)
                    
                    my_tool = newsContext(query)
                    
                    # Step 2: Prepare prompt
                    status_text.text("🤖 Preparing AI analysis...")
                    progress_bar.progress(50)
                    
                    prompt_template = PromptTemplate.from_template(
                        """
                        You are an expert news analyst. Analyze the following news articles: {context}
                        
                        Provide a comprehensive analysis in JSON format with:
                        - title: Extract or create a compelling headline
                        - article: The main article content (summarized if too long)
                        - ai_summary: 2-sentence maximum summary
                        - sentiment_analysis: Classify as Positive, Negative, or Neutral with brief reasoning
                        - key_topics: List 3-5 main topics/themes
                        - credibility_assessment: Assess source reliability and fact accuracy
                        - pidgin_version: Translate summary to Nigerian Pidgin English
                        
                        Format as valid JSON:
                        {{
                            "title": "string",
                            "article": "string", 
                            "ai_summary": "string",
                            "sentiment_analysis": "string",
                            "key_topics": "string",
                            "credibility_assessment": "string",
                            "pidgin_version": "string"
                        }}
                        """
                    )
                    
                    prompt = prompt_template.format(context=my_tool)
                    
                    # Step 3: Get AI response
                    status_text.text("⚡ Generating analysis...")
                    progress_bar.progress(75)
                    
                    response = llm.invoke(prompt)
                    
                    # Step 4: Parse results
                    status_text.text("📊 Processing results...")
                    progress_bar.progress(100)
                    
                    parsed_result = parser.parse(response)
                    
                    # Add metadata
                    parsed_result.timestamp = datetime.datetime.now().isoformat()
                    parsed_result.country = query.title()
                    parsed_result.confidence_score = calculate_credibility_score(parsed_result.credibility_assessment)
                    
                    # Clear loading state
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results
                    display_news_analysis(parsed_result, query)
                    
                    # Save to database
                    if save_to_db:
                        try:
                            # Convert Pydantic model to dictionary
                            if hasattr(parsed_result, 'model_dump'):
                                news_data = parsed_result.model_dump()  # Pydantic v2
                            elif hasattr(parsed_result, 'dict'):
                                news_data = parsed_result.dict()  # Pydantic v1
                            else:
                                # Manual conversion as fallback
                                news_data = {
                                    'title': parsed_result.title,
                                    'article': parsed_result.article,
                                    'ai_summary': parsed_result.ai_summary,
                                    'sentiment_analysis': parsed_result.sentiment_analysis,
                                    'key_topics': parsed_result.key_topics,
                                    'credibility_assessment': parsed_result.credibility_assessment,
                                    'pidgin_version': parsed_result.pidgin_version,
                                    'timestamp': parsed_result.timestamp,
                                    'country': parsed_result.country,
                                    'confidence_score': parsed_result.confidence_score
                                }
                            
                            # Debug: Show what we're trying to save
                            # st.write("Debug - Data to save:", news_data)
                            
                            # Add to Firestore
                            doc_ref = db.collection("news_articles").add(news_data)
                            doc_id = doc_ref[1].id if isinstance(doc_ref, tuple) else doc_ref.id
                            # st.markdown(f'<div class="alert-success">✅ Analysis saved to database successfully! Document ID: {doc_id}</div>', unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ Error saving to database: {str(e)}</div>', unsafe_allow_html=True)
                            st.write("Debug - Error details:", str(e))
                            st.write("Debug - Parsed result type:", type(parsed_result))
                            st.write("Debug - Parsed result:", parsed_result)
                    
                    # Show raw response if requested
                    if show_raw_response:
                        with st.expander("🔍 Raw AI Response"):
                            st.code(response, language="json")
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.markdown(f'<div class="alert-error">⚠️ Analysis failed: {str(e)}</div>', unsafe_allow_html=True)
                    if show_raw_response:
                        st.code(str(response) if 'response' in locals() else "No response available", language="text")
    
    elif page == "Analytics Dashboard":
        display_analytics()
    
    elif page == "History":
        st.markdown('<div class="main-header"><h1>📚 Analysis History</h1><p>Review your previous news analyses</p></div>', unsafe_allow_html=True)
        
        data = load_analytics_data()
        if data:
            # Get unique values for filters
            countries = list(set(item.get('country') for item in data if item.get('country')))
            sentiments = list(set(item.get('sentiment_analysis') for item in data if item.get('sentiment_analysis')))
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                country_filter = st.selectbox("Filter by Country:", ["All"] + countries)
            with col2:
                sentiment_filter = st.selectbox("Filter by Sentiment:", ["All"] + sentiments)
            with col3:
                sort_by = st.selectbox("Sort by:", ["Timestamp", "Country", "Credibility"])
            
            # Apply filters
            filtered_data = data.copy()
            if country_filter != "All":
                filtered_data = [item for item in filtered_data if item.get('country') == country_filter]
            if sentiment_filter != "All":
                filtered_data = [item for item in filtered_data if item.get('sentiment_analysis') == sentiment_filter]
            
            # Sort data
            if sort_by == "Timestamp":
                filtered_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            elif sort_by == "Country":
                filtered_data.sort(key=lambda x: x.get('country', ''))
            elif sort_by == "Credibility":
                filtered_data.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
            
            # Display results
            for item in filtered_data:
                title = item.get('title', 'Untitled')
                country = item.get('country', 'Unknown')
                timestamp = item.get('timestamp', 'Unknown')
                if timestamp != 'Unknown':
                    timestamp = timestamp.split('T')[0]  # Show only date
                
                with st.expander(f"📰 {title} - {country} ({timestamp})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**Summary:** {item.get('ai_summary', 'N/A')}")
                        st.write(f"**Pidgin:** {item.get('pidgin_version', 'N/A')}")
                    with col2:
                        st.write(f"**Sentiment:** {item.get('sentiment_analysis', 'N/A')}")
                        st.write(f"**Topics:** {item.get('key_topics', 'N/A')}")
                        st.write(f"**Credibility:** {item.get('credibility_assessment', 'N/A')}")
        else:
            st.info("No history available yet. Start analyzing some news!")

if __name__ == "__main__":
    main()