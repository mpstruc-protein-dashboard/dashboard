#!/usr/bin/env python
# coding: utf-8

# In[75]:


## required library imports

import altair as alt
import pandas as pd 

## pandas options

pd.options.display.max_columns = 60
pd.options.display.min_rows = 20


# In[5]:


#!/usr/bin/env python
# coding: utf-8
# required library imports

import requests
import pandas as pd
from xml.etree import ElementTree as xml_etree

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 50)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 10)


class Group:
    def __init__(self, name):
        self.name = name
        self.subs = []

    def add_sub(self, sub):
        self.subs.append(sub)


class Sub:
    def __init__(self, group_name, name):
        self.group_name = group_name
        self.name = name
        self.proteins = []

    def add_protein(self, protein):
        self.proteins.append(protein.vars)


class Bib:
    def __init__(
        self, med_id, authors, year, title, journal,
        volume, issue, page, doi, notes
    ):
        self.med_id = med_id
        self.authors = authors
        self.year = year
        self.title = title
        self.journal = journal
        self.volume = volume
        self.issue = issue
        self.page = page
        self.doi = doi
        self.notes = notes


class MasterProtein:
    def __init__(
        self, group_name, sub_name, pdb_code, name, species, tax_domain, ex_species,
        res, des, bib, second_bib, related_pdb_ent, *args
    ):
        self.group_name = group_name
        self.sub_name = sub_name
        self.pdb_code = pdb_code
        self.name = name
        self.species = species
        self.tax_domain = tax_domain
        self.ex_species = ex_species
        self.res = res
        self.des = des
        self.second_bib = second_bib
        self.related_pdb_ent = related_pdb_ent

        self.med_id = None
        self.authors = None
        self.year = None
        self.title = None
        self.journal = None
        self.volume = None
        self.issue = None
        self.page = None
        self.doi = None
        self.notes = None

        if bib.__class__.__name__ == "Element":
            bib = Bib(*[item.text for item in list(bib)])
            self.med_id = bib.med_id
            self.authors = bib.authors
            self.year = bib.year
            self.title = bib.title
            self.journal = bib.journal
            self.volume = bib.volume
            self.issue = bib.issue
            self.page = bib.page
            self.doi = bib.doi
            self.notes = bib.notes

    @property
    def vars(self):
        return vars(self)


class Database:
    def __init__(self):
        super().__init__()
        group_arr = self.get_groups()
        self.monotopic = group_arr[0]
        self.b_barrel = group_arr[1]
        self.a_helical = group_arr[2]

    def get_groups(self):
        url = "https://blanco.biomol.uci.edu/mpstruc/listAll/mpstrucTblXml" ## weekly + diff()-Bash 
        response = requests.get(url)
        
        groups = list(xml_etree.fromstring(response.content))[1] # xml_tree's children attributes: [0]caption [1]groups
        group_arr = []

        for g in groups.findall('.//group'):
            group = Group(name = list(g)[0].text)
            sub_groups = list(g)[2]
            for sub in list(sub_groups):
                sub_name = sub[0].text
                proteins = list(sub[1])

                sub = Sub(group.name, sub_name)
                for p in proteins:
                    attrs = [ item.text if not len(list(item)) else item
                              for item in list(p) ]

                    attrs.insert(0, sub_name)
                    attrs.insert(0, group.name)
                    protein = MasterProtein(*attrs)
                    sub.add_protein(protein)

                group.add_sub(sub)
            group_arr.append(group)
        
        return group_arr


def get_dataframe(db:Database):
    protein_collection = []
    for group in [db.monotopic, db.a_helical, db.b_barrel]:
        for sub in group.subs:
            protein_collection.append(pd.DataFrame.from_dict(data=sub.proteins))
    
    protein_collection = pd.concat(protein_collection, ignore_index= True)
    return protein_collection


# In[6]:


db = Database()
protein_db = get_dataframe(db)
protein_db


# In[4]:


protein_db


# In[8]:


# if not run_import:
#     full_db = pd.read_pickle("./Database/pickleDB/full_db.pkl")
#     biblio_entry_db = pd.read_pickle("./Database/pickleDB/biblio_entry_db.pkl")
#     member_protein_db = pd.read_pickle("./Database/pickleDB/member_protein_db.pkl")


# In[7]:


# omit empty columns:

db_list = [protein_db]

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


# In[11]:


protein_db.dtypes

protein_db = protein_db.convert_dtypes()
protein_db['NMR'] = protein_db['res'].str.contains('NMR')
protein_db['res'] = pd.to_numeric(protein_db['res'], errors='coerce')
protein_db['group_name'] = protein_db['group_name'].astype('category')
protein_db['sub_name'] = protein_db['sub_name'].astype('category')
protein_db['tax_domain'] = protein_db['tax_domain'].astype('category')
protein_db['species'] = protein_db['species'].astype('category')
protein_db['ex_species'] = protein_db['ex_species'].astype('category')
protein_db['year'] = protein_db['year'].astype('category')

protein_db.dtypes


# In[12]:


## EXTERNAL DATA ENRICHMENT :: PDB DATABASE :: ##

# 1. get all possible "columns" for data enrichment from pdb.
# Method: https://towardsdatascience.com/web-scraping-html-tables-with-python-c9baba21059

import lxml.html as lh

query_columns = requests.get('https://www.rcsb.org/pdb/results/reportField.do')
query_columns = lh.fromstring(query_columns.content)
query_columns = query_columns.xpath('//tr')

#Create empty list
col=[]
i=0
#For each row, store each first element (header) and an empty list
for t in query_columns[0]:
    i+=1
    name=t.text_content()
    print('%d:"%s"'%(i,name))
    col.append((name,[]))

#Since out first row is the header, data is stored on the second row onwards
for j in range(1,len(query_columns)):
    #T is our j'th row
    T = query_columns[j]
    
    #If row is not of size 10, the //tr data is not from our table 
    if len(T)!=3:
        break
    
    #i is the index of our column
    i=0
    
    #Iterate through each element of the row
    for t in T.iterchildren():
        data=t.text_content() 
        #Check if row is empty
        if i>0:
        #Convert any numerical value to integers
            try:
                data=str(data)
            except:
                pass
        #Append the data to the empty list of the i'th column
        col[i][1].append(data)
        #Increment i for the next column
        i+=1

query_columns_dict = {title:column for (title,column) in col}
query_columns_df = pd.DataFrame(query_columns_dict)

## Table from https://www.rcsb.org/pdb/results/reportField.do as a pandas DataFrame with Srings as Fields.
query_columns_df = query_columns_df.convert_dtypes()



## There are several reports within the possible columns that can be queried to enrich the data. This step makes sure
## that these reports can be accessed properly.

for i in range(0,query_columns_df.shape[0]):
    if query_columns_df['Report Name'].iloc[i] == '\xa0':
        query_columns_df['Report Name'].iloc[i] = query_columns_df['Report Name'].iloc[i-1]

query_columns_df['Report Name'] = query_columns_df['Report Name'].astype('category')

query_columns_df.rename(columns= {'Report Name': 'Report_Name','Field Name': 'Field_Name', 'PDBx/mmCIF Item Name': 'Item_Name'}, inplace = True)

query_columns_df.Report_Name.unique()


# In[13]:



## query by report category.. there are 22 different reports that can be accessed in the PDB database. they sometimes do not work combined therefore they are beeing accessed "one by one"
report_no = 0
query_columns = query_columns_df.loc[query_columns_df.Report_Name == query_columns_df.Report_Name.unique()[report_no],'Field_Name']

query_columns = ','.join(query_columns)

query_columns =  'structureId,' + query_columns

print(query_columns)
#https://www.youtube.com/watch?v=NXwP8pSOiB8


# In[16]:


from pandas.core.common import flatten
from io import StringIO

import urllib

# protein_info_db: Subsetting for the PDB ids to look up further information such as resolution and releaseDate to "validate" and/or double-check the entries in mptopo

# for this the RESTFUL API is beeing utilized. A simple HTML request per specific URL is beeing done to query for certain data
# the URL contains the PDB codes as well as the columns in question aswell as the type of the report, which is by default csv so it can be easily read and understood by pandas.  

# extract the pdb codes from mptopo:

# there are some 'lists' in the Data that we need to get rid of first
pdbCodes_in_mptopo = ','.join(flatten(protein_db['pdb_code']))

# those lists contain duplicates which are eliminated in this step
unique_pdbCodes_in_mptopo = ','.join(set(flatten(protein_db['pdb_code'])))

# Build the URL for the REST-API. This holds a strange behaviour with ;&amp and &. Somehow the & does not get converted and causes some error if not
# handled with urllib.parse.urlparse.
getURL = 'http://www.pdb.org/pdb/rest/customReport?pdbids={0}'         '&customReportColumns={1}'         '&service=wsfile&format=csv'.format(unique_pdbCodes_in_mptopo,
                                             query_columns)
getURL = urllib.parse.urlparse(getURL)
# the URL is beeing requested and returns a text (StringIO) which now easily can be understood by pandas and be written to a data frame. 
string_from_url = requests.get(getURL.geturl()).text

enrichment = pd.read_csv(StringIO(string_from_url))
enrichment
## the enrichment data can now be merged onto the existing mptopo data

protein_info_db = protein_db.merge(enrichment, left_on='pdb_code', right_on= 'structureId', how = 'left')
protein_info_db


# In[17]:


query_columns_df.loc[query_columns_df.Report_Name == query_columns_df.Report_Name.unique()[0],'Field_Name']
report_no = [1,2,5]

if type(report_no) is list:
    query_columns_list = []
    for no in report_no: 
        query_columns_list.append(query_columns_df.loc[query_columns_df.Report_Name == query_columns_df.Report_Name.unique()[no],'Field_Name'])
pd.concat(query_columns_list)


# In[24]:


def get_enrichtment(reports = [], fields = [], query_columns_df = query_columns_df):
    
    from pandas.core.common import flatten
    from io import StringIO
    import urllib
    
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
    pdbCodes_in_mptopo = ','.join(flatten(protein_db['pdb_code']))

    # those lists contain duplicates which are eliminated in this step
    unique_pdbCodes_in_mptopo = ','.join(set(flatten(protein_db['pdb_code'])))

    # Build the URL for the REST-API. This holds a strange behaviour with ;&amp and &. Somehow the & does not get converted and causes some error if not
    # handled with urllib.parse.urlparse.
    getURL = 'http://www.pdb.org/pdb/rest/customReport?pdbids={0}'             '&customReportColumns={1}'             '&service=wsfile&format=csv'.format(unique_pdbCodes_in_mptopo,
                                                 query_columns)
    getURL = urllib.parse.urlparse(getURL)
    # the URL is beeing requested and returns a text (StringIO) which now easily can be understood by pandas and be written to a data frame. 
    string_from_url = requests.get(getURL.geturl()).text

    enrichment = pd.read_csv(StringIO(string_from_url))
    return enrichment


# In[25]:


## Function takes in the "original Data" and merges is on the pdbCode with the data from the pdb database.
def merge_with_mpstruct(mpstruct_data, enrichment):
    return(mpstruct_data.merge(enrichment, left_on='pdb_code', right_on= 'structureId', how = 'left'))


# In[26]:


def to_neat_data_table(dt):
    html = dt.to_html(classes=['example', 'panel-df'])
    return pn.pane.HTML(html+script, sizing_mode='stretch_width').servable()


# In[22]:


### DASHBOARD ###


# In[45]:


import panel as pn
import numpy as np
import param
import altair as alt


# In[28]:


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





# In[29]:


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
    name='pdb Code', options = list(set(protein_info_db['pdb_code'])),value = [None], width=600
)


# In[30]:


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


# In[31]:


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


# In[37]:


protein_db_s = protein_db
protein_db_s

protein_db_s.isnull().sum()


# In[38]:


external_data_dash


# In[31]:


test3.merged_data[test3.merged_data['structureId']=='4P79']


# In[36]:


protein_db_s = protein_db.drop(axis = 1, labels = ['bibliography', 'memberProteins', 'secondaryBibliographies', 'relatedPdbEntries', 'pages', 'volume', 'pubMedId', 'issue'])
protein_db_s

protein_db_s.isnull().sum()


# In[39]:


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


# In[40]:


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


# In[41]:


## Base-Overview
class base_overview(param.Parameterized):
    ## Data of the Base Overview:
    mpstruct = param.DataFrame(default=None)

test2 = base_overview()
test2.mpstruct = protein_db_s.head(1)
    
pn.Row(test2.mpstruct, width=1200)


# In[46]:


alt_types = ['O', 'Q', 'N']
data_cols = list(protein_db_s.columns.values)

class VisExplorer(param.Parameterized):
    x_type = param.Selector(objects=alt_types)
    y_type = param.Selector(objects=alt_types)
    x = param.Selector(default=None, objects=data_cols)
    y = param.Selector(default=None, objects=data_cols)
    
    @pn.depends('x', 'y', 'x_type', 'y_type')
    def plot(self):
        return alt_plot(self.x, self.x_type, self.y, self.y_type)


def alt_get_name(axis_name, alt_type):
    return ':'.join([axis_name, alt_type])
    

def alt_plot(x, x_type, y, y_type):
    ac = alt.Chart(protein_db_s.iloc[2:4]).mark_point(size = 15).encode(
    x = alt_get_name(x, x_type),
    y = alt_get_name(y, y_type)
    )
    return ac
    
explorer = VisExplorer()
pn.Pane(pn.Row(explorer.param,explorer.plot
              ))


# In[47]:


x = columns[5]
y = columns[5]

ac = alt.Chart(protein_db_s).mark_point(size = 15).encode(
    x = alt_get_name(x, 'Q'),
    y = alt_get_name(y, 'Q')
    )

ac


# In[60]:


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


# In[49]:


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

mono_text = '''
Out of {0} database entries there are {1} monotopic membrane proteins, so {2}%. \n
Their mean resolution is:
'''.format(no_of_entries, no_of_monotopic_proteins, round(mono_prot_ratio, 2))

mono_report = pn.Column(
mono_text
)
mono_report
protein_db.head(3)




entries_over_time


# In[48]:



# Generating Data
source = pd.DataFrame({
    'Trial A': np.random.normal(0, 0.8, 1000),
    'Trial B': np.random.normal(-2, 1, 1000),
    'Trial C': np.random.normal(3, 2, 1000)
})

alt.Chart(source).transform_fold(
    ['Trial A', 'Trial B', 'Trial C'],
    as_=['Experiment', 'Measurement']
).mark_area(
    opacity=0.3,
    interpolate='step'
).encode(
    alt.X('Measurement:Q', bin=alt.Bin(maxbins=100)),
    alt.Y('count()', stack=None),
    alt.Color('Experiment:N')
)

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


# In[ ]:


text = """ mpstruc is a curated database of membrane proteins of known 3D structure from the Stephen White laboratory at UC Irvine.
To be included in the database, a structure must be available in the RSCB Protein Data Bank (PDB) and have been published in a peer reviewed journal.
The database is manually curated based upon on-going literature surveys.
Because of the labor involved, new structures are not posted until they are released by the PDB and the complete reference,
including pagination for print journals, is available in PubMed.
Their goal is to make mpstruc as accurate and complete as possible.
If you find errors or omissions, please send a message to Stephen White, Gracie Han (gyewon.han@usc.edu),
or Craig Snider. mpstruc emphasizes structures determined by diffraction and cryo-EM methods.
NMR structures are also included whenever identified. A comprehensive list of NMR-determined
structures has been established by Dror Warschawski and is available from the Antoine Loquet lab. 
(source: https://blanco.biomol.uci.edu/mpstruc/)
"""

dash_text = """ 
This dashboard shall enable its user to visually explore the mpstruc database and its contents
by providing a base-line report aswell as a do-it-yourself sandbox visualization system, that
allowes the expierienced user to customize the vizualitaions to their liking.
"""

text_timeline = """
The database up-to-date holds {0} records which are divided into {1} categories: {2}. Features reported include {3}.\n\n
It was last updated at: {4}.
""".format(no_of_entries, db_types_len, db_types_as_str, features_as_str, ''.join(list(data2['@lastDatabaseEditDate'])))

text_plot_timeline = """
The following figure depicts the increasing pace in which entries are added to the mpstruc database.
It shows the start of an somewhat exponantional growth. The more data there is the harder it gets to
keep an rigid overview about the database's contents. This dashboard shall provide such basic overview to keep track of the
database and its progression. One thing to notice right away is the ratio between the entries. Out of {0} entries {1} are monotopic proteins ({2}%),
the majority of {3} are alpha helical ({4}%) and {5} are beta barrel proteins ({6}%).
""".format(no_of_entries,
           no_of_monotopic_proteins, mono_prot_ratio,
           no_of_alpha_proteins, alpha_prot_ratio,
           no_of_beta_proteins, beta_prot_ratio)

text_resolution_over_time = """
Over time also the resolution at which proteins are identified and validated changes.
This is depicted as the change in mean resolution over time for all database types in the next figure.
The slope has a slight positive trend so it seems the resolution of membrane proteins improves over time. 
This view is heavily skewed by the ratio of entries. In other words approximately {0}% of the trend is due to the alpha helical structures
and their high occurance in the database.
""".format(alpha_prot_ratio)

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


tab_view


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

