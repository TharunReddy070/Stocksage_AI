from crewai import Task
from agents import (
    data_analyst_agent,
    trading_strategy_agent,
    execution_agent,
    risk_management_agent,
    stock_selection_specialist,
    market_research_specialist
)

# Task for Data Analyst Agent: Analyze Market Data
data_analysis_task = Task(
    description=(
        "Continuously monitor and analyze market data for "
        "{analysis_target}. "
        "Use statistical modeling and machine learning to "
        "identify trends and predict market movements."
    ),
    expected_output=(
        "Insights and alerts about significant market "
        "opportunities or threats for {analysis_target}."
    ),
    agent=data_analyst_agent,
)

# Task for Trading Strategy Agent: Develop Trading Strategies
strategy_development_task = Task(
    description=(
        "Develop and refine trading strategies based on "
        "the insights from the Data Analyst and "
        "user-defined risk tolerance ({risk_tolerance}). "
        "Consider trading preferences ({trading_strategy_preference})."
    ),
    expected_output=(
        "A set of potential trading strategies for {analysis_target} "
        "that align with the user's risk tolerance."
    ),
    agent=trading_strategy_agent,
)

# Task for Trade Advisor Agent: Plan Trade Execution
execution_planning_task = Task(
    description=(
        "Analyze approved trading strategies to determine the "
        "best execution methods for {analysis_target}, "
        "considering current market conditions and optimal pricing."
    ),
    expected_output=(
        "Detailed execution plans suggesting how and when to "
        "execute trades for {analysis_target}."
    ),
    agent=execution_agent,
)

# Task for Risk Advisor Agent: Assess Trading Risks
risk_assessment_task = Task(
    description=(
        "Evaluate the risks associated with the proposed trading "
        "strategies and execution plans for {analysis_target}. "
        "Provide a detailed analysis of potential risks "
        "and suggest mitigation strategies."
    ),
    expected_output=(
        "A comprehensive risk analysis report detailing potential "
        "risks and mitigation recommendations for {analysis_target}."
    ),
    agent=risk_management_agent,
)

# Market Research Task
market_research_task = Task(
    description=(
        "Conduct an exhaustive market analysis to identify compelling investment opportunities "
        "across all sectors that align with the investor's parameters ({initial_capital} capital, "
        "{investment_timeframe} time horizon, {risk_tolerance} risk tolerance). Your research should:\n\n"
        "1. Evaluate current market conditions and sector performance trends\n"
        "2. Identify sectors positioned for outperformance given the current economic cycle\n"
        "3. Uncover potential catalysts that could drive exceptional stock performance\n"
        "4. Detect emerging trends before they're fully reflected in market prices\n"
        "5. Analyze institutional money flows and smart money positioning\n"
        "6. Identify stocks with favorable risk/reward profiles matching investor parameters\n"
        "7. Evaluate potential market headwinds and tailwinds affecting different sectors\n"
        "8. Consider global macroeconomic factors that could influence investment performance"
    ),
    expected_output=(
        "A comprehensive market intelligence briefing containing:\n\n"
        "1. Detailed analysis of current market conditions and sector positioning\n"
        "2. Identification of high-potential sectors given the investor's time horizon\n"
        "3. List of 10-15 preliminary stock candidates with exceptional potential\n"
        "4. Analysis of key performance drivers for each candidate\n"
        "5. Assessment of each candidate's alignment with investor parameters\n"
        "6. Risk factors and market conditions that could impact performance\n"
        "7. Identification of optimal entry timing based on technical and fundamental factors"
    ),
    agent=market_research_specialist,
)

# Task for Stock Selection
stock_selection_task = Task(
    description=(
        "Conduct a comprehensive analysis of the global market to identify the ideal 3-5 stock recommendations "
        "perfectly calibrated to the investor's profile ({initial_capital} capital, {investment_timeframe} time horizon, "
        "{risk_tolerance} risk tolerance) and current market conditions. Your selection should consider:\n\n"
        "1. Fundamental strength and financial health metrics\n"
        "2. Technical indicators and price momentum patterns\n"
        "3. Industry position and competitive advantage sustainability\n"
        "4. Alignment with macroeconomic trends and sector rotations\n"
        "5. Valuation metrics relative to growth potential\n"
        "6. Liquidity considerations based on investment capital\n"
        "7. Historical performance through similar market conditions\n"
        "8. Management quality and capital allocation effectiveness\n\n"
        "Each recommendation must be justified with compelling evidence and tailored precisely to the investor's requirements."
    ),
    expected_output=(
        "A meticulously crafted investment portfolio recommendation containing:\n\n"
        "1. The optimal selection of 3-5 stocks with detailed rationale for each selection\n"
        "2. Comprehensive analysis of why each selection aligns with the investor's time horizon and risk profile\n"
        "3. Specific allocation percentages for optimal portfolio construction\n"
        "4. Entry strategy with ideal price points and timing considerations\n"
        "5. Expected performance metrics including projected returns and volatility measures\n"
        "6. Key risk factors specific to each recommendation and mitigation strategies\n"
        "7. Strategic holding timeline with milestone evaluation points"
    ),
    agent=stock_selection_specialist,
) 