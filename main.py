## In this file the deployment of the dashboard should take place.
# import all_the_files

from retrieve_data import Database, get_dataframe

if __name__ == "__main__":
    db = Database()
    get_dataframe(db)                                                                                         