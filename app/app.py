import streamlit as st
import pandas as pd
from openpyxl import load_workbook


def load_excel_file(file):
    wb = load_workbook(file)
    sheet = wb.active
    data = sheet.values
    columns = next(data)[1:]
    df = pd.DataFrame(data, columns=columns)
    return df


st.title("Excel File Uploader")

file = st.file_uploader("Upload a file", type=["xlsx"])

if file is not None:
    df = load_excel_file(file)
    st.write(df)