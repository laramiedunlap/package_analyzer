import pandas as pd
import numpy as np
import openpyxl as pyxl
from dataclasses import dataclass
import json
from pathlib import Path


class LoanTape:
    df: pd.DataFrame
    raw_dfs: list

    def rm_unnamed(_cols:list)->list:
        return [c for c in _cols if "unnamed" not in str(c).lower()]

    def norm_raw_cols(self)->None:
        """Normalize the columns -- remove white space and line breaks"""
        if len(self.raw_dfs)>0:
            norm_dfs = []
            for df in self.raw_dfs:
                cols = df.columns.to_list()
                cols = [c.strip().replace("\n"," ") for c in cols]
                df.columns = cols
                norm_dfs.append(df)
            self.raw_dfs = norm_dfs
        else:
            print("No raw loan data")        
        return None
    
    def parse_data(self):
        """parse the raw loan data by using the available packages"""
        pkg_path = Path('package_maps/packages.json')
        pkg_file = open(pkg_path)
        format_opts = json.load(pkg_file)
        print(format_opts)
        return None

    def __init__(self, clean_columns, data=list()):
        self.df = pd.DataFrame(columns=clean_columns)
        self.raw_dfs = data
        self.raw_dfs = [df[[self.rm_unnamed(df.columns.to_list())]] for df in self.raw_dfs]
        self.norm_raw_cols()
        