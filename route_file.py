import os
import sys

# TODO sysopt
# TODO error handling and messaging

import pandas as pd

from boats.lib.common import DIR_HOME, timestamp

f_timestamp = timestamp().replace(':', '_').replace('/', ' ').replace(' ', '_')

zoom_start = 8

boat_name = sys.argv[1]
f_name = sys.argv[2]

f_csv_exported = os.path.join(DIR_HOME, 'routes', 'exported', '{}.csv'.format(f_name))
f_csv_fixed = os.path.join(DIR_HOME, 'routes', 'exported', '{}_fixed.csv'.format(f_name))
f_json = os.path.join(DIR_HOME, 'routes', 'exported', '{}.json'.format(f_name))
f_route = os.path.join(DIR_HOME, 'routes', 'import', '{}_{}.txt'.format(boat_name, f_timestamp))

with open(f_csv_exported, 'r') as f:
    contents = f.read()
with open(f_csv_fixed, 'w') as f:
    f.write(contents.replace(';', ';,'))

df = pd.read_csv(f_csv_fixed)
df.drop(0, axis=0, inplace=True)
text = '\n'.join(list(df['position;']))

with open(f_route, 'w') as f:
    f.write(text)
