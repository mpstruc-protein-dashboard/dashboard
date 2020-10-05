import re
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
        else:
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
        url = "https://blanco.biomol.uci.edu/mpstruc/listAll/mpstrucTblXml"
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
    protein_df = []
    for group in [db.monotopic, db.a_helical, db.b_barrel]:
        for sub in group.subs:
            protein_df.append(pd.DataFrame.from_dict(data=sub.proteins))
    
    protein_df = pd.concat(protein_df, ignore_index= True)
    return protein_df


def polish_db(db):
    def convert_type(db):
        db['NMR'] = db['res'].str.contains('NMR')
        db = db.convert_dtypes()
        db['res'] = pd.to_numeric(db['res'], errors='coerce')
        db['group_name'] = db['group_name'].astype('category')
        db['sub_name'] = db['sub_name'].astype('category')
        db['tax_domain'] = db['tax_domain'].astype('category')
        db['species'] = db['species'].astype('category')
        db['ex_species'] = db['ex_species'].astype('category')
        db['year'] = db['year'].astype('category')
        return db
    # Find the number of pages.
    # The amount of research on the protein might correlate with the resolution (?).
    # This hypothesis is based on the hypothesis that more pages mean longer or more research.

    def count_pages(db):
        def char_to_str(no_list):
            st_of_number = ''
            for number in no_list:
                st_of_number += number
            return st_of_number

        page_dict = {}
        for i in range(0, db.shape[0]):
            if not pd.isnull(db.page[i]):
                pages = re.split('-',db.page[i])
                if len(pages)==2:
                    page_dict[i] = {'page_count': int(char_to_str(re.findall('[0-9]',pages[1])))-int(char_to_str(re.findall('[0-9]',pages[0])))}
                else:
                    page_dict[i] = {'page_count': 1}
        return page_dict

    db = convert_type(db) ## returns the db with converted datatypes.
    pdict = count_pages(db) ## returns page-count column.
    ## adds page-count column. 
    db['page_count'] = pd.DataFrame.from_dict(pdict, orient = 'index')
    return db




# def data_update(new_timestamp):
#     timestamp_file = open("./Database/timestamp/old_timestamp.txt","r")
#     timestamp_old = timestamp_file.readlines()
#     timestamp_file.close()
#     if timestamp_old == [new_timestamp]:
#         ##do the update ... get all the data and rebuild all the enrichtment databases
#     else:
#         ##do nothing, just get the old database



# def get_timestamp():
#     import xml.etree.ElementTree as etree
#     import xmltodict
#     url = "https://blanco.biomol.uci.edu/mpstruc/listAll/mpstrucTblXml" ## weekly + diff()-Bash 
#     response = requests.get(url)
#     od = xmltodict.parse(etree.tostring(xml_etree.fromstring(response.content)),process_namespaces=True)
#     od2 = od.popitem()
#     timestamp = od2[1]['@timeStamp']
#     return timestamp