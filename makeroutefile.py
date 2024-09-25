import argparse
import os
import sys

from boats import DIR_ROUTE_IN
from boats.lib.df_route import get_route_from_pathway_file_as_df, get_route_from_route_file_as_df, \
    save_route_for_upload, make_route_upload_file


def main(args):

    parser = argparse.ArgumentParser(description='Prepares route file.')
    parser.add_argument('--route_name', type=str)
    parser.add_argument('--route_type', type=str)
    parser.add_argument('--step', type=int)
    args = parser.parse_args(args)

    fname_in = args.route_name
    fname_out = 'Route'

    if args.route_name is not None:
        fname_out = args.route_name

    # f = os.path.join(DIR_ROUTE_IN, '{}.csv'.format(fname_in))

    if args.route_type == 'route':
        make_route_upload_file(args.route_name)
        # df = get_route_from_route_file_as_df(f, step=args.step)
    elif args.route_type == 'pathway':
        df = get_route_from_pathway_file_as_df(f)
    else:
        sys.exit('Invalid route type: {}'.format(args.route_type))

    # print(df)
    #
    # save_route_for_upload(df, fname_out)


if __name__ == '__main__':
    main(sys.argv[1:])
