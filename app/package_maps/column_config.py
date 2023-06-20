import streamlit as st
import pandas as pd


# NOTE -- These methods are designed to work with specific column names for our format. They do not change frequently (if ever), so the code is coupled to the front end
# It IS possible to write this script in a way that does not need awareness of how the front end named their columns, but that would take MUCH longer to code.

# These are the columns for the finished loan tape
_cols =  ['Pck / Deal','GP#', 'Borrower Name', 'City', 'State', 'SIC / NAICS', 'ADJ', 'Accrual', 'Note Date',
'Note Maturity', 'Int. Paid to Date', 'Loan Spread', 'Loan Rate',
'Strip Rate', 'Original Balance', 'Current Balance', 'Multiple',
'Proceeds', 'Term', 'Age', 'Rmos', 'Industry', 'Prepayment Penalty',
'Term Bucket', 'Industry Bucket', 'Lender']

def add_flare(df:pd.DataFrame)->pd.DataFrame:
    """Add some flare columns -- this is a test method currently"""
    pass


def get_col_config(col_list:list)->dict:
    """Return a dictionary of column configurations to pass to the front end"""
    {'GP#':st.column_config.NumberColumn(format="%d"),
     'SIC / NAICS':st.column_config.NumberColumn(format="%d"),
     'Loan / Spread': st.column_config.NumberColumn(format=":.2%")
     }
    