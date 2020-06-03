"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from revibe.exceptions.api import ServerError

from surveys.exceptions import SurveyException

# -----------------------------------------------------------------------------

class BaseSurveyAPIException(
        ServerError,
        SurveyException
    ):
    pass
