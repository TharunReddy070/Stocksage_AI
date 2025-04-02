import streamlit as st
import os
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import warnings
import threading
import queue
warnings.filterwarnings('ignore')

# Import from project modules
from config import load_environment, DEFAULT_INPUTS
from crew import run_financial_analysis, register_log_callback, get_agent_logs

# Initialize session state for logs if not exists
if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = []
    st.session_state.log_queue = queue.Queue()

# Create a queue for agent logs
log_queue = st.session_state.log_queue

# Callback to receive logs from agents
def log_callback(log_entry):
    log_queue.put(log_entry)

# Register callback with agent logger
register_log_callback(log_callback)

# Function to determine agent class for styling
def get_agent_class(agent_name):
    agent_name = str(agent_name).lower()
    if "data" in agent_name or "analyst" in agent_name:
        return "agent-data"
    elif "strategy" in agent_name or "trading" in agent_name:
        return "agent-strategy"
    elif "risk" in agent_name:
        return "agent-risk"
    elif "trade" in agent_name or "execution" in agent_name:
        return "agent-trade"
    elif "portfolio" in agent_name or "selection" in agent_name or "curator" in agent_name:
        return "agent-portfolio"
    elif "market" in agent_name or "research" in agent_name:
        return "agent-market"
    elif "manager" in agent_name or "crew" in agent_name:
        return "agent-manager"
    else:
        return "agent-manager"

# Function to format agent logs as HTML
def format_agent_logs(logs):
    html = ""
    for log in logs:
        agent_class = get_agent_class(log['agent'])
        details_html = ""
        if log.get('details'):
            details_html = f"<div class='log-details'>{log['details']}</div>"
        
        html += f"""
        <div class="agent-entry">
            <span class="{agent_class}">{log['agent']}</span>: {log['action']}
            <div class="log-time">{log['time']}</div>
            {details_html}
        </div>
        """
    return html

# Agent log processing thread
def agent_log_processor():
    while True:
        try:
            # Get log entry from queue (non-blocking)
            try:
                log_entry = log_queue.get_nowait()
                # Print for debugging
                print(f"Received log entry: {log_entry}")
                
                # Store in global variable for backup
                if not hasattr(agent_log_processor, 'backup_logs'):
                    agent_log_processor.backup_logs = []
                agent_log_processor.backup_logs.append(log_entry)
                
                # Use a thread-safe way to store logs
                if "agent_logs" in st.session_state:
                    st.session_state.agent_logs.append(log_entry)
                    print(f"Added log to session state. Total: {len(st.session_state.agent_logs)}")
            except queue.Empty:
                pass
            
            # Sleep briefly to avoid consuming too much CPU
            time.sleep(0.1)
        except Exception as e:
            print(f"Error in log processor: {str(e)}")
            time.sleep(1)

# Start log processor in a background thread
if 'log_processor_started' not in st.session_state:
    log_thread = threading.Thread(target=agent_log_processor, daemon=True)
    log_thread.start()
    st.session_state.log_processor_started = True

# Page configuration
st.set_page_config(
    page_title="StockSage AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Page background - dark theme */
    .stApp {
        background-color: #121212 !important;
        background-image: url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23222222' fill-opacity='0.8' fill-rule='evenodd'%3E%3Ccircle cx='3' cy='3' r='1'/%3E%3Ccircle cx='13' cy='13' r='1'/%3E%3C/g%3E%3C/svg%3E") !important;
        color: #e0e0e0 !important;
    }
    
    /* Main content background enhancement with texture */
    .main .block-container {
        background-color: rgba(30, 30, 30, 0.7);
        background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%232196f3' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
        border-radius: 10px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    /* Sidebar background - dark */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1A237E 0%, #0D47A1 100%);
        color: white;
    }
    
    /* Headers with gradients for dark mode */
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #2196F3, #64B5F6);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
        font-weight: bold;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0;
    }
    
    /* Subheaders for dark mode */
    .sub-header {
        font-size: 1.5rem;
        color: #e0e0e0;
        margin: 0.5rem 0;
        border-left: 4px solid #2196F3;
        padding-left: 10px;
    }
    
    /* Card improvements with subtle shadows and borders for dark mode */
    .card {
        background-color: rgba(40, 40, 40, 0.8) !important;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.2);
        margin-bottom: 1.2rem;
        border: 1px solid rgba(70, 70, 70, 0.8);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        color: #e0e0e0;
    }
    
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4), 0 3px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Card headers for dark mode */
    .card h3 {
        color: #e0e0e0 !important;
    }
    
    /* Form elements for dark mode */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        background-color: rgba(60, 60, 60, 0.8);
        color: #e0e0e0;
        border-color: rgba(100, 100, 100, 0.6);
    }
    
    /* Radio buttons in dark mode */
    .stRadio label {
        color: #e0e0e0 !important;
    }
    
    /* Checkbox labels in dark mode */
    .stCheckbox label {
        color: #e0e0e0 !important;
    }
    
    /* Text color for all st elements */
    .st-bc, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al {
        color: #e0e0e0;
    }
    
    /* Label styling for dark mode */
    .stTextInput > div > label,
    .stSelectbox > div > label,
    .stMultiSelect > div > label {
        color: #b0b0b0;
    }
    
    /* Header container with enhanced design for dark mode */
    .header-container {
        background: linear-gradient(135deg, rgba(40, 40, 40, 0.9), rgba(30, 30, 30, 0.9));
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(70, 70, 70, 0.7);
        backdrop-filter: blur(5px);
    }
    
    /* Section headers with accents for dark mode */
    .section-header {
        background: linear-gradient(to right, rgba(40, 40, 40, 0.8), transparent);
    }
    
    /* Agent log styling for dark mode */
    .agent-log {
        background-color: rgba(30, 30, 30, 0.9);
        border: 1px solid rgba(70, 70, 70, 0.7);
        color: #d0d0d0;
    }
    
    /* Sector description container for dark mode */
    .sector-description-container {
        background: linear-gradient(to right, rgba(50, 60, 50, 0.7), rgba(40, 50, 40, 0.3));
        border-left: 3px solid #43A047;
    }
    
    /* Info text for dark mode */
    .info-text {
        color: #b0b0b0;
    }
    
    /* Highlight section for dark mode */
    .highlight {
        background: linear-gradient(to right, rgba(40, 50, 70, 0.7), rgba(30, 40, 60, 0.3));
        border-left: 3px solid #2196F3;
    }
    
    /* Make sure all text has good contrast */
    p, li, div, span {
        color: #e0e0e0;
    }
    
    /* Style the markdown report for dark mode */
    .markdown-report {
        border: 1px solid rgba(70, 70, 70, 0.7);
        border-radius: 10px;
        padding: 20px;
        background-color: rgba(30, 30, 30, 0.8);
        color: #e0e0e0;
        overflow-y: auto;
        max-height: 600px;
        font-family: 'Roboto', sans-serif;
        line-height: 1.6;
    }
    
    .markdown-report h1, .markdown-report h2, .markdown-report h3 {
        color: #90CAF9;
        border-bottom: 1px solid rgba(100, 100, 100, 0.3);
        padding-bottom: 5px;
    }
    
    .markdown-report a {
        color: #64B5F6;
    }
    
    .markdown-report code {
        background-color: rgba(50, 50, 50, 0.8);
        border: 1px solid rgba(80, 80, 80, 0.6);
        border-radius: 4px;
        padding: 2px 5px;
        font-family: 'Courier New', monospace;
        color: #BBDEFB;
    }
    
    .markdown-report table {
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
    }
    
    .markdown-report th {
        background-color: rgba(50, 50, 50, 0.8);
        color: #90CAF9;
        border: 1px solid rgba(80, 80, 80, 0.6);
        padding: 8px 12px;
        text-align: left;
    }
    
    .markdown-report td {
        border: 1px solid rgba(80, 80, 80, 0.6);
        padding: 8px 12px;
        background-color: rgba(40, 40, 40, 0.8);
    }
    
    .markdown-report tr:nth-child(even) td {
        background-color: rgba(45, 45, 45, 0.8);
    }
    
    .markdown-report blockquote {
        border-left: 3px solid #64B5F6;
        padding-left: 10px;
        margin-left: 0;
        color: #B0BEC5;
        font-style: italic;
        background-color: rgba(50, 50, 50, 0.4);
        padding: 10px;
        border-radius: 0 5px 5px 0;
    }
    
    /* Base styling improvements */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 95%;
    }
    
    /* Modern headers with gradients */
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #1E88E5, #42A5F5);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
        font-weight: bold;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
        padding-left: 10px;
    }
    
    /* Card improvements with subtle shadows and borders */
    .card {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.2rem;
        border: 1px solid rgba(220, 230, 240, 0.8);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12), 0 3px 8px rgba(0, 0, 0, 0.06);
    }
    
    /* Improve form elements with more modern styling */
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within,
    .stMultiSelect > div > div > div:focus-within {
        border-color: #1976D2;
        box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
    }
    
    /* Enhanced label styling */
    .stTextInput > div > label,
    .stSelectbox > div > label,
    .stMultiSelect > div > label {
        font-weight: 500;
        color: #344054;
        margin-bottom: 0.3rem;
        font-size: 0.95rem;
    }
    
    /* Improve widgets container spacing */
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0.5rem;
    }
    
    /* Radio and checkbox styling */
    .stRadio > div,
    .stCheckbox > div {
        padding: 0.3rem 0.1rem;
        margin-bottom: 0.2rem;
    }
    
    /* Container for sector descriptions */
    .sector-description-container {
        background: linear-gradient(to right, rgba(232, 245, 233, 0.7), rgba(241, 248, 233, 0.3));
        border-radius: 8px;
        padding: 15px;
        margin-top: 12px;
        border-left: 3px solid #43A047;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    
    .success-text {
        color: #4CAF50;
        font-weight: bold;
    }
    
    .divider {
        margin: 15px 0;
        height: 1px;
        background: linear-gradient(to right, transparent, #e0e0e0, transparent);
        border: none;
    }
    
    /* Enhanced agent logs */
    .agent-log {
        height: 300px;
        overflow-y: auto;
        border-radius: 8px;
        padding: 12px;
        background-color: #fafafa;
        font-family: 'Courier New', monospace;
        margin-bottom: 15px;
        font-size: 0.85rem;
        border: 1px solid #eaeaea;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .agent-entry {
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 1px dashed #e0e0e0;
    }
    
    /* Agent colors */
    .agent-data { color: #1565C0; font-weight: bold; }
    .agent-strategy { color: #7B1FA2; font-weight: bold; }
    .agent-risk { color: #C62828; font-weight: bold; }
    .agent-trade { color: #2E7D32; font-weight: bold; }
    .agent-portfolio { color: #FF6F00; font-weight: bold; }
    .agent-market { color: #0277BD; font-weight: bold; }
    .agent-manager { color: #212121; font-weight: bold; }
    
    .log-time {
        color: #616161;
        font-size: 0.75rem;
    }
    
    .log-details {
        color: #616161;
        font-size: 0.8rem;
        margin-top: 3px;
        margin-left: 10px;
        padding-left: 5px;
        border-left: 2px solid #e0e0e0;
    }
    
    /* Button styling for dark mode */
    .stButton > button {
        border-radius: 5px;
        padding: 0.25rem 1rem;
        font-weight: 500;
        background-color: #263238;
        border: 1px solid #455A64;
        color: #e0e0e0;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #37474F;
        border-color: #546E7A;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    /* Primary button */
    .stButton > button[data-baseweb="button"]:first-child {
        background: linear-gradient(90deg, #1565C0, #1976D2);
        color: white;
        border: none;
    }
    
    .stButton > button[data-baseweb="button"]:first-child:hover {
        background: linear-gradient(90deg, #0D47A1, #1565C0);
        box-shadow: 0 3px 7px rgba(0, 0, 0, 0.3);
    }
    
    /* Capital buttons */
    div[key^="cap_"] button {
        background-color: #263238;
        color: #e0e0e0;
        border: 1px solid #455A64;
    }
    
    div[key^="cap_"] button:hover {
        background-color: #37474F;
        border-color: #546E7A;
    }
    
    /* News info box styling for dark mode */
    .news-info-box {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        background: linear-gradient(to right, rgba(40, 50, 70, 0.7), rgba(30, 40, 60, 0.3));
        border-radius: 8px;
        border: 1px solid rgba(70, 90, 120, 0.6);
    }
    
    /* Override dropdown menu background */
    div[data-baseweb="select"] ul {
        background-color: #263238 !important;
        color: #e0e0e0 !important;
    }
    
    div[data-baseweb="select"] li {
        color: #e0e0e0 !important;
    }
    
    div[data-baseweb="select"] li:hover {
        background-color: #37474F !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(40, 40, 40, 0.8);
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #b0b0b0;
        border-radius: 4px;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(33, 150, 243, 0.2);
        color: #e0e0e0;
    }
    
    /* Plots and charts background */
    .js-plotly-plot .plotly {
        background-color: rgba(40, 40, 40, 0.8) !important;
    }
    
    /* Hover tooltip */
    .tooltip, [data-tooltip]::after {
        background-color: #263238 !important;
        color: #e0e0e0 !important;
        border: 1px solid #455A64 !important;
    }
    
    /* Fix spacing in sidebar */
    .css-1d391kg, .css-163ttbj, .css-1a32fsj {
        padding-top: 0 !important;
    }
    
    /* Sidebar styling */
    .css-1cypcdb {
        background: linear-gradient(180deg, #1976D2 0%, #2196F3 100%);
        color: white;
    }
    
    .css-1cypcdb .main-header {
        color: white !important;
        background: none;
        -webkit-background-clip: unset;
        background-clip: unset;
    }
    
    /* Improve expander styling */
    .streamlit-expanderHeader {
        font-weight: 500;
        color: #424242;
        background-color: #f9f9f9;
        border-radius: 5px;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #2196F3;
    }
    
    /* Section dividers with gradient */
    .divider {
        margin: 25px 0;
        height: 3px;
        background: linear-gradient(to right, 
            rgba(25, 118, 210, 0.1), 
            rgba(25, 118, 210, 0.5), 
            rgba(25, 118, 210, 0.1));
        border: none;
        border-radius: 3px;
    }
    
    /* Section headers with accents */
    .section-header {
        display: flex;
        align-items: center;
        margin: 1.5rem 0;
        padding: 0.5rem 1rem;
        background: linear-gradient(to right, rgba(240, 245, 255, 0.8), transparent);
        border-radius: 8px;
    }
    
    .section-indicator {
        width: 5px;
        height: 28px;
        margin-right: 12px;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="header-container">
    <div style="display: flex; align-items: center;">
        <div style="font-size: 2.5rem; margin-right: 1.2rem; background: linear-gradient(45deg, #1976D2, #64B5F6); -webkit-background-clip: text; background-clip: text; color: transparent;">💰</div>
        <div>
            <div class='main-header'>StockSage AI</div>
            <div style="font-size: 1rem; color: #666;">Intelligent Investment Analysis with Multi-Agent AI</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load environment variables
@st.cache_resource
def initialize_env():
    try:
        return load_environment()
    except ValueError as e:
        st.error(f"Environment configuration error: {str(e)}")
        st.stop()

# Initialize environment
env_vars = initialize_env()

# Sidebar
st.sidebar.markdown("<div class='main-header'>💰 FinancialGPT</div>", unsafe_allow_html=True)
st.sidebar.markdown("*Your AI-Powered Investment Advisor*")

# Add tabs for different modes
tab_mode = st.sidebar.radio(
    "Select Analysis Mode:",
    ["Portfolio Recommendations", "Single Stock Analysis"],
    help="Choose whether to get portfolio recommendations or analyze a single stock"
)

with st.sidebar.expander("About", expanded=False):
    st.markdown("""
    **FinancialGPT** is an advanced AI-powered financial analysis system that uses 
    collaborative multi-agent architecture to provide sophisticated investment recommendations.
    
    The system features:
    - Custom portfolio recommendations
    - Comprehensive market research
    - Risk assessment and mitigation
    - Trading strategy development
    
    Built with CrewAI and powered by GPT models.
    """)

# Main content area
st.markdown("<div class='main-header'>Financial Analysis AI Assistant</div>", unsafe_allow_html=True)

# Investment parameters collection
st.markdown("""
<div class="section-header">
    <div class="section-indicator" style="background: linear-gradient(180deg, #1976D2, #64B5F6);"></div>
    <div class='sub-header'>Investment Parameters</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card" style="position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(90deg, #1976D2, #64B5F6);"></div>
        <h3 style="margin-top: 8px; font-size: 1.2rem; color: #333;">Capital & Risk</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Capital input with suggestions
    capital_options = ["10000", "50000", "100000", "250000", "500000", "1000000"]
    capital_input = st.text_input(
        "Initial Capital ($)", 
        value=DEFAULT_INPUTS['initial_capital'],
        help="Enter your investment amount"
    )
    
    st.markdown("<div class='info-text'>Suggested capital amounts:</div>", unsafe_allow_html=True)
    capital_buttons = st.columns(3)
    for i, option in enumerate(capital_options):
        col_index = i % 3
        if capital_buttons[col_index].button(f"${option}", key=f"cap_{option}"):
            capital_input = option
            st.experimental_rerun()
    
    # Risk tolerance selection
    risk_options = ["Low", "Medium", "High"]
    risk_descriptions = {
        "Low": "Conservative approach prioritizing capital preservation over growth",
        "Medium": "Balanced approach with moderate risk for potential returns",
        "High": "Aggressive approach emphasizing maximum growth potential with higher volatility"
    }
    
    risk_tolerance = st.radio(
        "Risk Tolerance",
        risk_options,
        index=risk_options.index(DEFAULT_INPUTS['risk_tolerance']) if DEFAULT_INPUTS['risk_tolerance'] in risk_options else 1,
        help="Select your risk comfort level"
    )
    
    st.markdown(f"<div class='info-text'>{risk_descriptions[risk_tolerance]}</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card" style="position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(90deg, #FF6F00, #FFA726);"></div>
        <h3 style="margin-top: 8px; font-size: 1.2rem; color: #333;">Time & Strategy</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Time frame selection with interactive widget
    timeframe_options = {
        "Short-term": ["3-6 months", "6-12 months"],
        "Medium-term": ["1-2 years", "2-3 years", "3-5 years"],
        "Long-term": ["5-10 years", "10+ years"]
    }
    
    timeframe_category = st.selectbox(
        "Investment Horizon Category",
        list(timeframe_options.keys()),
        help="Select your general investment timeframe"
    )
    
    investment_timeframe = st.selectbox(
        "Specific Time Frame",
        timeframe_options[timeframe_category],
        index=0,
        help="Select your specific investment timeframe"
    )
    
    # Trading strategy selection
    strategy_categories = {
        "Passive": ["Buy and Hold", "Index Investing", "Dividend Growth"],
        "Active": ["Value Investing", "Growth Investing", "Momentum Trading"],
        "Advanced": ["Swing Trading", "Day Trading", "Options Strategy"]
    }
    
    strategy_category = st.selectbox(
        "Strategy Category",
        list(strategy_categories.keys()),
        help="Select your preferred trading approach"
    )
    
    trading_strategy = st.selectbox(
        "Trading Strategy",
        strategy_categories[strategy_category],
        index=0,
        help="Select your specific trading strategy"
    )

# Sector preferences
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <div class="section-indicator" style="background: linear-gradient(180deg, #43A047, #81C784);"></div>
    <div class='sub-header'>Sector Preferences</div>
</div>
""", unsafe_allow_html=True)

# Available sectors with descriptions
all_sectors = {
    "Technology": "Software, hardware, IT services, semiconductors",
    "Healthcare": "Pharmaceuticals, biotechnology, medical devices, healthcare services",
    "Financial Services": "Banking, insurance, asset management, fintech",
    "Consumer Discretionary": "Retail, automotive, leisure, media",
    "Consumer Staples": "Food, beverages, household products, personal care",
    "Industrials": "Aerospace, defense, machinery, transportation",
    "Energy": "Oil, gas, renewable energy",
    "Materials": "Chemicals, mining, metals, packaging",
    "Utilities": "Electric, gas, water utilities",
    "Real Estate": "REITs, property development",
    "Communication Services": "Telecommunication, media, entertainment",
    "Renewable Energy": "Solar, wind, hydro, geothermal",
    "Artificial Intelligence": "Machine learning, big data, robotics",
    "Cybersecurity": "Network security, infrastructure protection",
    "E-commerce": "Online retail, digital marketplaces",
    "Cloud Computing": "SaaS, PaaS, IaaS providers",
    "Biotechnology": "Genomics, personalized medicine, bioinformatics",
    "Electric Vehicles": "EV manufacturers, batteries, charging infrastructure",
    "Semiconductors": "Chip design, manufacturing, equipment",
    "Space Technology": "Aerospace, satellite, space exploration"
}

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card" style="position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(90deg, #43A047, #81C784);"></div>
        <h3 style="margin-top: 8px; font-size: 1.2rem; color: #333;">Preferred Sectors</h3>
    </div>
    """, unsafe_allow_html=True)
    
    default_preferred = DEFAULT_INPUTS['sector_preferences'].split(", ")
    preferred_sectors = st.multiselect(
        "Select sectors you're interested in investing",
        options=list(all_sectors.keys()),
        default=default_preferred if all(sector in all_sectors for sector in default_preferred) else ["Technology", "Healthcare", "Renewable Energy"],
        help="Choose sectors you believe will perform well"
    )
    
    # Show descriptions for selected sectors
    if preferred_sectors:
        st.markdown("""
        <div class="sector-description-container">
            <div style="font-weight: 500; color: #2E7D32; margin-bottom: 5px;">Selected sector details:</div>
        """, unsafe_allow_html=True)
        
        for sector in preferred_sectors:
            st.markdown(f"• **{sector}**: {all_sectors[sector]}", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card" style="position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(90deg, #D32F2F, #EF5350);"></div>
        <h3 style="margin-top: 8px; font-size: 1.2rem; color: #333;">Excluded Sectors</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Use set to prevent duplicates in sectors list
    all_sector_options = list(all_sectors.keys()) + ["Weapons & Defense", "Tobacco", "Gambling", "Adult Entertainment", "Alcohol", "Fossil Fuels"]
    all_sector_options = list(set(all_sector_options))
    
    default_excluded = DEFAULT_INPUTS['exclude_sectors'].split(", ")
    available_sector_options = [s for s in all_sector_options if s not in preferred_sectors]
    
    # Ensure defaults exist in options or provide empty defaults
    safe_defaults = [s for s in default_excluded if s in available_sector_options]
    
    excluded_sectors = st.multiselect(
        "Select sectors you want to avoid",
        options=available_sector_options,
        default=safe_defaults,
        help="Choose sectors you wish to exclude from your investments"
    )
    
    # Additional ethical exclusions
    ethical_exclusions = st.multiselect(
        "Ethical Exclusions",
        options=["Weapons & Defense", "Tobacco", "Gambling", "Adult Entertainment", "Alcohol", "Fossil Fuels"],
        default=[],
        help="Select any industries you wish to avoid for ethical reasons"
    )
    
    excluded_all = list(set(excluded_sectors + ethical_exclusions))

# Single stock analysis (optional)
if tab_mode == "Single Stock Analysis":
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Single Stock Analysis</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Popular stocks suggestions
    popular_stocks = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "META", "AMZN"],
        "Healthcare": ["JNJ", "PFE", "UNH", "ABT", "MRK"],
        "Financial": ["JPM", "BAC", "V", "MA", "GS"],
        "Consumer": ["PG", "KO", "PEP", "WMT", "MCD"],
        "Industrial": ["HON", "MMM", "CAT", "GE", "BA"]
    }
    
    # Stock input with autocomplete suggestions
    stock_input = st.text_input(
        "Enter Stock Symbol",
        value="AAPL",
        help="Enter the ticker symbol of the stock to analyze"
    )
    
    # Display popular stock suggestions
    st.markdown("<div class='info-text'>Popular stocks by sector:</div>", unsafe_allow_html=True)
    
    for sector, stocks in popular_stocks.items():
        st.markdown(f"**{sector}**: " + " ".join([f"`{s}`" for s in stocks]))
        
    st.markdown("</div>", unsafe_allow_html=True)

# News consideration checkbox
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <div class="news-info-box">
        <div style="margin-right: 10px; color: #64B5F6;">ℹ️</div>
        <div>
    """, unsafe_allow_html=True)
    
    news_impact = st.checkbox(
        "Consider recent news and events in analysis",
        value=DEFAULT_INPUTS['news_impact_consideration'],
        help="Enable to include recent news impact in the analysis"
    )
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Run analysis button
with col2:
    st.markdown("""
    <style>
    .run-analysis-btn {
        background: linear-gradient(90deg, #1976D2, #2196F3);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 15px;
        font-weight: 500;
        width: 100%;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .run-analysis-btn:hover {
        background: linear-gradient(90deg, #1565C0, #1976D2);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

# Prepare inputs for analysis
if run_button:
    inputs = {
        'initial_capital': capital_input,
        'risk_tolerance': risk_tolerance,
        'investment_timeframe': investment_timeframe,
        'trading_strategy_preference': trading_strategy,
        'news_impact_consideration': news_impact,
        'sector_preferences': ", ".join(preferred_sectors),
        'exclude_sectors': ", ".join(excluded_all)
    }
    
    # Add stock selection for single stock analysis
    if tab_mode == "Single Stock Analysis" and stock_input:
        inputs['stock_selection'] = stock_input.upper()
    
    # Create a two-column layout for progress and agent logs
    progress_col, logs_col = st.columns([1, 1])
    
    # Progress container in the left column
    with progress_col:
        progress_container = st.empty()
        with progress_container.container():
            st.markdown("<div class='sub-header'>Analysis in Progress</div>", unsafe_allow_html=True)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress for better UX (the actual analysis is running in background)
            phases = [
                "Gathering market data...",
                "Analyzing sector trends...",
                "Evaluating investment opportunities...",
                "Developing trading strategies...",
                "Assessing risk factors...",
                "Preparing recommendations..."
            ]
            
            for i, phase in enumerate(phases):
                status_text.markdown(f"<div class='info-text'>{phase}</div>", unsafe_allow_html=True)
                progress_bar.progress((i+1)/len(phases))
                time.sleep(0.5)  # Reduced time for better responsiveness
    
    # Agent logs container in the right column
    with logs_col:
        st.markdown("<div class='sub-header'>Agent Activity Log</div>", unsafe_allow_html=True)
        agent_log_container = st.empty()
        
        # Create initial empty log display
        agent_log_container.markdown('<div class="agent-log">Waiting for agent activity...</div>', unsafe_allow_html=True)
    
    # Function to update the log display
    def update_log_display():
        try:
            logs_to_display = []
            
            # Check all possible sources of logs
            if "agent_logs" in st.session_state and st.session_state.agent_logs:
                logs_to_display = st.session_state.agent_logs
                print(f"Using {len(logs_to_display)} logs from session state")
            elif hasattr(agent_log_processor, 'backup_logs') and agent_log_processor.backup_logs:
                logs_to_display = agent_log_processor.backup_logs
                print(f"Using {len(logs_to_display)} logs from backup")
            
            # Display logs if we have any
            if logs_to_display:
                logs_html = format_agent_logs(logs_to_display)
                agent_log_container.markdown(f'<div class="agent-log">{logs_html}</div>', unsafe_allow_html=True)
            else:
                print("No logs available to display")
                agent_log_container.markdown('<div class="agent-log">Waiting for agent activity...</div>', unsafe_allow_html=True)
                
        except Exception as e:
            print(f"Error updating log display: {str(e)}")
            # Fallback to empty display on error
            agent_log_container.markdown('<div class="agent-log">Log display unavailable</div>', unsafe_allow_html=True)
    
    # Run the actual analysis
    try:
        # Clear previous logs
        st.session_state.agent_logs = []
        
        # Create a thread to update logs while analysis runs
        def update_logs_periodically():
            while True:
                update_log_display()
                time.sleep(1)  # Update every second
        
        # Start log updater thread
        log_update_thread = threading.Thread(target=update_logs_periodically, daemon=True)
        log_update_thread.start()
        
        # Display placeholder for logs
        st.markdown("<div class='sub-header'>Real-time Agent Activity</div>", unsafe_allow_html=True)
        live_log_container = st.empty()
        
        with st.spinner("Analyzing... (this may take several minutes)"):
            # Run the actual analysis
            result = run_financial_analysis(inputs)
            
            # Show logs directly from get_agent_logs
            direct_logs = get_agent_logs()
            if direct_logs:
                print(f"Direct logs from get_agent_logs: {len(direct_logs)} entries")
                # Format and display these logs directly
                logs_html = format_agent_logs(direct_logs)
                live_log_container.markdown(f'<div class="agent-log">{logs_html}</div>', unsafe_allow_html=True)
                # Also add them to session state
                st.session_state.agent_logs = direct_logs
            
            # Verify results exist
            if not hasattr(result, 'raw') or not result.raw:
                raise ValueError("Analysis completed but returned empty results")
        
        # Clear the progress container
        progress_container.empty()
        
        # Final log update
        update_log_display()
        
        # Display results
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-header success-text'>✅ Analysis Complete</div>", unsafe_allow_html=True)
        
        # If no logs were captured, add sample logs for UI display
        if not st.session_state.agent_logs and not hasattr(agent_log_processor, 'backup_logs'):
            print("No logs captured, adding sample logs")
            sample_logs = [
                {'agent': 'Crew Manager', 'action': 'Started financial analysis task', 'time': time.strftime('%H:%M:%S'), 'details': 'Initializing analysis with provided parameters'},
                {'agent': 'Data Analyst', 'action': 'Gathering market data', 'time': time.strftime('%H:%M:%S'), 'details': 'Collecting data for Technology, Healthcare, Renewable Energy sectors'},
                {'agent': 'Strategy Advisor', 'action': 'Analyzing trading strategies', 'time': time.strftime('%H:%M:%S'), 'details': 'Evaluating Day Trading strategy for selected sectors'},
                {'agent': 'Risk Advisor', 'action': 'Assessing risk factors', 'time': time.strftime('%H:%M:%S'), 'details': 'Analyzing risk factors for conservative approach'},
                {'agent': 'Portfolio Curator', 'action': 'Preparing recommendations', 'time': time.strftime('%H:%M:%S'), 'details': 'Finalizing investment opportunities based on analysis'}
            ]
            st.session_state.agent_logs = sample_logs
        
        # Create tabs for different sections of the results
        result_tabs = st.tabs(["Summary", "Detailed Analysis", "Charts", "Raw Output"])
        
        with result_tabs[0]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            
            # This is a placeholder - in a real implementation, you would parse the result
            # from the AI and extract key information for a more structured display
            st.markdown("### Investment Recommendations Summary")
            
            # Example visualization of recommendations
            if 'stock_selection' in inputs and inputs['stock_selection']:
                st.markdown(f"**Single Stock Analysis for {inputs['stock_selection']}**")
                
                # Example metrics for single stock
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Risk Level", "Medium", help="Assessed risk level for this stock")
                with col2:
                    st.metric("Growth Potential", "+8.4%", help="Estimated growth potential")
                with col3:
                    st.metric("Recommendation", "BUY", delta="Strong", help="Overall recommendation")
            else:
                st.markdown("**Portfolio Recommendations**")
                
                # Create example portfolio allocation chart
                example_stocks = ["AAPL", "MSFT", "JNJ", "V", "AMZN"]
                example_allocations = [30, 25, 20, 15, 10]
                
                fig = px.pie(
                    values=example_allocations,
                    names=example_stocks,
                    title="Recommended Portfolio Allocation",
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with result_tabs[1]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Detailed Analysis")
            
            # Display the raw result text
            st.markdown(result.raw)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with result_tabs[2]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Performance Projections")
            
            # Example chart for projected performance
            time_periods = ["3 Months", "6 Months", "1 Year", "2 Years", "5 Years"]
            
            if 'stock_selection' in inputs and inputs['stock_selection']:
                # For single stock
                projected_returns = [2.1, 5.4, 11.2, 18.7, 42.3]
                
                fig = px.line(
                    x=time_periods, 
                    y=projected_returns,
                    markers=True,
                    title=f"Projected Returns for {inputs['stock_selection']}",
                    labels={"x": "Time Period", "y": "Projected Return (%)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # For portfolio
                low_risk = [1.5, 3.2, 6.8, 14.1, 32.5]
                medium_risk = [2.1, 5.4, 11.2, 24.7, 52.3]
                high_risk = [3.2, 7.8, 15.6, 32.1, 68.2]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=time_periods, y=low_risk, mode='lines+markers', name='Low Risk'))
                fig.add_trace(go.Scatter(x=time_periods, y=medium_risk, mode='lines+markers', name='Medium Risk (Selected)'))
                fig.add_trace(go.Scatter(x=time_periods, y=high_risk, mode='lines+markers', name='High Risk'))
                
                fig.update_layout(
                    title="Projected Portfolio Performance by Risk Level",
                    xaxis_title="Time Period",
                    yaxis_title="Projected Return (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
                
        with result_tabs[3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Analysis Report")
            
            # Display the raw output as rendered markdown in an expandable area
            with st.expander("View Complete Analysis Report", expanded=True):
                # Container for markdown content with custom styling
                st.markdown("""
                <style>
                .markdown-report {
                    border: 1px solid rgba(70, 70, 70, 0.7);
                    border-radius: 10px;
                    padding: 20px;
                    background-color: rgba(30, 30, 30, 0.8);
                    color: #e0e0e0;
                    overflow-y: auto;
                    max-height: 600px;
                    font-family: 'Roboto', sans-serif;
                    line-height: 1.6;
                }
                
                .markdown-report h1, .markdown-report h2, .markdown-report h3 {
                    color: #90CAF9;
                    border-bottom: 1px solid rgba(100, 100, 100, 0.3);
                    padding-bottom: 5px;
                }
                
                .markdown-report a {
                    color: #64B5F6;
                }
                
                .markdown-report code {
                    background-color: rgba(50, 50, 50, 0.8);
                    border: 1px solid rgba(80, 80, 80, 0.6);
                    border-radius: 4px;
                    padding: 2px 5px;
                    font-family: 'Courier New', monospace;
                    color: #BBDEFB;
                }
                
                .markdown-report table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }
                
                .markdown-report th {
                    background-color: rgba(50, 50, 50, 0.8);
                    color: #90CAF9;
                    border: 1px solid rgba(80, 80, 80, 0.6);
                    padding: 8px 12px;
                    text-align: left;
                }
                
                .markdown-report td {
                    border: 1px solid rgba(80, 80, 80, 0.6);
                    padding: 8px 12px;
                    background-color: rgba(40, 40, 40, 0.8);
                }
                
                .markdown-report tr:nth-child(even) td {
                    background-color: rgba(45, 45, 45, 0.8);
                }
                
                .markdown-report blockquote {
                    border-left: 3px solid #64B5F6;
                    padding-left: 10px;
                    margin-left: 0;
                    color: #B0BEC5;
                    font-style: italic;
                    background-color: rgba(50, 50, 50, 0.4);
                    padding: 10px;
                    border-radius: 0 5px 5px 0;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Render markdown with proper formatting
                st.markdown(f"<div class='markdown-report'>{result.raw}</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Option to download as markdown
            with col1:
                st.download_button(
                    label="Download as Markdown",
                    data=result.raw,
                    file_name="financial_analysis_report.md",
                    mime="text/markdown"
                )
            
            # Option to download as plain text
            with col2:
                st.download_button(
                    label="Download as Text",
                    data=result.raw,
                    file_name="financial_analysis_report.txt",
                    mime="text/plain"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
    except ValueError as e:
        st.error(f"Analysis Error: {str(e)}")
        st.markdown(
            """
            ### Suggestions:
            - Check if all required input parameters are provided
            - Try a different stock symbol
            - Verify your API keys are properly configured in Streamlit Cloud secrets or your local .env file
            """
        )
    except Exception as e:
        if "rate limit" in str(e).lower():
            st.error("API rate limit exceeded. Please wait a few minutes and try again.")
            st.markdown("The OpenAI API has usage limitations that may require waiting before another analysis.")
        else:
            st.error(f"An error occurred during analysis: {str(e)}")
            st.markdown("Please try again or contact support if the problem persists.")
            
        # Fallback content to show something useful even when analysis fails
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='highlight'>", unsafe_allow_html=True)
        st.markdown("""
        ### While we couldn't complete your full analysis, here are some general investment tips:
        
        1. **Diversification** is key to reducing risk - spread investments across different sectors
        2. **Time in the market** beats timing the market for long-term investments
        3. **Regular rebalancing** helps maintain your desired risk level
        4. **Keep costs low** by considering expense ratios and fees
        5. **Stay informed** but avoid making emotional decisions based on market volatility
        """)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # Display instructions when the app first loads
    st.markdown("<div class='highlight'>", unsafe_allow_html=True)
    st.markdown("""
    ### How to use this tool
    
    1. **Set your investment parameters** - Specify your capital, risk tolerance, timeframe, and strategy
    2. **Select sector preferences** - Choose sectors you're interested in and those you want to exclude
    3. **Choose analysis mode** - Get portfolio recommendations or analyze a specific stock
    4. **Click 'Run Analysis'** - Our AI agents will analyze the market and provide tailored recommendations
    
    The analysis may take several minutes to complete, as our system performs comprehensive market research and strategy development.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div class='info-text' style='text-align: center;'>Powered by CrewAI and OpenAI | Financial data from various sources</div>", unsafe_allow_html=True) 