import pandas as pd
import numpy as np
import datetime
from abc import ABC, abstractmethod
from typing import Optional, Sequence
import re
from dateutil.relativedelta import relativedelta
import warnings

warnings.filterwarnings('ignore')

# NOTE: These are helper functions for the COLRESOLVER class -- it can be imported elsewhere but they needs to remain here 

def month_diff(start_date: datetime.date, end_date: datetime.date):
    """Calculate the difference in months between two dates"""
    diff = relativedelta(end_date, start_date)
    return diff.years * 12 + diff.months

def days_diff(start_date: datetime.date, end_date: datetime.date, accrual_cal) -> int:
    """Calculates the difference in days between two dates, then divides them by the accrual method's calendar basis, then multiplies it by 12 to get months"""
    return (pd.Timedelta(end_date-start_date).days / accrual_cal) * 12

def conv_date(d:str)-> datetime.date:
    """Convert MOST dates -- input a string format"""
    d = d.replace(',','')    
    # If it is some attempt at a date, give it a shot with the coerce exception return
    if '-' in d or '/' in d:
        try:
            new_date = pd.to_datetime(d)
            return new_date.date()
        except:
            return pd.to_datetime(d,errors='coerce')
    else:
        # assume its serialized, give it a shot with a Not-A-Time exception return 
        pattern = re.compile(r'[0-9]+')
        match = pattern.match(d)
        if match:
            try:
                new_date = pd.to_datetime('1899-12-30') + pd.to_timedelta(int(match.group()), 'D')
                return new_date.date()
            except:
                return pd.NaT
            
def term_map(value):
    """Used to map term bucket values onto the loan tape"""
    term_mapping = {
        1: range(0, 96),
        2: range(97, 132),
        3: range(132, 192),
        4: range(192, 252),
        5: range(252, 500)
    }
    for key, range_values in term_mapping.items():
        if value in range_values:
            return key
    # Return a default value if no match is found
    return None

# Classes for resolving column discrepancies between our loan tape format and the lender format
# Create a new format by writing the JSON pointers for that format inside the packages.json file, then create a new ColResolver for that format
# Please read note on column method decorator --> methods designed to operate on a column need the decorator
# All of the @abstractmethod decorated functions must be present in the children classes.

class ColResolver(ABC):
    in_df: pd.DataFrame
    out_df: pd.DataFrame
    col_order: list
    bad_data: pd.DataFrame

    def __init__(self, df, output_columns, params=None)-> None:
        self.in_df = df
        self.col_order = output_columns
        # This allows users to set some options (like multiple, settlement date, etc.) without needing to set all of them
        if params is not None:
            for key, value in params.items():
                setattr(self,key,value)
      
    # A) These next two methods aren't explicilty required to be implemented, but if you want them you can use them
    def find_digit(str_value: str) -> float:
        """Converts common excel style number formats."""
        temp_bin = []
        temp_values = [1,1]
        for ch in str_value:
            if '-' in ch or '.' in ch:
                temp_bin.append(ch)
            elif ch.isdigit():
                temp_bin.append(ch)
            elif ch == "(":
                temp_values[0] = -1
            elif ch == "%":
                temp_values[1] = 100
        new_value = ''.join(temp_bin)
        if new_value != '':
            return (float(new_value) * temp_values[0] ) / temp_values[1]
        else: 
            return str_value
      
    # B) This method is not required to be implemented, but can accomplish all the 
    def convert_number_formats(self, excluded_columns: Optional[Sequence] = None) -> None:
        """Converts common excel style number formats across a dataframe -- applies the find_digit function element-wise"""
        if excluded_columns is None:
            excluded_columns = []
        for col in self.in_df.columns:
            if col not in excluded_columns and self.in_df[col].dtype == 'object':
                self.in_df[col] = self.in_df[col].apply(lambda x: self.find_digit(x) if pd.notnull(x) else x)

    # C) This method converts excel datetime numbers to datetime.dates --> see helper function above class definition
    def convert_date_strings(self) -> None:
        if self.__getattribute__('user_date_cols') is not None:
            for c in self.user_date_cols:
                dates = self.in_df[c].to_list()
                dates = [str(d) for d in dates]
                new_dates = [d for d in map(conv_date, dates)]
                self.in_df[c] = new_dates

    # 1)
    def create_blank_column(self, new_column:str):
        self.in_df[new_column] = None

    # 2)
    def sort_columns(self):
        """Make sure the columns are in the correct order"""
        return self.in_df[self.col_order]

    # Decorator that tells the class that the method you're making is a column method ()
    # ** NOTE ** you do --NOT-- need to define this decorator in the subclass, just use this decorator:
    # @ColResolver.column_method on your column functions
    @staticmethod
    def column_method(func):
        """decorate a method to be called by the run_methods function. Each column method should add a column to the
        self.in_df attribute of the subclass"""
        setattr(func, "is_column_method", True)
        return func
    
    # D) This method sets the Int. Paid to Date --> usually you will need to do this for every LoanTape
    def int_paid_to_date(self)->None:
        """This method will set the `Int. Paid To Date` column"""
        if self.__getattribute__('user_stlmt_date') is not None:
            settlement_date = self.__getattribute__('user_stlmt_date')
            self.in_df['Int. Paid to Date'] = self.in_df['Note Date'].apply(lambda x: max(settlement_date-pd.Timedelta(50,'D') , x) if pd.notnull(x) else None )
        else:
            # This is technically an error that we may want to display on the front end or handle somehow (it would be a very unique corner case)
            print("No int to date")

    
    
    def term(self)->None:
        self.in_df['Term'] = self.in_df.apply(lambda row: month_diff(row['Note Date'], row['Note Maturity']), axis=1)
    
    def accrual(self)->None:
        self.in_df.loc[self.in_df['Accrual'].str.contains('365'), 'Accrual'] = 'ACT/365'
        self.in_df.loc[self.in_df['Accrual'].str.contains('360'), 'Accrual'] = '30/360'
    
    def age(self)->None:
        self.in_df['Age'] = 0
        self.in_df.loc[self.in_df['Accrual'] == 'ACT/365', 'Age'] = self.in_df.apply(lambda row: days_diff(row['Note Date'], row['Int. Paid to Date'], 365), axis=1 )
        self.in_df.loc[self.in_df['Accrual'] == '30/360', 'Age'] = self.in_df.apply(lambda row: days_diff(row['Note Date'], row['Int. Paid to Date'], 360), axis=1 )
    
    def rmos(self)-> None:
        self.in_df['Rmos'] = self.in_df['Term'] - self.in_df['Age']

    def multiple(self)-> None:
        if self.__getattribute__('static_mult_chkbox') is not None:
            if self.static_mult_chkbox:
                if self.__getattribute__('user_static_multiple') is not None:
                    self.in_df['Multiple'] = self.user_static_multiple
        else:
            pass

    def proceeds(self)->None:
        self.in_df['Proceeds'] = self.in_df['Current Balance'] * self.in_df['Strip Rate'] * self.in_df['Multiple']

    def prepayment_penalty(self)->None:
        self.in_df['Prepayment Penalty'] = np.nan
        mask_5 = (self.in_df['Term'] >= 180) & (self.in_df['Age']<=12)
        mask_3 = (self.in_df['Term'] >= 180) & (self.in_df['Age']>12) & (self.in_df['Age']<24)
        mask_1 = (self.in_df['Term'] >= 180) & (self.in_df['Age']>24) & (self.in_df['Age']<36)
        self.in_df.loc[mask_5,'Prepayment Penalty'] = .05
        self.in_df.loc[mask_3,'Prepayment Penalty'] = .03
        self.in_df.loc[mask_1,'Prepayment Penalty'] = .01
        self.in_df.loc[self.in_df['Prepayment Penalty'].isna(), 'Prepayment Penalty'] = 0.0
    
    def term_bucket(self)->None:
        term_vars = self.in_df['Term'].to_list()
        self.in_df['Term Bucket'] = np.array(map(term_map,term_vars))
    
    def industry_bucket(self)->None:
        codes = [721110,447110,722511,811192,624410]
        self.in_df['Industry Bucket'] = 0
        self.in_df.loc[self.in_df['Industry Bucket'].isin(codes), 'Industry Bucket'] = 1

    def run_col_methods(self)->None:
        """Run all the column methods"""
        methods = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), "is_column_method")]
        for method_name in methods:
            method = getattr(self, method_name)
            method()
        self.int_paid_to_date()
        self.term()
        self.accrual()
        self.age()
        self.rmos()
        self.multiple()
        self.proceeds()
        self.prepayment_penalty()
        self.term_bucket()
        self.industry_bucket()
        return None

    def resolve_columns(self)->pd.DataFrame:
        """Equivalent of running main() on the Class if it were a standalone script -- run all methods,
        check for resolution by creating blank columns to match the users column order,
        sort the columns, and set the out_df attribute. This function returns the final dataframe."""

        # Remove rows without a note date, these will have to be modified by the user for now:
        missing_note_date = self.in_df[self.in_df['Note Date'].isna()]
        self.in_df = self.in_df.dropna(subset=['Note Date'])

        # Ensure that all date-like variables are correctly formatted 
        self.convert_date_strings()

        # Run the orchestration method for all the columns
        self.run_col_methods()
        
        # NOTE--> CODE HERE
        # Find the difference between the current columns on the in_df and the desired cols `col_order`, and then fill those as blanks  
        existing_columns = set(self.in_df.columns.to_list())
        desired_columns = set(self.col_order)
        if existing_columns != desired_columns:
            for column_to_create in list(desired_columns - existing_columns):
                self.create_blank_column(column_to_create)

        self.in_df = self.sort_columns()

        # Add the missing Note Date rows back at the bottom of the dataframme
        if not missing_note_date.empty:

            existing_columns = (missing_note_date.columns.to_list())
            desired_columns = (self.in_df)
            
            for col in desired_columns:
                if col in existing_columns:
                    continue
                else:
                    missing_note_date[col] = np.NaN

            missing_note_date = missing_note_date[self.in_df.columns]
            
            
            # self.in_df = self.in_df.loc[~self.in_df.index.duplicated(keep='first')]
            # missing_note_date = missing_note_date.loc[~missing_note_date.index.duplicated(keep='first')]
            try:
                self.in_df = pd.concat([self.in_df,missing_note_date], axis= 0)
            except:
                print(set(self.in_df.columns)- set(missing_note_date.columns))
                print(len(self.in_df.columns))
                print(self.in_df.columns)
                print('----------------')
                print(len(missing_note_date.columns))
                print(missing_note_date.columns)
                raise
        
        self.out_df = self.in_df

        return self.out_df


class FHN_resolver(ColResolver):

    @ColResolver.column_method
    def geo_split(self):
        """For FHN loan tapes, split the city and state out into two columns named `City` and `State`"""
        self.in_df[['City','State']] = self.in_df['func_geosplit'].str.extract(r'^(.*),\s([A-Z]{2})+')

    @ColResolver.column_method
    def adj_rates(self):
        """This structure ensures the functions happen in the correct order at runtime, because the results are dependendent"""
        self.in_df['Loan Spread'] = self.in_df['Loan Spread'] / 100
        if self.__getattribute__('user_prime_rate'):
            self.in_df['Loan Rate'] = self.in_df['Loan Spread'] + self.user_prime_rate
        else:
            self.in_df['Loan Rate'] = None
    
    @ColResolver.column_method
    def strip_rate(self):
        self.in_df['Strip Rate'] = self.in_df['Strip Rate'] / 100

    @ColResolver.column_method
    def original_balance(self):
        self.in_df['Original Balance'] = self.in_df['Current Balance']

    # @ColResolver.column_method
    # def note_date(self):
    #     self.in_df = self.in_df[self.in_df['Note Date'].notna()]


class RJ_resolver(ColResolver):
    
    @ColResolver.column_method
    def original_balance(self):
        self.in_df['Original Balance'] = self.in_df['Current Balance']

    @ColResolver.column_method
    def set_accural(self):
        self.in_df['Accrual'] = 'ACT/365'

    @ColResolver.column_method
    def set_adj(self):
        self.in_df['ADJ'] = 'Q'



class BMO_resolver(ColResolver):

    @ColResolver.column_method
    def adj_rates(self):
        self.in_df['Loan Rate'] = self.in_df['Loan Rate']/100
        self.in_df['Loan Spread'] = self.in_df['Loan Spread']/100
        self.in_df['Strip Rate'] = self.in_df['Strip Rate']/100
        
    

    





    