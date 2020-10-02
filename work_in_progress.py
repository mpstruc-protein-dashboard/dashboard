## finding the number of pages. The amount of research on the protein might correlate with the resolution (?). This hypothesis is based on the hypothesis that more pages mean longer or more research.

import re

def con_char_to_string(no_list):
    st_of_number = ''
    for number in no_list:
        st_of_number += number
    return st_of_number

def find_no_of_pages(db):
    page_dict = {}
    for i in range(0,db.shape[0]):
        if db.page[i]:
            pages = re.split('-',db.page[i])
            if len(pages)==2:
                page_dict[i] = {'no_of_pages': (int(con_char_to_string(re.findall('[0-9]',pages[1])))-int(con_char_to_string(re.findall('[0-9]',pages[0]))))}
            else:
                page_dict[i] = {'no_of_pages': 1}
    return page_dict

pdict = find_no_of_pages(protein_db)

protein_db['no_of_pages'] = pd.DataFrame.from_dict(pdict, orient = 'index')

### finish thing 1 .. it just finds the no of pages for the paper via regex and basic string comprehension.. sometimes its faulty but i don't care. ill omit extreme values later ###


### then the second thing.. ###

def check_for_dead_fields():
    dead_field = []
    for field in range(0,len(query_columns_df.Field_Name.unique())):
        res = get_enrichtment(None,[field], query_columns_df)
        if res.columns[0] != 'structureId':
            dead_field.append(field)
    return dead_field

dead_fields = check_for_dead_fields()

## this checks for all the "empty" HTTP requests and saves the ids of the columns (i think?).. they should be available via query_columns_df.unique[dead_fields]

## the third thing is making the external data persistent locally .. ##



# persist the external data locally.
query_columns_df.to_pickle("./Database/External/query_columns_df.pkl")

def persist_external_data(query_columns_df):
    
    for field in range(0,len(query_columns_df.Field_Name.unique())):
        res = get_enrichtment(None,[field], query_columns_df)
        if res.columns[0] == 'structureId':
            res.to_pickle(("./Database/External/{0}.pkl").format(query_columns_df.Field_Name.unique()[field]))

## but in the project folder there needs to be the folder structure for this to work so you probably have to make 2 new folders in the project root, database and external.