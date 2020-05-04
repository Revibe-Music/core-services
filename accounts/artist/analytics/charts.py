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

