
import unittest
from time import sleep
from random import random
from threading import Thread
from buffer import RingBuffer


class TestRingBuffer(unittest.TestCase):
    def test_len(self):
        buf = RingBuffer(3)
        buf.append("test1")
        self.assertEqual(len(buf), 1)
        buf.append("test2")
        self.assertEqual(len(buf), 2)
        buf.append("test3")
        self.assertEqual(len(buf), 3)
        buf.append("test4")
        self.assertEqual(len(buf), 3)

    def test_get_item_key_is_not_int(self):
        try:
            buf = RingBuffer(1)
            buf["0"]
        except BaseException as e:
            self.assertIsInstance(e, TypeError)

    def test_get_item_not_full(self):
        buf = RingBuffer(3)
        buf.append("test1")
        buf.append("test2")
        buf.append("test3")
        self.assertEqual(buf[0], "test1")
        self.assertEqual(buf[1], "test2")
        self.assertEqual(buf[2], "test3")

    def test_get_item_full(self):
        buf = RingBuffer(3)
        buf.append("test1")
        buf.append("test2")
        buf.append("test3")
        buf.append("test4")
        buf.append("test5")
        self.assertEqual(buf[0], "test3")
        self.assertEqual(buf[1], "test4")
        self.assertEqual(buf[2], "test5")

    def test_get_item_out_of_index(self):
        try:
            buf = RingBuffer(1)
            buf[1]
        except BaseException as e:
            self.assertIsInstance(e, IndexError)

    def test_iter(self):
        buf = RingBuffer(3)
        buf.append("test1")
        buf.append("test2")
        buf.append("test3")
        buf.append("test4")
        buf.append("test5")
        actual1 = []
        for i in buf:
            actual1.append(i)
        self.assertListEqual(actual1, ["test3", "test4", "test5"])

        actual2 = []
        for i in buf:
            actual2.append(i)
        self.assertListEqual(actual2, ["test3", "test4", "test5"])

    class TestIterThreading(Thread):
        def __init__(self, buf):
            super().__init__()
            self.buf = buf
            self.actual = []

        def run(self):
            for i in self.buf:
                sleep(random() / 4.0)
                self.actual.append(i)

    def test_threading(self):
        buf = RingBuffer(3)
        buf.append("test1")
        buf.append("test2")
        buf.append("test3")

        thread1 = self.__class__.TestIterThreading(buf)
        thread2 = self.__class__.TestIterThreading(buf)
        thread1.start()
        thread2.start()
        thread1.join(3)
        thread2.join(3)
        self.assertListEqual(thread1.actual, ["test1", "test2", "test3"])
        self.assertListEqual(thread2.actual, ["test1", "test2", "test3"])
