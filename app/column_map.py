import pandas as pd
from abc import ABC, abstractmethod


class ColResolver(ABC):
    in_df: pd.DataFrame
    out_df: pd.DataFrame
    col_order: list
    
    @abstractmethod
    def resolve_columns(self):
        """Check for resolution"""
        pass

    @abstractmethod
    def sort_columns(self):
        """sort_cols"""
        return self.out_df[self.col_order]
    
    @staticmethod
    def column_method(func):
        """decorate a method to be called by the run_methods function. Each column method should add a column to the
        self.in_df attribute"""
        setattr(func, "is_column_method", True)
        return func
    
    def run_methods(self):
        """Run all the column methods"""
        methods = [method for method in dir(self) if callable(getattr(self, method)) and hasattr(getattr(self, method), "is_column_method")]
        for method_name in methods:
            method = getattr(self, method_name)
            method()


class FHN_resolver(ColResolver):

    def __init__(self, df: pd.DataFrame, output_columns: list)->None:
        self.in_df = df
        self.col_order = output_columns

    def resolve_columns(self):
        return super().resolve_columns()
    
    def sort_columns(self):
        return super().sort_columns()
    
    def run_methods(self):
        super().run_methods()
        return(self.in_df[['Pck / Deal','GP#','Borrower Name','City','State','SIC / NAICS','ADJ','Accrual','Note Date',
                            'Note Maturity', 'Loan Spread','Loan Rate','Strip Rate','Original Balance','Current Balance',
                            'Multiple','Proceeds','Term','Age','Rmos','Industry','Lender']])
    
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

        

    