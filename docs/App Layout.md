# Overview

...


# Directories

## Root


| File Name | Purpose |
|--- |--- |
| \_\_init\_\_.py | Marks the folder as a python module. |
| admin.py | Contains the admin classes that populate information in admin portal. All the app's models are registered here |
| apps.py | Standard Django app configuration file | 
| exceptions.py | Define standard exceptions for the app |
| managers.py | Define the app's model managers. |
| models.py | Define the app's database models here. |
| tests.py | Write high-level tests for the app. |
| urls.py | Define the app's url structure |
| views.py | Write Django views |

Sub-modules
- api
- exceptions
- migrations
- permissions
- utils

## api

The API module contains all the logic for the app's API connections. The API module contains additionals folders for each version of the API.

| File Name | Purpose | 
|--- |--- |
| \_\_init\_\_.py | Make the folder a python module |
| serializers.py | Base serializers that can be used across all versions of the API. Seldom used for anything important |
| urls.py | All the API urls for this app |

Sub-modules
- _version number_

