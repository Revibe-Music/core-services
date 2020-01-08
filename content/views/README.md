# Content Views

## Version 1

### Artists

### Albums

### Songs

### Search

Version 1 search function is broken into separate pieces for each of the kinds of content being searched for.
Each type of content has it's own search hierarchy for returning objects.

#### Artsit Seach

The Artist search hierarchy is:
1. Artists whose name is exactly the search value.

##### Special Artist Search

There is a special Artist-Search endpoint for retrieving artists in a way/format that is more optimal for finding contributors for content.
This endpoint is only designed to be used in the Artist Portal in the 'Add Contributors' areas. 

The hierarchy for this artist search is:
1. If the search text is only 1 character, find artist's whose name starts with that character. Returns after that.
2. Finds artists whose name is exactly the current search value.
3. Artist's whose name contains the search value.

#### Albums Search

#### Song Search

#### Playlist Search

Not implemented.
