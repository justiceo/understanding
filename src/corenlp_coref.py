# Co-reference resolution using SpanBert - https://github.com/mandarjoshi90/coref
# Input is a text and output is a co-reference resolved text.
# Alternatives:
# - Spacy coref - https://spacy.io/universe/project/neuralcoref
# - CoreNLP coref - https://stanfordnlp.github.io/CoreNLP/coref.html
# Usage:
# - Start the server in ../coref by running (virtualenv) python predict.py
# - Start client (this script) python3 corenlp_coref.py
# Notes:
# - SpanBert's coref uses a different tokenizer than CoreNLP.
# - Input: Earth's
# - SpanBert tokenizer: [Earth, ', s]
# - CoreNlp tokenizer: [Earth, 's]
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
