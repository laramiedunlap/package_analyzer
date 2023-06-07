import streamlit as st
import pandas as pd
from loantape import LoanTape
import base64
import datetime

st.title("Package File Uploader")

files = st.file_uploader("Upload a csv file (columns and data)", type=["csv"], accept_multiple_files=True)

# These are the columns for the finished loan tape
_cols =  ['Pck / Deal','GP#', 'Borrower Name', 'City', 'State', 'SIC / NAICS', 'ADJ', 'Accrual', 'Note Date',
'Note Maturity', 'Int. Paid to Date', 'Loan Spread', 'Loan Rate',
'Strip Rate', 'Original Balance', 'Current Balance', 'Multiple',
'Proceeds', 'Term', 'Age', 'Rmos', 'Industry', 'Prepayment Penalty',
'Term Bucket', 'Industry Bucket', 'Lender', 'Prepayment Notice']


if 'loan_tape_form_change' not in st.session_state:
    st.session_state['loan_tape_form_change'] = True

def form_callback():
    st.session_state['loan_tape_form_change'] = True


# This code allows users to set the prime rate and projected settlement date
with st.sidebar:
    with st.form("loan_tape_form"):
        st.write("Set the Prime Rate:")
        user_prime_rate =st.number_input(label='Prime Rate',value=8.000,step=0.1)
        st.write("Set the Projected Settlement Date:")
        todays_date = datetime.date.today()
        user_stlmt_date = st.date_input(label='Default: 50 days from today', value=todays_date+datetime.timedelta(days=50))
        mult_choice = st.checkbox(label="Set Static Multiple")
        if mult_choice:
            static_multiple = st.number_input(label='Multiple', value=3.500, step=.1)
        else:
            static_multiple = None
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit",on_click=form_callback)
    
        

if files is not None:
    if st.button('Create Loantape') or st.session_state['loan_tape_form_change']:
        st.session_state['loan_tape_form_change'] = False
        raw_data = list()
        for f in files:
            raw_data.append(pd.read_csv(f))

        loan_tape = LoanTape(clean_columns=_cols, data=raw_data)
        loan_tape.format_columns()
        loan_tape.resolve_columns()

        for key in loan_tape.raw_dfs:
            if 'unknown' not in key:
                test_df = loan_tape.raw_dfs[key]
                st.write(test_df)

                if not test_df.empty:
                # Create a download button for the test_df
                    csv = test_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="test_df.csv">Download Test DataFrame</a>'
                    st.markdown(href, unsafe_allow_html=True)
else:
    st.write('Please add CSVS of your loantapes to the file drop location above')

        
