# StockSage AI

A sophisticated AI-powered financial analysis system that uses collaborative multi-agent architecture to analyze investments, generate trading strategies, and provide stock recommendations.

## 🌟 Features

- **Investment Portfolio Recommendations**: Get personalized stock recommendations based on your financial profile, time horizon, and risk tolerance
- **Market Research & Analysis**: Comprehensive market research across sectors to identify investment opportunities
- **Trading Strategy Development**: Generate detailed trading strategies for specific stocks
- **Risk Assessment**: Evaluate risks of proposed strategies with detailed mitigation recommendations
- **Execution Planning**: Receive detailed guidance on how and when to execute trades
- **Real-time Agent Activity**: Watch AI agents work in real-time as they analyze and develop recommendations

## 🏗️ Architecture

This application uses a modular multi-agent system architecture:

### Agents

- **Data Analyst**: Monitors and analyzes market data to identify trends and make predictions
- **Trading Strategy Developer**: Creates trading strategies based on market analysis
- **Trade Advisor**: Suggests optimal execution methods for trading strategies
- **Risk Advisor**: Evaluates and provides insights on potential risks
- **Investment Portfolio Curator**: Identifies and recommends an optimal selection of stocks
- **Market Opportunity Scout**: Uncovers hidden opportunities and emerging trends across markets

### System Components

- **config.py**: Manages environment variables and default configurations
- **agents.py**: Defines all agent roles, goals, and backstories
- **tasks.py**: Contains task definitions for each agent
- **crew.py**: Orchestrates agent collaboration and task execution with real-time logging
- **main.py**: Main entry point with command-line interface
- **streamlit_app.py**: Interactive web interface with visualizations and real-time agent logs

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- SerperDev API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stocksage-ai.git
   cd stocksage-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   OPENAI_MODEL_NAME=gpt-4o  # Optional, defaults to gpt-4o-mini
   ```

### Usage

#### Web Interface

Launch the Streamlit app for an interactive experience:

```bash
streamlit run streamlit_app.py
```

The web interface allows you to:
- Select between portfolio recommendations or single stock analysis
- Set your investment parameters and preferences
- Watch AI agents work in real-time
- View interactive charts and visualizations
- Download analysis reports in markdown or text format

#### Command Line

Run the analysis with default parameters:

```bash
python main.py
```

Customize the analysis with command-line arguments:

```bash
python main.py --capital 50000 --risk High --timeframe "1-2 years" --sectors "Technology, AI, Semiconductors" --strategy "Growth" --output "my_analysis.md"
```

#### Command Line Options

- `--capital`: Initial investment capital (e.g., "50000")
- `--risk`: Risk tolerance (Low, Medium, High)
- `--timeframe`: Investment timeframe (e.g., "1-2 years", "5+ years")
- `--strategy`: Trading strategy preference (e.g., "Day Trading", "Long-term")
- `--sectors`: Preferred sectors (comma separated)
- `--exclude`: Sectors to exclude (comma separated)
- `--stock`: Specific stock to analyze (for single stock analysis)
- `--output`: Output file for analysis results (default: analysis_result.txt)

## 📊 Sample Output

The system will generate a comprehensive analysis that includes:

- **Market Intelligence Briefing**: Current market conditions and sector performance trends
- **Stock Recommendations**: 3-5 stocks with detailed rationale and allocation percentages
- **Entry Strategies**: Ideal price points and timing considerations
- **Performance Projections**: Expected returns and volatility metrics
- **Risk Analysis**: Key risk factors and mitigation strategies
- **Strategic Timeline**: Holding timeline with milestone evaluation points

## 🔒 Security Note

- Never commit your `.env` file or API keys to version control
- Add `.env` to your `.gitignore` file
- Keep your API keys secure
- When deploying to Streamlit Cloud, use their secrets management system

## 🛠️ Development

### Project Structure

```
stocksage-ai/
├── .env                  # Environment variables (not in repo)
├── README.md             # Project documentation
├── requirements.txt      # Required packages
├── main.py               # Main entry point
├── streamlit_app.py      # Streamlit web interface
├── config.py             # Configuration and environment setup
├── agents.py             # Agent definitions
├── tasks.py              # Task definitions
└── crew.py               # Crew orchestration with logging
```

### Adding New Agents

To add a new agent, modify `agents.py` with a new Agent definition following the existing pattern.

### Adding New Tasks

To add a new task, modify `tasks.py` with a new Task definition and associate it with an agent.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI)
- Powered by OpenAI's GPT models
- Market data from SerperDev API
- Interactive UI with Streamlit 