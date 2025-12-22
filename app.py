import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from parser_utils import get_resume_text
import os
import json

# --- CONFIGURATION ---
GEMINI_API_KEY = "REPLACE WITH YOUR API KEY"
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(45deg, #3b82f6, #8b5cf6);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        background: linear-gradient(45deg, #2563eb, #7c3aed);
    }

    .score-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        text-align: center;
        margin-bottom: 2rem;
    }

    .header-text {
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .subheader-text {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .section-container {
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: rgba(30, 41, 59, 0.7);
        border-left: 5px solid #3b82f6;
    }

    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- GENAI LOGIC ---
def analyze_resume(resume_text, job_description):
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    As an expert HR Manager and Technical Recruiter with 20 years of experience, analyze the provided Resume against the Job Description.
    
    Resume Text:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Provide a detailed evaluation in JSON format with the following structure:
    {{
        "match_score": (0-100),
        "summary": "Professional summary of the candidate's fit",
        "strengths": ["list of key strengths"],
        "weaknesses": ["list of areas for improvement or missing requirements"],
        "skills_match": {{
            "matched_skills": ["extracted from resume and jd"],
            "missing_skills": ["present in jd but missing in resume"]
        }},
        "experience_score": (1-10),
        "education_relevance": "Highly Relevant/Relevant/Partially Relevant",
        "verdict": "Shortlist/Consider/Reject"
    }}
    
    Respond ONLY with the JSON object.
    """
    
    response = model.generate_content(prompt)
    try:
        # Clean potential markdown from response
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except Exception as e:
        return {"error": f"Failed to parse AI response: {str(e)}", "raw": response.text}

# --- UI LAYOUT ---
def main():
    st.markdown('<div class="header-text">Resume Intellect AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-text">Revolutionizing recruitment with Gemini-powered deep analysis</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("Job Requirements")
        jd_input = st.text_area("Paste Job Description here...", height=300, 
                               placeholder="Enter the role requirements, technical skills, and experience needed...")
        
        st.divider()
        st.markdown("### Settings")
        show_charts = st.checkbox("Show Visual Analytics", value=True)
        detail_level = st.select_slider("Analysis Depth", options=["Fast", "Standard", "Deep"])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Upload Candidate Profile")
        uploaded_file = st.file_uploader("Choose a Resume (PDF or DOCX)", type=["pdf", "docx"])
        
        if uploaded_file and jd_input:
            if st.button("Run AI Analysis"):
                with st.spinner("Gemini is analyzing the profile..."):
                    # Extract text
                    resume_text = get_resume_text(uploaded_file)
                    
                    if resume_text:
                        # Call API
                        result = analyze_resume(resume_text, jd_input)
                        
                        if "error" not in result:
                            st.session_state['analysis_result'] = result
                            st.success("Analysis Complete!")
                        else:
                            st.error(result["error"])
                    else:
                        st.error("Could not extract text from the file.")

    # --- RESULTS DISPLAY ---
    if 'analysis_result' in st.session_state:
        res = st.session_state['analysis_result']
        
        # Dashboard Top Row
        st.divider()
        m_col1, m_col2, m_col3 = st.columns([1, 1, 1])
        
        with m_col1:
            st.markdown(f"""
            <div class="score-card">
                <h3 style='color: #60a5fa;'>Match Score</h3>
                <h1 style='font-size: 3.5rem; color: white;'>{res['match_score']}%</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with m_col2:
            verdict_color = "#10b981" if res['verdict'] == "Shortlist" else "#f59e0b" if res['verdict'] == "Consider" else "#ef4444"
            st.markdown(f"""
            <div class="score-card">
                <h3 style='color: #60a5fa;'>AI Verdict</h3>
                <h1 style='font-size: 2.5rem; color: {verdict_color};'>{res['verdict']}</h1>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col3:
            st.markdown(f"""
            <div class="score-card">
                <h3 style='color: #60a5fa;'>Experience Score</h3>
                <h1 style='font-size: 3.5rem; color: white;'>{res['experience_score']}/10</h1>
            </div>
            """, unsafe_allow_html=True)

        # Charts Section
        if show_charts:
            c_col1, c_col2 = st.columns([1, 1])
            
            with c_col1:
                # Skill Match Gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = res['match_score'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Matching Accuracy", 'font': {'size': 24, 'color': '#60a5fa'}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#3b82f6"},
                        'bgcolor': "rgba(0,0,0,0)",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                            {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.3)'},
                            {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.3)'}],
                    }
                ))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig, use_container_width=True)

            with c_col2:
                # Skills Bar Chart
                skills_data = {
                    'Category': ['Matched', 'Missing'],
                    'Count': [len(res['skills_match']['matched_skills']), len(res['skills_match']['missing_skills'])]
                }
                df_skills = pd.DataFrame(skills_data)
                fig_bar = px.bar(df_skills, x='Category', y='Count', 
                                title="Skills Breakdown",
                                color='Category', 
                                color_discrete_map={'Matched': '#10b981', 'Missing': '#ef4444'})
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig_bar, use_container_width=True)

        # Detailed Breakdown
        st.markdown("### Profile Summary")
        st.info(res['summary'])

        d_col1, d_col2 = st.columns(2)
        
        with d_col1:
            st.markdown('<div class="section-container"><h4> Key Strengths</h4>', unsafe_allow_html=True)
            for s in res['strengths']:
                st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="section-container" style="border-left-color: #10b981;"><h4> Matched Skills</h4>', unsafe_allow_html=True)
            st.write(", ".join(res['skills_match']['matched_skills']))
            st.markdown('</div>', unsafe_allow_html=True)

        with d_col2:
            st.markdown('<div class="section-container" style="border-left-color: #f59e0b;"><h4> Areas for Improvement</h4>', unsafe_allow_html=True)
            for w in res['weaknesses']:
                st.markdown(f"- {w}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="section-container" style="border-left-color: #ef4444;"><h4> Missing Skills</h4>', unsafe_allow_html=True)
            st.write(", ".join(res['skills_match']['missing_skills']))
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"**Eduation Relevance:** {res['education_relevance']}")

if __name__ == "__main__":
    main()
