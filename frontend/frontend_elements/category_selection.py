import panel as pn


def category_selection(overview):
    overview_only_cats = overview[overview.data_type == "Ordinal"]

    cat_selector = \
        pn.widgets.Select(name="Category",
                          options=list(overview_only_cats.name),
                          value='')

    return cat_selector
