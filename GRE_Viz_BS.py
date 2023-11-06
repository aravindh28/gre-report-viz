from bs4 import BeautifulSoup
#from pathlib import Path
from IPython.display import display
import streamlit as st
import pandas as pd
from datetime import time
from io import StringIO

#'''This is a script to scrape data from ETS GRE diagnostic report html page for the Quant section and convert them into a df to be visualized by a Streamlit App'''

# -------------------- TO DOs --------------------
# 1. Convert datatypes in final html table to proper format
# 2. Convert into a basic streamlit app with basic charts
# 3. Allow user to input the html file
# 4. Is possible, try to web scrape with python twill library??


# takes on the tables which have the table structure we need, also while filtering only for rows which have values in timespent(the html file o/p was a bit weird, so filtering here makes it easy)
def table_clean_up(tab_df_list: list) -> list:
    col_name_set = {'Reference #','Question Type','Setting','Right/Wrong','Difficulty Level', 'Time Spent'}
    tab_df_list[:] = [ tab_df[tab_df['Time Spent'].str.contains(r"^\d\d:\d\d$")] for tab_df in tab_df_list if set(tab_df.columns.values.tolist()) == col_name_set]
    
    return tab_df_list

# for each table present in the data, see if there is a h3/h4 - if not then discard, this is because Section and Category of questions info is present as headers above the table and not as a part of the html table
def html_header_cleanup(headings: object) -> object:
    headings[:] = [header for header in headings if (header.find_previous_sibling('h3') is not None and header.find_previous_sibling('h4') is not None)] #find previous sibling finds the first instance of h3/h4 before in the html tree - see BS documentation for info
    
    return headings

# add the section, category data as new columns to each table dataframe.
def add_headers_to_df(h: list, t: list) -> list:
    df_list=[]
    for bs_table_tag, pd_table in zip(h, t):
        data = {'Section' : bs_table_tag.find_previous_sibling('h3').get_text(), 'Category': bs_table_tag.find_previous_sibling('h4').get_text()}
        pd_table = pd_table.assign(**data)
        df_list.append(pd_table)
        
    return df_list

def highlight_df_rows(og_df: pd.DataFrame) -> pd.DataFrame:
    mask_df = og_df.copy()
    mask = mask_df['Right/Wrong'] == "Right"
    mask_df.loc[mask,:] = 'background-color: green'
    mask = mask_df['Right/Wrong'] == "Wrong"
    mask_df.loc[mask,:] = 'background-color: red'
    print(mask_df)
    return mask_df
    

def convert_dtypes(og_df: pd.DataFrame) -> pd.DataFrame:
    convert_dict = {'Difficulty Level': int}
    og_df['Time Spent'] = pd.to_datetime(og_df['Time Spent'], format="%M:%M")
    og_df = og_df.astype(convert_dict)  
    return og_df
  

# main function
if __name__ == "__main__":
    
    # enter path to the html file of quant section of GRE - TBD will be replaced by streamlit upload or smth

    data = st.file_uploader("Upload html file here", type="htm")

    default_html_path = r'C:\Users\Admin\Desktop\GRE Diagnostic Analyser\ETS GRE Diagnostic Service Quantitative Reasoning.htm'

    if data is not None:
        #st.write(data.read())
        stringio = StringIO(data.getvalue().decode("windows-1252"))

    else:
        data = open(default_html_path, "r")
        data = data.read()
        stringio = StringIO(data)

    # create a BeautifulSoup object of the file to parse through the html, using lxml parser
    soup = BeautifulSoup(data, features="lxml")

    # find all tables present in the bs object, searching for tag table
    headings = soup.find_all('table')

    # read_html function coverts all tables present in a html file directly to dataframes
    tables = pd.read_html(stringio)

    clean_table = table_clean_up(tables) 
    clean_headings = html_header_cleanup(headings)
    new_df_list = add_headers_to_df(clean_headings, clean_table)

    if len(clean_table) == len(clean_headings):
        print('$$$$ table length matches with header length - looks fine')

    else:
        print('$$$$ something wrong with table length - check')

    for x in new_df_list:
        display(x)

    #concat all the table dataframes in the list into one, reset index 

    full_pd = pd.concat(new_df_list, axis=0)
    full_pd.reset_index(drop = True, inplace=True)

    print(full_pd.dtypes)

    full_pd = convert_dtypes(full_pd)

    print(full_pd.dtypes)

    full_pd.style.apply(highlight_df_rows, axis= None)

    #display(full_pd)

    tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
    options = st.multiselect('Question Type',[1,2])
    #st.write(full_pd)
    #tab1.write("sd")
    tab1.title("GRE Quant score visualizer")
    tab1.markdown("Use this app to visalize your diagnostic report data! :) ")
    tab1.info("Currently works for quant section of the OLD GRE, need to test with new diagnostic versions")
    tab2.dataframe(full_pd)




