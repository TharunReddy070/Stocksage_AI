import os
from dotenv import load_dotenv

# Load environment variables from .env file
def load_environment():
    """Load environment variables from .env file and set them in os.environ"""
    load_dotenv()
    
    # Access environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    serper_api_key = os.getenv("SERPER_API_KEY")
    
    # API key validation with detailed error messages
    api_errors = []
    
    if not openai_api_key:
        api_errors.append("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
    
    if not serper_api_key:
        api_errors.append("SERPER_API_KEY not found in environment variables. Please check your .env file.")
    
    if api_errors:
        error_message = "\n".join(api_errors)
        error_message += "\n\nMake sure to create a .env file with your API keys in the project root directory."
        raise ValueError(error_message)
    
    # Set environment variables for the libraries to use
    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Check for model override in environment
    openai_model = os.getenv("OPENAI_MODEL_NAME", 'gpt-4o-mini')
    os.environ["OPENAI_MODEL_NAME"] = openai_model
    
    os.environ["SERPER_API_KEY"] = serper_api_key
    
    return {
        "OPENAI_API_KEY": openai_api_key,
        "SERPER_API_KEY": serper_api_key,
        "OPENAI_MODEL_NAME": openai_model
    }

# Get currently available OpenAI models for reference
AVAILABLE_OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo"
]

# Default user input parameters
DEFAULT_INPUTS = {
    'initial_capital': '100000',
    'risk_tolerance': 'Medium',
    'trading_strategy_preference': 'Long-term',
    'investment_timeframe': '3-5 years',
    'news_impact_consideration': True,
    'sector_preferences': 'Technology, Healthcare, Renewable Energy',
    'exclude_sectors': 'Tobacco, Gambling',
    'stock_selection': ''  # Empty default for portfolio mode
} 