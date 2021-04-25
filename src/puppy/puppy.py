from typing import Callable, Any, TypeVar, Generic, Optional, Union
import threading
import queue

T = TypeVar("T")


class Publisher(Generic[T]):
    def __init__(self, puppy, topic: str):
        self.puppy = puppy
        self.topic = topic

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


def sanitize_topic(topic: str, delim: str) -> str:
    """
    >>> sanitize_topic(['aaa','aaa/bbb','aaa/bbb/ccc'],'/')
    ['aaa', 'aaa/bbb', 'aaa/bbb/ccc']

    >>> sanitize_topic(['aaa','aaa/','/aaa/','/aaa/bbb/'],'/')
    ['aaa', 'aaa', 'aaa', 'aaa/bbb']

    >>> sanitize_topic(['aaa','aaa/bbb','aaa/bbb/ccc'],'/')
    ['aaa', 'aaa/bbb', 'aaa/bbb/ccc']

    #TODO: update above.
    """

    return topic.strip(delim)


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

        self.topic: dict[str, Topic[T]] = {"": Topic("")}
        self.published_topics = {""}

    def Publisher(self, topic: str) -> Publisher:
        topic = sanitize_topic(topic, self.delim)

        for topic_key, topic_obj in self.getTopicsInChain(topic, self.delim).items():
            self.topic[topic_key] = topic_obj
            self.published_topics.add(topic_key)

        return Publisher(self, topic)

    def Subscribe(
        self,
        topic: str,
        f: Callable[[T], Any],
        filter: Callable[[T], bool] = None,
    ):
        topic = sanitize_topic(topic, self.delim)

        for topic_key, topic_obj in self.getTopicsInChain(topic, self.delim).items():
            self.topic[topic_key] = topic_obj

        self.topic[topic].add_subscriber(f, filter)

    def inject(self, topic: str, data: T):
        topic = sanitize_topic(topic, self.delim)

        self.topic[topic].send(data)

    def getTopicsInChain(self, topic: str, delim: str = "/"):
        res: dict[str, Topic] = {"": self.topic[""]}
        topics = topic.split(delim)
        for i in range(len(topics)):
            t = delim.join(topics[: i + 1])
            if t in self.topic:
                res[t] = self.topic[t]
                continue
            if i == 0:
                res[t] = Topic(name=t, parent=res[""])
            else:
                res[t] = Topic(name=t, parent=res[delim.join(topics[:i])])
        return res

    def verify(self) -> bool:
        return list(self.published_topics) == [*self.topic]
