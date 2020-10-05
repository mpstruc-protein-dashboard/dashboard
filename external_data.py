import requests
import urllib
import pandas as pd
from bs4 import BeautifulSoup as bs

from pandas.core.common import flatten
from io import StringIO

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def get_external_data_overview():
    url = 'https://www.rcsb.org/pdb/results/reportField.do'
    table = bs(requests.get(url).content, 'html.parser').table
    rows = table.find_all('tr')
    field_arr = [[cell.text for cell in row.findChildren(recursive=False)] for row in rows]
    query_columns_df = pd.DataFrame(field_arr[1:], columns=['report_name', 'field_name', 'item_name'])
    for index, row in query_columns_df.iterrows():
        if row['report_name'] == '\xa0':
            row['report_name'] = query_columns_df.iloc[index-1]['report_name']

    query_columns_df.to_pickle("./Database/External/query_columns_df.pkl")
    return query_columns_df


def get_enrichment(protein_db, query_columns_df, reports = [], fields = []):    
    '''
    Given a Table (@query_columns_df) this function will query
    the pdb for fields and reports which are specified by the
    given index parameters (@reports, @fields). The parameters
    are outputted by the respective widgets that let the user
    specify which reports or fields they want to see. 
    '''
    #TODO: ERROR HANDLING: IF REPORTS OR FIELDS ISNT A LIST THINGS WILL PROBABLY BREAK ###
    query_columns_reports = []
    query_columns_fields = []
    
    # gather all the field names from the specified reports   
    if reports:
        # the inputs should always be lists by default when they are output by the widgets.
        
        #init empty list
        query_columns = []
        
        # for each report the list will be filled with the names of the fields from the respective report.
        # this happens in "one big swoop". For example: Report 1 will append 10 items onto query_colums
        # Report 2 will append another 15 items onto query_colums. Query_columns will now have 2 lists,
        # each containing several items.
        for no in reports:
            query_columns.append(
                query_columns_df.loc[
                    query_columns_df.report_name == query_columns_df.report_name.unique()[no],
                    'field_name'
                ]
            )
            
        # after going through each report and appending the names of each fields onto a list all Report-Fields are beeing concatinated into
        # one big list reporesenting the fieldnames from the reports.
        query_columns_reports = pd.concat(query_columns)
        
                
    # # gather all the field names from the specified fields
    if fields is not None and fields != []: 
        # the inputs should always be lists by default when they are output by the widgets. 
        
        #init empty list
        query_columns = []
        
        # it is a little bit different for the fields as they come in one big list instead of reports that each contain fieldnames.
        # thats why there is only one iteration of appending lots of fields onto a list.
        for no in fields: 
            query_columns.append(query_columns_df.loc[query_columns_df.field_name == query_columns_df.field_name.unique()[no],'field_name'])
        
        # after iterating over all fields the fieldnames also get concatinated onto a list reporesenting the fieldnames from the fields.
        query_columns_fields = pd.concat(query_columns)
    
    # now there is the possibility for either reports or fields to be []. In this case things will break..
    # joining the field-names into one string
    vessel = pd.DataFrame(columns=['field_name'])
    vessel = vessel.append(pd.DataFrame(query_columns_fields))
    vessel = vessel.append(pd.DataFrame(query_columns_reports))
    query_columns = 'structureId,' + ','.join(vessel['field_name'].unique())
    
    
    # ## the default if nothing is selected.
    if query_columns == 'structureId,': 
        query_columns = 'structureId,structureTitle,resolution'
    
    ###### The query_columns are now specified. In the next section of the function
    ###### the actual connection to the pdb is going to happen.

    # for this the RESTFUL API is beeing utilized. A simple HTML request per specific URL
    # is beeing done to query for certain data the URL contains the PDB codes as well as
    # the columns in question aswell as the type of the report, which is by default csv so
    # it can be easily read and understood by pandas.  

    # extract the pdb codes from mptopo:
    
    # there are some 'lists' in the Data that we need to get rid of first
    # (this might be not needed after all but it works, still.)
    pdbCodes_in_mptopo = ','.join(flatten(protein_db['pdb_code']))

    # # those lists contain duplicates which are eliminated in this step
    unique_pdbCodes_in_mptopo = ','.join(set(flatten(protein_db['pdb_code'])))

    # # Build the URL for the REST-API. This holds a strange behaviour with ;&amp and &. Somehow the & does not get converted and causes some error if not
    # # handled with urllib.parse.urlparse.
    getURL = 'http://www.pdb.org/pdb/rest/customReport?pdbids={0} \
              &customReportColumns={1}&service=wsfile&format=csv' \
              .format(unique_pdbCodes_in_mptopo, query_columns)

    getURL = urllib.parse.urlparse(getURL)
    # # the URL is beeing requested and returns a text (StringIO) which now easily can be understood by pandas and be written to a data frame. 
    string_from_url = requests.get(getURL.geturl()).text

    enrichment = pd.read_csv(StringIO(string_from_url))
    enrichment.rename(columns={'structureId': 'pdb_code'}, inplace=True)
    return enrichment

## Function takes in the "original Data" and merges is on the pdbCode with the data from the pdb database.

# the third thing is making the external data persistent locally ..
# persist the external data locally.

def persist_external_data(protein_db, query_columns_df):
    for field in range(0,len(query_columns_df.field_name.unique())):
        res = get_enrichment(protein_db, query_columns_df, None, [field])
        if res.columns[0] == 'pdb_code':
            res.to_pickle(("./Database/External/{0}.pkl").format(query_columns_df.field_name.unique()[field]))


# but in the project folder there needs to be the folder structure for this to work so you probably have to make 2 new folders in the project root, database and external.