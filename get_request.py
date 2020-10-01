#!/usr/bin/env python
# coding: utf-8
# required library imports

import pandas as pd
from pandas.tseries.offsets import YearBegin 

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 50)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 10)

import requests
from xml.etree import ElementTree as xml_etree


class Group:
    def __init__(self, name):
        self.name = name
        self.subs = []

    def add_sub(self, sub):
        self.subs.append(sub)


class Sub:
    def __init__(self, name):
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


class BaseProtein:
    def __init__(
        self, pdb_code, name, species, tax_domain, ex_species,
        res, des, bib, second_bib, related_pdb_ent
    ):
        self.pdb_code = pdb_code
        self.name = name
        self.species = species
        self.tax_domain = tax_domain
        self.ex_species = ex_species
        self.res = res
        self.des = des
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
        

class MemberProtein(BaseProtein):
    def __init__(
        self, pdb_code, name, species, tax_domain, ex_species,
        res, des, bib, second_bib, related_pdb_ent, master_pdb_code
    ):
        super().__init__(
            pdb_code, name, species, tax_domain,
            ex_species, res, des, bib, second_bib, related_pdb_ent
        )

        self.master_pdb_code = master_pdb_code


class MasterProtein(BaseProtein):
    def __init__(
        self, pdb_code, name, species, tax_domain, ex_species,
        res, des, bib, second_bib, related_pdb_ent, members
    ):
        super().__init__(
            pdb_code, name, species, tax_domain,
            ex_species, res, des, bib, second_bib, related_pdb_ent
        )

        self.members = []
        self.process_members(members)

    def process_members(self, members):
        if members:
            for m in members:
                member = MemberProtein(*[ item.text if not len(item) else item
                                          for item in list(m)])
                self.members.append(member)
        else:
            self.members = None

    @property
    def vars(self):
        return vars(self)


class Database:
    def __init__(self):
        super().__init__()
        self.monotopic = self.get_groups()[0]
        self.b_barrel = self.get_groups()[1]
        self.a_helical = self.get_groups()[2]

    def get_groups(self):
        url = "https://blanco.biomol.uci.edu/mpstruc/listAll/mpstrucTblXml" ## weekly + diff()-Bash 
        response = requests.get(url)
        
        groups = list(xml_etree.fromstring(response.content))[1] # xml_tree's children attributes: [0]caption [1]groups
        group_arr = []

        for g in groups.findall('.//group'):
            group = Group(name = list(g)[0].text)
            sub_groups = list(g)[2]
            for sub in list(sub_groups):
                name = sub[0].text
                proteins = list(sub[1])

                sub = Sub(name)
                for p in proteins:
                    protein = MasterProtein(*[ item.text if not len(list(item))
                                            else item for item in list(p) ])
                    sub.add_protein(protein)

                group.add_sub(sub)
            group_arr.append(group)
        
        return group_arr


def get_dataframe():
    db = Database()
    for sub in db.monotopic.subs:
        print(pd.DataFrame.from_dict(data=sub.proteins))


get_dataframe()