#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import seaborn as sns 
import numpy as np
import statsmodels.api as sm
import scipy.stats as stats
from scipy.stats import epps_singleton_2samp as epps
import matplotlib.pyplot as plt
import warnings
from math import floor
from mlxtend.evaluate import permutation_test

MIN_SAMPLE_SIZE = 20
MIN_SAMPLE_SIZE_2 = 20

pd.set_option('precision', 2)

sns.set(
    context="paper",
    style="darkgrid",
    rc={"figure.dpi": 150}
)
df = pd.read_pickle('complete_lifetimes_v4.pd')
df_code_age = pd.read_json('codelifetimes.json', orient='index') 


# In[ ]:


df = df.loc[pd.isna(df.c_lifetime) == False]
df


# In[ ]:


df['lp_error'] = df.apply(lambda x: x.lp_lifetime - x.c_lifetime, axis=1)
df['vccfinder_error'] = df.apply(lambda x: x.vccfinder_lifetime - x.c_lifetime, axis=1)
df['w_error'] = df.apply(lambda x: x.h_lifetime - x.c_lifetime, axis=1)
np.mean(df.lp_error.to_numpy())


# In[ ]:


for project in ['kernel', 'chrome', 'httpd']:
    df_proj = df.loc[df.project == project]
    
    lp_err = np.mean(df_proj.lp_error)
    lp_std = np.std(df_proj.lp_error)
    
    vcc_err = np.mean(df_proj.vccfinder_error)
    vcc_std = np.std(df_proj.vccfinder_error) 
    
    w_err = np.mean(df_proj.w_error)
    w_std = np.std(df_proj.w_error) 
    
    print(f'{project:<10}{df_proj.shape[0]:<7}& {f"{lp_err:0.2f}":<10}& {f"{lp_std:0.2f}":<10}& {f"{vcc_err:0.2f}":<10}& {f"{vcc_std:0.2f}":<10}& {f"{w_err:0.2f}":<10}& {f"{w_std:0.2f}":<10}')

df_proj = df
lp_err = np.mean(df_proj.lp_error)
lp_std = np.std(df_proj.lp_error)

vcc_err = np.mean(df_proj.vccfinder_error)
vcc_std = np.std(df_proj.vccfinder_error) 

w_err = np.mean(df_proj.w_error)
w_std = np.std(df_proj.w_error) 

print(f'{"all":<10}{df_proj.shape[0]:<7}& {f"{lp_err:0.2f}":<10}& {f"{lp_std:0.2f}":<10}& {f"{vcc_err:0.2f}":<10}& {f"{vcc_std:0.2f}":<10}& {f"{w_err:0.2f}":<10}& {f"{w_std:0.2f}":<10}')



# In[ ]:


1-117/(346.88-117)


# In[ ]:


#df = df
df_temp = df.loc[df.w_error != 0]
ax = sns.histplot(data=df_temp, x='w_error', bins=100, stat='density')
ax.set_xlabel('Heuristic error (days)')
ax.set(xlim=(-2000, 2000))
print(f'Bin-width: {ax.patches[0].get_width()}')
plt.savefig('../out/gt_eval/w_average_error_wo_zero.pdf', bbox_inches='tight')
plt.figure()
#df = df.loc[df.lp_error != 0]
ax = sns.histplot(data=df, x='lp_error', bins=200)
ax.set(xlim=(-2000, 2000))


# ## Constant factor

# In[ ]:


df_chrome1 = df.loc[df.project == 'chrome'].loc[df.fix_year < 2014]
df_kernel1 =df.loc[df.project == 'kernel'].loc[df.fix_year < 2014]
df_chrome2 = df.loc[df.project == 'chrome'].loc[df.fix_year >= 2014]
len(df_chrome1), len(df_chrome2)


# In[ ]:


constant = np.mean(df_chrome1.lp_error)
print(f'Constant for fixes pre 2014: {constant}')
df_chrome2['lp_adj_const'] = df.lp_error.apply(lambda x: x - constant)
print(f'Error using constant on 2014 and older: {np.mean(df_chrome2.lp_adj_const)}')
print(f'W avg error on 2014 and older: {np.mean(df_chrome2.w_error)}')
print()
print(f'Kernel pre 2014 const:{np.mean(df_kernel1.lp_error)}')

