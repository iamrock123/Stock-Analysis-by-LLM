import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from crewai import Crew, Process
from financial_tools import AnalysisAgents, AnalysisTasks  # Import the new module
import streamlit as st

# Load environment variables
load_dotenv(find_dotenv(), override=True)

# Initialize LLM with OpenAI API
llm = ChatOpenAI(
    openai_api_base=os.environ['CHATGPT_API_ENDPOINT'],
    openai_api_key=os.environ['OPENAI_API_KEY'],
    model="gpt-4o-mini"
)

class FinancialCrew:

    def __init__(self, company: str):
        self.company = company

    def run(self):
        agents = AnalysisAgents(llm)  # Create agents
        tasks = AnalysisTasks()       # Create tasks

        mr_analyst = agents.market_research_analyst()
        cfa = agents.chartered_financial_analyst()

        research = tasks.research(mr_analyst, self.company)
        analysis = tasks.analysis(cfa, research)

        crew = Crew(
            agents=[mr_analyst, cfa],
            tasks=[research, analysis],
            process=Process.sequential,  # Execute sequentially
            verbose=True
        )

        result = crew.kickoff()  # Start the process

        return result

# Main execution with Streamlit
st.title("Investment Advisory Team")

st.write("Please enter the name of the company you want to analyze to get a professional financial analysis.")

# Input form for company name
company = st.text_input("Company Name", placeholder="e.g., NVIDIA")

# Button to start the analysis
if st.button("Start Analysis"):
    if company:
        st.write(f"Analyzing company: {company}...")

        # Instantiate the financial crew and run the process
        financial_crew = FinancialCrew(company)
        result = financial_crew.run()
        
        # Display the analysis result
        st.write("## Analysis Result")
        st.write(result)
    else:
        st.write("Please enter a company name first.")
