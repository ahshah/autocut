from pytz import timezone
from datetime import datetime
from datetime import timedelta
import json

class VideoSegment:
    filePath = ''
    metaData = None
    timeStart = None
    timeEnd  = None
    duration = None
    dayOfTheWeek = None
    WEDNESDAY = 2

    @staticmethod
    def check_metadata_sanity(metaData):
        # Necessary tags: 
        #  QuickTime:TrackDuration
        #  QuickTime:TrackCreateDate
        tags = ['QuickTime:TrackCreateDate', 'QuickTime:TrackDuration']
        for t in tags:
            if t not in metaData:
                print (f'Skipping file missing EXIF tag {t}: {metaData["SourceFile"]}')
                return False
        return True

    def getEDT(self):
        dt = datetime.strptime(self.metaData['QuickTime:TrackCreateDate'], '%Y:%m:%d %H:%M:%S')
        dt_utc = dt.replace(tzinfo=timezone('UTC'))
        return dt_utc.astimezone(timezone('US/Eastern'))

    def getDurationTimeDelta(self):
        duration = self.metaData['QuickTime:TrackDuration']
        secs = int(duration)
        msecs = str(duration-int(duration))[2:6]
        return timedelta(seconds=secs, milliseconds=int(msecs))

    def isWednesday(self):
        if self.dayOfTheWeek == self.WEDNESDAY:
            return True
        return False

    def getDateStr(self):
        return self.timeStart.strftime('%Y-%m-%d')

    def getStartTime(self):
        return self.timeStart;

    def getStartTimeStr(self):
        return self.timeStart.strftime('%Y-%m-%d %H:%M:%S %Z');

    def getStartTimeStrForFileName(self):
        return self.timeStart.strftime('%Y%m%d_%H%M%S');

    def getEndTime(self):
        return self.timeEnd;

    def getDuration(self):
        return self.duration;

    def __str__(self):
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"
        ret  = f'File:     {self.filePath} '
        ret += f'Start:    {self.timeStart.strftime(fmt)} '
        ret += f'End:      {self.timeEnd.strftime(fmt)} '
        ret += f'Duration: {repr(self.duration)} '
        return ret

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"
        ret = {}
        ret[self.filePath] = {
                'Start' : self.timeStart.strftime(fmt),
                'End': self.timeEnd.strftime(fmt),
                'Duration': str(self.duration)
                }
        return ret

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def __init__(self, metaData):
        self.metaData = metaData
        self.filePath = metaData['SourceFile']
        self.timeStart = self.getEDT()
        self.duration  = self.getDurationTimeDelta()
        self.timeEnd = self.timeStart + self.duration
        self.dayOfTheWeek = self.timeStart.weekday()
