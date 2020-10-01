def no_of_entries(protein_db):
    return protein_db.shape[0]

def name_of_features(protein_db):
    return list(protein_db.columns)

def features_as_str(protein_db):
    return ', '.join(name_of_features(protein_db)).lower()

def db_types_len(protein_db):
    print("neuer Name!! - check mit Quang.")
    return len(list(protein_db['#'].unique()))    

def db_types_as_str(protein_db):
    print("neuer Name!! - check mit Quang.")
    return ', '.join(list(protein_db['#'].unique())).lower()


def resolution_mean_over_time(protein_db):
    return protein_db[['db_type', 'resolution', 'year']].groupby(['year'], as_index = False).mean()

def db_type_reso(protein_db):
    return protein_db[['db_type', 'resolution']].groupby(['db_type'], as_index = False).mean()

no_of_monotopic_proteins = protein_db[protein_db['db_type'] == 'MONOTOPIC MEMBRANE PROTEINS'].shape[0]
mono_prot_ratio = round((no_of_monotopic_proteins / no_of_entries) * 100,2)

no_of_alpha_proteins = protein_db[protein_db['db_type'] == 'TRANSMEMBRANE PROTEINS: ALPHA-HELICAL'].shape[0]
alpha_prot_ratio = round((no_of_alpha_proteins / no_of_entries) * 100,2)

no_of_beta_proteins = protein_db[protein_db['db_type'] == 'TRANSMEMBRANE PROTEINS: BETA-BARREL'].shape[0]
beta_prot_ratio = round((no_of_beta_proteins / no_of_entries) * 100,2)


def no_of_proteins_per_cat(protein_db, cat):
    print("neuer Name - check mit Quang.")
    return protein_db[protein_db['#'] == cat].shape[0]

