# Introduction

# Models

## Variable

The Variables model exists to allow Revibe staff and administrators to change the behavior of various pieces of the service without having to update the app or API. 

### Browse Variables

There are a certain set of variables that have the boolean 'browse' as True. These variables, as the name states, change the behavior of the browse page, specifically which sections of the browse page to show. Not all variables starting with "browse_" are considered 'browse' variables, "browse_time_period" for example. A browse variable **must** be one of those variables that allows or denies a section from appearing in the page. 

