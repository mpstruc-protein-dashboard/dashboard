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