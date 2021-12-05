from typing import Callable, Any, TypeVar, Generic

T = TypeVar("T")

# TODO: Add reasonable logging to this.

# TODO: Each publisher should have a name.
class Publisher(Generic[T]):
    def __init__(self, puppy, topic: str):
        self.puppy = puppy
        self.topic = topic

    def send(self, data: T):
        self.puppy.inject(self.topic, data)

# TODO: Each subscriber should have a name.
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

        if self.parent:
            self.parent.send(data)

    def add_subscriber(self, f: Callable[[Any], Any], filter=None):
        self.sub.append((Subscriber(f), filter))

class Puppy(Generic[T]):
    def __init__(self, delim: str = "/"):
        self.delim = delim
        self.topic: dict[str, Topic[T]] = {"": Topic[T]("")}
        self.published_topics = {""}

    def Publisher(self, topic: str) -> Publisher:
        topic = topic.strip(self.delim)

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
        topic = topic.strip(self.delim)
        for topic_key, topic_obj in self.getTopicsInChain(topic, self.delim).items():
            self.topic[topic_key] = topic_obj
        self.topic[topic].add_subscriber(f, filter)

    def inject(self, topic: str, data: T):
        self.topic[topic].send(data)

    def getTopicsInChain(self, topic: str, delim: str = "/"):
        res: dict[str, Topic[T]] = {"": self.topic[""]}
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

    # TODO: If a topic does not have both pub and sub, remove it.
    # If a pub isn't associated with a topic, remove it.
    # If a sub isn't associated with a topic, remove it.
    # How about the root publisher that isn't subscribed to anything? There isn't.
    # Convert into a tree, allowing pubs to call subs directly.
    def optimize(self):
        return False

    # Print the graph of the execution.
    def plan(self):
        return False


    # TODO: This should verify that every topic has both a publisher and a subscriber.
    # How about parent topics?
    def verify(self) -> bool:
        return list(self.published_topics) == [*self.topic]

