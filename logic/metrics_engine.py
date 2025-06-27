
import pandas as pd

def compute_metric(df, metric, store=None, period=None):
    data = df[df['Metric'] == metric]
    if store:
        data = data[data['Store'] == store]
    if period:
        data = data[data['Month'].isin(period)]
    return data.groupby(['Month', 'Store'])['Amount'].sum().reset_index()
