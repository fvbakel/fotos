from test.config import *

from photo_project import MeasureDuration,MeasureProgress

import unittest
import time
from datetime import datetime


class TestMeasure(unittest.TestCase):

    def test_MeasureDuration(self):
        measure  = MeasureDuration(label='test_MeasureDuration')

        
        time.sleep(0.1)
        self.assertGreater(measure.duration_seconds,0.1)
        time.sleep(0.1)
        #measure.start()
        #measure.start()
        measure.stop()
        self.assertGreater(measure.duration_seconds,0.2)
        d2 = measure.duration_seconds
        measure.stop()
        self.assertEqual(measure.duration_seconds,d2)
        measure.start()
        time.sleep(0.1)
        d3 = measure.duration_seconds
        self.assertGreater(d3,d2)
        time.sleep(0.1)
        d4 = measure.duration_seconds
        measure.stop()
        self.assertGreater(d4,d3)

        measure = MeasureDuration(label='test_MeasureDuration',autostart=False)
        time.sleep(0.1)
        self.assertEqual(measure.duration_seconds,0.0)
        measure.start()
        time.sleep(0.1)
        self.assertGreater(measure.duration_seconds,0.1)


    def test_MeasureProgress(self):
        measure = MeasureProgress(total=200)
        self.assertEqual(measure.done,0)
        self.assertEqual(measure.average_speed_nr_per_sec,0.0)
        measure.done = 20
        time.sleep(0.1)
        self.assertEqual(measure.todo,180)
        self.assertGreater(measure.average_speed_nr_per_sec,0.0)
        self.assertEqual(measure.done_percentage,10.0)
        self.assertGreater(measure.remaining_estimate_sec,0.0)


