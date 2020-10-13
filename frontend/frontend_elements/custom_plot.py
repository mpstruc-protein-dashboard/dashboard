import panel as pn
import altair as alt

# plot logic. this is going to be the biggest nightmare of all times.
#
#


def mark_type_selector():
    mark_type_selector = pn.widgets.Select(name="mark_type", options=['area', 'bar', 'line', 'image', 'trail',
                                                                      'point', 'text', 'tick', 'rect', 'rule',
                                                                      'circle', 'square', 'geoshape'], values="point")
    return mark_type_selector


def create_custom_plot(x_axis, y_axis, data_type, mark_type):
    df = ...
    # -TODO create a selection for the category selection.
    # this should be optionally.
    # category = category_selector.value
    altChart = \
        alt.Chart(data=df,
                  mark_type=mark_type_selector.value)\
        .encode(
            x=alt.X(),
            y=y_axis,
            # color = category,
        )
    return altChart


alt.Chart().
