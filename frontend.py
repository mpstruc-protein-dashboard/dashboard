import panel as pn
import hvplot.pandas

## 
dashboard_instance = Dashboard()

## servering multiple apps.
pn.serve({'markdown': '# This is a Panel app', 'json': pn.pane.JSON({'abc': 123})})