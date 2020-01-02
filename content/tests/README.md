# Content Tests

## Artists

#### Artist List

- Status Code is 200
- Number of artists returned is the same as the number of viable artists in the database
- Response type is 'ReturnList'

#### Artist Details

- Status Code is 200
- Response type is 'ReturnDict'
- Requested artist's ID is the same as the one in the request

#### Artist Albums

- Status Code is 200
- Response type is 'ReturnList'
- Number of albums returned is the same as the number of available albums for that artist in the databse

#### Artist Songs

- Status Code is 200
- Response type is 'ReturnList'
- Number of songs returned is the same as the number of available songs for that artist in the database

## Albums

#### Album List

- Status Code is 200
- Response type is 'ReturnList'
- Number of albums returned is the same as the viable albums in the database

#### Album Details

- Status Code is 200
- Response type is 'ReturnDict'

#### Album Songs

- Status Code is 200
- Response type is 'ReturnList'
- Number of songs returned is the same as the available songs for that album in the database

## Songs

## Search

