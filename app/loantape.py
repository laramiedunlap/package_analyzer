import pandas as pd
import numpy as np
import json
from pathlib import Path
import os

import column_map

def rm_unnamed(_cols:list)->list:
    return [c for c in _cols if "unnamed" not in str(c).lower()]


class LoanTape:
    df: pd.DataFrame
    raw_dfs: dict
    naics: dict
    format_packages: dict
    correct_columns: list

    def norm_raw_cols(self):
        """Normalize the columns -- remove white space and line breaks"""
        if len(self.raw_dfs):
            # This creates a clone of the dict SELF.RAW_DFS cleaning up the original columns
            norm_dfs = {}
            for key, df in self.raw_dfs.items():
                cols = df.columns.to_list()
                cols = [c.strip().replace("\n"," ") for c in cols]
                df = df[rm_unnamed(cols)]
                norm_dfs[key] = df
            self.raw_dfs = norm_dfs
        else:
            # This probably needs to be changed to a try-except block
            # So that an error gets raised to the user
            print("No raw loan data")
        return None

    def load_format_packges(self):
        """parse the raw loan data by using the available packages"""
        pkg_path = Path('package_maps/packages.json')
        pkg_file = open(pkg_path)
        format_opts = json.load(pkg_file)
        return format_opts
    
    def __init__(self, clean_columns, data=list()):
        self.correct_columns = clean_columns
        self.df = pd.DataFrame(columns=clean_columns)
        self.raw_dfs = {f'unknown_{i}': df for i, df in enumerate(data)}
        self.norm_raw_cols()
        naics_tbl = pd.read_csv('package_maps/NAICS_2017.csv')
        self.naics = dict(naics_tbl.values)
        # self.raw_dfs = [df[self.rm_unnamed(df.columns.to_list())] for df in self.raw_dfs]
        self.format_packages = self.load_format_packges()

    def format_columns(self):
        """Use the format packages to reformat the raw data"""
        # get all available formats
        format_keys = self.format_packages.keys()
        # At this point, the pointer == 'unknown_n'
        temp = {}
        for df in self.raw_dfs.values():
            # for each dataframe the user uploaded, get the columns
            temp_cols = set(df.columns.to_list())
            # for each possible format type:
            for key in format_keys:
                # get the unformatted column names from the format option
                format_type_keys = set(self.format_packages[key].keys())
                # see if the format matches ~90% --> if not exact, it will still work and you can debug
                match_ratio = 1-len(temp_cols - format_type_keys) / len(format_type_keys)
                if match_ratio < .9:
                    continue
                else:
                    # If match, format the dataframe
                    temp[key] = df.rename(columns=self.format_packages[key])
                    temp[key]['Pck / Deal'] = key
                    # This could/should be done in the column_map function
                    temp[key]['Industry'] = temp[key]['SIC / NAICS'].map(self.naics)
                    break
        self.raw_dfs.update(temp)
        return None
    
    def test_fhn(self):
        fhn_resolver = column_map.FHN_resolver(self.raw_dfs['FHN'], self.correct_columns)
        return fhn_resolver.resolve_columns()
    
    def test_rj(self):
        rj_resolver = column_map.RJ_resolver(self.raw_dfs['RJ'], self.correct_columns)
        return rj_resolver.resolve_columns()
    

    def combine_raw_dfs(self):
        temp = []
        # Combine the dfs with formatted columns -- excluding the originals (non-destructive)
        for key in [key for key in self.raw_dfs.keys() if 'unknown' not in key]:
            df = self.raw_dfs[key]
            existing_cols = [c for c in df.columns if c != ""]
            temp.append(df[existing_cols])
        temp = pd.concat(temp, ignore_index=True)
        temp = temp[temp['GP#'].notna()]
        self.df = temp
        return self.df


        
        
    
