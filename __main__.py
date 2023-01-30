import getopt
import sys

import boats.racemap as racemap
import boats.route_pos as route_pos
import boats.racemarks as racemarks
import boats.chart_pos as chart_pos


def usage():
    print('-p <boat> : Boat position and route with or without opening map')
    print('-r <boat> <race> <zoom or \'noview\'> (optional, 7 if omitted): Race status with or without opening map')
    print('-m <race> : Get racemarks and save in CSV files')


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hprmc")
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    if len(opts) == 0 or len(args) == 0:
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == '-h':
            usage()
            sys.exit(0)
        if o == '-p':
            route_pos.main(args)
        if o == "-r":
            racemap.main(args)
        if o == '-m':
            racemarks.main(args[0])
        if o == '-c':
            chart_pos.main(args)


if __name__ == "__main__":
    main()
