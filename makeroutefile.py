import argparse
import sys
import pandas as pd
from argparse import ArgumentParser

from boats import DIR_ROUTE_IN, DIR_ROUTE_OUT
from lib.common import dd_to_dddm_single


def main(args):
    parser: ArgumentParser = argparse.ArgumentParser(description='Prepares route file.')
    parser.add_argument('--boat_name', type=str)
    args = parser.parse_args(args)

    f_in = f'{DIR_ROUTE_IN}/{args.boat_name}.csv'
    f_out = f'{DIR_ROUTE_OUT}/{args.boat_name}.txt'

    df = pd.read_csv(f_in)
    df['LAT'] = df['LAT'].apply(lambda x: dd_to_dddm_single(x, coortype=0))
    df['LON'] = df['LON'].apply(lambda x: dd_to_dddm_single(x, coortype=1)) + ';'
    df.to_csv(f_out, index=False, header=None)

    with open(f_out, 'r') as f:
        text = f.read().replace(',', '  ')
    with open(f_out, 'w') as f:
        f.write(text)


if __name__ == '__main__':
    main(sys.argv[1:])
