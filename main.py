## In this file the deployment of the dashboard should take place.
# import all_the_files

from retrieve_data import (
    Database,
    get_dataframe,
    convert_type
)

from external_data import (
    get_enrichment,
    merge_with_mpstruct
)

if __name__ == "__main__":
    db = Database()
    protein_db = get_dataframe(db) 
    protein_db = convert_type(protein_db)
    enrichment = get_enrichment(protein_db, [0], None)
    merged_db = merge_with_mpstruct(protein_db, enrichment)