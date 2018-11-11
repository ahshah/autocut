import sys, os, mock
from pytz import timezone
import unittest
from datetime import timedelta
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(SRC_PATH, '../src/')
sys.path.append(SRC_PATH)
from cutter import SegmentCutter
from Scheduling import SegmentCut
from VideoSegment import VideoSegment

from pyfakefs import fake_filesystem_unittest

class TestCutter(fake_filesystem_unittest.TestCase):
    dirSrc = None
    dirDst = None
    dirTmp = None
    segments = []

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory('/usr/local/lib/python3.6/dist-packages')
        self.dirSrc = '/mnt/src'
        self.dirDst = '/mnt/dst'
        self.dirTmp = '/mnt/tmp'

        self.fs.create_dir(self.dirSrc)
        self.fs.create_dir(self.dirDst)
        self.fs.create_dir(self.dirTmp)
        self.setupSegments()


    def cleanUp(self, objectList):
        for o in objectList:
            self.fs.remove_object(o)

    def test_ffmpeg_command(self):
        cutter = SegmentCutter(self.dirTmp)
        cutStart = timedelta(seconds=100)
        duration = timedelta(seconds=30)
        cut = SegmentCut(segment=self.segments[0], cutStart=cutStart, cutDuration=duration, cutFilePath='/tmp/barbarfoo')
        cutter.run(cut, dryRun=True);

        print (f"FFMPEG command for cut with: {cut}" )
        for f in os.listdir(self.dirTmp):
            print ("In Tmp: " + f)

    def setupSegments(self):
        segs = ({"SourceFile":"/home/user/videoSrc/18.10.31_185801.mp4",
        "QuickTime:TrackCreateDate":"2018:10:31 22:58:01",
        "QuickTime:TrackDuration":1353.352},
        {"SourceFile":"/home/user/videoSrc/18.10.31_192035.mp4",
        "QuickTime:TrackCreateDate":"2018:10:31 23:20:35",
        "QuickTime:TrackDuration":1353.36})
        for s in segs:
            self.segments.append(VideoSegment(s))
