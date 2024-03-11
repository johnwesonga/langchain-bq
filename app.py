from flask import Flask, render_template, request, jsonify
from flask_assets import Environment, Bundle

from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
import os
import json


#google imports
from google.cloud import bigquery

# LLM imports
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.chains import create_sql_query_chain
from langchain.chains.openai_tools import create_extraction_chain_pydantic
import openai

import dbconfig 
from table import Table

openai.api_key = os.getenv("OPENAI_API_KEY")

app= Flask(__name__)

assets = Environment(app)
css = Bundle('src/main.css',  output='dist/main.css')
js = Bundle("src/*.js", output="dist/main.js") # new

assets.register('css', css)
assets.register('js', js)

css.build()
js.build()

service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
project = os.getenv('GCP_PROJECT')
dataset = os.getenv("BQ_DATASET")

dataConf = dbconfig.Config(service_account_file,project, dataset)
db = dataConf.get_connection()
db.get_context()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

table_names = "\n".join(db.get_usable_table_names())
system = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
The tables are:

{table_names}

Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/llm/query', methods=['POST'])
def query():
    # Get the user's input from the form
    input = request.form.get('search')

    chain = create_extraction_chain_pydantic(Table, llm, system_message=system)
    #table_chain.invoke({"input": "What are all the genres of Alanis Morisette songs"})
    
    #chain = create_sql_query_chain(llm, db)
    chain.get_prompts()[0].pretty_print()
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_sql_agent(llm=llm,
                                      toolkit=toolkit,
                                      verbose=True,
                                      top_k=1000,
                                      agent_type="openai-tools",)
    # First query
    # agent_executor.run("How many shop_names are there? ")
    response = agent_executor.invoke({"input": input})
    #json_string = json.dumps(response, indent=4)
    
    return response['output']


if __name__ == '__main__':
	app.run(debug=True)