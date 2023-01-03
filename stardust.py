#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import pandas as pd

url='https://sarl.ingenium.net.au/racelog?racenr=38602'
res=requests.get(url)
me='VIPER VIT'


# In[2]:


boats = res.json()['result']


# In[3]:


boats


# In[4]:


ranks=[ (boats[boat]['usrname'].upper(),
         boats[boat]['rank'],
         boats[boat]['resultdescr'].split(',')[1].replace(' Hdg: ', ''),
         boats[boat]['resultdescr'].split(',')[2].replace(' Spd: ', '').replace('kn.', ''),
         boats[boat]['resultdescr'].split(',')[3].split('nm')[0].split('.')[0].strip(),
         boats[boat]['resultdescr'].split(',')[3].split('mark ')[1],
         boats[boat]['resultdescr'].split(',')[0],
         str(boats[boat]['lat_dec']) + " " + str(boats[boat]['lon_dec'])
        )
       for boat in boats if 'heading' in boats[boat]
      ]


# In[5]:


df=pd.DataFrame(ranks)
df.columns=['User', 'Rank', 'HDG', 'SPD', 'DTW', 'WPT', 'POS1', 'POS2']
df['Rank']=df['Rank'].astype(int)
df=df.set_index('Rank')
df.sort_values('Rank', ascending=True, inplace=True)

df.at[df[df['User']==me].index[0], 'User']='<======= ' + me + ' =======>'


# In[6]:


behind=float(df[df.index==1]['DTW'][1]) - float(df[df['User'].str.contains(me)]['DTW'].values[0])
print(df)
print('')
print('Behind leader by: {} nm'.format(round(behind),2))


# In[ ]:




