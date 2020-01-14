# Account Tests

# Version 1 Tests

The tests are organized by the organization of the Postman docs, not necessarily by TestCase in the test files.

## User Account

#### Register

#### Login

#### Refresh Token

#### Logout

#### Logout All

## Artist Portal

### Artist Profile

### Uploads

#### Albums

##### Retrieving Albums

Test Get Albums
- Status Code is 200
- Response type is ReturnList
- Each album's uploader's ID is the same as the current artist's ID

##### Uploading Albums

Test Upload Album
- Status Code is 201
- Response type is ReturnDict
- There is a contributors list in the response
- The contributors list is only 1 object
- The 'uploaded_by' ID is the same as the current artist's ID
- The 'uploaded_by' ID the same as the contributor's ID

Test Upload Album - Not Artist
- Status Code is 403

##### Editing Albums

Test Edit Album
- Status Code is 200
- Response type is ReturnDict
- Returned album ID is the same as the sent album ID
- Each field sent changes the value already in the database

##### Deleting Albums

Test Delete Album
- Status Code is 204
- The album is set to 'is_deleted'
- Each song is set to 'is_deleted'
- The album is not available to 'display_objects'
- Each song is not available to 'display_objects'

#### Songs

##### Retrieving Songs

Test Get Songs
- Status Code is 200
- Response type is ReturnList
- The number of objects returned is the same those available by the 'hidden_objects' manager

##### Uploading Songs

Test Upload Song
- Status Code is 201
- Response type is ReturnDict
- Album ID of sent data and returned object are equal
- The Song is not deleted

Test Upload Song - Not Artist
- Status Code is 403

Test Upload Song - Not Authenticated
- Status Code is 401

##### Editing Songs

Test Edit Song
- Status Code is 200
- Response type is ReturnDict
- Sent song ID is the same as the returned object's ID
- Returned title (changed) is the same as the sent title
- Returned title (changed) is the same as the title in the database
- Returned title (changed) is not the same as the title pre-request

Test Edit Song - Not Artist
- Status Code is 403

Test Edit Song - Not Uploading Artist
- Status Code is 403

##### Deleting Songs

Test Delete Song
- Status Code is 204
- Song is not returned when using 'display_objects' manager

Test Delete Song - Not Uploading Artist
- Status Code is 403

### Contributions

#### Albums

#### Songs

##### Retrieving Song Contributions

Test Get Song Contribution
- Status Code is 200
- Response type is ReturnList
- Each returned object's 'artist_id' is the current artist's ID

##### Adding Song Contributions

Test Add Song Contribution
- Status Code is 201
- Response type is ReturnDict

##### Editing Song Contributions

Test Edit Song Contribution
- Status Code is 200
- Response type is ReturnDict
- The Contribution type updated in the database

Test Edit Song Contribution - Not Uploading Artist
- Request 1 - Settings do not permit editing
    - Status Code is 403
- Request 2 - Settings do permit editing
    - Status Code is 200
    - Response type is ReturnDict
    - The contribution type updated in the database

##### Deleting Song Contributions

Test Delete Song Contribution
- Status Code is 204
- The contribution does not exist in the database

Test Delete Song Contribution - Not Uploading Artist
- Status Code is 204
- The contribution does not exist in the database

##### Approving Song Contributions

No tests

## Linked Accounts

No tests

# Version 2 Tests

No endpoints
