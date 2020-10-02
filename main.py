## In this file the deployment of the dashboard should take place.
# import all_the_files

from retrieve_data import (
    Database,
    get_dataframe,
    polish_db
)

from external_data import (
    get_external_data_overview,
    persist_external_data,
    merge_with_mpstruct
)

if __name__ == "__main__":
    db = Database()
    protein_db = get_dataframe(db) 
    protein_db = polish_db(protein_db)
    query_columns_df = get_external_data_overview()
    enrichment = persist_external_data(protein_db, query_columns_df)
    merged_db = merge_with_mpstruct(protein_db, enrichment)