# package_analyzer (1.0.0)
A streamlit app and libs to format loan packages from different lenders and combine into a consistent loantape
___
## Current working process to add a new counter party:
1. For each counterparty excel format, add column mapping values to packages.json (outer key== name/abbr, inner key-val pairs are column mappings from theirs to ours)
2. Add `counterparty_abbr`_resolver child class to column_map.py, add any custom logic that needs to be performed on a column inside the class with a `ColResolver.column_method` decorater. See column_map.py for examples.
3. Write instantiation and orchestration into loantape.py file
4. If counterparty changes or updates column headers, simply add the new key-value pairs to the packages.json file (do not delete old mapping)


## Version 1.0.1 Additions
___
- ~~Paginate app, write up to date col resolves for the existing packages~~
### Col resolver methods to add to the ABC
1. ~~Make a version in the abstract base class that will handle the vast majority of datetime conversions from excel~~
2. ~~Add a method that will convert point expressions of interest to actual~~
3. ~~Code these to work on an unspecified number of columns~~
4. ~~add to children classes~~
___
### Stratifications
1. ~~Add method to loan tape that concats all the user data, or a front end method that allows them to select or deselect loan tapes before concat (may just have them remove and remake).~~
2. Build flexibility into the next step after the user has uploaded and set up their loan tape. Maybe a function that yields streamlit components so that the program doesn't need to know how many loantapes or combinations a user wants
3. Create a stratifications.py file that can be imported and run to generate all the data for the stratifications tab on the front end.
4. write front end to render and format the data
___
### Summary page
1. Figure out which components from the summary page would be helpful to have
___
___
## Version 1.1.0 features to add
- Incorporate AWS 
- Add excel support so users don't have to create a csv


### Context notes and dynamically replacing page content:
    import streamlit as st
    page = st.empty()
    with page:
        content = st.container()
        content.write('Hello!')
        x = content.button('Goobye?')
    if x:
        page.empty()

This code will create an empty one element container called page, the with that page add a content container. Then with that content container, it will write hello, add a button, and when the button is pressed -- remove all the pages content.