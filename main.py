## In this file the deployment of the dashboard should take place.
# import all_the_files

from retrieve_data import Database, get_dataframe
from external_data import get_external_data_overview, persist_external_data

if __name__ == "__main__":
    db = Database()
    db = get_dataframe(db)                 

    persist_external_data(protein_db=db, query_columns_df=get_external_data_overview())