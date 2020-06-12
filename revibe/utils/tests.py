"""
Created: 12 June 2020
"""

from revibe._helpers.test import RevibeTestCase
from revibe.utils import mail


# -----------------------------------------------------------------------------


class ErrorMailTestCase(RevibeTestCase):
    def setUp(self):
        self.func_name = "`Klass.func`"
        self.exc = Exception("Exception raised!")

    def test_send_error_mail(self):
        to = "test@revibe.tech"

        # call the function
        mail.error_email(to, self.func_name, self.exc)


    def test_send_error_mail_bad_email(self):
        to="test@gmail.com"

        # call the function expecting an issue
        self.assertRaises(
            ValueError,
            mail.error_email,
            *[to, self.func_name, self.exc],
            **{}
        )

    def test_send_mail_bad_email_no_error(self):
        to="test@gmail.com"

        # call the function without raising anything
        mail.error_email(to, self.func_name, self.exc, False)
