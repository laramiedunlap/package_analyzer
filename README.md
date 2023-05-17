# package_analyzer
A streamlit app and libs to format loan packages from different lenders and combine into a consistent loantape
___
### to-dos
-- backend
Known bugs:
1) Cannot upload multiple packages of the same format --> collision on a key. Two dataframes need to be concated inside the `format_columns` method on the `LoanTape` class

To-dos:

Add method to combine all the LoanTape.raw_dfs, create option in streamlit app to combine or post to database as seperate packages

Add column methods to calculate all columns


