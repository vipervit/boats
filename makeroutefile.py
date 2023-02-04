import argparse
import os
import sys

from boats import DIR_ROUTE_IN, DIR_ROUTE_OUT
from boats.lib.common import timestamp
from boats.lib.df_route import get_route_from_file_as_df


# TODO sysopt
# TODO error handling and messaging


def main(args):

    parser = argparse.ArgumentParser(description='Prepares route file.')
    parser.add_argument('--boat_name')
    parser.add_argument('--file_name')
    args = parser.parse_args(args)

    boat_name = args.boat_name
    f_name = args.file_name

    f_timestamp = timestamp().replace(':', '_').replace('/', ' ').replace(' ', '_')

    f_csv = os.path.join(DIR_ROUTE_IN, '{}.csv'.format(f_name))
    f_route = os.path.join(DIR_ROUTE_OUT, '{}_{}.txt'.format(boat_name, f_timestamp))

    df = get_route_from_file_as_df(f_csv)

    with open(f_route, 'w') as f:
        f.write('\n'.join(list(df['Full'])))


if __name__ == '__main__':
    main(sys.argv[1:])
