# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""

import time
import threading
from queue import Empty, Full
from typing import Any, Deque

# Importing collections module for deque
from collections import deque


class cached_property:
    """Decorator for read-only properties evaluated only once within TTL period.
    It can be used to create a cached property like this::

        import random

        # the class containing the property must be a new-style class
        class MyClass:
            # create property whose value is cached for ten minutes
            @cached_property(ttl=600)
            def randint(self):
                # will only be evaluated every 10 min. at maximum.
                return random.randint(0, 100)

    The value is cached  in the '_cached_properties' attribute of the object instance that
    has the property getter method wrapped by this decorator. The '_cached_properties'
    attribute value is a dictionary which has a key for every property of the
    object which is wrapped by this decorator. Each entry in the cache is
    created only when the property is accessed for the first time and is a
    two-element tuple with the last computed property value and the last time
    it was updated in seconds since the epoch.

    The default time-to-live (TTL) is 0 seconds i.e. cached value will never expire.

    To expire a cached property value manually just do::
        del instance._cached_properties[<property name>]

    Adopted from https://wiki.python.org/moin/PythonDecoratorLibrary#Cached_Properties
    © 2011 Christopher Arndt, MIT License.

    NOTE: We need this function only because Python in-built are only available
    for 3.8+.  Hence, we must get rid of this function once proxy.py no longer
    support version older than 3.8.

    .. spelling::

       backports
       getter
       Arndt
       del
    """

    def __init__(self, ttl: float = 0):
        """cached_property initialization"""
        self.ttl = ttl

    def __call__(self, fget: Any, doc: Any = None) -> 'cached_property':
        """Called when using the decorator"""
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst: Any, owner: Any) -> Any:
        """Getter method for cached property"""
        now = time.time()
        try:
            value, last_update = inst._cached_properties[self.__name__]
            if self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError("Cache expired")
        except (KeyError, AttributeError):
            value = self.fget(inst)
            try:
                cache = inst._cached_properties
            except AttributeError:
                cache, inst._cached_properties = {}, {}
            finally:
                cache[self.__name__] = (value, now)
        return value


class NonBlockingQueue:
    """Simple, unbounded, non-blocking FIFO queue.

    Supports only a single consumer.

    NOTE: This is available in Python since 3.7 as SimpleQueue.
    Here because proxy.py still supports 3.6
    """

    def __init__(self, maxsize: int = 0) -> None:
        """NonBlockingQueue initialization"""
        self._queue: Deque[Any] = deque()
        self._maxsize = maxsize
        self._count: threading.Semaphore = threading.Semaphore(0)

    def put(self, item: Any, block: bool = True, timeout: float = None) -> None:
        """Put the item on the queue."""
        if self._maxsize and len(self._queue) >= self._maxsize:
            if not block:
                raise Full
            elif timeout is None:
                while len(self._queue) >= self._maxsize:
                    time.sleep(0.1)  # Polling
            else:
                end_time = time.time() + timeout
                while len(self._queue) >= self._maxsize:
                    remaining_time = end_time - time.time()
                    if remaining_time <= 0:
                        raise Full
                    time.sleep(min(0.1, remaining_time))
        self._queue.append(item)
        self._count.release()

    def get(self, block: bool = True, timeout: float = None) -> Any:
        """Remove and return an item from the queue."""
        if not self._count.acquire(blocking=block, timeout=timeout):
            raise Empty
        with self._count._cond:
            return self._queue.popleft()

    def empty(self) -> bool:
        """Return True if the queue is empty, False otherwise (not reliable!)."""
        return not self._queue

    def full(self) -> bool:
        """Return True if the queue is full, False otherwise (not reliable!)."""
        if self._maxsize:
            return len(self._queue) >= self._maxsize
        else:
            return False

    def qsize(self) -> int:
        """Return the approximate size of the queue (not reliable!)."""
        return len(self._queue)

    def clear(self) -> None:
        """Clear all items from the queue."""
        self._queue.clear()
        # Clearing semaphore counter to make sure it's consistent
        while self._count.acquire(False):
            pass


# Example usage:

if __name__ == "__main__":
    # Creating a NonBlockingQueue instance with a maximum size of 5
    queue = NonBlockingQueue(maxsize=5)

    # Putting items into the queue
    for i in range(7):
        try:
            queue.put(i)
            print(f"Put {i} into the queue")
        except Full:
            print("Queue is full, cannot put more items")

    # Getting items from the queue
    for _ in range(7):
        try:
            item = queue.get()
            print(f"Got {item} from the queue")
        except Empty:
            print("Queue is empty, cannot get more items")
