from typing import Callable, Any, TypeVar, Generic, Optional, Union
import threading
import queue

T = TypeVar("T")


class Publisher(Generic[T]):
    def __init__(self, puppy, topics: list[str]):
        self.puppy = puppy
        self.topic = topics

    def send(self, data: T):
        self.puppy.inject(self.topic, data)


class Subscriber(Generic[T]):
    def __init__(self, callback: Callable):
        self.callback = callback

    def send(self, data: T):
        self.callback(data)


class Topic(Generic[T]):
    def __init__(self, name: str, parent=None):
        self.name = name
        self.sub = []
        self.parent = parent

    def send(self, data: T):
        for s, f in self.sub:
            if f != None:
                try:
                    if f(data) is False:
                        continue
                except:
                    continue
            s.send(data)
            # t = threading.Thread(target=s.send, args=(data,))
            # t.daemon = False
            # t.start()
            # t = None

        if self.parent:
            self.parent.send(data)

    def add_subscriber(self, f: Callable[[Any], Any], filter=None):
        self.sub.append((Subscriber(f), filter))


def sanitize_topics(topic: Union[str, list[str]], delim: str):
    """
    >>> sanitize_topics(['aaa','aaa/bbb','aaa/bbb/ccc'],'/')
    ['aaa', 'aaa/bbb', 'aaa/bbb/ccc']

    >>> sanitize_topics(['aaa','aaa/','/aaa/','/aaa/bbb/'],'/')
    ['aaa', 'aaa', 'aaa', 'aaa/bbb']

    >>> sanitize_topics(['aaa','aaa/bbb','aaa/bbb/ccc'],'/')
    ['aaa', 'aaa/bbb', 'aaa/bbb/ccc']
    """

    if not isinstance(topic, list):
        topic = [topic]

    return [e.strip(delim) for e in topic]


def get_parent_child(topic, delim):
    """
    >>> pc = get_parent_child('aaa/bbb/ccc','/')
    >>> pc == [('', 'aaa'),
    ...        ('aaa', 'aaa/bbb'),
    ...        ('aaa/bbb', 'aaa/bbb/ccc')]
    True

    >>> get_parent_child('aaa','/')
    [('', 'aaa')]
    """

    t = [e for e in topic.split(delim) if e != ""]

    temp = []
    for i in range(len(t)):
        temp.append((delim.join(t[:i]), delim.join(t[: i + 1])))

    return temp


class Puppy(Generic[T]):
    def __init__(self, delim: str = "/"):
        assert isinstance(delim, str)
        assert len(delim) == 1
        self.delim = delim

        self.topic: dict[str, Topic] = {"": Topic("")}
        self.published_topics = [""]

    def Publisher(self, topics1: str) -> Publisher:
        topics = sanitize_topics(topics1, self.delim)

        for t in topics:
            for a, b in get_parent_child(t, self.delim):
                if b not in self.topic.keys():
                    self.topic[b] = Topic(name=b, parent=self.topic[a])
                    self.published_topics.append(b)

        return Publisher(self, topics)

    def Subscribe(
        self,
        topics: list[str],
        f: Callable[[T], Any],
        filter: Callable[[T], bool] = None,
    ):
        topics = sanitize_topics(topics, self.delim)

        for t in topics:
            self.topic[t].add_subscriber(f, filter)

    def inject(self, topics: list[str], data: T):
        topics = sanitize_topics(topics, self.delim)

        for t in topics:
            self.topic[t].send(data)

    def verify(self) -> bool:
        return self.published_topics == [*self.topic]