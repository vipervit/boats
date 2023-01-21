#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
import datetime
import pytz

from bs4 import BeautifulSoup


# In[2]:


def get_races(oRaces):
    return oRaces.find_all('a')


# In[3]:


def get_mileage(oRace):
    return round(float(oRace.find_all_next('td')[3].contents[0].strip(' NM')))


# In[4]:


def get_race_name(oRace):
    return oRace.contents[0]


# In[5]:


def get_race_time(oRace):
    return datetime.datetime.fromisoformat(oRace.find_all_next('span')[1].contents[0]).astimezone(pytz.timezone('EST')).strftime('%A %d-%h %I:%M %p')


# In[6]:


short_mileage = 50


# In[7]:


r = requests.get('https://sarl.ingenium.net.au/index')


# In[8]:


soup = BeautifulSoup(r.text, 'html.parser')
upcoming = soup.find('table')


# In[9]:


data=[(get_race_name(race), get_mileage(race), get_race_time(race)) for race in get_races(upcoming)]


# In[10]:


df=pd.DataFrame(data, columns=['Race', 'Mileage', 'Time'])
df


# In[11]:


df_short_on_weekends = df[(df['Mileage'] < short_mileage) & (df['Time'].str.contains('Saturday') | df['Time'].str.contains('Sunday'))]


# In[12]:


print(df)


# In[17]:


print('------------------\nShort starting on weekends:\n {}'.format(df_short_on_weekends))


# In[ ]:




