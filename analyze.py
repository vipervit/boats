#!/usr/bin/env python
# coding: utf-8

# In[1]:


import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
from lib.common import *
from lib.boat import boat


# In[2]:


boatname = 'Petsamo'

sails = ['Nr.1', 'Nr.2', 'Nr.3', 'Stormjib', 'Mainsail', 'Genaker', 'Mizzen', 'Mizzen staysail']
points_of_sail={
    'close haul': list(range(0,37)),
    'close reach': list(range(36,73)),
    'beam': list(range(72,109)),
    'broad reach': list(range(108,145)),
    'run': list(range(144,181))
}
yesmark = 'x'
nomark = '-'


# In[3]:


df=boat(boatname).get_sail_data()
df.dropna(inplace=True)
df['heel']=df['heel'].apply(lambda x: int(abs(x)))
df['twa']=df['twa'].apply(lambda x: abs(x))
df=df[df['spd']!=0]
df['spd / tws']=round(df['spd']/df['tws'],2)
df.reset_index(inplace=True, drop=True)
df.head()


# #### Expand sail data:

# In[4]:


for i in range(len(df.index)):
    for sail in sails:
        if sail in df.iloc[i]['sails']:
            mark = yesmark
        else:
            mark = nomark
        df.at[i, sail] = mark
        
df.drop(['sails'], axis=1, inplace=True)
df.head()    


# In[5]:


df['pos'] = [name for i in df.index for name in points_of_sail if df.iloc[i]['twa'] in points_of_sail[name]]
df


# In[20]:


sns.regplot(df, x='tws', y='spd').set(title='spd to tws')


# In[17]:


for sail in sails:
    sns.lmplot(df, x='tws', y='spd', hue=sail).set(title='spd to tws by sail')


# In[18]:


sns.lmplot(df, x='tws', y='heel').set(title='heel by tws')


# In[19]:


sns.lmplot(df, x='tws', y='spd / tws').set(title='Speed efficiency to tws')


# In[9]:


df_pos=df.sort_values('twa')[['pos'] + sails].reset_index(drop=True)
df_pos


# In[10]:


df_pos=df_pos.replace(yesmark, 1)
df_pos=df_pos.replace(nomark, 0)
df_pos


# In[11]:


df_plot=df_pos.groupby('pos').sum()
df_plot


# In[15]:


sns.heatmap(df_plot).set(title='Sail types usage by point of sail')


# In[14]:


sns.countplot(df_pos, x='pos').set(title='Points of sail frequency')


# In[ ]:




