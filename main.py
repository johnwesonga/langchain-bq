from google.cloud import bigquery
from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
import os
import getpass

from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.chains import create_sql_query_chain


from langchain_openai import ChatOpenAI
import openai

service_account_file = "/Users/johnwesonga/projects/python/langchain-bq/sixth-tribute-92520-f4722eaa8807.json" # Change to where your service account key file is located
project = "sixth-tribute-92520"
dataset = "test"
table = "vwSalesAnalysis"
sqlalchemy_url = f'bigquery://{project}/{dataset}?credentials_path={service_account_file}'
# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# Set up langchain
db = SQLDatabase.from_uri(sqlalchemy_url)
print(db.dialect)
print(db.get_usable_table_names())
db.run("SELECT * FROM `sixth-tribute-92520.test.vwSalesAnalysis` LIMIT 10;")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
#chain = create_sql_query_chain(llm, db)
#response = chain.invoke({"question": "How many shop_names are there?"})
#db.run(response)


toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
llm=llm,
toolkit=toolkit,
verbose=True,
top_k=1000,
)
# First query
# agent_executor.run("How many shop_names are there? ")
agent_executor.run("Give me a list of all the salesreps")
agent_executor.run("which salesrep has the highest sales_value?")



