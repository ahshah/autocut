import argparse
import time
from pytz import timezone
import os
from datetime import datetime
import collections

import ffmpeg
import pytz
import exiftool
import json
from datetime import timedelta
from VideoSegment import VideoSegment

FileDate = collections.namedtuple('FileDate', ['fpath', 'date', 'start_time', 'end_time', 'duration'])

def concatenateVideos(args):
    files = []
    streams =[]
    for fileName in os.listdir(args.directorySrc):
        files.append(fileName)
        fileName = os.path.join(args.directorySrc, fileName)
        #probe = ffmpeg.probe(fileName)
        #print(probe)

    files.sort()
    for f in files:
        print ('Got file: ' + f)
        streams.append(ffmpeg.input(fileName, format='concat'))
        print(f)

    fname = os.path.splitext(files[0])[0]
    fext  = os.path.splitext(files[0])[1]
    dest = fname+"_full"+fext
    dest = os.path.join(args.directoryDst, dest)

    print("Concatenate to: " + dest)
    l = len(streams)
    print("length of files: " +  str(l))

#    cmd = ffmpeg.concat(*streams).output(dest, codec='copy').compile()
    c = ffmpeg.concat(*streams)
    cmd = ffmpeg.output(c, dest).compile()

    print("COMPLETE concatenation to: " + dest)
    print("COMPLETE concatenation command : " + ' '.join(cmd))


def buildSegments(args):
    files = []
    days = {}
    for fileName in os.listdir(args.directorySrc):
        fileName = os.path.join(args.directorySrc, fileName)
        files.append(fileName)

    with exiftool.ExifTool() as et:
        metadata = et.get_metadata_batch(files)

    for m in metadata:
        if not VideoSegment.check_metadata_sanity(m):
            continue

        segment = VideoSegment(m)
        segDate = segment.getDate()
        if not segment.isWednesday():
            continue
        if segDate not in days:
            days[segDate]= []
        days[segDate].append(segment.__dict__())

    print("Got dict:" + json.dumps(days, sort_keys=True, indent=4))

def dumpExifInfo(args):
    files = []
    days = {}
    for fileName in os.listdir(args.directorySrc):
        fileName = os.path.join(args.directorySrc, fileName)
        files.append(fileName)

    with exiftool.ExifTool() as et:
        metadata = et.get_metadata_batch(files)

    for m in metadata:
        print("Got Exif:" + json.dumps(m, sort_keys=True, indent=4))
        if 'QuickTime:TrackCreateDate' not in m:
            print ("Skipping file")
            continue

def main():
    print('AutoCutter started @ ' + getTimeStr() + '!')
    args = parseArguments()
    print (args)
    while (checkSanityDir(args.directorySrc, args.directoryDst) == False):
        print ('Failed sanity check, looping..')
        time.sleep(5)
#    concatenateVideos(args)
    dumpExifInfo(args)
    buildSegments(args)

def getTimeStr():
    try:
        tz = timezone('America/New_York')
    except pytz.exceptions.UnknownTimeZoneError:
        tz = timezone('UTC')

    tz = timezone('America/New_York')
    return datetime.now() \
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
            'timestamp of each cut segment')
    parsed_args = parser.parse_args()
    parsed_args.directorySrc = os.path.abspath(parsed_args.directorySrc[0])
    parsed_args.directoryDst = os.path.abspath(parsed_args.directoryDst[0])
    return parsed_args

if __name__ == '__main__':
    main()

