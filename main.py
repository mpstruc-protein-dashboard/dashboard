## In this file the deployment of the dashboard should take place.
# import all_the_files

from retrieve_data import (
    Database,
    get_dataframe,
    convert_type
)

from external_data import *

if __name__ == "__main__":
    db = Database()
    protein_db = get_dataframe(db) 
    protein_db = convert_type(protein_db)                                                                               