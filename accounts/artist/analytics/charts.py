"""
Created: 01 May 2020
Author: Jordan Prechac
"""

from django.db.models import Count, Q

from content.models import Song

from .utils import Chart

# -----------------------------------------------------------------------------

class LineChart(Chart):
    def initial(self):
        self.calculation_function = self._calculate_over_time

    def format_data(self, data):
        # configure y axis
        y_axis_title = getattr(self, 'type_', 'value').title()
        y_axis_config = {
            "title": y_axis_title
        }

        # configure x axis
        x_axis_title = getattr(self, 'time_interval', 'time interval').title()
        x_axis_config = {
            "title": x_axis_title
        }

        # configure chart info
        title = getattr(self, 'title', f'{y_axis_title} by {x_axis_title}')
        description = getattr(self, 'description', None)

        final_data = {
            "title": title,
            "description": description,
            "y_axis_config": y_axis_config,
            "x_axis_config": x_axis_config,
            "data": data,
        }

        return final_data


class CardChart(Chart):
    def initial(self):
        self.calculation_function = self._calculate_static

    def format_data(self, data):
        # configure chart info
        title = getattr(self, 'title', getattr(self, 'type_').title())
        if getattr(self, 'time_period_string', None) != 'all-time':
            title += (' This ' + self.time_period_string.title()) if self.time_period_string != 'day' else " Today"

        # final stuff
        final_data = {
            "title": title,
            "data": data,
        }

        return final_data


class BarChart(Chart):
    def initial(self):
        self.calculation_function = self._calculate_bars

    @property
    def songs(self):
        filter_upload  = Q(uploaded_by=self.artist)
        filter_contrib = Q(contributors=self.artist)

        song_filter = filter_upload
        if self.include_contributions:
            song_filter = song_filter | filter_contrib

        count_string = f"streams__{self.lookup}"
        if self.time_period:
            stream_filter = Q(streams__timestamp__gte=self.time_period)
            value_expression = Count(count_string, distinct=self.lookup_distinct, filter=stream_filter)
        else:
            value_expression = Count(count_string, distinct=self.lookup_distinct)

        songs = Song.hidden_objects \
            .filter(song_filter) \
            .annotate(value=value_expression) \
            .order_by('-value') \
            [:self.num_bars]
        
        return songs

    def format_data(self, data):
        # configure y axis
        y_axis_title = getattr(self, 'type_', 'value').title()
        y_axis_config = {
            "title": y_axis_title,
        }

        # configure x axis
        x_axis_title = f"Songs"
        x_axis_config = {
            "title": x_axis_title,
        }

        # configure chart info
        title = f'Top {self.num_bars} Songs by {y_axis_title}'
        description = getattr(self, 'description', None)

        # final stuff
        final_data = {
            "title": title,
            "description": description,
            "y_axis_config": y_axis_config,
            "x_axis_config": x_axis_config,
            "data": data,
        }

        return final_data

