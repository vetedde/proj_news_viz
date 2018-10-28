from importlib import import_module


class TopicVisualizer():
    def __init__(self, data, topics, topic_names=None):
        """
        data -- dataframe with dates and docs - topics matrix
        topics -- cols to be used as topics
        topic_names -- dict to replace colnames with topic description
        """
        self.data = data
        self.topics = topics

        if topic_names is None:
            topic_names = {t: t for t in topics}

        self.topic_names = topic_names
        self.s = None
        self.chart = None

    def draw(self, title='Topics over time', normed=False):
        pass


class TopicVisualizerPygal(TopicVisualizer):
    def __init__(self, data, topics, topic_names=None):
        TopicVisualizer.__init__(self, data, topics, topic_names)
        self.pygal = import_module('pygal')

    def draw(self, normed=False, title='Topics over time'):
        line_chart = self.pygal\
            .StackedLine(fill=True, show_dots=False,
                         stroke_style={'width': 0.5},
                         style=self.pygal.style.Style(legend_font_size=6),
                         legend_at_bottom=True, x_label_rotation=90,
                         x_labels_major_every=6,
                         show_minor_x_labels=False)

        line_chart.title = title
        line_chart.x_labels = self.data['date'].values

        if normed:
            if self.s is None:
                self.s = self.data[self.topics].sum(axis=1)
            divisor = self.s
        else:
            divisor = 1

        for topic in self.topics:
            vals = self.data[topic].values / divisor
            line_chart.add(self.topic_names[topic], vals)

        line_chart.render_in_browser(is_unicode=True)
        self.chart = line_chart

    def save(self, filename):
        if self.chart is None:
            print('You should draw first')
        else:
            self.chart.render_to_file(filename)


class TopicVisualizerPlotly(TopicVisualizer):
    def __init__(self, data, topics, username, api_key, topic_names=None):
        """
        username -- plotly account username
        api_key -- plotly account api key
        """
        TopicVisualizer.__init__(self, data, topics, topic_names)

        self.py = import_module('plotly.plotly')
        self.go = import_module('plotly.graph_objs')
        self.pt = import_module('plotly.tools')

        self.pt.set_credentials_file(username=username, api_key=api_key)

    def draw(self, title='Topics over time', normed=False):
        # TODO: add normalization

        plotdata = [{'x': self.data['date'].values,
                     'y': self.data[topic].values,
                     'stackgroup': 'one',
                     'mode': 'none',
                     'type': 'scatter',
                     'name': self.topic_names[topic]}
                    for topic in self.topics]

        layout = {
            'autosize': True,
            'showlegend': True,
            'xaxis': {
             'autorange': True,
             'type': 'date',
             "rangeselector": {"buttons": [{'count': 1,
                                            'label': '1m',
                                            'step': 'month',
                                            'stepmode': 'backward'},
                                            {'count': 6,
                                             'label': '6m',
                                             'step': 'month',
                                             'stepmode': 'backward'},
                                            {'step': 'all'}]},
             'rangeslider': {'visible': True}
            },
            "yaxis": {
                "autorange": True,
                "type": "linear"
            }
        }

        fig = self.go.Figure(data=plotdata, layout=self.go.Layout(layout))
        self.py.plot(fig, filename=title, auto_open=True)
