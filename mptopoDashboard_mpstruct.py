#!/usr/bin/env python
# coding: utf-8

# In[1]:


## required library imports

import altair as alt
import pandas as pd 

## pandas options

pd.options.display.max_columns = 60
pd.options.display.min_rows = 20


# In[2]:


import requests
import urllib
from urllib.request import urlopen
import xml.etree.ElementTree as etree
from lxml import etree as lxml_etree

## load the XML files per URL to stay up-to-date when changes occur.

all_data = "https://blanco.biomol.uci.edu/mpstruc/listAll/mpstrucTblXml" ## weekly + diff()-Bash 

try:
    response = requests.get(all_data)
    treeFile = etree.fromstring(response.content)
except:
    traceback.print_exc()
    print('Cell[2]: Tree coulnd\'t be build, is the Website/Database online?\nCheck https://blanco.biomol.uci.edu/mptopo/mptopoTblXml')


# In[3]:


import xmltodict
import json
import os.path

try:
    data_dict = xmltodict.parse(etree.tostring(treeFile),process_namespaces=True)

    json_data = json.dumps(data_dict)

    with open("./Database/JSON/mpstruc.json", "w") as json_file:
            json_file.write(json_data)
    json_file.close()
except:
    traceback.print_exc()
    print('Cell[3]: json couldnt be written to the db-file.')
    


# In[4]:


# Opening JSON file 
f = open('./Database/JSON/mpstruc.json') 
data = json.load(f)
f.close() 


# In[5]:


from pandas import json_normalize
import math
import numpy as np

data2 = json_normalize(data['mpstruc'])
editDate_new = data2['@lastDatabaseEditDate']

## run import only if Database has changed.
## for now never run import.
run_import = False

# if editDate_new != editDate_old
#     editDate_old = editDate_new
#     run_import = True


# In[6]:


## testing json_normalize() function: 
# current_db = json_normalize(json_normalize(data2['groups.group'][0])['subgroups.subgroup'][0], max_level= 0)
# current_protein_group  = json_normalize(json_normalize(current_db['proteins'], max_level= 0)['protein'][0], max_level= 0)
# json_normalize(current_protein_group['memberProteins'], max_level = 0)
# json_normalize(current_protein_group['memberProteins.memberProtein'][0])
# json_normalize(current_protein_group['bibliography'].iloc[0])


# In[7]:


full_db = []
member_protein_db = []
biblio_entry_db = []
counter = 1
family_counter = 1
## 3 DB Types




if run_import:
    # i iterates over DB the 3 types - Monotopic, Transmembrane Beta and Transmembrane Alpha
    for i in range(0,json_normalize(data2['groups.group'][0]).shape[0]):

        # selects a certain DB, 1: Mono, 2: Transm. Beta, 3: Transm. Alpha
        current_db = json_normalize(json_normalize(data2['groups.group'][0])['subgroups.subgroup'][i], max_level= 0)

        ## j iterates over the number of rows in the current database schema.
        for j in range(0, current_db.shape[0]):
            family_counter = family_counter+1

            ## there are two ways: either a family has multiple protein entries. in this case the list needs to be iterated over to get all entries
            ## for the second case there is only one entry in the family. in this scenario the fields are beeing filled 
            try:
                current_protein_group  = json_normalize(json_normalize(current_db['proteins'], max_level= 0)['protein'][j], max_level= 0)
                ## each j-th row depicts a family of proteins, which in the next forloop
                ## are beeing iterated over.
                ## certain proteins within a family 
                current_protein_group.insert(loc= 0, column = 'db_type', value = json_normalize(data2['groups.group'][0]).name[i])
                current_protein_group.insert(loc= 1, column = 'protein_group_name', value = current_db.name[j])
                full_db.append(current_protein_group)

                ### within the proteins there are member-proteins. at this point they get extracted into their own database, which
                ### can be merged together with the "main" database on the given "toplevel" Keys if needed.

                try:
                    for k in range(0, current_protein_group.shape[0]):
                        try:
                            member_protein_entry = json_normalize(json_normalize(current_protein_group['memberProteins'].iloc[k], max_level = 0)['memberProtein'].iloc[0], max_level = 0)
                            member_protein_entry.insert(loc= 0, column = 'db_type', value = json_normalize(data2['groups.group'][0]).name[i])
                            member_protein_entry.insert(loc= 1, column = 'protein_group_name', value = current_db.name[j])
                            member_protein_entry.insert(loc= 2, column = 'toplevel_protein', value = current_protein_group.name[k])
                            member_protein_entry.insert(loc= 3, column = 'toplevel_pdbCode', value = current_protein_group.pdbCode[k])
                            member_protein_entry.insert(loc= 4, column = 'toplevel_species', value = current_protein_group.species[k])
                            member_protein_db.append(member_protein_entry)
                        except:
                            0 # has no member-protein-entry
                        # same for bibliography entries:
                        try:
                            biblio_entry = json_normalize(current_protein_group['bibliography'].iloc[k])
                            biblio_entry.insert(loc= 0, column = 'db_type', value = json_normalize(data2['groups.group'][0]).name[i])
                            biblio_entry.insert(loc= 1, column = 'protein_group_name', value = current_db.name[j])
                            biblio_entry.insert(loc= 2, column = 'toplevel_protein', value = current_protein_group.name[k])
                            biblio_entry.insert(loc= 3, column = 'toplevel_pdbCode', value = current_protein_group.pdbCode[k])
                            biblio_entry.insert(loc= 4, column = 'toplevel_species', value = current_protein_group.species[k])
                            biblio_entry_db.append(biblio_entry)
                        except:
                            0 # no bib entry
                except:
                    print('this should not occur! Since every entry in the database holds a protein-family there should always be information about their proteins.')
            except:
                0
    full_db = pd.concat(full_db)
    biblio_entry_db = pd.concat(biblio_entry_db)
    member_protein_db = pd.concat(member_protein_db)
    
    
    ## export to pickle 
    try:
        full_db.to_pickle("./Database/pickleDB/full_db.pkl")
        biblio_entry_db.to_pickle("./Database/pickleDB/biblio_entry_db.pkl")
        member_protein_db.to_pickle("./Database/pickleDB/member_protein_db.pkl")

    except:
        traceback.print_exc()
        print('Cell[3]: data base files couldnt be written to the pickle-file directory.')


# In[8]:


if not run_import:
    full_db = pd.read_pickle("./Database/pickleDB/full_db.pkl")
    biblio_entry_db = pd.read_pickle("./Database/pickleDB/biblio_entry_db.pkl")
    member_protein_db = pd.read_pickle("./Database/pickleDB/member_protein_db.pkl")


# In[9]:


# omit empty columns:

db_list = [full_db, biblio_entry_db, member_protein_db]

for elem in db_list:

    # first: check if every entry in a column is NaN, none or NA
    dropouts = pd.DataFrame(data={ 'dropouts': elem.isnull().sum().index[elem.isnull().sum() == elem.shape[0]]}, dtype = str)
    
    if dropouts.shape != (0,1):
        print('Carefull, empty columns detected')
    else: 
        print('No complete empty columns detected')
    
    # drop the empty columns
    elem.drop(inplace = True,
              labels = dropouts['dropouts'].tolist(),
              axis = 1)
    
    elem.reset_index(inplace=True, drop= True)
    
    # get the parent_pdb ids to be able to join the original data upon the parent key.
    print(elem.isnull().sum())


# In[10]:


## which ones are missing ? should i be correcting them - in theroy not because the db should be updateable.


# In[11]:


biblio_entry_db.head(2)


# In[13]:


# Huge merge over all 3 Databases. This is most likely an unneccessary step but might give insight in some structure of the given data.

db_with_biblio = full_db.merge(biblio_entry_db,
                               how = 'left',
                               left_on = ['db_type', 'protein_group_name', 'name', 'pdbCode', 'species'],
                               right_on = ['db_type', 'protein_group_name', 'toplevel_protein', 'toplevel_pdbCode', 'toplevel_species'])

## omit duplicate comlumns.
db_with_biblio.drop(inplace = True,
                        labels = ['toplevel_protein', 'toplevel_pdbCode', 'toplevel_species'],
                        axis = 1)


complete_db = db_with_biblio.merge(member_protein_db,
                                  how = 'left', 
                                  left_on = ['db_type', 'protein_group_name', 'name', 'pdbCode', 'species'],
                                  right_on = ['db_type', 'protein_group_name', 'toplevel_protein', 'toplevel_pdbCode', 'toplevel_species'],
                                  suffixes=('_parent_proetin', '_member_protein'))

complete_db.drop(inplace = True,
                        labels = ['toplevel_protein', 'toplevel_pdbCode', 'toplevel_species'],
                        axis = 1)
complete_db.head(2)


# In[ ]:


db_with_biblio.dtypes

protein_db = db_with_biblio.convert_dtypes()
protein_db['NMR'] = protein_db['resolution'].str.contains('NMR')
protein_db['resolution'] = pd.to_numeric(protein_db['resolution'], errors='coerce')
protein_db['db_type'] = protein_db['db_type'].astype('category')
protein_db['protein_group_name'] = protein_db['protein_group_name'].astype('category')
protein_db['taxonomicDomain'] = protein_db['taxonomicDomain'].astype('category')
protein_db['species'] = protein_db['species'].astype('category')
protein_db['expressedInSpecies'] = protein_db['expressedInSpecies'].astype('category')
protein_db['year'] = protein_db['year'].astype('category')

protein_db.dtypes


# In[15]:


## EXTERNAL DATA ENRICHMENT :: PDB DATABASE :: ##

# 1. get all possible "columns" for data enrichment from pdb.
# Method: https://towardsdatascience.com/web-scraping-html-tables-with-python-c9baba21059

import external_data

external_data.get_external_data_overview()

# In[16]:



## query by report category.. there are 22 different reports that can be accessed in the PDB database. they sometimes do not work combined therefore they are beeing accessed "one by one"
report_no = 0
query_columns = query_columns_df.loc[query_columns_df.Report_Name == query_columns_df.Report_Name.unique()[report_no],'Field_Name']

query_columns = ','.join(query_columns)

query_columns =  'structureId,' + query_columns

print(query_columns)
#https://www.youtube.com/watch?v=NXwP8pSOiB8


# In[17]:

# only for testing
# from pandas.core.common import flatten
# from io import StringIO

# import urllib

# # protein_info_db: Subsetting for the PDB ids to look up further information such as resolution and releaseDate to "validate" and/or double-check the entries in mptopo

# # for this the RESTFUL API is beeing utilized. A simple HTML request per specific URL is beeing done to query for certain data
# # the URL contains the PDB codes as well as the columns in question aswell as the type of the report, which is by default csv so it can be easily read and understood by pandas.  

# # extract the pdb codes from mptopo:

# # there are some 'lists' in the Data that we need to get rid of first
# pdbCodes_in_mptopo = ','.join(flatten(protein_db['pdbCode']))

# # those lists contain duplicates which are eliminated in this step
# unique_pdbCodes_in_mptopo = ','.join(set(flatten(protein_db['pdbCode'])))

# # Build the URL for the REST-API. This holds a strange behaviour with ;&amp and &. Somehow the & does not get converted and causes some error if not
# # handled with urllib.parse.urlparse.
# getURL = 'http://www.pdb.org/pdb/rest/customReport?pdbids={0}'         '&customReportColumns={1}'         '&service=wsfile&format=csv'.format(unique_pdbCodes_in_mptopo,
#                                              query_columns)
# getURL = urllib.parse.urlparse(getURL)
# # the URL is beeing requested and returns a text (StringIO) which now easily can be understood by pandas and be written to a data frame. 
# string_from_url = requests.get(getURL.geturl()).text

# enrichment = pd.read_csv(StringIO(string_from_url))
# enrichment
# ## the enrichment data can now be merged onto the existing mptopo data

# protein_info_db = protein_db.merge(enrichment, left_on='pdbCode', right_on= 'structureId', how = 'left')
# protein_info_db.columns


# In[18]:

# ### only for testing
# query_columns_df.loc[query_columns_df.Report_Name == query_columns_df.Report_Name.unique()[0],'Field_Name']
# report_no = [1,2,5]

# if type(report_no) is list:
#     query_columns_list = []
#     for no in report_no: 
#         query_columns_list.append(query_columns_df.loc[query_columns_df.Report_Name == query_columns_df.Report_Name.unique()[no],'Field_Name'])
# pd.concat(query_columns_list)


# In[19]:


# def get_enrichtment(reports = [], fields = [], query_columns_df = query_columns_df):
    
#     from pandas.core.common import flatten
#     from io import StringIO
#     import urllib
    
#     '''
#     Given a Table (@query_columns_df) this function will query
#     the pdb for fields and reports which are specified by the
#     given index parameters (@reports, @fields). The parameters
#     are outputted by the respective widgets that let the user
#     specify which reports or fields they want to see. 
#     '''
#     #TODO: ERROR HANDLING: IF REPORTS OR FIELDS ISNT A LIST THINGS WILL PROBABLY BREAK ###

    
#     query_columns_reports = []
#     query_columns_fields = []
    
#     # gather all the field names from the specified reports   
#     if reports is not None and reports != []:
#         # the inputs should always be lists by default when they are output by the widgets.
        
#         #init empty list
#         query_columns = []
        
#         # for each report the list will be filled with the names of the fields from the respective report.
#         # this happens in "one big swoop". For example: Report 1 will append 10 items onto query_colums
#         # Report 2 will append another 15 items onto query_colums. Query_columns will now have 2 lists,
#         # each containing several items.
#         for no in reports: 
#             query_columns.append(query_columns_df.loc[query_columns_df.Report_Name == query_columns_df.Report_Name.unique()[no],'Field_Name'])
            
#         # after going through each report and appending the names of each fields onto a list all Report-Fields are beeing concatinated into
#         # one big list reporesenting the fieldnames from the reports.
#         query_columns_reports = pd.concat(query_columns)
        
                
#     # gather all the field names from the specified fields
#     if fields is not None and fields != []: 
#         # the inputs should always be lists by default when they are output by the widgets. 
        
#         #init empty list
#         query_columns = []
        
#         # it is a little bit different for the fields as they come in one big list instead of reports that each contain fieldnames.
#         # thats why there is only one iteration of appending lots of fields onto a list.
#         for no in fields: 
#             query_columns.append(query_columns_df.loc[query_columns_df.Field_Name == query_columns_df.Field_Name.unique()[no],'Field_Name'])
        
#         # after iterating over all fields the fieldnames also get concatinated onto a list reporesenting the fieldnames from the fields.
#         query_columns_fields = pd.concat(query_columns)
    
#     # now there is the possibility for either reports or fields to be []. In this case things will break..
#     # joining the field-names into one string
#     vessel = pd.DataFrame(columns=['Field_Name'])
#     vessel = vessel.append(pd.DataFrame(query_columns_fields))
#     vessel = vessel.append(pd.DataFrame(query_columns_reports))
#     query_columns = 'structureId,' + ','.join(vessel['Field_Name'].unique())
    
    
#     ## the default if nothing is selected.
#     if query_columns == 'structureId,': 
#         query_columns = 'structureId,structureTitle,resolution'
    
#     ###### The query_columns are now specified. In the next section of the function
#     ###### the actual connection to the pdb is going to happen.

#     # for this the RESTFUL API is beeing utilized. A simple HTML request per specific URL
#     # is beeing done to query for certain data the URL contains the PDB codes as well as
#     # the columns in question aswell as the type of the report, which is by default csv so
#     # it can be easily read and understood by pandas.  

#     # extract the pdb codes from mptopo:
    
#     # there are some 'lists' in the Data that we need to get rid of first
#     # (this might be not needed after all but it works, still.)
#     pdbCodes_in_mptopo = ','.join(flatten(protein_db['pdbCode']))

#     # those lists contain duplicates which are eliminated in this step
#     unique_pdbCodes_in_mptopo = ','.join(set(flatten(protein_db['pdbCode'])))

#     # Build the URL for the REST-API. This holds a strange behaviour with ;&amp and &. Somehow the & does not get converted and causes some error if not
#     # handled with urllib.parse.urlparse.
#     getURL = 'http://www.pdb.org/pdb/rest/customReport?pdbids={0}'             '&customReportColumns={1}'             '&service=wsfile&format=csv'.format(unique_pdbCodes_in_mptopo,
#                                                  query_columns)
#     getURL = urllib.parse.urlparse(getURL)
#     # the URL is beeing requested and returns a text (StringIO) which now easily can be understood by pandas and be written to a data frame. 
#     string_from_url = requests.get(getURL.geturl()).text

#     enrichment = pd.read_csv(StringIO(string_from_url))
#     return enrichment


# In[20]:


## Function takes in the "original Data" and merges is on the pdbCode with the data from the pdb database.
def merge_with_mpstruct(mpstruct_data, enrichment):
    return(mpstruct_data.merge(enrichment, left_on='pdbCode', right_on= 'structureId', how = 'left'))


# In[21]:


def to_neat_data_table(dt):
    html = dt.to_html(classes=['example', 'panel-df'])
    return pn.pane.HTML(html+script, sizing_mode='stretch_width').servable()


# In[22]:


### DASHBOARD ###


# In[23]:


import panel as pn
import numpy as np
import param


# In[24]:


pn.extension('vega')


# In[25]:


# # ALTERNATIVE DATA TABLE, looks more neat but right now more clumpy because of non existing formatting.
# import panel as pn
# import numpy as np
# import param

# css = ['https://cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css']

# js = {
#     '$': 'https://code.jquery.com/jquery-3.4.1.slim.min.js',
#     'DataTable': 'https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js'
# }

# pn.extension()


# script = """
# <script>
# if (document.readyState === "complete") {
#   $('.example').DataTable();
# } else {
#   $(document).ready(function () {
#     $('.example').DataTable();
#   })
# }
# </script>
# """

# pn.extension('vega', css_files=css, js_files=js)


# In[ ]:





# In[26]:


class External_Data(param.Parameterized):
    external_data = param.DataFrame(default=None)
    
test = External_Data()
test.external_data = get_enrichtment(None,None, query_columns_df = query_columns_df).head(15)


report_number = pn.widgets.MultiChoice(
    name='Reports', options=list(query_columns_df.Report_Name.unique()),value = [None], width=600
)

field_number = pn.widgets.MultiChoice(
    name='Fields', options=list(query_columns_df.Field_Name.unique()),value = [None], width=600
)

# neat idea would be to have some kind of cross selection that shows what fields are still avaliable.
# cross_selector_fields = pn.widgets.CrossSelector(name='Field-Selection', value=[None], 
#     options=list(query_columns_df.Field_Name.unique())
# )

pdbCode = pn.widgets.MultiChoice(
    name='pdb Code', options = list(set(protein_info_db['pdbCode'])),value = [None], width=600
)


# In[27]:


def get_report_indices(report_widget, query_column_df = query_columns_df):
    
    indices = []
    reportNames = query_columns_df['Report_Name'].unique()
    try:
    # this is the case, when there are elements selected.
    # It is only [] (empty list) when no selection has been done.
        if report_widget !=[]:
            for i in range(0,len(report_widget.value)): 
                indices.append(reportNames.to_list().index(report_widget.value[i]))
    except:
        print("something went wrong getting the report indices")

    return indices

def get_field_indices(field_widget, query_column_df = query_columns_df):
    
    indices = []
    fieldNames = query_columns_df['Field_Name']
    try:
    # this is the case, when there are elements selected.
    # It is only [] (empty list) when no selection has been done.
        if field_widget !=[]:
            for i in range(0,len(field_widget.value)): 
                indices.append(fieldNames.to_list().index(field_widget.value[i]))
    except:
        print("something went wrong getting the field indices")

    return indices


# In[28]:


##
update_button = pn.widgets.Button(name='Update')

def update_click(event):    
    """ 
    When the update Button is clicked the external Data refreshes.
    This happens given the selected Report- and Fieldnames in the
    Multi-Choice Option Wigdets
    """
    
    # on click the values from the respective widgets are beeing
    # checked. For these instances a new external data shall 
    # then be queried.
    # the problem here is the following: because the user should see the Names of the Columns the Names
    # need to be reverse-matched back the the corresponding index. This is happening
    # in the respective helperfunction, which is just a index look-up in the original table. 
    field_indices = get_field_indices(field_number)
    report_indices = get_report_indices(report_number)
    pdb_indices = pdbCode.value
    
    df = get_enrichtment(report_indices,field_indices, query_columns_df)

    # in case pdb codes are specified:
    if pdb_indices != []:
        df = get_enrichtment(report_indices,field_indices, query_columns_df)
        df = df[df['structureId'].isin(pdb_indices)]
    test.external_data = df.head(15)

def get_df():
    df = test.external_data
    sio = StringIO()
    df.to_csv(sio)
    sio.seek(0)
    return sio
        
update_button.on_click(update_click)

file_download = pn.widgets.FileDownload(
    callback=get_df, filename='custom_report_mpstruct.csv'
)

ext_data_widgets = pn.WidgetBox('## External Data',
                                report_number,
                                field_number,
                                pdbCode,
                                update_button,
                                width=640)

external_data_dash = pn.Pane(pn.Column(pn.Row(ext_data_widgets),
                  pn.Row(test.param, width=1200),
                  pn.Row(file_download)))


# In[57]:


external_data_dash


# In[30]:


class MergedData(param.Parameterized):
    merge_button = param.Action(lambda x: x.param.trigger('merge_button'), label='Combine with External Data')
    merged_data = param.DataFrame(default=None)     
    
    @param.depends('merge_button', watch=True)
    def update_df(self):
        self.merged_data = pd.read_json(merge_with_mpstruct(protein_db_s, test.external_data).to_json())

        
def get_df2():
    df = test3.merged_data
    sio = StringIO()
    df.to_csv(sio)
    sio.seek(0)
    return sio
        
file_download2 = pn.widgets.FileDownload(
    callback=get_df, filename='combined_mpstruct.csv'
)

test3 = MergedData()

# noch nicht interaktiv. geht aber ansich. weiss nicht warum.
pn.Column(test3.param,
         pn.Column(file_download2))


# In[31]:


test3.merged_data[test3.merged_data['structureId']=='4P79']


# In[ ]:





# In[33]:


protein_db_s = protein_db.drop(axis = 1, labels = ['bibliography', 'memberProteins', 'secondaryBibliographies', 'relatedPdbEntries', 'pages', 'volume', 'pubMedId', 'issue'])
protein_db_s

protein_db_s.isnull().sum()


# In[34]:


# entries where 'species' is null
protein_db_s[protein_db_s['species'].isnull()]


# In[35]:


# entries where 'taxonomicDomain' is null
protein_db_s[protein_db_s['taxonomicDomain'].isnull()]


# In[36]:


# entries where 'resolution' is null
protein_db_s[protein_db_s['resolution'].isnull()].head(5)


# In[37]:


## Experimental Plot oder Base-Overview ...


# In[38]:


## Base-Overview
class base_overview(param.Parameterized):
    ## Data of the Base Overview:
    mpstruct = param.DataFrame(default=None)

test2 = base_overview()
test2.mpstruct = protein_db_s.head(1)
    
pn.Row(test2.mpstruct, width=1200)


# In[39]:


# alt_types = ['O', 'Q', 'N']
# data_cols = list(te.columns.values)

# class VisExplorer(param.Parameterized):
#     x_type = param.Selector(objects=alt_types)
#     y_type = param.Selector(objects=alt_types)
#     x = param.Selector(default=None, objects=data_cols)
#     y = param.Selector(default=None, objects=data_cols)
    
#     @pn.depends('x', 'y', 'x_type', 'y_type')
#     def plot(self):
#         return alt_plot(self.x, self.x_type, self.y, self.y_type)


# def alt_get_name(axis_name, alt_type):
#     return ':'.join([axis_name, alt_type])
    

# def alt_plot(x, x_type, y, y_type):
#     ac = alt.Chart(protein_db_s.iloc[2:4]).mark_point(size = 15).encode(
#     x = alt_get_name(x, x_type),
#     y = alt_get_name(y, y_type)
#     )
#     return ac
    
# explorer = VisExplorer()
# pn.Pane(pn.Row(explorer.param,explorer.plot
#               ))


# In[40]:


x = columns[5]
y = columns[5]

ac = alt.Chart(protein_db_s).mark_point(size = 15).encode(
    x = alt_get_name(x, 'Q'),
    y = alt_get_name(y, 'Q')
    )

ac


# In[41]:


import hvplot.pandas
from bokeh.sampledata.autompg import autompg
import altair as alt 


def hv_plot(x='db_type', y='taxonomicDomain', color='#058805'):
    return test3.merged_data.hvplot.scatter(x, y, c=color, padding=0.1)

# def alt_plot(x, y):
#     dt = protein_db_s
#     ac = alt.Chart(dt).mark_point(size = 15).encode(
#     x = ':'.join([x,'Q']),
#     y = ':'.join([y,'Q'])
#     )
#     return ac

columns = list(test3.merged_data.columns)

class Explorer(param.Parameterized):

    x = param.Selector(objects=columns)
    y = param.Selector(default='db_type', objects=columns)

    
    @param.depends('x', 'y') # optional in this case
    def plot(self):
        return hv_plot(self.x, self.y)
    
#     @param.depends('x', 'y') # optional in this case
#     def plot2(self):
#         return alt_plot(self.x, self.y)
    
    
    

explorer = Explorer()

pn.Row(explorer.param, explorer.plot)


# In[ ]:


pn.Pane(pn.Row(explorer,alt_get_name(explorer.x, explorer.x_type),alt_get_name(explorer.y, explorer.y_type),
              ))


# In[42]:


alt.Chart(te).mark_point(size = 15).encode(
    x = alt_get_name(explorer.x, explorer.x_type),
    y = alt_get_name(explorer.y, explorer.y_type)
    ).interactive()


# In[43]:


protein_db_s


# In[44]:


test3 = VisExplorer()

pn.Row(test3)


# In[45]:


# Entries over Time-Visualitaion
entries_over_time = alt.Chart(d).mark_bar(size=15).encode(
    x='year:O',
    y='CummulativeCount:Q',
    color=alt.Color('db_type', legend=alt.Legend(title="DB Type by color"))
).properties(
    width=600,
    height=400
).interactive()

entries_over_time


# In[46]:


def alt_get_name(axis_name, alt_type):
    return ':'.join([axis_name, alt_type])
    
alt_get_name('test', 'O')


# In[50]:


# Variables used in the Base-Reporting - this works dynamically and updates everytime the data from mptopo changes. The report does stay up to date this way.

# Entries over Time-Visualitaion

protein_db['year'] = pd.to_datetime(protein_db['year'], format='%Y')
protein_db['year'] = pd.DatetimeIndex(protein_db['year']).year
d = pd.crosstab(protein_db.year, columns=protein_db.db_type).cumsum()
d = d.stack().reset_index()
d = d.rename(columns={0:'CummulativeCount'})
d = d.convert_dtypes()
d.dtypes

entries_over_time = alt.Chart(d).mark_bar(size=15).encode(
    x='year:O',
    y=alt.Y('CummulativeCount:Q', title = 'Entries'),
    color=alt.Color('db_type', legend=alt.Legend(title="DB Type")),
    tooltip=[alt.Tooltip('CummulativeCount:Q'),
            alt.Tooltip('db_type'),
            alt.Tooltip('year:O')]
).properties(
    width=600,
    height=400,
    title="Number of DB Entries over Time"
)


no_of_entries = protein_db.shape[0]
name_of_features = list(protein_db.columns)
features_as_str = ', '.join(name_of_features).lower()
db_types_len = len(list(protein_db['db_type'].unique()))
db_types_as_str = ', '.join(list(protein_db['db_type'].unique())).lower()


reso_over_time_mean = protein_db[['db_type', 'resolution', 'year']].groupby(['year'], as_index = False).mean()

db_type_reso = protein_db[['db_type', 'resolution']].groupby(['db_type'], as_index = False).mean()

mean_reso = alt.Chart(reso_over_time_mean).mark_line().encode(
    y = alt.Y('resolution:Q',scale=alt.Scale(domain=(2, 4))),
    x = 'year:O'
)


no_of_monotopic_proteins = protein_db[protein_db['db_type'] == 'MONOTOPIC MEMBRANE PROTEINS'].shape[0]
mono_prot_ratio = round((no_of_monotopic_proteins / no_of_entries) * 100,2)

no_of_alpha_proteins = protein_db[protein_db['db_type'] == 'TRANSMEMBRANE PROTEINS: ALPHA-HELICAL'].shape[0]
alpha_prot_ratio = round((no_of_alpha_proteins / no_of_entries) * 100,2)

no_of_beta_proteins = protein_db[protein_db['db_type'] == 'TRANSMEMBRANE PROTEINS: BETA-BARREL'].shape[0]
beta_prot_ratio = round((no_of_beta_proteins / no_of_entries) * 100,2)

pd.DataFrame({'ratio':[mono_prot_ratio,alpha_prot_ratio, beta_prot_ratio]})


mono_report = pn.Column(
mono_text
)
mono_report
protein_db.head(3)




entries_over_time


# In[48]:


reso_comparison = alt.Chart(protein_db[['resolution', 'db_type']].melt(id_vars = 'db_type', value_vars = 'resolution')).mark_area(opacity = 1, interpolate = 'step').encode(
    alt.X('value:Q',bin=alt.Bin(maxbins=25), title = 'Resolution'),
    alt.Y('count()', stack=None),
    alt.Color('db_type:N'),
    tooltip = ['count()']
).transform_filter(
     alt.FieldEqualPredicate(field = 'db_type', equal = protein_db.db_type.unique()[0])
) | alt.Chart(protein_db[['resolution', 'db_type']].melt(id_vars = 'db_type', value_vars = 'resolution')).mark_area(opacity = 1, interpolate = 'step').encode(
    alt.X('value:Q',bin=alt.Bin(maxbins=25), title = 'Resolution'),
    alt.Y('count()', stack=None),
    alt.Color('db_type:N'),
    tooltip = ['count()']
).transform_filter(
     alt.FieldEqualPredicate(field = 'db_type', equal = protein_db.db_type.unique()[1])
) | alt.Chart(protein_db[['resolution', 'db_type']].melt(id_vars = 'db_type', value_vars = 'resolution')).mark_area(opacity = 1, interpolate = 'step').encode(
    alt.X('value:Q',bin=alt.Bin(maxbins=25), title = 'Resolution'),
    alt.Y('count()', stack=None),
    alt.Color('db_type:N'),
    tooltip = ['count()']
).transform_filter(
     alt.FieldEqualPredicate(field = 'db_type', equal = protein_db.db_type.unique()[2])
) 

reso_comparison.properties(title="Distribution of Resolution for different Protein Types")


# In[49]:


## idee : für jede spalte, die kategorien enthölt a) die unique categories identifizieren und b) zählen -> Tabelle mit counts, counts sind größe der Bubbles. Bubbles sind clickable.
def count_unique_category_values(data_table):
    
    dct = {}
    index = 0
    for j in range(0,data_table.shape[1]):
        if type(data_table.dtypes[j]) is pd.core.dtypes.dtypes.CategoricalDtype:
            
            dct[index] = {'column_name' :data_table.columns[j], 'unique_values': len(list(data_table.iloc[:,j].unique()))}
            index = index+1
    return dct


dct = count_unique_category_values(protein_db)
category_table = pd.DataFrame.from_dict(dct, orient = 'index')
category_table


# In[ ]:





# In[ ]:





# In[ ]:


pd.DataFrame({'ratio':[mono_prot_ratio,alpha_prot_ratio, beta_prot_ratio]})

## Base Report ##
base_report = pn.Column(
    '# Membrane Protein Topology Database',
    
    # intro text for dashboard
    dash_text,
    
    pn.layout.Divider(),
    '#mpstruc Database',
    
    # intro text for mpstruc
    text,
    
    pn.layout.Divider(),
    '# Database Report',
    
    # time line text
    text_timeline,
    
    # description text plot timeline
    text_plot_timeline,
    
    # time line plot: progression of entries over time
    pn.Row(entries_over_time, height=500),
    
    # resolution text
    text_resolution_over_time,
    pn.Row(mean_reso, height=400),
    pn.Row(
        pn.Column('''Two types have only a slight different in mean resolution whereas better resolutions for alpha helical structures seem to be more feasable overall.'''),
        pn.Column(db_type_reso)
    ),
      
    
    background='whitesmoke', width=1200,

)


tab_view = pn.Tabs(
    ('Overview', base_report),
    ('Experimental', pn.Column(external_data_dash)),
    ('Case Study', pn.Column(),
    ('About', pn.Column())
)

tab_view
# In[48]:





# In[78]:





# In[ ]:





# In[178]:





# In[251]:


taxo_d = protein_db[['taxonomicDomain', 'pdbCode']].groupby('taxonomicDomain').count().sort_values('taxonomicDomain',ascending=False)
taxo_d['taxonomicDomain'] = taxo_d.index
taxo_plot = alt.Chart(taxo_d).mark_bar().encode(
    y = alt.Y('pdbCode:Q', sort='y'),
    x = 'taxonomicDomain:N', 
    color=alt.Color('taxonomicDomain', legend=alt.Legend(title=""))
).properties(
    width=400,
    height=200
)

taxo_text = alt.Chart(taxo_d).mark_text(dx=0, dy=-6, color='black').encode(
    x=alt.X('taxonomicDomain:N', stack='zero', title = 'taxonomic Domain'),
    y=alt.Y('pdbCode:Q', sort='y',title='entries'),
    text=alt.Text('pdbCode', format='.0f')
)

taxo_plot + taxo_text

