import pandas as pd


def wide2long(data, **kwards):
    data['date'] = ['{}-{:02d}-01'.format(y, m) for y, m in data[['year', 'month']].values]
    cols = [c for c in data.columns if c.startswith('topic')]
    data_long = data[cols + ['date']].melt('date', var_name='topic', value_name='mentions')
    data_long = data_long[data_long['mentions'] > 0].groupby(['date', 'topic']).sum().reset_index()
    data_long.reset_index(inplace=True)

    return data_long