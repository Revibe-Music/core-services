"""
Created: 17 Mar. 2020
Author: Jordan Prechac
"""

from django.db import models
from django.db.models import Func

# -----------------------------------------------------------------------------

class Hour(Func):
    function = 'EXTRACT'
    template = '%(function)s(HOUR from %(expressions)s)'
    output_field = models.IntegerField()

class Day(Func):
    function = 'EXTRACT'
    template = '%(function)s(DAY from %(expressions)s)'
    output_field = models.IntegerField()

class Week(Func):
    function = 'EXTRACT'
    template = '%(function)s(WEEK from %(expressions)s)'
    output_field = models.IntegerField()

class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()

class Year(Func):
    function = 'EXTRACT'
    template = '%(function)s(YEAR from %(expressions)s)'
    output_field = models.IntegerField()

