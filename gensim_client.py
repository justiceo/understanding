from multiprocessing.managers import BaseManager


def get_queues():
    BaseManager.register('terms_queue')
    BaseManager.register('similarities_queue')
    m = BaseManager(address=('localhost', 9100), authkey=b'random auth')
    m.connect()

    shared_terms_queue = m.terms_queue()
    shared_similarities_queue = m.similarities_queue()
    return (shared_terms_queue, shared_similarities_queue)


def most_similar(terms):
    (shared_terms_queue, shared_similarities_queue) = get_queues()
    shared_terms_queue.put(terms)
    return shared_similarities_queue.get()


if __name__ == "__main__":
    print(most_similar(["barack", "obama"]))
