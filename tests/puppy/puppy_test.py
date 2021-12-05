import time
from understanding.src.puppy.puppy import *


class Latch(object):
    def __init__(self):
        self.value = None
        self.all_values = []

    def set(self, e):
        self.value = e
        self.all_values.append(e)


def test__basic():
    pupper = Puppy()
    pub = pupper.Publisher("topic1/")

    latch = Latch()
    pupper.Subscribe("/topic1", latch.set)

    assert latch.value == None
    pub.send("hello")
    time.sleep(0.1)
    assert latch.value == "hello"
    pub.send("world")
    time.sleep(0.1)
    assert latch.value == "world"
    assert latch.all_values == ["hello", "world"]
    assert pupper.verify()


def test__multiple_children():
    pupper = Puppy()

    pub1 = pupper.Publisher("topic1")
    pub2 = pupper.Publisher("topic2")

    latch1 = Latch()
    latch2 = Latch()
    latchP = Latch()
    pupper.Subscribe("topic1", latch1.set)
    pupper.Subscribe("topic2", latch2.set)
    pupper.Subscribe("", latchP.set)

    pub1.send("hello-1")
    pub1.send("world-1")
    pub2.send("hello-2")
    pub2.send("world-2")
    time.sleep(0.1)
    assert latch1.all_values == ["hello-1", "world-1"]
    assert latch2.all_values == ["hello-2", "world-2"]
    assert latchP.all_values == ["hello-1", "world-1", "hello-2", "world-2"]
    assert  pupper.published_topics == set([*pupper.topic])


def test__multiple_publishers():
    pupper = Puppy()

    latch = Latch()
    pupper.Subscribe("topic1", latch.set)

    pub1 = pupper.Publisher("topic1")
    pub2 = pupper.Publisher("topic1")
    pub1.send("hello")
    pub2.send("world")
    time.sleep(0.1)
    latch.all_values == ["hello", "world"]
    assert pupper.verify()


def test__multiple_subscribers():
    pupper = Puppy()
    pub = pupper.Publisher("topic1")

    latch1 = Latch()
    latch2 = Latch()
    pupper.Subscribe("topic1", latch1.set)
    pupper.Subscribe("topic1", latch2.set)

    pub.send("hello")
    time.sleep(0.1)

    assert latch1.all_values == ["hello"]
    assert latch2.all_values == ["hello"]
    assert pupper.verify()


def test__filter():
    pupper = Puppy()

    pub = pupper.Publisher("topic1")

    latch = Latch()
    pupper.Subscribe("topic1", latch.set, filter=lambda i: i[2] == "c")

    pub.send("ab")
    pub.send("abc")
    pub.send("abd")
    pub.send("abcd")
    time.sleep(0.1)
    assert latch.all_values == ["abc", "abcd"]
    assert pupper.verify()


def test__verify():
    pupper = Puppy()
    pupper.verify()


def test__topicsInChain():
    pupper = Puppy()

    topics = pupper.getTopicsInChain("", "/")
    assert [*topics] == [""]

    topics = pupper.getTopicsInChain("aaa", "/")
    assert [*topics] == ["", "aaa"]

    topics = pupper.getTopicsInChain("aaa/bbb", "/")
    assert [*topics] == ["", "aaa", "aaa/bbb"]

    topics = pupper.getTopicsInChain("111/@#B='", "/")
    assert [*topics] == ["", "111", "111/@#B='"]