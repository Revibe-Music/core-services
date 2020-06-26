"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from django.urls import reverse
from django.core import mail

from revibe._helpers import status
from revibe._helpers.test import RevibeTestCase

from surveys.models import ArtistOfTheWeek
from surveys.models import Contact

# -----------------------------------------------------------------------------

class ArtistOfTheWeekTestCase(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self._get_artistoftheweek()

    def test_post_application(self):
        url = reverse('artistoftheweek-application-list')
        data = {
            "promotion_ideas": "Shit could be so dope!",
        }

        # send the request
        response = self.client.post(url, data, format="json", **self._get_headers(artist=True))

        # validate the response
        self.assert201(response)

    def test_get_applications(self):
        url = reverse('artistoftheweek-application-list')

        # send the request
        response = self.client.get(url, format="json", **self._get_headers(artist=True))

        # validate the response
        self.assert200(response)
        self.assertReturnList(response)
    
    def test_get_application_detail(self):
        app = ArtistOfTheWeek.objects.filter(user=self.artist_user).first()
        url = reverse('artistoftheweek-application-detail', args=[app.id])

        # send the request
        response = self.client.get(url, format="json", **self._get_headers(artist=True))

        # validate the response
        self.assert200(response)
        self.assertReturnDict(response)

    def test_get_applications_not_artist(self):
        url = reverse('artistoftheweek-application-list')

        # send the request
        response = self.client.get(url, format="json", **self._get_headers())

        # validate the response
        self.assert403(response)

class TestContact(RevibeTestCase):
    """ Testing contact model """

    def setUp(self):
        self._get_application()
        Contact.objects.create(
            first="test-first",
            last="test-last",
            subject="test-subject",
            email="test-email@gmail.com",
            message="wow. incredible.",
        )
        self._get_user()
    
    def test_first_max_length(self):
        contact = Contact.objects.first()
        max_length = contact._meta.get_field('first').max_length
        self.assertEquals(max_length, 100)
    
    def test_last_max_length(self):
        contact = Contact.objects.first()
        max_length = contact._meta.get_field('last').max_length
        self.assertEquals(max_length, 100)
    
    def test_email_max_length(self):
        contact = Contact.objects.first()
        max_length = contact._meta.get_field('email').max_length
        self.assertEquals(max_length, 250)
    
    def test_subject_max_length(self):
        contact = Contact.objects.first()
        max_length = contact._meta.get_field('subject').max_length
        self.assertEquals(max_length, 250)

    def test_submit_contact(self):
        """
        Ensures creation of a contact object/model is possible.
        """
        # data
        data = {
            "first": "test-first",
            "last": "test-last",
            "subject": "test-subject",
            "email": "test-email@gmail.com",
            "message": "wow. incredible.",
        }
        # send request
        response = self.client.post("/api/v1/surveys/contact/", data, format="json", **self._get_headers())
        self.assert201(response)
    
    def test_submit_contact_no_message(self):
        """
        Creation of a contact model is not possible without a message.
        **should fail**
        """
        # data
        data = {
            "first": "test-first",
            "last": "test-last",
            "subject": "test-subject",
            "email": "test-email@gmail.com",
        }
        # send request
        response = self.client.post("/api/v1/surveys/contact/", data, format="json", **self._get_headers())
        self.assert400(response)
    
    def test_email(self):
        """
        Test case for delivering email from contact submission.
        """
        mail.send_mail(
            'test-subject',
            'wow. incredible',
            'test-email@gmail.com',
            ['to-test-email@gmail.com'],
            fail_silently=False
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test-subject')


