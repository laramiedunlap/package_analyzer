import pandas as pd


def main(in_df:pd.DataFrame)->pd.DataFrame:
    try:
        in_df['GP'] = in_df['GP'].astype(int)
    except:
        in_df['GP'] = in_df['GP'].astype(str)
        in_df['GP'].str.replace('.0','')
        in_df['GP'] = in_df['GP'].astype(int)

    return in_df