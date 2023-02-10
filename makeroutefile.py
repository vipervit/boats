import argparse
import os
import sys

from boats import DIR_ROUTE_IN
from boats.lib.df_route import get_route_from_route_file_as_df, save_route_df_to_pickle, \
    save_route_for_upload


# TODO sysopt
# TODO error handling and messaging


def main(args):

    parser = argparse.ArgumentParser(description='Prepares route file.')
    parser.add_argument('--boat_name')
    parser.add_argument('--route_name')
    parser.add_argument('--step', type=int)
    args = parser.parse_args(args)

    fname_in = args.route_name

    if args.boat_name is not None:
        fname_out = args.boat_name
    else:
        fname_out = 'Route'

    df = get_route_from_route_file_as_df(os.path.join(DIR_ROUTE_IN, '{}.csv'.format(fname_in)), step=args.step)
    save_route_df_to_pickle(df, args.route_name)
    print(df)

    save_route_for_upload(df, fname_out)


if __name__ == '__main__':
    main(sys.argv[1:])
