from langchain_community.utilities import SQLDatabase

class Config(object):
    def __init__(self, service_account_file, project, dataset):
        self.service_account_file = service_account_file
        self.project = project
        self.dataset = dataset
        self.sqlalchemy_url = f'bigquery://{self.project}/{self.dataset}?credentials_path={self.service_account_file}'

    def get_connection(self):
       return SQLDatabase.from_uri(self.sqlalchemy_url)
     