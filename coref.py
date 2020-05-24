# Co-reference resolution.
# Input is a text and output is a co-reference resolved text.
# See https://spacy.io/universe/project/neuralcoref
# Also stanford coref
from multiprocessing.managers import BaseManager


BaseManager.register('sent_queue')
BaseManager.register('coref_queue')
m = BaseManager(address=('localhost', 50000), authkey=b'random auth')
m.connect()

shared_sent_queue = m.sent_queue()
shared_coref_queue = m.coref_queue()

def resolve(text):
    shared_sent_queue.put(text)
    return shared_coref_queue.get()

print(resolve("John has a red car, he loves to drive it."))