import sys, os, mock
import pytest
from collections import namedtuple
from pyfakefs import fake_filesystem_unittest
import CommonUtils
from datetime import datetime
import pytz

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(SRC_PATH, '../src/')
sys.path.append(SRC_PATH)
from autocut import checkSanityDir
from autocut import main
from autocut import shouldDelete
from Scheduling import SegmentScheduler, ScheduledEvent
from CommonUtils import createVideoSegment


from pyfakefs import fake_filesystem_unittest

class TestAutocut(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory('/usr/local/lib/python3.6/dist-packages')
        self.dirSrc = '/mnt/src'
        self.dirDst = '/mnt/dst'
        self.dirTmp = '/mnt/tmp'

        self.fs.create_dir(self.dirSrc)
        self.fs.create_dir(self.dirDst)
        self.fs.create_dir(self.dirTmp)


    def cleanUp(self, objectList):
        for o in objectList:
            self.fs.remove_object(o)

    def fest_sanity(self):
        self.assertFalse(checkSanityDir('/mnt/src', '/mnt/dst'))
        self.fs.create_dir(self.dirSrc)
        self.fs.create_dir(self.dirDst)
        self.assertTrue(checkSanityDir('/mnt/src', '/mnt/dst'))

    @mock.patch('autocut.parseArguments')
    def test_main(self, pa):
        #self.fs.create_dir(self.dirSrc)
        #self.fs.create_dir(self.dirDst)
        #self.fs.add_real_directory('/home/user/videoSrc')

        ParsedArgs = namedtuple('ParsedArgs', ['directorySrc', 'directoryDst', 'directoryTmp', 'dryRun'])
        args = ParsedArgs(
                directorySrc=self.dirSrc,
                directoryDst=self.dirDst,
                directoryTmp=self.dirTmp,
                dryRun=True)
        pa.return_value = args
        #main()

    def test_should_delete(self):
        ParsedArgs = namedtuple('ParsedArgs', ['directorySrc', 'directoryDst', 'directoryTmp', 'dryRun'])
        args = ParsedArgs(
                directorySrc=self.dirSrc,
                directoryDst=self.dirDst,
                directoryTmp=self.dirTmp,
                dryRun=True)
        events = []
        events.append(ScheduledEvent(name='Alegria',  hour=6, minute=30, second=0, PM=True, duration='1:35:00'))
        events.append(ScheduledEvent(name='Footwork', hour=8, minute=00, second=0, PM=True, duration='1:05:00'))
        events.append(ScheduledEvent(name='Ritmo',    hour=9, minute=00, second=0, PM=True, duration='1:35:00'))

        segments = []

        segments.append(createVideoSegment('/mnt/tmp/Footwork_2', '2018:10:31 20:06:00', 1353.352))
        segments.append(createVideoSegment('/mnt/tmp/Footwork_3', '2018:10:31 20:28:00', 1353.352))
        clippedForRitmo = createVideoSegment('/mnt/tmp/Footwork_1', '2018:10:31 20:55:00', 1353.352)
        segments.append(clippedForRitmo)

        for s in segments:
            self.fs.create_file(s.filePath)

        scheduler = SegmentScheduler(args.directoryTmp, events)
        dt = datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S")
        scheduler.set_date(dt)
        ret = scheduler.calculate(segments)

        for team, cutList in ret.items():
            for cut in cutList:
                ret = shouldDelete(cut, events, args)
                if cut.segment == clippedForRitmo:
                    print("asserting: Segment must be deleted:" + cut.cutFilePath + " vs " + str(ret))
                    self.assertTrue(ret)
                else:
                    print("asserting: Segment must not be deleted:" + cut.cutFilePath)
                    self.assertFalse(ret)
