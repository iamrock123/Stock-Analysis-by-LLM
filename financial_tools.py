import os
import requests
import json
from dotenv import load_dotenv, find_dotenv
from crewai import Agent, Task
from textwrap import dedent
from langchain.tools import tool

# Search tools for gathering company news and information
class SearchTools:

    @tool
    def searchInfo(query: str):
        """Search for relevant information on the web about the specified content."""
        return SearchTools.search(query)

    def search(query: str):
        load_dotenv(find_dotenv(), override=True)
        url = "https://google.serper.dev/news"

        payload = json.dumps({
            "q": query,
            "hl": "en"  # Set language to English
        })
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        results = response.json().get('news', [])

        string = []
        for result in results:
            try:
                string.append('\n'.join([
                    f"Title: {result['title']}",
                    f"Date: {result['date']}",
                    f"Source: {result['source']}",
                    f"Summary: {result['snippet']}", "\n-----------------"
                ]))
            except KeyError:
                continue

        content = '\n'.join(string)
        return f"\nSearch result: {content}\n"

# Class to define analysis agents
class AnalysisAgents:
    
    def __init__(self, llm):
        self.llm = llm

    # Market Research Analyst Agent
    def market_research_analyst(self):
        return Agent(
            llm=self.llm,
            role="Market Research Analyst",
            goal="Research the company's market position and financial status, and provide a comprehensive summary of its performance and financial health based on the gathered information.",
            backstory="An experienced market research analyst, highly skilled at uncovering the truth within a company’s internal workings. Please think and respond in English, whether addressing client queries or interacting with colleagues.",
            tools=[SearchTools().searchInfo],  # Use method from SearchTools instance
            allow_delegation=False,
            max_iter=3,
            verbose=True
        )
     
    # Chartered Financial Analyst (CFA) Agent
    def chartered_financial_analyst(self):
        return Agent(
            llm=self.llm,
            role="Chartered Financial Analyst (CFA)",
            goal="Analyze the information collected by the Market Research Analyst and provide a detailed summary of the company's status, along with recommendations on whether the company’s stock is worth buying.",
            backstory="A seasoned financial expert with a keen sense for market trends and stock performance. You are now advising the most important client in your career. Please think and respond in English, either to clients or when discussing matters with colleagues.",
            tools=[],  # No specific tools assigned
            allow_delegation=False,
            verbose=True
        )

# Class to define tasks for agents
class AnalysisTasks:
    
    def research(self, agent, company):
        return Task(
            description=dedent(
                f"""
                Conducting research and summarizing the latest updates and news about {company}.
                Focus on any significant recent events.
                """
            ),
            async_execution=True,  # Set to asynchronous execution
            agent=agent,
            expected_output=f"Summarize the top 5 most important {company} news items in list format."
        )
    
    def analysis(self, agent, context):
        return Task(
            description=dedent(
                """
                Analyze the gathered information and provide a summary.
                """
            ),
            agent=agent,
            context=[context],
            expected_output="Provide a detailed report summarizing the company's market position and trends, concluding with a recommendation on whether to buy the company's stock."
        )