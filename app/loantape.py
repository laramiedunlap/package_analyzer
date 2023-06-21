import pandas as pd
import numpy as np
import json
from pathlib import Path
import os
import column_map


# NOTE -- These are helper functions for the LoanTape Class -- I felt they shouldn't be included inside the class
# but they could be

def rm_unnamed(_cols:list)->list:
    """Remove Unnamed columns from a dataframe"""
    return [c for c in _cols if "unnamed" not in str(c).lower()]

def flatten(list_of_lists):
    """Flatten a list of lists: [[x.y.z],[a,b,c]]->[x,y,z,a,b,c]"""
    return [item for sublist in list_of_lists for item in sublist]

def pkg_increment(temp_dict:dict, curr_key:str):
    """format the dictionary inside the format_columns method to ensure collisions don't occur from multiple pkg 
    uploads from the same counterparty"""   
    key_list = list(temp_dict.keys())
    key_list = flatten([e.split('_') for e in key_list])
    if curr_key not in key_list:
        return f"{curr_key}_1"         
    else:
        next_elem = key_list[key_list.index(curr_key)+1]
        if next_elem.isdigit():
            return f"{curr_key}_{int(next_elem)+1}"
        
def get_NAICS_path():
    """returns the path for NAICS data"""
    naics_path = Path(__file__).resolve().parent / 'package_maps' / 'NAICS_2017.csv'
    return naics_path


class LoanTape:
    df: pd.DataFrame
    raw_dfs: dict
    naics: dict
    format_packages: dict
    correct_columns: list
    session_params: dict

    def norm_raw_cols(self):
        """Normalize the columns -- remove white space and line breaks"""
        if len(self.raw_dfs):
            # This creates a clone of the dict SELF.RAW_DFS cleaning up the original columns
            # NOTE -- This section has no error handling right now: any parsing errors will probably occur here
            norm_dfs = {}
            for key, df in self.raw_dfs.items():
                cols = df.columns.to_list()
                cols = [c.strip().replace("\n"," ") for c in cols]
                df.columns = cols
                df = df[rm_unnamed(cols)]
                norm_dfs[key] = df
            self.raw_dfs = norm_dfs
        else:
            print("No raw loan data")
        return None

    def load_format_packges(self):
        """parse the raw loan data by using the available packages"""
        pkg_path = Path(__file__).resolve().parent / 'package_maps' / 'packages.json'
        pkg_file = open(pkg_path)
        format_opts = json.load(pkg_file)
        return format_opts
    
    def __init__(self, clean_columns, data=list(), params:dict=None ):
        if params:
            self.session_params = params
        self.correct_columns = clean_columns
        self.df = pd.DataFrame(columns=clean_columns)
        self.raw_dfs = {f'unknown_{i}': df for i, df in enumerate(data)}
        self.norm_raw_cols()
        naics_tbl = pd.read_csv( get_NAICS_path() )
        self.naics = dict(naics_tbl.values)
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
                # NOTE--> if the format matches ~90% --> if not exact, it will still work and you can debug
                match_ratio = 1-len(temp_cols - format_type_keys) / len(format_type_keys)
                if match_ratio < .9:
                    continue
                else:
                    new_pkg_key = pkg_increment(temp_dict = temp, curr_key = key)
                    temp[new_pkg_key] = df.rename(columns=self.format_packages[key])
                    # This could/should be done in the column_map function
                    temp[new_pkg_key]['Pck / Deal'] = new_pkg_key
                    temp[new_pkg_key]['Industry'] = temp[new_pkg_key]['SIC / NAICS'].map(self.naics)
                    break
        self.raw_dfs.update(temp)
        return None


    def resolve_fhn(self, in_df):
        fhn_resolver = column_map.FHN_resolver(in_df, self.correct_columns, self.session_params)
        return fhn_resolver.resolve_columns()
    
    def resolve_rj(self, in_df):
        rj_resolver = column_map.RJ_resolver(in_df, self.correct_columns, self.session_params)
        return rj_resolver.resolve_columns()
    
    def resolve_bmo(self, in_df):
        bmo_resolver = column_map.BMO_resolver(in_df, self.correct_columns, self.session_params)
        return bmo_resolver.resolve_columns()
    
    # def resolve_columns(self):
    #     for key in self.raw_dfs.keys():
    #         pkg_type = str(key).split('_')[0]
    #         match pkg_type:
    #             case 'FHN':
    #                 self.raw_dfs[key] = self.resolve_fhn(self.raw_dfs[key])
    #             case 'RJ':
    #                 self.raw_dfs[key] = self.resolve_rj(self.raw_dfs[key])
    #             case 'BMO':
    #                 self.raw_dfs[key] = self.resolve_bmo(self.raw_dfs[key])


    def resolve_columns(self):
        for key in self.raw_dfs.keys():
            pkg_type = str(key).split('_')[0]
            if pkg_type == 'FHN':
                self.raw_dfs[key] = self.resolve_fhn(self.raw_dfs[key])
            elif pkg_type == 'RJ':
                self.raw_dfs[key] = self.resolve_rj(self.raw_dfs[key])
            elif pkg_type == 'BMO':
                self.raw_dfs[key] = self.resolve_bmo(self.raw_dfs[key])



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


        
        
    
