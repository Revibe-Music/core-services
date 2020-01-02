# Music Tests

## Library

#### List Libraries

- Status Code is 200
- Response is type 'ReturnList'
- Length of response is 2
    - *The user that is created only has YouTube and Revibe for libraries*

#### Save Revibe Song to Library

- Status Code is 201
- Response is type 'ReturnDict'
- The Song that is returned has the same ID as the one that was sent
- The song that the request-data song_id has the same ID as the same object saved in the current library (queries DB after requets to get library)

## Playlist

#### List Playlists

- Status Code is 200
- Response is type 'ReturnList'
- Length of response is the same as the number of playlists in the DB (both based on current user)
- If there are playlists in the response, checks that the user on each is the same as the current user

#### Create Playlist

- Status Code is 201
- The playlist name is the same as the one that was sent
- Checks database for the number of playlists and compares to that before the request was made

#### Adding a Song to a Playlist

- Status Code is 201
- Checks database for the number of songs in the playlist and compares to that before the request was made

#### Deleting a Song from a Playlist

- Status Code is 204
- Checks databse for the number of songs in the playlist and compares to that before the request was made
