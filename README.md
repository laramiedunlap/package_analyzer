# package_analyzer (1.0.0)
A streamlit app and libs to format loan packages from different lenders and combine into a consistent loantape
___
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
1. Add method to loan tape that concats all the user data, or a front end method that allows them to select or deselect loan tapes before concat (may just have them remove and remake).
2. Create a stratifications.py file that can be imported and run to generate all the data for the stratifications tab on the front end. 
3. write front end to render and format the data
___
### Summary page
1. Figure out which components from the summary page would be helpful to have
___
___
## Version 1.1.0 features to add
- Incorporate AWS, create generators to yield streamlit buttons and options 
- Add excel support so users don't have to create a csv

