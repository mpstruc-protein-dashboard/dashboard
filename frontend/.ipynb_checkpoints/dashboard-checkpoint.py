import altair as alt
import panel as pn
from frontend_elements import (
    axis_picker,
    category_selection,
    # custom_plot,
    variables_of_interest_picker
)

from . import MasterDatabase

# the masterdata object holds every possible column
# caution: there is no "one single huge" merged table
# as this is not feasible.
masterData = MasterDatabase()
