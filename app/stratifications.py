import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def calculate_summary(df:pd.DataFrame, group_col:str|list)-> pd.DataFrame:
    """Perform the summary calculations from the Stratifications tab in the Package Analyzer"""
    result = df.groupby(group_col).agg({'Current Balance':'sum','Number of Loans':'count'})
    result['Pct of Pool by Current Balance'] = result['Current Balance'] / result['Balance'].sum() * 100


def original_maturity(df:pd.DataFrame)->pd.DataFrame:
    """Group the loantape by greater than or less than 15 year Maturities"""