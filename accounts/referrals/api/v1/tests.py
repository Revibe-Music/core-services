"""
"""

from django.urls import reverse

from revibe._helpers.test import RevibeTestCase

from accounts.referrals.models import Referral

# -----------------------------------------------------------------------------


class ReferralsTestCase(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_superuser()

    def test_add_referrer(self):
        # set up
        url = reverse('my-referrals-list')
        referrer = self.superuser.id
        data = {
            "user_id": referrer
        }

        # send request
        response = self.client.post(url, data, format="json", **self._get_headers())

        # validate response
        self.assert201(response)
    
    def test_add_referrer_fail(self):
        # set up
        url = reverse('my-referrals-list')
        referrer = self.superuser
        data = {
            "user_id": referrer.id
        }

        Referral.objects.create(referrer=referrer, referree=self.user)

        # send request
        response = self.client.post(url, data, format="json", **self._get_headers())

        # validate response
        self.assert409(response)

    def test_get_referrals(self):
        # set up
        url = reverse('my-referrals-list')

        # send request
        response = self.client.get(url, format="json", **self._get_headers())

        # validate response
        self.assert200(response)




