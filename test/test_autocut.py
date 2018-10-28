import sys, os, mock
import pytest
from collections import namedtuple
from pyfakefs import fake_filesystem_unittest
import CommonUtils
import pytz

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(SRC_PATH, '../src/')
sys.path.append(SRC_PATH)
from autocut import checkSanityDir
from autocut import main

# Seen on drusus
# PATH=[/home/user/mount] FILENAME=[IMG-20181012-WA0007.jpg] EVENT_TYPES=['IN_MOVED_TO']

def func(x):
    return x + 1

class TestExample:
    def setUp(self):
#        self.setUpPyfakefs()
#        self.fs.add_real_directory('/usr/local/lib/python3.6/dist-packages')
        self.dirSrc = '/mnt/src'
        self.dirDst = '/mnt/dst'

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

        ParsedArgs = namedtuple('ParsedArgs', 'directorySrc, directoryDst, dryRun')
        args = ParsedArgs(directorySrc='/home/user/videoSrc/', directoryDst='/home/user/', dryRun=False)
        pa.return_value = args
        main()
