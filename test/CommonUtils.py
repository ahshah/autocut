import sys, os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(SRC_PATH, '../src/')
sys.path.append(SRC_PATH)
from VideoSegment import VideoSegment
from datetime import datetime
import pytz 

class ErrorAfter(object):
    '''
    Callable that will raise `CallableExhausted`
    exception after `limit` calls

    '''
    def __init__(self, limit):
        self.limit = limit
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls > self.limit:
            raise CallableExhausted

class CallableExhausted(Exception):
    pass

def createVideoSegment(filePath, date, duration):
    md = {}
    dt = datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
    first_dt_str = dt.strftime('%Y:%m:%d %H:%M:%S')
    dt = pytz.timezone('US/Eastern').localize(dt).astimezone(tz=pytz.timezone('GMT'))
    dt_str = dt.strftime('%Y:%m:%d %H:%M:%S')

    md['SourceFile'] = filePath
    md['QuickTime:TrackCreateDate'] = dt.strftime('%Y:%m:%d %H:%M:%S')
    md['QuickTime:TrackDuration'] = duration
    return VideoSegment(md)

