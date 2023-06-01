# package_analyzer
A streamlit app and libs to format loan packages from different lenders and combine into a consistent loantape
___
### to-dos
- Paginate app, write up to date col resolves for the existing packages
- Incorporate AWS, create generators to yield streamlit buttons and options 
- Add excel support so users don't have to create a csv
___
### Col resolver methods to add to the ABC
1. Make a version in the abstract base class that will handle the vast majority of datetime conversions from excel
2. Add a class that will convert point expressions of interest to actual
3. Code these to work on an unspecified number of columns
4. add to children classes

