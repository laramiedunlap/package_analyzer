import pandas as pd
import datetime
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Sequence
import re


# This is a helper function for the COLRESOLVER class -- it can be imported elsewhere but it needs to remain here 
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

# Classes for resolving column discrepancies between our loan tape format and the one a lender sends
# Create a new format by writing the json pointers for that format, then create a new ColResolver for that format
# All numbered methods must be defined in the subclass, although for most cases, you can define a method as:
# def method_name(self):
    # return super().method_name()
# Please read note on column method decorator --> methods designed to operate on a column need the decorator
# All of the @abstractmethod decorated functions must be present in the children classes. This guarantees that every loantape is handled programmtically the same way

class ColResolver(ABC):
    in_df: pd.DataFrame
    out_df: pd.DataFrame
    col_order: list

    @abstractmethod
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
    @abstractmethod
    def convert_date_strings(self) -> None:
        if self.__getattribute__('user_date_cols') is not None:
            for c in self.user_date_cols:
                dates = self.in_df[c].to_list()
                dates = [str(d) for d in dates]
                new_dates = [d for d in map(conv_date, dates)]
                self.in_df[c] = new_dates

    # D) This method sets the Int. Paid to Date --> usually you will need to do this for every LoanTape
    @abstractmethod
    def int_paid_to_date(self):
        """This method will set the `Int. Paid To Date` column"""
        if self.__getattribute__('user_stlmt_date') is not None:
            settlement_date = self.__getattribute__('user_stlmt_date')
            self.in_df['Int. Paid to Date'] = self.in_df['Note Date'].apply(lambda x: max( settlement_date-pd.Timedelta(50,'D') , x) )
        else:
            # This is technically an error that we may want to display on the front end
            print("No int to date")

    # 1)
    @abstractmethod
    def create_blank_column(self, new_column:str):
        self.in_df[new_column] = None

    # 2)
    @abstractmethod
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
    
    
    # 3)
    def run_methods(self):
        """Run all the column methods"""
        methods = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), "is_column_method")]
        for method_name in methods:
            method = getattr(self, method_name)
            method()
    
    # 4)
    @abstractmethod
    def resolve_columns(self)->pd.DataFrame:
        """Equivalent of running main() on the Class if it were a standalone script -- run all methods,
        check for resolution by creating blank columns to match the users column order,
        sort the columns, and set the out_df attribute. This function returns the final dataframe."""
        self.convert_date_strings()
        self.run_methods()
        existing_columns = set(self.in_df.columns.to_list())
        desired_columns = set(self.col_order)
        
        if existing_columns != desired_columns:
            for column_to_create in list(desired_columns - existing_columns):
                self.create_blank_column(column_to_create)
        
        self.out_df = self.sort_columns()
        return self.out_df



class FHN_resolver(ColResolver):

    def __init__(self, df, output_columns, params) -> None:
        super().__init__(df, output_columns, params)

    def create_blank_column(self, new_column: str):
        return super().create_blank_column(new_column)
    
    def sort_columns(self):
        return super().sort_columns()
    
    def run_methods(self):
        return super().run_methods()

    def convert_date_strings(self) -> None:
        return super().convert_date_strings()
    
    @ColResolver.column_method
    def int_paid_to_date(self) -> None:
        return super().int_paid_to_date()

    @ColResolver.column_method
    def geo_split(self):
        """For FHN loan tapes, split the city and state out into two columns named `City` and `State`"""
        self.in_df[['City','State']] = self.in_df['func_geosplit'].str.extract(r'^(.*),\s([A-Z]{2})+')

    @ColResolver.column_method
    def int_paid_to_date(self):
        return super().int_paid_to_date()

    @ColResolver.column_method
    def loan_rate(self):
        self.in_df['Loan Rate'] = None

    @ColResolver.column_method
    def original_balance(self):
        self.in_df['Original Balance'] = self.in_df['Current Balance']

    @ColResolver.column_method
    def strip_rate(self):
        self.in_df['Strip Rate'] = self.in_df['Strip Rate'] / 100
    
    @ColResolver.column_method
    def loan_spread(self):
        self.in_df['Loan Spread'] = self.in_df['Loan Spread'] / 100

    @ColResolver.column_method
    def proceeds(self):
        self.in_df['Proceeds'] = None

    @ColResolver.column_method
    def term(self):
        self.in_df['Term'] = None

    @ColResolver.column_method
    def age(self):
        self.in_df['Age'] = None

    @ColResolver.column_method
    def rmos(self):
        self.in_df['Rmos'] = None

    def resolve_columns(self):
        return super().resolve_columns()
    

class RJ_resolver(ColResolver):

    def __init__(self, df, output_columns, params) -> None:
        super().__init__(df, output_columns, params)
    
    def create_blank_column(self, new_column: str):
        return super().create_blank_column(new_column)
    
    def convert_date_strings(self) -> None:
        return super().convert_date_strings()
    
    @ColResolver.column_method
    def int_paid_to_date(self) -> None:
        return super().int_paid_to_date()
    
    @ColResolver.column_method
    def original_balance(self):
        self.in_df['Original Balance'] = self.in_df['Current Balance']
    
    def sort_columns(self):
        return super().sort_columns()
    
    def run_methods(self):
        return super().run_methods()
    
    def resolve_columns(self):
        return super().resolve_columns()


class BMO_resolver(ColResolver):

    def __init__(self, df, output_columns, params) -> None:
        super().__init__(df, output_columns, params)

    def create_blank_column(self, new_column: str):
        return super().create_blank_column(new_column)
    
    def convert_date_strings(self) -> None:
        return super().convert_date_strings()
    
    @ColResolver.column_method
    def int_paid_to_date(self) -> None:
        return super().int_paid_to_date()
    
    def sort_columns(self):
        return super().sort_columns()
    
    def run_methods(self):
        return super().run_methods()
    
    def resolve_columns(self):
        return super().resolve_columns()
    





    