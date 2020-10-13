import panel as pn

## 
# dashboard_instance = Dashboard()

## servering multiple apps.
pn.serve({'markdown': '# This is a Panel app', 'json': pn.pane.JSON({'abc': 123})})