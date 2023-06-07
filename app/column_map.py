import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional, Sequence

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
    def __init__(self, df, output_columns)-> None:
        self.in_df = df
        self.col_order = output_columns
    
    # These methods aren't explicilty required to be implemented, but if you want them you can use them
    def find_digit(str_value: str) -> float:
        """Converts common excel style number formats"""
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

    def convert_number_formats(self, excluded_columns: Optional[Sequence] = None) -> None:
        """Converts common excel style number formatts across a dataframe"""
        if excluded_columns is None:
            excluded_columns = []
        for col in self.in_df.columns:
            if col not in excluded_columns and self.in_df[col].dtype == 'object':
                self.in_df[col] = self.in_df[col].apply(lambda x: self.find_digit(x) if pd.notnull(x) else x)
    
    # 1)
    @abstractmethod
    def create_blank_column(self, new_column:str):
        self.in_df[new_column] = None

    # 2)
    @abstractmethod
    def sort_columns(self):
        """Make sure the columns are in the correct order"""
        return self.in_df[self.col_order]
    
    # Decorator that tells the class the method you're making is a column method ()
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
        self.run_methods()
        existing_columns = set(self.in_df.columns.to_list())
        desired_columns = set(self.col_order)
        
        if existing_columns != desired_columns:
            for column_to_create in list(desired_columns - existing_columns):
                self.create_blank_column(column_to_create)
        
        self.out_df = self.sort_columns()
        return self.out_df



class FHN_resolver(ColResolver):

    def __init__(self, df, output_columns) -> None:
        super().__init__(df, output_columns)

    def create_blank_column(self, new_column: str):
        return super().create_blank_column(new_column)
    
    def sort_columns(self):
        return super().sort_columns()
    
    def run_methods(self):
        return super().run_methods()

    @ColResolver.column_method
    def geo_split(self):
        """For FHN loan tapes, split the city and state out into two columns named `City` and `State`"""
        self.in_df[['City','State']] = self.in_df['func_geosplit'].str.extract(r'^(.*),\s([A-Z]{2})+')

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

    def __init__(self, df, output_columns) -> None:
        super().__init__(df, output_columns)
    
    def create_blank_column(self, new_column: str):
        return super().create_blank_column(new_column)
    
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

    def __init__(self, df, output_columns) -> None:
        super().__init__(df, output_columns)

    def create_blank_column(self, new_column: str):
        return super().create_blank_column(new_column)
    
    def sort_columns(self):
        return super().sort_columns()
    
    def run_methods(self):
        return super().run_methods()
    
    def resolve_columns(self):
        return super().resolve_columns()
    





    