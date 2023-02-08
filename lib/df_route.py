import geopy.distance
import pandas as pd

from boats.lib.common import ddm_to_dd


def get_route_from_file_as_df(f_csv, step=None):
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
        keep = [i for i in df.index if i % step == 0]
        keep.insert(0, 1)
        df.drop(df.index.drop(keep), axis=0, inplace=True)
        df.reset_index(inplace=True)
    dtws = [round(geopy.distance.geodesic((df.iloc[i - 1]['Lat'], df.loc[i]['Lon']),
                                          (df.iloc[i]['Lat'], df.iloc[i - 1]['Lon'])).nm) for i in range(1, len(df))]
    dtws.insert(0, 0)
    df['DTW'] = dtws
    df['Name'] = ['P{}'.format(i) for i in range(len(df))]
    return df
