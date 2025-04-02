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
                st.session_state.agent_logs.append(log_entry)
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
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-text {
        font-size: 0.9rem;
        color: #616161;
    }
    .highlight {
        background-color: #f0f7ff;
        padding: 10px;
        border-left: 3px solid #1E88E5;
        margin: 10px 0;
    }
    .success-text {
        color: #4CAF50;
        font-weight: bold;
    }
    .divider {
        margin: 20px 0;
        border-bottom: 1px solid #e0e0e0;
    }
    .agent-log {
        height: 300px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        background-color: #f5f5f5;
        font-family: monospace;
        margin-bottom: 15px;
        font-size: 0.85rem;
    }
    .agent-entry {
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 1px dashed #e0e0e0;
    }
    .agent-data {
        color: #1565C0;
        font-weight: bold;
    }
    .agent-strategy {
        color: #7B1FA2;
        font-weight: bold;
    }
    .agent-risk {
        color: #C62828;
        font-weight: bold;
    }
    .agent-trade {
        color: #2E7D32;
        font-weight: bold;
    }
    .agent-portfolio {
        color: #FF6F00;
        font-weight: bold;
    }
    .agent-market {
        color: #0277BD;
        font-weight: bold;
    }
    .agent-manager {
        color: #212121;
        font-weight: bold;
    }
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
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("<div class='main-header'>StockSage AI</div>", unsafe_allow_html=True)
st.markdown("<div class='info-text'>Intelligent Investment Analysis with Multi-Agent AI</div>", unsafe_allow_html=True)

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
st.markdown("<div class='sub-header'>Investment Parameters</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
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
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
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
    
    st.markdown("</div>", unsafe_allow_html=True)

# Sector preferences
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Sector Preferences</div>", unsafe_allow_html=True)

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
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**Preferred Sectors**", unsafe_allow_html=True)
    
    default_preferred = DEFAULT_INPUTS['sector_preferences'].split(", ")
    preferred_sectors = st.multiselect(
        "Select sectors you're interested in investing",
        options=list(all_sectors.keys()),
        default=default_preferred if all(sector in all_sectors for sector in default_preferred) else ["Technology", "Healthcare", "Renewable Energy"],
        help="Choose sectors you believe will perform well"
    )
    
    # Show descriptions for selected sectors
    if preferred_sectors:
        st.markdown("<div class='highlight'>", unsafe_allow_html=True)
        st.markdown("**Selected sector details:**", unsafe_allow_html=True)
        for sector in preferred_sectors:
            st.markdown(f"• **{sector}**: {all_sectors[sector]}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**Excluded Sectors**", unsafe_allow_html=True)
    
    default_excluded = DEFAULT_INPUTS['exclude_sectors'].split(", ")
    excluded_sectors = st.multiselect(
        "Select sectors you want to avoid",
        options=[s for s in all_sectors.keys() if s not in preferred_sectors],
        default=default_excluded if all(sector in all_sectors for sector in default_excluded) else ["Tobacco", "Gambling"],
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
    
    st.markdown("</div>", unsafe_allow_html=True)

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
    news_impact = st.checkbox(
        "Consider recent news and events in analysis",
        value=DEFAULT_INPUTS['news_impact_consideration'],
        help="Enable to include recent news impact in the analysis"
    )

# Run analysis button
with col2:
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
        logs_html = format_agent_logs(st.session_state.agent_logs)
        agent_log_container.markdown(f'<div class="agent-log">{logs_html}</div>', unsafe_allow_html=True)
    
    # Run the actual analysis
    try:
        # Clear previous logs
        st.session_state.agent_logs = []
        
        # Create a thread to update logs while analysis runs
        def update_logs_periodically():
            while True:
                update_log_display()
                time.sleep(0.5)  # Update every half second
        
        # Start log updater thread
        log_update_thread = threading.Thread(target=update_logs_periodically, daemon=True)
        log_update_thread.start()
        
        with st.spinner("Analyzing... (this may take several minutes)"):
            # Run the actual analysis
            result = run_financial_analysis(inputs)
            
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
                    border: 1px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: white;
                    overflow-y: auto;
                    max-height: 600px;
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
            - Verify your API keys in the .env file
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