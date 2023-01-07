#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
from datetime import datetime


# In[2]:


url='https://sarl.ingenium.net.au/racelog?racenr=38602'
res=requests.get(url)
myboat='PETSAMO'


# In[3]:


boats = res.json()['result']


# In[4]:


boats


# In[5]:


ranks=[ (boats[boat]['ubtname'].upper(),
         boats[boat]['usrname'].upper(),
         boats[boat]['rank'],
         boats[boat]['resultdescr'].split(',')[1].replace(' Hdg: ', ''),
         boats[boat]['resultdescr'].split(',')[2].replace(' Spd: ', '').replace('kn.', ''),
         boats[boat]['resultdescr'].split(',')[3].split('nm')[0].split('.')[0].strip(),
         boats[boat]['resultdescr'].split(',')[3].split('mark ')[1],
         boats[boat]['resultdescr'].split(',')[0],
         str(boats[boat]['lat_dec']) + " " + str(boats[boat]['lon_dec']),
         datetime.fromtimestamp(boats[boat]['timestamp']/1000).strftime('%d/%m %H:%M')
        )
       for boat in boats if 'heading' in boats[boat]
      ]


# In[6]:


ranks


# In[8]:


#!/usr/bin/env python
# coding: utf-8



df=pd.DataFrame(ranks)
df.columns=['Boat', 'User', 'Rank', 'HDG', 'SPD', 'DTW', 'WPT', 'POS1', 'POS2', 'As of']
df['Rank']=df['Rank'].astype(int)
df=df.set_index('Rank')
df.sort_values('Rank', ascending=True, inplace=True)

df.at[df[df['Boat']==myboat].index[0], 'Boat']='<======= ' + myboat + ' =======>'

behind=float(df[df.index==1]['DTW'][1]) - float(df[df['Boat'].str.contains(myboat)]['DTW'].values[0])
print(df)
print('')
print('Behind leader by: {} nm'.format(round(behind),2))


# In[ ]:





# In[ ]:





# In[ ]:




