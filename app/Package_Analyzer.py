import streamlit as st
import pandas as pd
from loantape import LoanTape
import base64
import datetime
from typing import Optional
from collections import OrderedDict
import json
from pathlib import Path
import sys

py_version = sys.version

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
    """Code to be run after the Create LoanTape button is pressed"""
    st.session_state['loan_tape_form_change'] = True
    # passes the status of the static multiple checkbox and the static multiple to the callback caller
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
    pkg_path = Path(__file__).resolve().parent / 'package_maps' / 'packages.json'
    pkg_file = open(pkg_path)
    pkg_dict = json.load(pkg_file)
    return list(pkg_dict.keys())

path_to_pkgs = ('package_maps/packages.json')

# This code allows users to set the prime rate and projected settlement date
with st.sidebar:
    st.subheader(f"Python version: {py_version[0:4]}")
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


tab1, tab2, tab3 = st.tabs(['Loan Tape', 'Stratifications','Summary'])

# This Code is designed to re-render after the finalize button is pressed 
@st.cache_data
def convert_loantapes(_user_loan_tape:LoanTape)->dict:
    """display and cache the user's loan tape data"""
    user_data_dict = OrderedDict()
    pkg_counter = 0
    for key in _user_loan_tape.raw_dfs:
        if 'unknown' not in key:
            pkg_counter += 1 
            editted_df = _user_loan_tape.raw_dfs[key]
            user_data_dict[key] = editted_df
    
    return user_data_dict, pkg_counter

def write_unknown_number_of_items(arr_in:list, prefix:Optional[str]=None, suffix:Optional[str]=None, fifo: Optional[int]=0):
    """renders an unknown number of st.writes; add optional text before or after the thing using the optional kwargs."""
    arr = [i for i in arr_in]
    if fifo != 0: fifo = -1
    while len(arr)>0:   
        thing = arr.pop(fifo)
        if not prefix:
            if not suffix:
                yield st.write(f"{thing}")
            else:
                yield st.write(f"{thing}{suffix}")
        else:
            if suffix:
                yield st.write(f"{prefix}{thing}{suffix}")
            else:
                yield st.write(f"{prefix}{thing}")

def generate_linked_text_inputs(num_text_inputs:int, )-> None:
    """The plan here is to allow the user to rename the packages after generating the loantape, but I have to figure out how to render this before the form with the edit_dfs are made"""
    pass

with tab1:
    tab1.subheader('Loan Tape Build')
    files = st.file_uploader("Upload a csv file (columns and data)", type=["csv"], accept_multiple_files=True)
    pkg_counter = 0
    if files is not None:
        # First check if the submitted button has been pressed -- this means the user is trying to process new data, so we'll clear the cache
        if submitted:
            convert_loantapes.clear()
            st.session_state['submitted_button_pressed'] = True

        if 'submitted_button_pressed' in st.session_state and st.session_state['submitted_button_pressed']:
            prime_rate = st.session_state.user_prime_rate
            raw_data = list()
            for f in files:
                raw_data.append(pd.read_csv(f))
            loan_tape = generate_loantape(_cols, raw_data, st.session_state)
            # NOTE --> Processed_data_dict is an ORDERED_DICT, so you can access items in the order they were added
            processed_data_dict, pkg_count = convert_loantapes(_user_loan_tape=loan_tape)

            # RENAMING MODULE
            
            st.write("Give packages a unique name:")
            prebuild_container = st.empty()
            
            prebuild_container = st.container()
            with prebuild_container:
                curr_names = list(processed_data_dict.keys())
                raw_name_generator = write_unknown_number_of_items(curr_names)
                writing_job = [i for i in raw_name_generator]
                                
                names = [st.text_input(f"enter name for {curr_names[i]}:", key=f"{curr_names[i]}-textinput") for i in list( range( len(writing_job) ) )]

                rename_button= st.button('Rename Packages')

                if rename_button:
                    for k , v in st.session_state.items():
                        if 'textinput' in k:
                            data_dict_key = k.split('-')[0]
                            new_pkg_name = st.session_state[k]
                            processed_data_dict[data_dict_key]['Pck / Deal']  = new_pkg_name
                
                st.write('Previews:')
                previews = [st.dataframe(df.head(2)) for df in processed_data_dict.values()]

            

            # Here we build another form inside the Loan Tape tab
            lt_build_form_container = st.empty()
            lt_build_form = lt_build_form_container.form("Loan Tapes", clear_on_submit=True)
            with lt_build_form:

                col_config =   { 'GP#':st.column_config.NumberColumn(format="%d"),
                                'SIC / NAICS':st.column_config.NumberColumn(format="%d"),
                                'Loan / Spread': st.column_config.NumberColumn(format="{:.2f}%")
                                    }
                
                # Convert the LoanTape (non-cacheable) data into data we can persist
                # This data has been processed via python - now the user has an opportunity to edit 
                edited_data_dict = OrderedDict( {key: st.data_editor( processed_data_dict[key], column_config=col_config, hide_index=False, num_rows="dynamic" ) for key in processed_data_dict.keys() })
                
                # Next we'll create a function to highlight cells with missing fields to the user, and then a function to show the user where there are issues
                def highlight_cells(val)->str:
                    color = 'yellow' if pd.isna(val) else ''
                    return 'background-color: {}'.format(color)
                

                def find_loantape_issues(processed_data:dict)->None:
                    """Render Streamlit Components to direct the user where there could be errors in the data sent from a lender"""
                    check_columns = ['GP#', 'Note Date', 'Note Maturity', 'Strip Rate', 'Current Balance']
                    for pkg_id in processed_data.keys():
                        df = processed_data[pkg_id]
                        idx_list = []
                        for c in check_columns:
                            if not df[df[c].isna()].empty:
                                idx_list += df[df[c].isna()].index.to_list()
                        problems_to_display = df[df.index.isin(idx_list)]
                        if not problems_to_display.empty:
                            st.write(f"{pkg_id} could have errors on these rows:")
                            st.write(problems_to_display.style.applymap(highlight_cells))
                    return None
                
                
                find_loantape_issues(processed_data=processed_data_dict)


                lt_submit = lt_build_form.form_submit_button(label="Finalize", help="To rebuild or restart the app, click the tool bar in the top right and select:\n `Clear cache` then `Rerun` ")
            
            if lt_submit:
                
                # here we remove the form from the Loan Tape tab
                lt_build_form_container.empty()

                for key, edited_data in edited_data_dict.items():
                    # Get the loan package name (if the user has changed it)
                    pkg_name = edited_data['Pck / Deal'].iloc[0]
                    # Create a download button for each individual loantape
                    csv = edited_data.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="{pkg_name}.csv">Download Loan Tape {pkg_name}</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                loan_tape.combine_raw_dfs()



                    
                with tab2:
                        st.write(pd.concat([df for df in edited_data_dict.values()], axis=0))

                with tab3:
                        tab3.subheader('Under Construction')
                            
                lt_clear_button = st.button("Reset")
                if lt_clear_button:        
                    st.experimental_rerun()
                            
    else:
        st.write('Please add CSVS of your loantapes to the file drop location in the sidebar')


