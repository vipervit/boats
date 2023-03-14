import os

import geopy.distance
import pandas as pd

from boats import DIR_PKL, DIR_ROUTE_OUT
from boats.lib.common import ddm_to_dd


def get_route_from_txt_as_df(routename, f_dir=DIR_ROUTE_OUT):
    f_path = os.path.join(f_dir, '{}.txt'.format(routename))
    try:
        with open(f_path, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError
    text = text.replace(';', '')
    text = text.replace('\'', ' ')
    df = pd.DataFrame([(ddm_to_dd(x.split('  ')[0]), ddm_to_dd(x.split('  ')[1])) for x in text.split('\n')],
                      columns=['Lat', 'Lon'])
    df['Name'] = ['P{}'.format(i) for i in range(len(df))]
    return df


def get_route_from_route_file_as_df(f_csv, step=None):
    df = pd.read_csv(f_csv)
    df.drop(0, axis=0, inplace=True)
    df['Full'] = [x.split(';')[0] for x in df['position;heure']]
    df.drop('position;heure', axis=1, inplace=True)
    df['LAT'] = [x.split('  ')[0] for x in df['Full']]
    df['LON'] = [x.split('  ')[1] for x in df['Full']]
    df = df.assign(Lat=lambda x: x['LAT'].apply(ddm_to_dd))
    df = df.assign(Lon=lambda x: x['LON'].apply(ddm_to_dd))
    df['Full'] = [x + ';' for x in df['Full']]
    if step is not None:
        keep = [i for i in df.index if i % step == 0 or i == df.index[-1]]
        keep.insert(0, 1)
        df.drop(df.index.drop(keep), axis=0, inplace=True)
        df.reset_index(inplace=True)
    dtws = [round(geopy.distance.geodesic((df.iloc[i - 1]['Lat'], df.loc[i]['Lon']),
                                          (df.iloc[i]['Lat'], df.iloc[i - 1]['Lon'])).nm) for i in range(1, len(df))]
    dtws.insert(0, 0)
    df['DTW'] = dtws
    df['Name'] = ['P{}'.format(i) for i in range(len(df))]
    return df


def get_route_from_pathway_file_as_df(f_csv):
    df = pd.read_csv(f_csv)
    df.drop(0, axis=0, inplace=True)
    df.rename(columns={'From': 'Name', 'Lat': 'LAT', 'Lon': 'LON'}, inplace=True)
    df = df[['Name', 'LAT', 'LON']]
    df = df.assign(Lat=lambda x: x['LAT'].str.replace('\'', ' ').apply(ddm_to_dd))
    df = df.assign(Lon=lambda x: x['LON'].str.replace('\'', ' ').apply(ddm_to_dd))
    df['Full'] = ['{}  {};'.format(df.iloc[i]['LAT'].replace('\'', ' '), df.iloc[i]['LON'].replace('\'', ' ')) for i in range(len(df))]
    dtws = [round(geopy.distance.geodesic((df.iloc[i - 1]['Lat'], df.loc[i]['Lon']),
                                          (df.iloc[i]['Lat'], df.iloc[i - 1]['Lon'])).nm) for i in range(1, len(df))]
    dtws.insert(0, 0)
    df['DTW'] = dtws
    return df

def get_route_df_from_pickle(route_name):
    return pd.read_pickle(os.path.join(DIR_PKL, '{}.pkl'.format(route_name)))


def save_route_df_to_pickle(df, route_name):
    df.to_pickle(os.path.join(DIR_PKL, '{}.pkl'.format(route_name)))


def save_route_for_upload(df, filename):
    with open(os.path.join(DIR_ROUTE_OUT, '{}.txt'.format(filename)), 'w') as f:
        f.write('\n'.join(list(df['Full'])))
