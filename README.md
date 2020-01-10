# Revibe API
Welcome to the Revibe API repository.


# Apps

The Revibe API is broken into 5 apps, **Accounts**, **Content**, **Music**, **Metrics**, and **Administration**. Each app is designed to contain the basic funcitonality for individual components of Revibe's business model.

You may notice in the published Revibe API documentation that these 5 areas are referred to as *namespaces*. The reason for the difference is that Django refers to these individual components as apps, so that's the terminology used here; but outside of Django, 'apps' is a very general term, which is why we avoid using it in published documentation.

## Accounts

## Content

## Music

## Metrics

## Administration


# Conventions and Standards

All parts of this API follow a set of rules that dictate things like code organization, url naming, serializer purposing, HTTP status codes, and more; for the simple reason of having a consistent set of standards to make API consumption easy for Revibe's front-end development and continued API development simpler for whichever sorry souls have to pick this up after me. 

## Models

## Serializers

## Platforms

## Views & ViewSets

*Some stuff about views and some stuff about viewsets...*

### Status Codes

1xx- Informational:
- *no convention*

2xx Successful:
- 200 OK - default, request processed successfully
- 201 Created - successfully created an object/instance
- 204 No Content - object/instance successfully deleted

3xx Redirection:
- *no convention*

4xx Client Error:
- 400 Bad Request - default, returned if no other 4xx error was applicable
- 401 Unauthorized - could not identify the current user
- 402 Payment Required - the requested feature is a payed-only feature and cannot be access with the access level of the current user
- 403 Forbidden - user is not permitted to perform the request function
- 404 Not Found - duh
- 409 Conflict - the object attemting to be created already exists, i.e., a user with an artist account creating another
- 415 Unsupported Media Type - the sent file is of an invalid type and cannot be accepted by the server
- 417 Expectation Failed - The sent data is invalid, response *should* contain the error information

5xx - Server Error:
- 500 Internal Server Error: this response will **NEVER** be sent intentionally, this will only be sent when an unknown server error occurs.
- 501 Not Implemented: the requested functionality has not yet been built, but the endpoint infrastructure has been put in place
- 503 Service Unavailable - the requested endpoint cannot be reached in the current environment, this is usually an indication that some kind of AWS resource is only accessible while running the app in the cloud.
- 512 Program Error: basically a 500 error but intentionally not that

### Recording Request Data

All requests in the API have a unique string identifier, called the **Request Code** that is used to track usage of the API. The standard for creating each request's name is "*version*-*app*-*viewset*-*url name*-*request type*". For example, the request to get details about an Album - /v1/content/album/*album_id*/ - is named "v1-content-album-detail-get". 

## URLs

Revibe's API was created with evolution in mind, so the URL configuration has been built to allow for easy versioning in the future. The leading component of every endpoint is the version number; so when we begin developing new endpoints for existing features, old versions of Revibe applications can continue to work on the older endpoints without inhibiting continuing support and development.

## Other

### File Layout

#### Import Statements

The imports for python files are separated into blocks to make it easier to
read. The blocks are: anything Django/DRF related, other python modules, the
logger, anything from the *revibe* module, and anything from any other API app.

### Tests

# Authors

Jordan Prechac - [**jprechac@gmail.com**](mailto:jprechac@gmail.com "Jordan Prechac")