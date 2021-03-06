from django.db.models import Count, Q
from rest_framework import views, viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

import random

from revibe.pagination import CustomLimitOffsetPagination
from revibe.permissions.scopes.third_party import content
from revibe.viewsets import *
from revibe.utils.params import get_url_param
from revibe._errors.network import ProgramError, ExpectationFailedError, PageUnavailableError, BadRequestError
from revibe._helpers import const, responses
from revibe._helpers.platforms import get_platform

from accounts.permissions import TokenOrSessionAuthentication
from accounts.models import SocialMedia
from content import browse
from content.mixins import V1Mixin
from content.models import *
from content.serializers import v1 as ser_v1
from content.utils import search
from content.utils.models import get_tag
from metrics.models import ArtistPublicURLClick
from metrics.utils.models import record_search_async
from payments.serializers.v1 import ThirdPartyDonationSerializer

# -----------------------------------------------------------------------------


class ArtistViewset(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.ArtistSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"], content.read_content, content.read_artists],
        "POST": [["ADMIN"],["first-party"]],
    }

    def create(self, request, *args, **kwargs):
        pass
    def update(self, request, *args, **kwargs):
        pass
    def destroy(self, request, *args, **kwargs):
        pass

    def get_queryset(self):
        return self.platform.Artists

    @action(detail=True, url_name="cnt-artist-albums")
    def albums(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.Albums.filter(uploaded_by=artist)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.AlbumSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.AlbumSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-songs")
    def songs(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.Songs.filter(uploaded_by=artist)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.SongSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.SongSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-album-contributions")
    def album_contributions(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.AlbumContributors.filter(artist=artist, primary_artist=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.AlbumContributorSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.AlbumContributorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-song-contributions")
    def song_contributions(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.SongContributors.filter(artist=artist, primary_artist=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.SongContributorSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.SongContributorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path="top-songs", url_name="top-songs")
    def top_songs(self, request, pk=None):
        # return Response(status=status.HTTP_501_NOT_IMPLEMENTED) # temp
        artist = self.get_object()

        annotation = Count('streams__id')
        ordering = '-count'

        queryset = self.platform.Songs.filter(uploaded_by=artist) \
            .annotate(count=annotation) \
            .order_by(ordering)[:10]

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.SongSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.SongSerializer(queryset, many=True)
        return responses.OK(serializer=serializer)

    @action(detail=True, methods=['post'], url_path="donate/third-party", url_name='donate-third-party')
    def donate_third_party(self, request, pk=None, *args, **kwargs):
        artist = self.get_object()

        kwargs['context'] = self.get_serializer_context()
        kwargs.pop('pk', None)

        serializer = ThirdPartyDonationSerializer(data=request.data, *args, **kwargs)
        if not serializer.is_valid():
            raise ExpectationFailedError(detail=serializer.errors)

        instance = serializer.save()

        return responses.CREATED()


class AlbumViewSet(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.AlbumSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"], ['first-party'], content.read_content, content.read_album],
    }

    def get_queryset(self):
        return self.platform.Albums
    
    @action(detail=True)
    def songs(self, request, pk=None, url_name="album-songs"):
        album = self.get_object()
        queryset = self.platform.Songs.filter(album=album).order_by('album_order')
        serializer = ser_v1.SongSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SongViewSet(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.SongSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"], content.read_content, content.read_song],
    }

    def get_queryset(self):
        return self.platform.Songs


class MusicSearch(GenericPlatformViewSet):
    platform = 'Revibe'
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"], content.read_content, content.read_search],
    }

    def initialize_request(self, request, *args, **kwargs):
        """
        """
        # do the normal thing
        request = super().initialize_request(request, *args, **kwargs)

        # record the search
        record_search_async(request.user, get_url_param(request.query_params, 'text'))

        return request

    def list(self, request, *args, **kwargs):
        params = request.query_params

        if 'text' not in params.keys():
            return Response({"error": "'text' must be included as a parameter in this request"}, status=status.HTTP_417_EXPECTATION_FAILED)
        text = params['text']
        
        result = {}

        t = params.get('type', False)
        if t:
            if t not in ['songs','albums','artists']:
                return Response({'error': "parameter 'type' must be 'songs', 'albums', or 'artists'."}, status=status.HTTP_417_EXPECTATION_FAILED)

        if (t == 'songs') or (not t):
            # result['songs'] = ser_v1.SongSerializer(self.search_songs(text), many=True).data
            result['songs'] = ser_v1.SongSerializer(search.search_songs(text), many=True).data
        if (t == 'albums') or (not t):
            # result['albums'] = ser_v1.AlbumSerializer(self.search_albums(text), many=True).data
            result['albums'] = ser_v1.AlbumSerializer(search.search_albums(text), many=True).data
        if (t == 'artists') or (not t):
            # result['artists'] = ser_v1.ArtistSerializer(self.search_artists(text), many=True).data
            result['artists'] = ser_v1.ArtistSerializer(search.search_artists(text), many=True).data

        return Response(result ,status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'], url_path="tags", url_name="search-tags")
    def tags(self, request, *args, **kwargs):
        params = request.query_params

        if 'text' not in params:
            raise ExpectationFailedError("Param 'text' not in query params")
        text = get_url_param(params, 'text')
        content = get_url_param(params, 'content')
        if (content == None) or (content not in ['songs', 'albums']):
            content = 'songs'
        
        objs = self.search_tags(text, content)
        data = {
            content: objs.data
        }

        return responses.OK(data=data)

    def search_tags(self, text, obj, *args, **kwargs):
        """
        return songs/albums by the tag that was sent
        """
        # get the tag
        tag = get_tag(text)
        objs = []

        # which object to search
        if obj.lower() == 'songs':
            objs = ser_v1.SongSerializer(tag.songs.all(), many=True)
        elif obj.lower() == 'albums':
            objs = ser_v1.AlbumSerializer(tag.albums.all(), many=True)
        else:
            raise ProgramError("Must send either 'songs' or 'albums' to 'search_tags'.")

        return objs

    @action(detail=False, methods=['get'], url_path="artists", url_name="search-artists")
    def artists(self, request, *args, **kwargs):
        """
        Special endpoint just for artists to be able to search other artsists
        when adding contributors.
        """
        params = request.query_params

        if 'text' not in params:
            return responses.SERIALIZER_ERROR_RESPONSE(detail="missing parameter 'text'.")
        text = params['text']

        artists = self.exclusive_artist_search(text)
        serializer = ser_v1.ArtistSerializer(artists, many=True)

        return responses.OK(serializer=serializer)

    def exclusive_artist_search(self, text, *args, **kwargs):
        assert (text) and (text != " "), "method 'exclusive_artist_search' requires a search value."
        limit = const.SEARCH_LIMIT
        # perform search
        if len(text) == 1:
            # artist name begins with the search value
            artists = self.platform.Artists.filter(name__istartswith=text).distinct()
        else:
            # artist name is exactly the search value
            artists = self.platform.Artists.filter(name__iexact=text).distinct()
            if artists.count() >= limit:
                return artists[:limit]
            
            # artist name contains the search value
            artists = artists | self.platform.Artists.filter(name__icontains=text).distinct()
            artists = artists.distinct()
            if artists.count() >= limit:
                return artists[:limit]
            
        return artists[:limit]


class Browse(GenericPlatformViewSet):
    platform = 'Revibe'
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"], content.read_content, content.read_browse]
    }

    def list(self, request, *args, **kwargs):
        page = browse.full_browse_page()

        return responses.OK(data=page)


    @action(detail=False, methods=['get'], url_path=r"(?P<endpoint>[a-zA-Z0-9-]+)")
    def browse_endpoint(self, request, endpoint=None, *args, **kwargs):
        if endpoint==None:
            raise ProgramError(f"Improperly configured: no endpoint in function 'browse_endpoint' in class '{self.__class__.__name__}'")
        # replace '-' with '_'
        endpoint = endpoint.replace('-','_')

        # get the actual browse function
        func = getattr(browse, endpoint, None)
        if func == None:
            raise BadRequestError(f"No browse endpoint found for value '{endpoint}'")

        # get the params
        params = request.query_params
        options = {}
        optional_params = ['time_period', 'limit']
        for p in optional_params:
            param = get_url_param(params, p, type_=(int if p=='limit' else None))
            if param != None:
                options.update({p:param})

        # return the proper data
        data = func(**options)
        return responses.OK(data=data)


class PublicArtistViewSet(ReadOnlyPlatformViewSet):
    platform = 'Revibe'
    queryset = Artist.objects.filter(
        platform='Revibe'
    )
    serializer_class = ser_v1.ArtistSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [permissions.AllowAny]

    cashapp_or_venmo = Q(artist_profile__social_media__service=SocialMedia._cashapp_text) | Q(artist_profile__social_media__service=SocialMedia._venmo_text)
    donate_queryset = queryset.filter(cashapp_or_venmo).distinct()
    
    public_filter = Q(artist_profile__allow_revibe_website_page=True)
    public_queryset = queryset.filter(public_filter).distinct()

    def list(self, request, *args, **kwargs):
        params = request.query_params
        artist_url = get_url_param(params, "artist", *args, **kwargs)
        if artist_url != None:
            artist = self.get_artist(artist_url, queryset=self.public_queryset)
            serializer = ser_v1.ArtistSerializer(artist)

            # record that their page was looked at
            url_click = ArtistPublicURLClick.objects.create(artist=artist)
            url_click.save()

        else:
            page = self.paginate_queryset(self.public_queryset)
            if page is not None:
                serializer = ser_v1.ArtistSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = ser_v1.ArtistSerializer(self.public_queryset, many=True)
            

        return responses.OK(serializer=serializer)

    def retrieve(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        id_or_url = self.kwargs[lookup_url_kwarg]

        artist = self.get_artist(id_or_url)

        serializer = ser_v1.ArtistSerializer(artist)

        return responses.OK(serializer=serializer)

    def get_artist(self, id_or_url, queryset=None):
        q_object = Q(artist_profile__public_url=id_or_url) | Q(id=id_or_url)
        queryset = self.queryset if queryset == None else queryset
        try:
            artist = queryset.get(q_object)
        except Artist.DoesNotExist:
            raise PageUnavailableError("No artist found")

        return artist

    @action(detail=False, methods=['get'], url_path="artists/donate", url_name="artists-donate")
    def artists_donate(self, request, *args, **kwargs):
        # re-establish the queryset
        queryset = self.donate_queryset

        params = request.query_params
        artist_url = get_url_param(params, "artist", *args, **kwargs)

        # list them all
        if artist_url == None:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ser_v1.ArtistSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = ser_v1.ArtistSerializer(queryset, many=True)
        else: # get details on one artist
            return self.artists_donate_detail(request, artist_id=artist_url)

        return responses.OK(serializer=serializer)

    @action(detail=False, methods=['get','post'], url_path=r"artists/donate/(?P<artist_id>[a-zA-Z0-9-]+)", url_name="artist-donate-detail")
    def artists_donate_detail(self, request, artist_id=None, *args, **kwargs):
        queryset = self.donate_queryset
        artist = self.get_artist(artist_id, queryset=queryset)

        if request.method == 'GET':
            # get artist details
            serializer = ser_v1.ArtistSerializer(artist)
            return responses.OK(serializer=serializer)

        elif request.method == 'POST':
            kwargs['context'] = self.get_serializer_context()
            serializer = ThirdPartyDonationSerializer(request.data, *args, **kwargs)

            data = request.data
            data['recipient'] = str(artist.id)

            serializer = ThirdPartyDonationSerializer(data=request.data, *args, **kwargs)
            if not serializer.is_valid():
                raise ExpectationFailedError(detail=serializer.errors)

            instance = serializer.save()

            return responses.CREATED()

        raise ProgramError("Could not identify request method")


