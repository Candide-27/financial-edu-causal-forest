# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 19:28:40 2022

@author: t.huynh
"""
import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from os.path import isfile, join

from econml.dml import (
    CausalForestDML,
    LinearDML
)
from econml.cate_interpreter import (
    SingleTreePolicyInterpreter,
    SingleTreeCateInterpreter
)
from sklearn.linear_model import MultiTaskLassoCV
from sklearn.model_selection import train_test_split

from utils import export_df



def transform_df(PATH,
                 f,
                 round=1):
    #Reading the data----------------------------------------------------------
    df = pd.read_stata(join(PATH, f))
    var_labels = pd.io.stata.StataReader(join(PATH, f)).variable_labels()
    
    #one-hot encoding treatment and female coded
    for col in ['treatment', 'female_coded']:
        df[col] = pd.get_dummies(df[col])['yes']
    
    #Retain round1 and round2 surveys------------------------------------------
    round_one = df[
        df['round']=='no'    
    ]
    round_two = df[
        df['round']=='yes'    
    ]
    
    #Single out baseline variables---------------------------------------------
    baseline = {
        col : var_labels.get(col) 
        for col in df.columns if col.endswith('bl')
    }
    baseline['female_coded'] = var_labels.get('female_coded')
    
    #List out the prefixes of the covar that we would like to include in our causal forest
    prefixes = (
        'female_coded',
        'vl_proficiencia',
        'dumm_rp_08',
        'dumm_rp_09',
        'dumm_rp_24',
        'dumm_rp_14',
        'dumm_rp_23',
        'dumm_rp_50',\
        'dumm_rp_49',
        'dumm_rp_65A',
        'dumm_rp_64A',
        'dumm_rp_95'        
    )
    
    #Specify the Y, X, W columns-----------------------------------------------
    W = ['treatment']
    X = [
        var for var in baseline
        if var.startswith(prefixes)
    ]
    Y = ['vl_proficiencia_fup']
    ID = ['id_geral', 'cd_escola']
    
    #Retain the columns in the 2 dataset accordingly
    round_one = round_one[
        ID + Y + W + X     
    ]
    round_two = round_two[
        ID + Y + W + X    
    ]
    
    #Drop NA in the Y columns
    round_one = round_one.dropna(subset=Y)
    round_two = round_two.dropna(subset=Y)
    
    #Set student_id as index
    round_one = round_one.set_index(['id_geral'])
    round_two = round_two.set_index(['id_geral'])
    
    #Returning
    if round == 1:
        return round_one
    else:
        return round_two
    
    
    
    
    #Check for the distribution of nan values in each variables----------------
    #First replace all the nan with a string
    round_one = round_one.replace(np.nan, 'NA')
    round_two = round_two.replace(np.nan, 'NA')
    #Then check
    distribution = {}
    for var in list(baseline.keys()):
        if var.startswith(prefixes):
            count = round_one[[var, 'id_geral']].groupby([var]).count()
            count['prop'] = count['id_geral'] / sum(count['id_geral'])
            distribution[var_labels.get(var)] = count['prop']
    #Check individually for endline proficiencia
    count = round_one[['vl_proficiencia_fup', 'id_geral']].groupby('vl_proficiencia_fup').count()
    count['prop'] = count['id_geral'] / sum(count['id_geral'])
    



if __name__ == 'main':
    
    #BASE
    BASE_PATH = r'C:\Personal\Thesis\git'
    
    #ALL_PATHS
    BRAZIL_PATH = join(BASE_PATH, r'raw')
    
    SAVE_PATH_TRANSFORM = join(BASE_PATH, r'transform')
    
    #variables
    F = 'school_intervention_panel_final.dta'
    round = 1
    
    #Export====================================================================
    export_df(
        transform_df,
        SAVE_PATH_TRANSFORM, 
        f'Brazil2016_transform_round{round}',
        fun_kwargs={
            'PATH':join(BASE_PATH, BRAZIL_PATH),
            'f':F,
            'round':round
        }
    )