"""
Created: 01 May 2020
Author: Jordan Prechac
"""

from django.db.models import Count, Q
from django.utils import timezone

import datetime

from revibe.contrib.queries.functions import Year, Month, Week, Day, Hour
from revibe._errors import network

from administration.utils import retrieve_variable
from metrics.models import Stream

from .serializers import DashboardSongSerializer

# -----------------------------------------------------------------------------



class Chart:
    def __init__(self, artist, type_, include_contributions=False, time_period=None, time_interval=None, num_bars=None, **kwargs):
        self.initial()

        self.artist = artist
        # self.type_ = type_
        if type_ not in self._annotation_lookup.keys():
            raise network.BadRequestError(f"Improper type value: '{type_}'")
        self.type_ = type_

        self.include_contributions = include_contributions
        self.num_bars = num_bars if num_bars else retrieve_variable('artist-dashboard_bar-chart_num-bars', 5)

        self.get_time_period(time_period)
        self.get_time_interval(time_interval)

        # configure lookup stuff
        self._lookup_dict = self._annotation_lookup.get(self.type_)
        self.lookup = self._lookup_dict.get('lookup')
        self.lookup_distinct = self._lookup_dict.get('distinct', False)
        self.lookup_calc = self._lookup_dict.get('calc', Count)

        # configure graph options
        options = kwargs.get('options', None)
        if options == None:
            self.use_options = False
        else:
            self.use_options = True
            for key, value in options.items():
                setattr(self, key, value)
    
    def initial(self):
        """
        Function to include import class variables and other things on instantiation.
        Basically it's a safer way to add things to the __init__() method.
        """
        pass

    @property
    def streams(self):
        filter_song_upload  = Q(song__uploaded_by=self.artist)
        filter_song_contrib = Q(song__contributors=self.artist)
        filter_by_time = Q(timestamp__gte=self.time_period)
        
        stream_filter = filter_song_upload
        if self.include_contributions:
            stream_filter = stream_filter | filter_song_contrib
        
        streams = Stream.objects.filter(stream_filter)
        if self.time_period:
            streams = streams.filter(filter_by_time)
        
        return streams

    @property
    def songs(self):
        pass

    def get_time_period(self, time_period):
        periods = self._time_periods
        time_period = time_period if time_period in periods.keys() else 'month'
        self.time_period = periods.get(time_period)
        self.time_period_string = time_period

    def get_time_interval(self, time_interval):
        self.time_interval = self._time_intervals.get(time_interval or 'day')

        # build annotation
        options = (
            ('year', Year),
            ('month', Month), 
            ('day', Day), 
            ('hour', Hour),
        )
        intervals = {}
        values = []
        for op in options:
            intervals.update({op[0]: op[1]('timestamp')})
            values.append(op[0])
            if op[0] == self.time_interval:
                break
        
        self.time_interval_annotation = intervals
        self.time_interval_values = values

    @property
    def _time_periods(self):
        now = timezone.now()
        today = now - datetime.timedelta(days=1)
        week = now - datetime.timedelta(days=7)
        month = now - datetime.timedelta(days=30)
        year = now - datetime.timedelta(days=365)

        return {
            "day": today,
            "week": week,
            "month": month,
            "year": year,
            "all-time": None
        }

    @property
    def _time_intervals(self):
        return {
            "hour": "hour",
            "day": "day",
            "month": "month",
            "year": "year"
        }

    @property
    def _annotation_lookup(self):
        return {
            "listeners": {
                "lookup": "user",
                "distinct": True,
                "bar-name": "num_listeners",
            },
            "streams": {
                "lookup": "id",
                "distinct": False,
                "bar-name": "num_streams",
            }
        }

    def _calculate(self):
        # actually create the graphs n shit
        try:
            func = getattr(self, 'calculation_function', self.default_calc)
        except Exception as e:
            print("Uh oh spaghettio")
            raise e

        data = func()
        return self.format_data(data)

    def _calculate_over_time(self):
        numbers = self.streams \
            .annotate(
                **self.time_interval_annotation
            ) \
            .values(*self.time_interval_values) \
            .order_by(*self.time_interval_values) \
            .annotate(value=self.lookup_calc(self.lookup, distinct=self.lookup_distinct))
        
        return numbers
    default_calc = _calculate_over_time

    def _calculate_static(self):
        numbers = self.streams \
            .aggregate(value=self.lookup_calc(self.lookup, distinct=self.lookup_distinct)) \
        
        return numbers

    def _calculate_bars(self):
        numbers = DashboardSongSerializer(self.songs, many=True).data

        return numbers

    def format_data(self, data):
        """
        Override this function to format the data for graphing/display purposes
        """
        return data

    @property
    def data(self):
        return self._calculate()

