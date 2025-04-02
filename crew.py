from crewai import Crew, Process
from langchain_openai import ChatOpenAI
import time
import os
import random
import datetime
from typing import List, Dict, Any, Optional, Callable

from agents import (
    data_analyst_agent,
    trading_strategy_agent,
    execution_agent,
    risk_management_agent,
    stock_selection_specialist,
    market_research_specialist
)

from tasks import (
    data_analysis_task,
    strategy_development_task,
    execution_planning_task,
    risk_assessment_task,
    market_research_task,
    stock_selection_task
)

from config import AVAILABLE_OPENAI_MODELS

# Define types for agent logs
AgentLogEntry = Dict[str, Any]

# Rate limit handling for API calls
def handle_rate_limits(func):
    """Decorator to handle rate limits with exponential backoff"""
    def wrapper(*args, **kwargs):
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                    retry_count += 1
                    wait_time = (2 ** retry_count) + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    raise  # Re-raise if it's not a rate limit error
        
        raise Exception("Maximum retry attempts reached for API rate limits")
    
    return wrapper

# Define a class to track agent logs
class AgentLogger:
    def __init__(self):
        self.logs: List[AgentLogEntry] = []
        self.callbacks: List[Callable[[AgentLogEntry], None]] = []
    
    def add_log(self, agent_name: str, action: str, details: Optional[str] = None):
        """Add a new log entry and notify all callbacks"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "agent": agent_name,
            "action": action,
            "details": details,
            "time": timestamp
        }
        self.logs.append(log_entry)
        
        # Notify all callbacks
        for callback in self.callbacks:
            callback(log_entry)
    
    def register_callback(self, callback: Callable[[AgentLogEntry], None]):
        """Register a callback to be notified on new log entries"""
        self.callbacks.append(callback)
    
    def get_logs(self) -> List[AgentLogEntry]:
        """Get all logs"""
        return self.logs

# Create a global logger instance
agent_logger = AgentLogger()

# Register a CrewAI callback to capture agent activities
def register_crew_callbacks(crew):
    """Register callbacks on the crew to capture agent activities"""
    
    # This would be replaced with actual CrewAI callback API when available
    # For now, we'll just add a way to manually log activities
    
    # Example manual logging during crew execution
    def on_agent_start(agent_name):
        agent_logger.add_log(agent_name, "Starting task")
    
    def on_agent_end(agent_name, output):
        agent_logger.add_log(agent_name, "Completed task", details=str(output)[:100] + "...")
    
    # Return functions that can be called during crew execution
    return {
        "on_agent_start": on_agent_start,
        "on_agent_end": on_agent_end
    }

# Define the crew with agents and tasks
def create_financial_trading_crew(mode='portfolio'):
    """
    Create and return the financial trading crew with all agents and tasks
    
    Args:
        mode (str): 'portfolio' for multi-stock recommendations or 'single' for single stock analysis
    """
    
    # Select appropriate model
    model_name = os.environ.get("OPENAI_MODEL_NAME", 'gpt-4o-mini')
    if model_name not in AVAILABLE_OPENAI_MODELS:
        print(f"Warning: {model_name} not in known model list. Defaulting to gpt-4o-mini.")
        model_name = 'gpt-4o-mini'
    
    # Create the right agent/task combination based on mode
    if mode == 'portfolio':
        agents = [
            market_research_specialist,
            stock_selection_specialist,
            trading_strategy_agent, 
            risk_management_agent
        ]
        
        tasks = [
            market_research_task,
            stock_selection_task,
            strategy_development_task, 
            risk_assessment_task
        ]
    else:  # single stock mode
        agents = [
            data_analyst_agent,
            trading_strategy_agent, 
            execution_agent, 
            risk_management_agent
        ]
        
        tasks = [
            data_analysis_task, 
            strategy_development_task, 
            execution_planning_task, 
            risk_assessment_task
        ]
    
    # Log agent setup
    for agent in agents:
        agent_logger.add_log(agent.role, "Agent initialized")
        
    # Create and return crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        manager_llm=ChatOpenAI(
            model=model_name, 
            temperature=0.7
        ),
        process=Process.hierarchical,
        verbose=True
    )
    
    # Register callbacks (would be implemented with CrewAI's official callback API)
    register_crew_callbacks(crew)
    
    return crew

@handle_rate_limits
def run_financial_analysis(inputs):
    """
    Run the financial analysis with the given inputs
    
    Args:
        inputs (dict): Dictionary containing user inputs
    
    Returns:
        CrewOutput: Result from the crew execution
    """
    
    # Determine analysis mode
    mode = 'single' if inputs.get('stock_selection') else 'portfolio'
    
    # Prepare the input parameters
    processed_inputs = {k: v for k, v in inputs.items()}
    
    # Set analysis_target based on mode
    if mode == 'single':
        processed_inputs['analysis_target'] = inputs['stock_selection']
    else:
        # For portfolio mode, set a descriptive target for the agents
        processed_inputs['analysis_target'] = "the selected market sectors"
    
    # Ensure all required fields have values
    required_fields = [
        'initial_capital', 
        'risk_tolerance', 
        'investment_timeframe',
        'trading_strategy_preference'
    ]
    
    for field in required_fields:
        if not processed_inputs.get(field):
            raise ValueError(f"Missing required parameter: {field}")
    
    # Log analysis start
    agent_logger.add_log("Crew Manager", f"Starting financial analysis in {mode} mode")
    
    # Create the crew for the appropriate mode
    financial_trading_crew = create_financial_trading_crew(mode)
    
    # Execute the crew with the processed inputs
    print(f"Starting financial analysis in {mode} mode...")
    
    # Log the analysis parameters
    agent_logger.add_log("Crew Manager", "Analysis parameters", 
                       details=f"Capital: {processed_inputs['initial_capital']}, Risk: {processed_inputs['risk_tolerance']}")
    
    # Execute the crew
    result = financial_trading_crew.kickoff(inputs=processed_inputs)
    
    # Log completion
    agent_logger.add_log("Crew Manager", "Analysis complete")
    
    return result

# Function to get the current agent logs
def get_agent_logs():
    """Get the current agent logs"""
    return agent_logger.get_logs()

# Function to register a callback for new log entries
def register_log_callback(callback):
    """Register a callback function to be called when new logs are added"""
    agent_logger.register_callback(callback) 