#from pytz import timezone
import tempfile
import pytz
from datetime import datetime
from datetime import timedelta
import os
import collections


ScheduledEvent = collections.namedtuple('ScheduledEvent', ['name', 'hour', 'minute', 'second', 'PM', 'duration'])

class EventInfo:
    startDateTime = None
    endDateTime = None
    durationDelta = None
    name = None

    def getName(self):
        return self.name

    def getStartTime(self):
        return self.startDateTime

    def getStartTimeStr(self):
        return self.startDateTime.strftime('%Y-%m-%d %H:%M:%S %Z');

    def getEndTime(self):
        return self.endDateTime

    def getEndTimeStr(self):
        return self.endDateTime.strftime('%Y-%m-%d %H:%M:%S %Z');

    def getDuration(self):
        return self.durationDelta

    def parseTimeDelta(self, event):
        tokenize = event.duration.split(':')
        return timedelta(hours=int(tokenize[0]), minutes=int(tokenize[1]), seconds=0)

    def __init__(self, event, date):
        self.name = event.name
        hour = event.hour + 12 if event.PM else event.hour
        minute = event.minute
        second = event.second
        time = datetime.strptime(f"{date.year}.{date.month}.{date.day}_{hour}.{minute}.{second}", "%Y.%m.%d_%H.%M.%S")
        #self.startDateTime = time.replace(tzinfo=timezone('US/Eastern'))
        self.startDateTime = pytz.timezone('US/Eastern').localize(time)
        #print ("Created event with: " + self.getStartTimeStr());
        self.durationDelta = self.parseTimeDelta(event)
        self.endDateTime  = self.startDateTime + self.durationDelta


SegmentCut = collections.namedtuple('SegmentCut', ['segment', 'cutStart', 'cutDuration', 'cutFilePath'])
class SegmentScheduler:
    m_dateAtMidnight = None
    m_dirTmp = None
    m_events = None

    def set_date(self, in_date):
        self.m_dateAtMidnight = datetime.strptime(f"{in_date.year}.{in_date.month}.{in_date.day}_0.0.0", "%Y.%m.%d_%H.%M.%S")
        pass

    def get_event_date(self, event):
        return EventInfo(event, self.m_dateAtMidnight)

    def generateTmpFile(self, tag):
        #FIXME close FD?
        generatedTmpFile = tempfile.mkstemp(prefix=tag+'_',
                suffix=".mp4", dir=self.m_dirTmp)
        os.close(generatedTmpFile[0])
        return generatedTmpFile[1]

    def calculate(self, segments):
        result = {}
        for event in self.m_events:
            ed = self.get_event_date(event)
            result[ed.getName()] = []

            for s in segments:
                segCut = None
                if not is_segment_in_event(s, ed):
                    continue

                # Segment begins after the event window, ends before the event window complets, use full segment
                if segment_begin_after_event_start(s, ed) and segment_ended_prior_event_end(s, ed):
                    offset = timedelta(seconds=0)
                    duration = s.getDuration()
                    tmpFile = s.filePath
                    segCut = SegmentCut(segment=s, cutStart=offset, cutDuration=duration, cutFilePath=tmpFile)
                    result[ed.getName()].append(segCut)
                    #print('0 Duration for ' + s.filePath + ': ' + str(s.getDuration()))

                # Segment begins after event window begins, ends after event window completes, must be cut at the tail
                elif segment_begin_after_event_start(s, ed) and segment_ended_after_event_end(s, ed):
                    offset = timedelta(seconds=0)
                    duration= ed.getEndTime() - s.getStartTime()
                    duration_foo = s.getEndTime() - ed.getEndTime()
                    tmpFile = self.generateTmpFile(ed.getName())
                    segCut = SegmentCut(segment=s, cutStart=offset, cutDuration=duration, cutFilePath=tmpFile)
                    result[ed.getName()].append(segCut)
                    #print('1 Duration for ' + s.filePath + ': ' + str(duration))
                    #print('1 Duration foooo ' + s.filePath + ': ' + str(duration_foo))
                    #print('1 segment starts at :' + str(s.getStartTime()) + ' event ends at: ' +  str(ed.getEndTime()))

                # Segment begins before the event window, ends before the event window completes, must be cut at the head
                elif segment_begin_prior_event_start(s, ed) and segment_ended_prior_event_end(s, ed):
                    # No indication its in the window Could be problematic
                    offset  = ed.getStartTime() - s.getStartTime()
                    duration =  ed.getStartTime() - s.getStartTime()
                    tmpFile = self.generateTmpFile(ed.getName())
                    segCut = SegmentCut(segment=s, cutStart=offset, cutDuration=duration, cutFilePath=tmpFile)
                    result[ed.getName()].append(segCut)
                    #print('2 Duration for ' + s.filePath + ': ' + str(duration))

                # Segment begins before the event window, ends after the event window completes, should never happen.
                elif segment_begin_prior_event_start(s, ed) and segment_ended_after_event_end(s, ed):
                    # Use the full event, should never happned
                    offset  = ed.getStartTime() - s.getStartTime()
                    duration = ed.getDuration()
                    tmpFile = self.generateTmpFile(ed.getName())
                    segCut = SegmentCut(segment=s, cutStart=offset, cutDuration=duration, cutFilePath=tmpFile)
                    result[ed.getName()].append(segCut)

        return result

    def __init__(self, dirTmp, events):
        self.m_dirTmp = dirTmp
        self.m_events = events
        pass

def is_segment_in_event(segment, eventDate):
    # Segment started and ended before event start
    if segment_ended_prior_event_start(segment, eventDate):
        return False

    # Segment started after the event ended
    if segment_begin_after_event_end(segment, eventDate):
        return False

    return True


def segment_begin_prior_event_start(seg, eventDate):
    ret = seg.getStartTime() < eventDate.getStartTime()
#    if ret:
#        print('Seg begin prior event start' + seg.filePath + ': ' + seg.getStartTimeStr() + ' vs ' + eventDate.getStartTimeStr())
    return ret

def segment_begin_prior_event_end(seg, eventDate):
    return seg.getStartTime() < eventDate.getEndTime()

def segment_begin_after_event_start(seg, eventDate):
    return seg.getStartTime() > eventDate.getStartTime()

def segment_begin_after_event_end(seg, eventDate):
    return seg.getStartTime() > eventDate.getEndTime()

def segment_ended_prior_event_start(seg, eventDate):
    return seg.getEndTime() < eventDate.getStartTime()

def segment_ended_prior_event_end(seg, eventDate):
    return seg.getEndTime() < eventDate.getEndTime()

def segment_ended_after_event_start(seg, eventDate):
    return seg.getEndTime() > eventDate.getStartTime()

def segment_ended_after_event_end(seg, eventDate):
    return seg.getEndTime() > eventDate.getEndTime()

