import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from loantape import LoanTape
import base64

# def load_excel_file(file):
#     wb = load_workbook(file)
#     sheet = wb.active
#     data = sheet.values
#     columns = next(data)[1:]
#     df = pd.DataFrame(data, columns=columns)
#     return df


st.title("Package File Uploader")

files = st.file_uploader("Upload a csv file (columns and data)", type=["csv"], accept_multiple_files=True)

# These are the columns for the finished loan tape
_cols =  ['Pck / Deal','GP#', 'Borrower Name', 'City', 'State', 'SIC / NAICS', 'ADJ', 'Accrual', 'Note Date',
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
    loan_tape.resolve_columns()
    for key in loan_tape.raw_dfs:

        test_df = loan_tape.raw_dfs[key]
        st.write(test_df)

    # if not test_df.empty:
    # # Create a download button for the test_df
    #     csv = test_df.to_csv(index=False)
    #     b64 = base64.b64encode(csv.encode()).decode()
    #     href = f'<a href="data:file/csv;base64,{b64}" download="test_df.csv">Download Test DataFrame</a>'
    #     st.markdown(href, unsafe_allow_html=True)


    
    
