import argparse
import os
import sys

# TODO sysopt
# TODO error handling and messaging

import pandas as pd

from boats import DIR_ROUTE_IN, DIR_ROUTE_OUT, DIR_ROUTE_TMP
from boats.lib.common import timestamp


def main(args):

    parser = argparse.ArgumentParser(description='Prepares route file.')
    parser.add_argument('boat_name')
    parser.add_argument('file_name')
    args = parser.parse_args(args)

    boat_name = args.boat_name
    f_name = args.file_name

    f_timestamp = timestamp().replace(':', '_').replace('/', ' ').replace(' ', '_')

    f_csv_exported = os.path.join(DIR_ROUTE_IN, '{}.csv'.format(f_name))
    f_csv_fixed = os.path.join(DIR_ROUTE_TMP, '{}_fixed.csv'.format(f_name))
    f_route = os.path.join(DIR_ROUTE_OUT, '{}_{}.txt'.format(boat_name, f_timestamp))

    with open(f_csv_exported, 'r') as f:
        contents = f.read()
    with open(f_csv_fixed, 'w') as f:
        f.write(contents.replace(';', ';,'))

    df = pd.read_csv(f_csv_fixed)
    df.drop(0, axis=0, inplace=True)
    text = '\n'.join(list(df['position;']))

    with open(f_route, 'w') as f:
        f.write(text)


if __name__ == '__main__':
    main(sys.argv[1:])
