#!/usr/bin/env python3
"""
Financial Analysis Agent - Main Entry Point
-------------------------------------------
This script is the main entry point for the Financial Analysis Agent application.
It orchestrates the execution of the financial analysis crew with user inputs.
"""

import warnings
import argparse
import json
import sys
from pprint import pprint

# Suppress warnings
warnings.filterwarnings('ignore')

# Import modules
from config import load_environment, DEFAULT_INPUTS
from crew import run_financial_analysis

def parse_arguments():
    """Parse command line arguments for customizing the analysis"""
    parser = argparse.ArgumentParser(description='Financial Analysis Agent')
    
    parser.add_argument('--capital', type=str, help='Initial investment capital')
    parser.add_argument('--risk', type=str, choices=['Low', 'Medium', 'High'], 
                        help='Risk tolerance (Low, Medium, High)')
    parser.add_argument('--timeframe', type=str, help='Investment timeframe (e.g., "1-2 years", "5+ years")')
    parser.add_argument('--strategy', type=str, help='Trading strategy preference')
    parser.add_argument('--sectors', type=str, help='Preferred sectors (comma separated)')
    parser.add_argument('--exclude', type=str, help='Sectors to exclude (comma separated)')
    parser.add_argument('--stock', type=str, help='Specific stock to analyze (for single stock analysis)')
    parser.add_argument('--output', type=str, help='Output file for analysis results (default: analysis_result.txt)')
    
    return parser.parse_args()

def prepare_inputs(args):
    """Prepare inputs by merging command line arguments with defaults"""
    inputs = DEFAULT_INPUTS.copy()
    
    # Update inputs with command line arguments if provided
    if args.capital:
        inputs['initial_capital'] = args.capital
    
    if args.risk:
        inputs['risk_tolerance'] = args.risk
    
    if args.timeframe:
        inputs['investment_timeframe'] = args.timeframe
    
    if args.strategy:
        inputs['trading_strategy_preference'] = args.strategy
    
    if args.sectors:
        inputs['sector_preferences'] = args.sectors
    
    if args.exclude:
        inputs['exclude_sectors'] = args.exclude
    
    if args.stock:
        inputs['stock_selection'] = args.stock
    
    return inputs

def main():
    """Main function to run the financial analysis"""
    
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Load environment variables
        env_vars = load_environment()
        print(f"Environment loaded. Using {env_vars['OPENAI_MODEL_NAME']} model.")
        
        # Prepare inputs
        inputs = prepare_inputs(args)
        
        print("\n=== Starting Financial Analysis ===")
        print("Input Parameters:")
        pprint(inputs)
        print("\nAnalysis in progress... (this may take several minutes)")
        
        # Determine analysis mode
        analysis_mode = "Single Stock" if inputs.get('stock_selection') else "Portfolio"
        print(f"Analysis Mode: {analysis_mode}")
        
        # Run the financial analysis
        result = run_financial_analysis(inputs)
        
        if not result or not hasattr(result, 'raw'):
            print("\nError: Analysis returned invalid results.")
            sys.exit(1)
        
        # Print the result
        print("\n=== ANALYSIS RESULT ===\n")
        print(result.raw)
        
        # Determine output file
        output_file = args.output if args.output else 'analysis_result.txt'
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write(result.raw)
        print(f"\nAnalysis saved to '{output_file}'")
        
        return result
    
    except ValueError as e:
        print(f"\nInput Error: {str(e)}")
        print("\nPlease check your parameters and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        if "rate limit" in str(e).lower():
            print("\nAPI rate limit hit. Please wait a few minutes before trying again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 