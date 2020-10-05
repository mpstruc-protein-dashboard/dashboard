import os
import pandas as pd
from retrieve_data import (
    polish_db,
    get_dataframe,
    Database
)


class MasterDatabase:
    def __init__(self, tabular_data):
        # self.data = external_data # external data
        self.tabular_data =  tabular_data # get tabular data from xml file.
        self.external_data_list = self.read_all_pkl()
        self.mpstruct_data = self.merge_with_mpstruct(self.external_data_list)

    def read_all_pkl(self):
        file_list = os.listdir("./Database/External/")
        external_data_list=[]
        for file_name in file_list:
            external_data_list.append({
                "name": file_name.split('.')[0],
                "data": pd.read_pickle(
                            './Database/External/{}'.format(file_name)
                        )
            })

        return external_data_list
    
    ## Function takes in the "original Data" and merges is on the pdbCode with the data from the pdb database.
    def merge_with_mpstruct(self, external_data_list):
        mpstruct_data = pd.DataFrame({
                            'pdb_code': self.tabular_data.pdb_code.unique()
                        })

        for field in external_data_list[:5]:
            mpstruct_data = mpstruct_data.merge(
                                field.get('data'),
                                on=['pdb_code'],
                                how='left',
                            )
        return mpstruct_data


db = Database()
tabular_data = polish_db(get_dataframe(db))
database = MasterDatabase(tabular_data)
print(database.mpstruct_data.head())

    ### define variables describing the tabular data (descriptive stats) ###
    # def no_of_entries(self) -> int:
    #     return self.tabular_data.shape[0]

    # def name_of_features(self) -> list:
    #     return list(self.tabular_data.columns)

    # def features_as_str(self) -> str:
    #     return ', '.join(name_of_features(self.tabular_data)).lower()

    # def db_types_len(self) -> int:
    #     print("neuer Name!! - check mit Quang.")
    #     return len(list(self.tabular_data['#'].unique()))    

    # def db_types_as_str(self) -> str:
    #     print("neuer Name!! - check mit Quang.")
    #     return ', '.join(list(self.tabular_data['#'].unique())).lower()


    # def resolution_mean_over_time(self):
    #     return self.tabular_data[['db_type', 'resolution', 'year']].groupby(['year'], as_index = False).mean()

    # def db_type_reso(self):
    #     return self.tabular_data[['db_type', 'resolution']].groupby(['db_type'], as_index = False).mean()

    
    
    # no_of_monotopic_proteins = protein_db[protein_db['db_type'] == 'MONOTOPIC MEMBRANE PROTEINS'].shape[0]
    # mono_prot_ratio = round((no_of_monotopic_proteins / no_of_entries) * 100,2)

    # no_of_alpha_proteins = protein_db[protein_db['db_type'] == 'TRANSMEMBRANE PROTEINS: ALPHA-HELICAL'].shape[0]
    # alpha_prot_ratio = round((no_of_alpha_proteins / no_of_entries) * 100,2)

    # no_of_beta_proteins = protein_db[protein_db['db_type'] == 'TRANSMEMBRANE PROTEINS: BETA-BARREL'].shape[0]
    # beta_prot_ratio = 

    # def no_of_proteins_per_cat(self, cat):
    #     print("neuer Name - check mit Quang.")
    #     return protein_db[protein_db['#'] == cat].shape[0]

    # def ratio_of_proteins_per_cat(self, cat):
    #     print("neuer Name - check mit Quang.")
    #     return round((no_of_proteins_per_cat(self,cat) / self.no_of_entries()) * 100,2)
