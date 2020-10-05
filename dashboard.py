import altair as alt
import panel as pn
import retrieve_data

db = retrieve_data.Database()
protein_data = retrieve_data.get_dataframe(db)
protein_data = retrieve_data.polish_db(protein_data)
print(protein_data)