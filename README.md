# package_analyzer
A streamlit app and libs to format loan packages from different lenders and combine into a consistent loantape
___
### to-dos
-- backend

test current user experience --> break it

    1) The Notional GTD Balance column saves in a very odd way as a .csv file from excel.
    I'm manually editing it in visual studio code.
    I'll need to make a csv script to go in and format the actual .csv on upload. I'll have to think about how to write that. I think I'll have to create a type of error and then a specific handler for it, because it's just strange.

finalize loantape class --> create ColResolvers where needed

combine different loan tapes --> simple concat if formatting is done 

build formatters --> add column number and date formatting to abstract base class

-- frontend

build strats.py and paginate streamlit app

build download buttons 

add openpyxl code
