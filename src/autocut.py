import argparse
import time
from pytz import timezone
import os
import datetime
import ffmpeg
import pytz


def printVideoInformation(args):
    for fileName in os.listdir(args.directorySrc):
        fileName = os.path.join(args.directorySrc, fileName)
        probe = ffmpeg.probe(fileName)
        print(probe)


def main():
    print('AutoCutter started @ ' + getTimeStr() + '!')
    args = parseArguments()
    print (args)
    while (checkSanityDir(args.directorySrc, args.directoryDst) == False):
        print ('Failed sanity check, looping..')
        time.sleep(5)
    printVideoInformation(args)

def getTimeStr():
    try:
        tz = timezone('America/New_York')
    except pytz.exceptions.UnknownTimeZoneError:
        tz = timezone('UTC')

    tz = timezone('America/New_York')
    return datetime.datetime.now() \
        .astimezone(tz) \
        .strftime("%a, %b %d, %Y %I:%M:%S %p")


def checkSanityDir(dirSrc, dirDst):
    # Check src existence
    if os.path.isdir(dirSrc) is not True:
        print ('Source directory does not exist: ' + dirSrc)
        return False;

    # Check dst existence
    if os.path.isdir(dirDst) is not True:
        print ('Destination directory does not exist: ' + dirDst)
        return False;

    # Check src permission existence
    if not os.access(dirSrc, os.W_OK):
        print ('Source directory has no write permission: ' + dirSrc)
        return False;

    # Check dest permission existence
    if not os.access(dirDst, os.W_OK):
        print ('Destination directory has no write permission: ' + dirDst)
        return False;

    # All set
    return True


def parseArguments():
    parser = argparse.ArgumentParser(description='Autocut Argument Parser')
    parser.add_argument('--src', dest='directorySrc', nargs=1, required=True,
            help='The source directory where to search for files to merge and join')
    parser.add_argument('--dst', dest='directoryDst', nargs=1, required=False,
            help='The destination directory where to move files that have ' +
            'been cut and joined')
    parser.add_argument('--dry', dest='dryRun', action='store_true',
            help='Dry run, do not rename, or move anything. Print each the' +
            'timestamp of each cut segement')
    parsed_args = parser.parse_args()
    parsed_args.directorySrc = os.path.abspath(parsed_args.directorySrc[0])
    parsed_args.directoryDst = os.path.abspath(parsed_args.directoryDst[0])
    return parsed_args

if __name__ == '__main__':
    main()

