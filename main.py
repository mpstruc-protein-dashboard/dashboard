# In this file the deployment of the dashboard should take place.
# import all_the_files

from database import MasterDatabase
from retrieve_data import Database, get_dataframe, get_timestamp, data_update
from external_data import get_external_data_overview, persist_external_data

if __name__ == "__main__":

    # run only when there is a change in the db.
    # because this could be way to often there should be
    # another control-mechanism such as
    # a weekly happening update or at a certain point
    # of time in the day (2:00 AM or so.)
    # or by choice in the frontend with an update DB button and
    # the info that it might take 5-10 minutes to update the server-data.
    data_update(get_timestamp())

    # this is the object the dashboard has to operate on data-wise.
    # it holds both the mpstruc aswell as all possible external data columns.
    full_data = MasterDatabase()
