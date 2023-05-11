import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from loantape import LoanTape

def load_excel_file(file):
    wb = load_workbook(file)
    sheet = wb.active
    data = sheet.values
    columns = next(data)[1:]
    df = pd.DataFrame(data, columns=columns)
    return df


st.title("Package File Uploader")

files = st.file_uploader("Upload a csv file (columns and data)", type=["csv"], accept_multiple_files=True)

# These are the columns for the finished loan tape
_cols =  ['Pck / Deal','GP#', 'Days', 'Borrower Name', 'City', 'State', 'SIC / NAICS', 'ADJ', 'Accrual', 'Note Date',
'Note Maturity', 'Int. Paid to Date', 'Loan Spread', 'Loan Rate',
'Strip Rate', 'Original Balance', 'Current Balance', 'Multiple', 
'Proceeds', 'Term', 'Age', 'Rmos', 'Industry', 'Prepayment Penalty',
'Term Bucket', 'Industry Bucket', 'Lender', 'Prepayment Notice']

if st.button('Create Loantape'):

    raw_data = list()
    for f in files:
        raw_data.append(pd.read_csv(f))
        
    loan_tape = LoanTape(clean_columns=_cols, data=raw_data)
    
    loan_tape.format_columns()
    test_df = loan_tape.test_fhn()
    st.write(test_df)



    # st.write(loan_tape.df)
    
