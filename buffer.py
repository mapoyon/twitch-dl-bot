from threading import RLock


class RingBuffer:
    def __init__(self, maxlen):
        self.lock = RLock()
        self.end = maxlen - 1
        self.buf = [None] * maxlen
        self.pos = -1
        self.full = False

    def append(self, value):
        with self.lock:
            if self.pos >= self.end:
                self.pos = -1
                self.full = True
            self.pos += 1
            self.buf[self.pos] = value

    def __len__(self):
        with self.lock:
            if self.full:
                return len(self.buf)
            return self.pos + 1

    def __getitem__(self, key):
        if type(key) is not int:
            raise TypeError
        if key > self.end:
            raise IndexError
        with self.lock:
            if self.full:
                if self.pos + key >= self.end:
                    return self.buf[self.pos + key - self.end]
                else:
                    return self.buf[self.pos + key + 1]
            else:
                if key > self.pos:
                    raise IndexError
                return self.buf[key]

    def __setitem__(self, key, value):
        if type(key) is not int:
            raise TypeError
        if key > self.end:
            raise IndexError
        with self.lock:
            if self.full:
                if self.pos + key >= self.end:
                    self.buf[self.pos + key - self.end] = value
                else:
                    self.buf[self.pos + key + 1] = value
            else:
                if key > self.pos:
                    raise IndexError
                self.buf[key] = value

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        self.lock.acquire()
        self.cur = 0
        return self

    def __next__(self):
        try:
            val = self.__getitem__(self.cur)
            self.cur += 1
            return val
        except IndexError:
            self.lock.release()
            raise StopIteration
        except Exception as e:
            self.lock.release()
            raise e
