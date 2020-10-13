import panel as pn


# create UI Element that allows to chose an Data-Element for an Axis.
# axis name should be x or y.
# multiple selection value stems from another UI element prior to this
# element.
def axis_selector(axis_name, multi_select_value):
    axis_picker = \
        pn.widgets.Select(name='{}-Axis'.format(axis_name),
                          options=multi_select_value,
                          value="")
    return axis_picker
