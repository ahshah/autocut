import sys, os, mock
import time
import pytz
from datetime import datetime
from datetime import timedelta
import unittest
import json

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(SRC_PATH, '../src/')
sys.path.append(SRC_PATH)
from Scheduling import SegmentScheduler
from Scheduling import ScheduledEvent
from VideoSegment import VideoSegment
from cutter import SegmentCutter
from cutter import SegmentJoiner
from CommonUtils import createVideoSegment


class TestSchheduling(unittest.TestCase):
    events = []
    segments = []

    def setUp(self):
        self.events.append(ScheduledEvent(name='Alegria',  hour=6, minute=30, second=0, PM=True, duration='1:35:00'))
        self.events.append(ScheduledEvent(name='Footwork', hour=8, minute=00, second=0, PM=True, duration='1:05:00'))
        self.events.append(ScheduledEvent(name='Ritmo',    hour=9, minute=00, second=0, PM=True, duration='1:35:00'))
        self.setupSegments()

    def test_set_date(self):
        dt = datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S")
        dt_expected = datetime.strptime("2018:10:31_00:00:00", "%Y:%m:%d_%H:%M:%S")
        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(dt)
        self.assertTrue(scheduler.m_dateAtMidnight == dt_expected)

    def test_get_event_date(self):
        dt = datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S")
        expected_start = datetime.strptime("2018:10:31_18:30:00", "%Y:%m:%d_%H:%M:%S")
        expected_start = pytz.timezone('US/Eastern').localize(expected_start)
        expected_end = datetime.strptime("2018:10:31_20:05:00", "%Y:%m:%d_%H:%M:%S")
        expected_end = pytz.timezone('US/Eastern').localize(datetime.strptime("2018:10:31_20:05:00", "%Y:%m:%d_%H:%M:%S"))
        expected_dur = timedelta(hours=1, minutes=35)

        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(dt)
        ev_date = scheduler.get_event_date(self.events[0])

        # print (f"Start : {ev_date.getStartTime()}")
        # print (f"Durat : {ev_date.getDuration()}")
        # print (f"End   : {ev_date.getEndTime()}")
        self.assertTrue(ev_date.getStartTime() == expected_start)
        self.assertTrue(ev_date.getEndTime() == expected_end)
        self.assertTrue(ev_date.getDuration() == expected_dur)


    def test_calculation(self):
        dt = datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S")
        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(dt)
        ret  = scheduler.calculate(self.segments)
        for k, value in ret.items():
#            print (f"Key : {k}")
            cut_duration = timedelta(seconds=0)
            for cut in ret[k]:
#                print (f"   File: {cut.segment.filePath}")
#                print (f" Dura: {cut.segment.duration}")
#                print (f" Dura: {cut.cutDuration}")
                cut_duration+=cut.cutDuration
#                print (f"   : {cut_duration}")

#            print (f"    total duration: {cut_duration}")
#        print("Got:" + json.dumps(ret, sort_keys=True, indent=4))

    def test_calculation_and_cut(self):
        cutter = SegmentCutter('/tmp/')
        dt = datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S")
        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(dt)
        ret  = scheduler.calculate(self.segments)
        for k, value in ret.items():
#            print (f"Key: {k}")
            for cut in ret[k]:
                pass
                #print ("Got command: " + cutter.run(cut))
#        for s in self.segments:
#            print ("Got segment: " + s.getStartTime().strftime("%Y-%m-%d %H:%M:%S"))

    def test_calculation_and_cut_and_join(self):
        cutter = SegmentCutter('/tmp/')
        joiner = SegmentJoiner('/tmp/out/', '/tmp/')
        dt = datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S")
        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(dt)
        runList = []
        ret  = scheduler.calculate(self.segments)
        for k, value in ret.items():
#            new_cuts = value
            for cutSegment in value:
                cutter.run(cutSegment, dryRun=True)
#        joiner.ffmpegJoin(new_cuts)


    def test_calculation_segment_is_in_the_middle_of_event(self):
        cutter = SegmentCutter('/tmp/')
        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S"))
        segments = []
        segments.append(createVideoSegment('/tmp/middle_alegria',  '2018:10:31 18:35:00', 1353.352))
        segments.append(createVideoSegment('/tmp/middle_footwork', '2018:10:31 20:35:00', 1353.352))
        segments.append(createVideoSegment('/tmp/middle_ritmo',    '2018:10:31 21:15:00', 1353.352))

        ret  = scheduler.calculate(segments)

        for k, value in ret.items():
#            print (f"Key: {k}")
            for cut in ret[k]:
                pass
#                print ("Got command: " + cutter.run(cut))

        self.assertTrue(len(ret['Alegria']) == 1)
        self.assertTrue(ret['Alegria'][0].segment.filePath == '/tmp/middle_alegria')
        self.assertTrue(len(ret['Footwork']) == 1)
        self.assertTrue(ret['Footwork'][0].segment.filePath == '/tmp/middle_footwork')
        self.assertTrue(len(ret['Ritmo']) == 1)
        self.assertTrue(ret['Ritmo'][0].segment.filePath == '/tmp/middle_ritmo')

    def test_calculation_segment_is_in_the_middle_of_two_events(self):
        cutter = SegmentCutter('/tmp/')
        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S"))
        segments = []
        segments.append(createVideoSegment('/tmp/end_alegria_begin_footwork',  '2018:10:31 19:55:00', 1353.352))
        ret  = scheduler.calculate(segments)

        self.assertTrue(len(ret['Alegria']) == 1)
        self.assertTrue(ret['Alegria'][0].segment.filePath == '/tmp/end_alegria_begin_footwork')
#        print("here: " + str(ret['Alegria'][0].segment.getDuration()))
        self.assertTrue(ret['Alegria'][0].cutDuration == timedelta(seconds=600))

        self.assertTrue(len(ret['Footwork']) == 1)
        self.assertTrue(ret['Footwork'][0].segment.filePath == '/tmp/end_alegria_begin_footwork')
        self.assertTrue(ret['Footwork'][0].cutDuration == timedelta(seconds=300))
        self.assertTrue(len(ret['Ritmo']) == 0)


    def test_calculation_segment_is_before_all_events(self):
        cutter = SegmentCutter('/tmp/')
        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S"))
        segments = []
        segments.append(createVideoSegment('/tmp/end_alegria_begin_footwork',  '2018:10:31 14:55:00', 1353.352))
        ret  = scheduler.calculate(segments)

        self.assertTrue(len(ret['Alegria']) == 0)
        self.assertTrue(len(ret['Footwork']) == 0)
        self.assertTrue(len(ret['Ritmo']) == 0)

    def test_calculation_segment_is_after_all_events(self):
        cutter = SegmentCutter('/tmp/')
        scheduler = SegmentScheduler('/tmp/', self.events);
        scheduler.set_date(datetime.strptime("2018:10:31_07:03:27", "%Y:%m:%d_%H:%M:%S"))
        segments = []
        segments.append(createVideoSegment('/tmp/end_alegria_begin_footwork',  '2018:10:31 22:48:00', 1353.352))
        ret  = scheduler.calculate(segments)

        self.assertTrue(len(ret['Alegria']) == 0)
        self.assertTrue(len(ret['Footwork']) == 0)
        self.assertTrue(len(ret['Ritmo']) == 0)

    def test_sleep(self):
        #print ("zzzzzzZZZ")
        #time.sleep(300)
        pass


    def setupSegments(self):
        if len(self.segments) != 0 :
            return

        segs = ({"SourceFile":"/home/user/videoSrc/18.10.31_185801.mp4",
        "QuickTime:TrackCreateDate":"2018:10:31 22:58:01",
        "QuickTime:TrackDuration":1353.352},

        {"SourceFile":"/home/user/videoSrc/18.10.31_192035.mp4",
        "QuickTime:TrackCreateDate":"2018:10:31 23:20:35",
        "QuickTime:TrackDuration":1353.36},

        {"SourceFile":"/home/user/videoSrc/18.10.31_194308.mp4",
        "QuickTime:TrackCreateDate":"2018:10:31 23:43:08",
        "QuickTime:TrackDuration":1229.244},

        {"SourceFile":"/home/user/videoSrc/18.10.31_200343.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 00:03:43",
        "QuickTime:TrackDuration":101.6015},

        {"SourceFile":"/home/user/videoSrc/18.10.31_202245.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 00:22:45",
        "QuickTime:TrackDuration":1353.352},

        {"SourceFile":"/home/user/videoSrc/18.10.31_204519.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 00:45:19",
        "QuickTime:TrackDuration":1353.36},

        {"SourceFile":"/home/user/videoSrc/18.10.31_210752.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 01:07:52",
        "QuickTime:TrackDuration":29.5455},

        {"SourceFile":"/home/user/videoSrc/18.10.31_212705.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 01:27:05",
        "QuickTime:TrackDuration":1353.352},

        {"SourceFile":"/home/user/videoSrc/18.10.31_214938.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 01:49:38",
        "QuickTime:TrackDuration":1353.36},

        {"SourceFile":"/home/user/videoSrc/18.10.31_221212.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 02:12:12",
        "QuickTime:TrackDuration":269.7855},

        {"SourceFile":"/home/user/videoSrc/18.10.31_221903.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 02:19:03",
        "QuickTime:TrackDuration":1353.352},

        {"SourceFile":"/home/user/videoSrc/18.10.31_224136.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 02:41:36",
        "QuickTime:TrackDuration":61.069},

        {"SourceFile":"/home/user/videoSrc/18.10.31_224246.mp4",
        "QuickTime:TrackCreateDate":"2018:11:01 02:42:46",
        "QuickTime:TrackDuration":111.6115})

        for s in segs:
            self.segments.append(VideoSegment(s))
            idx = len(self.segments)-1
            time = self.segments[idx].getStartTime().strftime("%Y-%m-%d %H:%M:%S")
            #print ("idx: " + time)
