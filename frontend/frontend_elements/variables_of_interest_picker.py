import panel as pn
import altair as alt
import pandas as pd


# be vary of the chainID. Columns selected with a chain
# id most likely contain 5000 > 10000 entries.

# Idee: Man kommt auf die Seite und soll auswaehlen, welche
# Variablen einen interessieren. Die Auswahl aktualisert eine
# übersichtstabelle, die beschreibt, wie viele Fälle in den
# jeweiligen Tabellen sind.

# Overview


def var_of_interest(mpstruc_variable_list, ext_overview):
    cross_selector = pn.widgets.CrossSelector(
        name='Variables of Interest',
        value=[],
        options=list(ext_overview.col_names, mpstruc_variable_list))
    return cross_selector


# could work, is hard to get to work. use simple solution for now.

# df = pd.melt(ext_overview, id_vars='data_type', value_vars='col_names')
# df.reset_index(inplace=True)

# idea : make the selection as a plot.
# concept: One can click on a label to select it.
#  Shift Click = x axis
#  Ctrl Click = y axis
#  Categories from dropdown? ..

# selec = alt.selection_interval(encodings=['y'], empty='none')


# base = alt.Chart(df).mark_circle(opacity=0).transform_aggregate(
#     groupby=["value","data_type"]
# ).encode(
#     x= alt.X('data_type', axis=None),
#     y= alt.Y('value:O', axis=None)
# )

# text = base.mark_text(align="left").encode(
#     text = "value:O"
# ).add_selection(
#     selec
# )

# (base + text).configure_axis(
#     grid=False
# ).configure_view(
#     strokeWidth=0
# )
