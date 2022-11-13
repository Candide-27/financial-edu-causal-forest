# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 19:14:07 2022

@author: t.huynh
"""
from datetime import datetime as dt
from os.path import join

def export_df(
    function,
    path,
    file_name,
    file_type=".csv",
    fun_kwargs={},
):

    # Perform function to generate df 
    df = function(**fun_kwargs)
    
    # Concatenate time
    now = dt.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{file_name}_{now}{file_type}"
  

    # make file_name and save
    file = join(path, file_name)
    df.to_csv(file)
    print(f"File saved under {file}")
    
    return None