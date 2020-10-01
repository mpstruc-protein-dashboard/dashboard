import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
    

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def get_external_data_overview():
    url = 'https://www.rcsb.org/pdb/results/reportField.do'
    table = bs(requests.get(url).content, 'html.parser').table
    rows = table.find_all('tr')
    text_arr = [[cell.text for cell in row.findChildren(recursive=False)] for row in rows]
    text_df = pd.DataFrame(text_arr[1:], columns=text_arr[0])
    for index, row in text_df.iterrows():
        if row['Report Name'] == '\xa0':
            row['Report Name'] = text_df.iloc[index-1]['Report Name']

    return text_df


def get_enrichtment(protein_db, reports = [], fields = []):    
    '''
    Given a Table (@query_columns_df) this function will query
    the pdb for fields and reports which are specified by the
    given index parameters (@reports, @fields). The parameters
    are outputted by the respective widgets that let the user
    specify which reports or fields they want to see. 
    '''
    #TODO: ERROR HANDLING: IF REPORTS OR FIELDS ISNT A LIST THINGS WILL PROBABLY BREAK ###

    query_columns_df = get_external_data_overview()
    query_columns_reports = []
    query_columns_fields = []
    
    # gather all the field names from the specified reports   
    if reports is not None and reports != []:
        # the inputs should always be lists by default when they are output by the widgets.
        
        #init empty list
        query_columns = []
        
        # for each report the list will be filled with the names of the fields from the respective report.
        # this happens in "one big swoop". For example: Report 1 will append 10 items onto query_colums
        # Report 2 will append another 15 items onto query_colums. Query_columns will now have 2 lists,
        # each containing several items.
        for no in reports: 
            query_columns.append(query_columns_df.loc[query_columns_df.Report_Name == query_columns_df.Report_Name.unique()[no],'Field_Name'])
            
        # after going through each report and appending the names of each fields onto a list all Report-Fields are beeing concatinated into
        # one big list reporesenting the fieldnames from the reports.
        query_columns_reports = pd.concat(query_columns)
        
                
    # gather all the field names from the specified fields
    if fields is not None and fields != []: 
        # the inputs should always be lists by default when they are output by the widgets. 
        
        #init empty list
        query_columns = []
        
        # it is a little bit different for the fields as they come in one big list instead of reports that each contain fieldnames.
        # thats why there is only one iteration of appending lots of fields onto a list.
        for no in fields: 
            query_columns.append(query_columns_df.loc[query_columns_df.Field_Name == query_columns_df.Field_Name.unique()[no],'Field_Name'])
        
        # after iterating over all fields the fieldnames also get concatinated onto a list reporesenting the fieldnames from the fields.
        query_columns_fields = pd.concat(query_columns)
    
    # now there is the possibility for either reports or fields to be []. In this case things will break..
    # joining the field-names into one string
    vessel = pd.DataFrame(columns=['Field_Name'])
    vessel = vessel.append(pd.DataFrame(query_columns_fields))
    vessel = vessel.append(pd.DataFrame(query_columns_reports))
    query_columns = 'structureId,' + ','.join(vessel['Field_Name'].unique())
    
    
    ## the default if nothing is selected.
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
    pdbCodes_in_mptopo = ','.join(flatten(protein_db['pdbCode']))

    # those lists contain duplicates which are eliminated in this step
    unique_pdbCodes_in_mptopo = ','.join(set(flatten(protein_db['pdbCode'])))

    # Build the URL for the REST-API. This holds a strange behaviour with ;&amp and &. Somehow the & does not get converted and causes some error if not
    # handled with urllib.parse.urlparse.
    getURL = 'http://www.pdb.org/pdb/rest/customReport?pdbids={0} \
              &customReportColumns={1}&service=wsfile&format=csv' \
              .format(unique_pdbCodes_in_mptopo, query_columns)

    getURL = urllib.parse.urlparse(getURL)
    # the URL is beeing requested and returns a text (StringIO) which now easily can be understood by pandas and be written to a data frame. 
    string_from_url = requests.get(getURL.geturl()).text

    enrichment = pd.read_csv(StringIO(string_from_url))
    return enrichment

## Function takes in the "original Data" and merges is on the pdbCode with the data from the pdb database.
def merge_with_mpstruct(mpstruct_data, enrichment):
    return(mpstruct_data.merge(enrichment, left_on='pdbCode', right_on= 'structureId', how = 'left'))



if __name__ == "__main__":
    a = get_external_data_overview()
    # b = get_enrichtment([0],[])
    # print(b)