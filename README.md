<div id="top"></div>


<!-- PROJECT LOGO -->
<br />
<div align="center">

<a href="https://github.com/Revibe-Music">
    <img src="./RevibeLogo.png" alt="Revibe Logo" ></a>

  <h3 align="center">Revibe Core Services</h3>
<!-- PROJECT SHIELDS -->
<div align="center">
  
[![Contributors][contributors-shield]][contributors-url] [![MIT License][license-shield]][license-url] ![archive-shield] ![top-languages-shield] ![languages-count-shield]
</div>
  Revibe was intended to provide an all-in-one business solution to independent artists, along with a proprietary streaming app that was tailored to underground hip-hop fans. The core services ran on AWS and powered the entire Revibe web and mobile platform.
  <p align="center">
    <!-- <a href="#demos">View Docs</a>
    · -->
    <a href="#contact">Contact</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<!-- <details>
  <summary>Table of Contents</summary>

- [Features](#features)
  - [Tech Highlights](#tech-highlights)
- [Tech Specs](#tech-specs)
  - [Backend](#backend)
  - [Patterns](#patterns)
- [Demos](#demos)
  - [Videos](#videos)
  - [Screenshots](#screenshots)
- [Contributors](#contributors)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)
- [TO DO](#to-do)
</details> -->


# Conventions and Standards

All parts of this API follow a set of rules that dictate things like code organization, url naming, serializer purposing, HTTP status codes, and more; for the simple reason of having a consistent set of standards to make API consumption easy for Revibe's front-end development and continued API development simpler for whichever sorry souls have to pick this up after me. 


### Status Codes

1xx- Informational:
- *no convention*

2xx Successful:
- 200 OK - default, request processed successfully
- 201 Created - successfully created an object/instance
- 204 No Content - object/instance successfully deleted
- 208 Already Reported - the object requesting to be made already exists. For example, adding a song to a playlist that already has that song

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

## Recording Request Data

All requests in the API have a unique string identifier, called the **Request Code** that is used to track usage of the API. The standard for creating each request's name is "*version*-*app*-*viewset*-*url name*-*request type*". For example, the request to get details about an Album - /v1/content/album/*album_id*/ - is named "v1-content-album-detail-get". 

## URLs

Revibe's API was created with evolution in mind, so the URL configuration has been built to allow for easy versioning in the future. The leading component of every endpoint is the version number; so when we begin developing new endpoints for existing features, old versions of Revibe applications can continue to work on the older endpoints without inhibiting continuing support and development.

## File Uploads

File uploads, such as Album covers or song files, are all stored in [Amazon Simple Storage Service (S3)](https://aws.amazon.com/s3/ "Amazon S3").
Each Artist or Album (or other future objects that have images) can have multiple files related to them. Each object has a subfolder in the S3 bucket, designated by the object's URI. Within that folder, the original image is stored as inputs/original%.*ext*. Any additional files created in post-processing (for example, creating different-sized images for faster load in the mobile app) will be stored in the 'outputs' folder, and further organized by file extension (JPG, WAV, etc.). 

Additional images are stored in the content.Image model, additional audio files are stored in the content.Track model. 

All post-processing of files is handled in a separate thread, so the user will not have to wait for the creation of *n* additional files to receive a good response; however, the user will then also not receive an error if there are issues in creating additional objects. 

## Other

### File Layout

#### Import Statements

The imports for python files are separated into blocks to make it easier to
read. The blocks are: anything Django/DRF related, other python modules, the
logger, anything from the *revibe* module, and anything from any other API app.

### Tests

### Asyncronous Tasks

Docs: [Implementing Celery with Django in AWS Elastic Beanstalk](https://stackoverflow.com/questions/41161691/how-to-run-a-celery-worker-with-django-app-scalable-by-aws-elastic-beanstalk)

# Authors
Lead Developer - Jordan Prechac - [**jprechac@gmail.com**](mailto:jprechac@gmail.com "Jordan Prechac")
Developer - Riley Stephens

Product Manager - Kayne Lynn

<!-- MARKDOWN LINKS & IMAGES -->

<!-- Project URLS-->
[github-url]: https://github.com/Revibe-Music/core-services
[repo-path]: Revibe-Music/core-services
[logo-path]: https://github.com/Revibe-Music/core-services/blob/main/assets/RevibeLogo.png

<!-- Contributors-->
[contributors-shield]: https://img.shields.io/github/contributors/Revibe-Music/core-services.svg?style=for-the-badge
[contributors-url]: https://github.com/Revibe-Music/core-services/graphs/contributors

<!-- License-->
[license-shield]: https://img.shields.io/github/license/Revibe-Music/core-services.svg?style=for-the-badge
[license-url]: https://github.com/Revibe-Music/core-services/blob/main/LICENSE.txt

<!-- Build Status-->
[archive-shield]: https://img.shields.io/static/v1?label=status&message=archived&color=red&style=for-the-badge

<!-- Languages-->
[top-languages-shield]: https://img.shields.io/github/languages/top/Revibe-Music/core-services.svg?style=for-the-badge
[languages-count-shield]: https://img.shields.io/github/languages/count/Revibe-Music/core-services?style=for-the-badge

<!-- Stars-->
[stars-shield]: https://img.shields.io/github/stars/Revibe-Music/core-services.svg?style=for-the-badge
[stars-url]: https://github.com/Revibe-Music/core-services/stargazers

<!-- Forks-->
[forks-shield]: https://img.shields.io/github/forks/Revibe-Music/core-services.svg?style=for-the-badge
[forks-url]: https://github.com/Revibe-Music/core-services/network/members


<!-- Social-->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew