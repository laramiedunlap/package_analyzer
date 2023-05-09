import pandas as pd
import numpy as np
from dataclasses import dataclass
import json
from pathlib import Path
from difflib import SequenceMatcher


class LoanTape:
    df: pd.DataFrame
    raw_dfs: list
    naics: dict
    format_packages: dict

    def rm_unnamed(self, _cols:list)->list:
        return [c for c in _cols if "unnamed" not in str(c).lower()]

    def norm_raw_cols(self):
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

    def load_format_packges(self):
        """parse the raw loan data by using the available packages"""
        pkg_path = Path('package_maps/packages.json')
        pkg_file = open(pkg_path)
        format_opts = json.load(pkg_file)
        return format_opts
    
    def __init__(self, clean_columns, data=list()):
        self.df = pd.DataFrame(columns=clean_columns)
        self.raw_dfs = data
        self.norm_raw_cols()
        naics_tbl = pd.read_csv('package_maps/NAICS_2017.csv')
        self.naics = dict(naics_tbl.values)
        self.raw_dfs = [df[self.rm_unnamed(df.columns.to_list())] for df in self.raw_dfs]
        self.format_packages = self.load_format_packges()

    def format_columns(self):
        """Use the format packages to reformat the raw data"""
        # get all available formats
        format_keys = self.format_packages.keys()
        for idx, df in enumerate(self.raw_dfs):
            # for each dataframe, get the columns
            temp_cols = set(df.columns.to_list())
            # for each possible format type:
            for key in format_keys:
                # get the unformatted column names from the format option
                format_type_keys = set(self.format_packages[key].keys())
                # see if the format matches ~90%
                match_ratio = 1-len(temp_cols - format_type_keys) / len(format_type_keys)
                if match_ratio < .9:
                    continue
                else:
                    # If match, format the dataframe
                    self.raw_dfs[idx] = df.rename(columns=self.format_packages[key])
                    self.raw_dfs[idx]['Industry'] = self.raw_dfs[idx]['SIC / NAICS'].map(self.naics)
                    break

    def combine_raw_dfs(self):
        temp = []
        for df in self.raw_dfs:
            existing_cols= [c for c in df.columns if c != ""]
            temp.append(df[existing_cols])
        temp = pd.concat(temp, ignore_index=True)
        temp = temp[temp['GP#'].notna()]
        self.df = temp


        
        
    
