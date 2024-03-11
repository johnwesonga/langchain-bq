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

import openai


service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
project = os.getenv('GCP_PROJECT')
dataset = os.getenv("BQ_DATASET")
sqlalchemy_url = f'bigquery://{project}/{dataset}?credentials_path={service_account_file}'
# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# Set up langchain
db = SQLDatabase.from_uri(sqlalchemy_url)
print(db.dialect)
print(db.get_usable_table_names())

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
chain = create_sql_query_chain(llm, db)
chain.get_prompts()[0].pretty_print()
#response = chain.invoke({"question": "How many shop_names are there?"})
#db.run(response)


toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
llm=llm,
toolkit=toolkit,
verbose=True,
top_k=1000,
agent_type="openai-tools",
)
# First query
# agent_executor.run("How many shop_names are there? ")
agent_executor.invoke(
    "List the total sales value per sales rep."
)


