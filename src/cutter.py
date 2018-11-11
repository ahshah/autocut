from Scheduling import ScheduledEvent, SegmentCut
import tempfile
import os
import subprocess


class SegmentCutter:
    m_dirTmp = None

    def ffmpegCut(self, segmentCut):
        # ffmpeg -ss $START_TIME -i $INPUT_FILE -c copy -t $END_TIME $OUTPUT_FILE
        fileIn = segmentCut.segment.filePath
        fileOut = segmentCut.cutFilePath
        cutStart = str(segmentCut.cutStart)
        cutDuration = str(segmentCut.cutDuration)

        timeStart = segmentCut.segment.timeStart.strftime("%Y-%m-%d %H:%M:%S")
        cmd = f"ffmpeg -ss {cutStart} -i {fileIn} -c copy -t {cutDuration} {fileOut}"
        cmdList = ['ffmpeg', '-ss', f'{cutStart}', '-i', f'{fileIn}', '-c', 'copy', '-t', f'{cutDuration}', f'{fileOut}']
        return cmd, cmdList

    def run(self, segmentCut, dryRun):
        cmd, cmdList = self.ffmpegCut(segmentCut)
        print ("Running:" + cmd)
        if segmentCut.cutDuration == segmentCut.segment.getDuration():
            print ("Going to skip full segment")
            return
        stdin_stream  = subprocess.PIPE #if input else None
        stdout_stream = subprocess.PIPE # if capture_stdout or quiet else None
        stderr_stream = subprocess.PIPE # if capture_stderr or quiet else None

        stdout_stream = subprocess.PIPE
        stderr_stream = subprocess.PIPE

        if dryRun:
            return
        p = subprocess.Popen(cmdList, stdin=stdin_stream, stdout=stdout_stream, stderr=stderr_stream)
        out, err = p.communicate(input=b'y\r')
        retcode = p.poll()

    def __init__(self, tmpDir):
        self.m_dirTmp = tmpDir

class SegmentJoiner:
    m_dirOut = None
    m_dirTmp = None

    def populateCutTempFile(self, cuts):
        fd, tmp_path = tempfile.mkstemp(suffix=".lst", dir=self.m_dirTmp)

        contents = ""
        for cut in cuts:
            contents += (f"file '{cut.cutFilePath}'\n")

        with os.fdopen(fd, 'w') as f:
            f.write(contents)
        print (f"Wrote contents out to {tmp_path}")
        return tmp_path
        # TODO..
        # os.close(fd)

    def generateOutputFilePath(self, team, first_cut_filepath, time_str):
        fileName = os.path.basename(first_cut_filepath)
        fileExt  = os.path.splitext(fileName)[1]
        # If its not a number use the time_str
        fileNamePortion =  time_str+'_'+team+'_full'+fileExt
        return os.path.join(self.m_dirOut, fileNamePortion)


    def ffmpegJoin(self, team, cuts, dryRun):
        cuts.sort(key=lambda x: x.segment.getStartTime())
        outputFile = self.generateOutputFilePath(team, cuts[0].segment.filePath, cuts[0].segment.getStartTimeStrForFileName())
        listFile = self.populateCutTempFile(cuts)
        cmdList = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', f'{listFile}', '-c', 'copy', f'{outputFile}']
        print (" ".join(cmdList))

        if not dryRun:
            stdin_stream = subprocess.PIPE #if input else None
            stdout_stream = subprocess.PIPE # if capture_stdout or quiet else None
            stderr_stream = subprocess.PIPE # if capture_stderr or quiet else None
            stdout_stream = None
            stderr_stream = None
            p = subprocess.Popen(cmdList, stdin=stdin_stream, stdout=stdout_stream, stderr=stderr_stream)
            out, err = p.communicate(input=b'y\r')
            retcode = p.poll()
            os.unlink(outputFile)
        print("Would unlink list file: " + outputFile)



    def __init__(self, dirOut, dirTmp):
        self.m_dirOut = dirOut
        self.m_dirTmp = dirTmp

