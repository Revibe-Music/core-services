"""
Created: 01 May 2020
Author: Jordan Prechac
"""

from django.db.models import Count, Q
from django.utils import timezone

import datetime

from revibe.contrib.queries.functions import Year, Month, Week, Day, Hour
from revibe._errors import network
from revibe.exceptions import db

from administration.models import ArtistAnalyticsCalculation
from administration.utils.models import retrieve_calculation, retrieve_variable
from content.models import Album, Song
from metrics.models import Stream
from music.models import Library, LibrarySong, Playlist, PlaylistSong

from .serializers import DashboardSongSerializer

# -----------------------------------------------------------------------------

class Chart:
    def __init__(self, artist, type_, include_contributions=False, time_period=None, time_interval=None, num_bars=None, distinct=None, **kwargs):
        self.initial()

        self.artist = artist
        self.type_ = type_

        # configure lookup stuff
        self._lookup()
        field_options = {
            "albums": {
                "time_field": "uploaded_date",
                "related_song_field": "album"
            },
            "libraries": {
                "related_song_field": "library_songs",
            },
            "librarysongs": {
                "time_field": "date_saved",
                "related_song_field": "song_to_library",
            },
            "playlists": {
                "time_field": "date_created",
                "related_song_field": "playlist_songs",
            },
            "playlistsongs": {
                "time_field": "date_saved",
                "related_song_field": "song_to_playlist",
            },
            "streams": {
                "time_field": "timestamp",
                "related_song_field": "streams",
            },
            "songs": {
                "time_field": "date_created",
            },
        }
        self.time_field = field_options.get(self.calculation.root_object, None).get('time_field', None)
        self.related_song_field = field_options.get(self.calculation.root_object, None).get('related_song_field', None)

        self.include_contributions = include_contributions
        self.num_bars = num_bars if num_bars else retrieve_variable('artist-dashboard_bar-chart_num-bars', 5, output_type=int)

        self.get_time_period(time_period)
        self.get_time_interval(time_interval)

        self.root_object = getattr(self, self.calculation.root_object)
        self.use_distinct = distinct if distinct else self.calculation.distinct

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
        filter_upload  = Q(uploaded_by=self.artist)
        filter_contrib = Q(contributors=self.artist)

        song_filter = filter_upload
        if self.include_contributions:
            song_filter = song_filter | filter_contrib

        songs = Song.hidden_objects \
            .filter(song_filter)
        
        return songs

    @property
    def libraries(self):
        lib_filter = {
            "platform": "Revibe",
            "songs__id__in": self.songs,
            # "library_to_song__song__in": self.artist.song_uploaded_by,
        }

        if self.time_period:
            lib_filter['library_to_song__date_saved__gte'] = self.time_period

        libraries = Library.objects.filter(**lib_filter).distinct()

        return libraries

    @property
    def librarysongs(self):
        lsong_filter = {
            "song__id__in": self.songs,
        }

        if self.time_period:
            lsong_filter['date_saved__gte'] = self.time_period
        
        librarysongs = LibrarySong.objects.filter(**lsong_filter).distinct()

        return librarysongs

    @property
    def playlists(self):
        plist_filter = {
            "songs__id__in": self.songs,
        }

        if self.time_period:
            plist_filter['playlist_to_song__date_saved__gte'] = self.time_period
        
        playlists = Playlist.objects.filter(**plist_filter).distinct()

        return playlists

    @property
    def playlistsongs(self):
        psong_filter = {
            "song__id__in": self.songs,
        }

        if self.time_period:
            psong_filter['date_saved__gte'] = self.time_period
        
        playlistsongs = PlaylistSong.objects.filter(**psong_filter).distinct()

        return playlistsongs

    @property
    def albums(self):
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
            intervals.update({op[0]: op[1](self.time_field)})
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
        month_3 = now - datetime.timedelta(days=30*3)
        month_6 = now - datetime.timedelta(days=30*6)
        year = now - datetime.timedelta(days=365)

        return {
            "day": today,
            "week": week,
            "month": month,
            "month_3": month_3,
            "month_6": month_6,
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

    def _lookup(self):
        _ = retrieve_calculation(self.type_)
        if _ == None:
            raise ArtistAnalyticsCalculation.DoesNotExist(f"Cannot find calculation for type '{self.type_}'")
        self.calculation = _
        return self.calculation

    def _calculate(self):
        # actually create the graphs n shit
        try:
            func = getattr(self, 'calculation_function', self.default_calc)
        except db.AnnotationError as e:
            # probably an issue with a .annotate() somewhere
            raise e
        except Exception as e:
            print("Uh oh spaghettio")
            raise e

        data = func()
        return self.format_data(data)

    def _calculate_over_time(self):
        annotation = {
            self.calculation.name: self.calculation.calculation(self.calculation.lookup, distinct=self.use_distinct)
        }

        try:
            numbers = self.root_object \
                .annotate(
                    **self.time_interval_annotation
                ) \
                .values(*self.time_interval_values) \
                .order_by(*self.time_interval_values) \
                .annotate(**annotation)
        except KeyError as e:
            raise db.AnnotationError(str(e))

        return numbers
    default_calc = _calculate_over_time

    def _calculate_static(self):
        aggregation = {
            self.calculation.name: self.calculation.calculation(self.calculation.lookup, distinct=self.use_distinct)
        }

        try:
            numbers = self.root_object \
                .aggregate(**aggregation)
        except KeyError as e:
            raise db.AnnotationError(str(e))

        return numbers

    def _calculate_bars(self):
        if self.time_period:
            obj_filter_keys = [self.related_song_field, self.time_field, 'gte'] if self.root_object != Song else [self.time_field, 'gte']
            obj_filter = Q(**{"__".join(obj_filter_keys): self.time_period})
            annotation = {
                self.calculation.name: self.calculation.calculation(
                    '__'.join([self.related_song_field, self.calculation.lookup]),
                    distinct=self.use_distinct,
                    filter=obj_filter
                )
            }
        else:
            annotation = {
                self.calculation.name: self.calculation.calculation(
                    '__'.join([self.related_song_field, self.calculation.lookup]),
                    distinct=self.use_distinct
                )
            }

        try:
            songs = self.songs \
                .annotate(**annotation) \
                .order_by('-' + self.calculation.name) \
                [:self.num_bars]
        except KeyError as e:
            raise db.AnnotationError(str(e))


        context = {"extra_fields": [self.calculation.name]}
        numbers = DashboardSongSerializer(songs, many=True, context=context).data
        return numbers

    def format_data(self, data):
        """
        Override this function to format the data for graphing/display purposes
        """
        return data

    @property
    def data(self):
        return self._calculate()


def format_title(title):
    if title:
        s = title.title().replace('_', ' ').replace('Num', '').strip()
        return s
    return title
