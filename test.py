import pandas as pd
import numpy as np
import panel as pn
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvas


data = pd.read_csv('occupancy_data/datatest.txt')
data['date'] = data.date.astype('datetime64[ns]')
data = data.set_index('date')


def mpl_plot(avg, highlight):
    fig = Figure()
    FigureCanvas(fig)  # not needed in mpl >= 3.1
    ax = fig.add_subplot()
    avg.plot(ax=ax)
    if len(highlight):
        highlight.plot(style='o', ax=ax)
    return fig


window = pn.widgets.FloatSlider(name='window', start=10, end=90, step=1)
sigma = pn.widgets.FloatSlider(name='sigma', start=10, end=30, step=1)


@pn.depends(window.param.value, sigma.param.value)
def find_outliers(window, sigma):
    variable = 'Temperature'
    avg = data[variable].rolling(window=window).mean()
    residual = data[variable] - avg
    std = residual.rolling(window=window).std()
    outliers = (np.abs(residual) > std * sigma)
    return mpl_plot(avg, avg[outliers])


dashboard = pn.Row(pn.Column(window, sigma), find_outliers)
dashboard.show(threaded=True)
