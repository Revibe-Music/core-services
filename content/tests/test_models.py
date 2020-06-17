"""
Created: 12 June 2020
"""

from revibe._helpers.test import RevibeTestCase

from content.models import Genre

# -----------------------------------------------------------------------------


class GenreTestCase(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self._create_song()


    def test_genre_manager_get_or_create(self):
        genres = ['test', 'testing', 'country']

        # create the genres
        for genre in genres:
            Genre.objects.get_or_create(genre)

        # check that they were created
        genre_objs = Genre.objects.filter(text__in=genres)
        self.assertEqual(
            genre_objs.count(), len(genres),
            msg="There are more or less Genre objects than should be"
        )

    def test_genre_manager_get_or_create_case(self):
        txt = "HIp-HoP"

        # create the object
        genre = Genre.objects.get_or_create(txt)

        # test that it's there
        # g = Genre.objects.get(text__exact=txt)
        # self.assertRaises(
        #     Genre.DoesNotExist,
        #     Genre.objects.get,
        #     **{'text__exact': txt}
        # )
        self.assertEqual(
            genre, Genre.objects.get(text__iexact=txt.lower()),
            msg="The object was not created properly"
        )

    def test_genre_manager_get_or_create_object_exists(self):
        txt = 'magic'

        genre = Genre.objects.create(text=txt)

        # test the get_or_create method
        genre2 = Genre.objects.get_or_create(txt)

        # assertions
        self.assertEqual(
            genre, genre2,
            msg="An incorrect object was returned"
        )

