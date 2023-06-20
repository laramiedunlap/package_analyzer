import streamlit as st
from streamlit.elements.data_editor import _apply_dataframe_edits
import pandas as pd
from loantape import LoanTape
import base64
import datetime
from typing import Optional
import json
from pathlib import Path


st.title("Package Analyzer")


# These are the columns for the finished loan tape
_cols =  ['Pck / Deal','GP#', 'Borrower Name', 'City', 'State', 'SIC / NAICS', 'ADJ', 'Accrual', 'Note Date',
'Note Maturity', 'Int. Paid to Date', 'Loan Spread', 'Loan Rate',
'Strip Rate', 'Original Balance', 'Current Balance', 'Multiple',
'Proceeds', 'Term', 'Age', 'Rmos', 'Industry', 'Prepayment Penalty',
'Term Bucket', 'Industry Bucket', 'Lender']

# Tell the backend which of the user columns are date columns that will already contain date data
_date_cols = ['Note Date','Note Maturity']

custom_ss_keys =['loan_tape_form_change','static_mult_chkbox','user_static_multiple','user_stlmt_date','user_prime_rate']

def init_session_state_keys():
    if 'loan_tape_form_change' not in st.session_state:
        st.session_state['loan_tape_form_change'] = False
    if 'static_mult_chkbox' not in st.session_state:
        st.session_state['static_mult_chkbox'] = False
    if 'user_static_multiple' not in st.session_state:
        st.session_state['user_static_multiple'] = None
    if 'user_stlmt_date' not in st.session_state:
        st.session_state['user_stlmt_date'] = None
    if 'user_prime_rate' not in st.session_state:
        st.session_state['user_prime_rate'] = None
    if 'user_date_cols' not in st.session_state:
        st.session_state['user_date_cols'] = _date_cols

init_session_state_keys()

def static_multiple_callback(cond:bool, static_val: Optional[float]=None)->None:
    """Just check the status of the box and the value"""
    st.session_state['static_mult_chkbox'] = cond
    if static_val:
        st.session_state['user_static_multiple'] = static_val
    else:
        st.session_state['user_static_multiple'] = None

def lt_form_callback(params:dict)->None:
    """Don't use this directly from the form button -- values won't update till next rerun"""
    st.session_state['loan_tape_form_change'] = True
    # passes the status of the static multiple checkbox and the static multiple to the callback
    static_multiple_callback(cond=params['static_mult_chkbox'], static_val=params['user_static_multiple'])
    st.session_state['user_stlmt_date'] = params['user_stlmt_date']
    st.session_state['user_prime_rate'] = params['user_prime_rate']/100

def generate_loantape(_cols, raw_data, _params):
    """This function Contains the loantape generation"""
    loan_tape = LoanTape(clean_columns=_cols, data=raw_data, params= _params)
    loan_tape.format_columns()
    loan_tape.resolve_columns()
    return loan_tape

def list_supported_packages(file_path_str:str)->list:
    pkg_path = Path(file_path_str)
    pkg_file = open(pkg_path)
    pkg_dict = json.load(pkg_file)
    return list(pkg_dict.keys())

path_to_pkgs = 'package_maps/packages.json'

# This code allows users to set the prime rate and projected settlement date
with st.sidebar:
    supported_pkgs = list_supported_packages(path_to_pkgs)
    with st.expander(f'**Currently Supported Counterparties**'):
        for p in supported_pkgs:
            st.write(f"*{p}*")

    with st.form("loan_tape_form"):
        st.write("**Set the Prime Rate**:")
        _prime_rate =st.number_input(label='Prime Rate',value=8.000,step=0.05)
        _prime_rate = round(_prime_rate,3)
        st.write("**Set the Projected Settlement Date**:")
        todays_date = datetime.date.today()
        _stlmt_date = st.date_input( label='Default: 50 days from today', value=todays_date+datetime.timedelta(days=50) )

        mult_choice = st.checkbox(label="**Set Static Multiple?**")
        static_multiple = st.number_input(label='Multiple', value=3.500, step=.1)
        static_multiple = round(static_multiple,3)
        params = dict(static_mult_chkbox = mult_choice, user_static_multiple=static_multiple,
                      user_stlmt_date=_stlmt_date, user_prime_rate=_prime_rate)
        # Every form must have a submit button.
        submitted = st.form_submit_button("Create LoanTape")
        if submitted:
            lt_form_callback(params)
    lt_clear_button = st.button("Reset")
    if lt_clear_button:
        st.experimental_rerun()


tab1, tab2, tab3 = st.tabs(['Loan Tape', 'Stratifications','Summary'])


# This Code is designed to re-render after the finalize button is pressed 
@st.cache_data
def convert_loantapes(_user_loan_tape:LoanTape)->dict:
    """display and cache the user's loan tape data"""
    user_data_dict = {}
    pkg_counter = 0
    for key in _user_loan_tape.raw_dfs:
        if 'unknown' not in key:
            pkg_counter += 1 
            editted_df = _user_loan_tape.raw_dfs[key]
            user_data_dict[key] = editted_df
    
    return user_data_dict, pkg_counter


with tab1:
    tab1.subheader('Loan Tape Build')
    files = st.file_uploader("Upload a csv file (columns and data)", type=["csv"], accept_multiple_files=True)
    pkg_counter = 0
    if files is not None:
        # First check if the submitted button has been pressed -- this means the user is trying to process new data, so we'll clear the cache
        if submitted:
            convert_loantapes.clear()

        prime_rate = st.session_state.user_prime_rate
        raw_data = list()
        for f in files:
            raw_data.append(pd.read_csv(f))
        loan_tape = generate_loantape(_cols, raw_data, st.session_state)
        
        lt_build_form = st.form("Loan Tapes")
        with lt_build_form:
            # First we'll convert the LoanTape (non-cacheable) data into data we can persist
            edited_data_dict, pkg_count = convert_loantapes(_user_loan_tape=loan_tape)

            test_config =     {'GP#':st.column_config.NumberColumn(format="%d"),
                            'SIC / NAICS':st.column_config.NumberColumn(format="%d"),
                            'Loan / Spread': st.column_config.NumberColumn(format="{:.2f}%")
                                }
            edited_data_dict = { key: st.data_editor( edited_data_dict[key], hide_index=True, num_rows="dynamic", column_config=test_config ) for key in edited_data_dict.keys() }
            lt_submit = lt_build_form.form_submit_button(label="Finalize")

            # This will cause a reload of the entire page, so whatever happens here needs to be cached.
            if lt_submit:
                for key, edited_data in edited_data_dict.items():
                    # Get the loan package name (if the user has changed it)
                    pkg_name = edited_data['Pck / Deal'].iloc[0]
                    # Create a download button for the test_df
                    csv = edited_data.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="{pkg_name}.csv">Download Loan Tape {pkg_name}</a>'
                    st.markdown(href, unsafe_allow_html=True)

                
    #     st.session_state['loan_tape_form_change'] = False

    # else:
    #     st.write('Please add CSVS of your loantapes to the file drop location in the sidebar')


with tab2:
        tab2.subheader('Under Construction')



with tab3:
        tab3.subheader('Under Construction')

            


                    


            
