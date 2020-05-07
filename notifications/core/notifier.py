"""
Created: 07 May 2020
Author: Jordan Prechac
"""


from django.core.mail import send_mail

# -----------------------------------------------------------------------------

class Notifier:
    def __init__(self, user, artist=False, force=False, *args, **kwargs):
        self.user = user

        self.email = getattr(user.profile, 'email')
        if artist:
            self.artist = getattr(user, 'artist')
            artist_email = getattr(self.artist.artist_profile, 'email', None)
            if artist_email != None:
                self.email = artist_email
    
    # def send()



