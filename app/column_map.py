import pandas as pd
from abc import ABC, abstractmethod

# Classes for resolving column discrepancies between our loan tape format and the one a lender sends
# Create a new format by writing the json pointers for that format, then create a new ColResolver for that format
# All numbered methods must be defined in the subclass, although for most cases, you can define a method as:
# def method_name(self):
    # return super().method_name()
# Please read note on column method decorator --> methods designed to operate on a column need the decorator

class ColResolver(ABC):
    in_df: pd.DataFrame
    out_df: pd.DataFrame
    col_order: list
    
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
    def resolve_columns(self):
        """Equivalent of running main() on the Class if it were a standalone script -- run all methods,
        check for resolution by creating blank columns to match the users column order,
        sort the columns, and set the out_df attribute"""
        self.run_methods()
        existing_columns = set(self.in_df.columns.to_list())
        desired_columns = set(self.col_order)
        
        if existing_columns != desired_columns:
            for column_to_create in list(desired_columns - existing_columns):
                self.create_blank_column(column_to_create)
        
        self.out_df = self.sort_columns()
        return self.out_df


class FHN_resolver(ColResolver):

    def __init__(self, df: pd.DataFrame, output_columns: list)->None:
        self.in_df = df
        self.col_order = output_columns

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
    def __init__(self, df: pd.DataFrame, output_columns: list)->None:
        self.in_df = df
        self.col_order = output_columns
    
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




    