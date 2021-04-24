import argparse
import os
import time
from nltk.tree import Tree
from models.corenlp import CoreNLP
from models.gensim import Gensim
import re
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from wiki_paragraphs import paragraphs_local
from utils import *
from utils import fix_punctuation
from multiprocessing.managers import BaseManager
import argparse
import os.path
from shutil import which
import json
import validators
import queue
from utils import get_logger

ORCHESTRATOR_HOST = "localhost"
ORCHESTRATOR_PORT = 9900
INPUT_QUEUE_NAME = "request"
OUTPUT_QUEUE_NAME = "response"

class QueueManager(BaseManager): pass

class Orchestrator:
    """
    Orchestrates the interactions between models to generate questions from text.
    """

    def init(self):
        self.logger = get_logger()
        self.coreNLP = CoreNLP()
        self.coreNLP.init()
        self.gensim = Gensim()
        self.gensim.init()

        QueueManager.register(INPUT_QUEUE_NAME, callable=lambda: queue.Queue())
        QueueManager.register(OUTPUT_QUEUE_NAME, callable=lambda: queue.Queue())
        self.manager = QueueManager(
            address=(ORCHESTRATOR_HOST, ORCHESTRATOR_PORT), authkey=b"random auth"
        )

        self.manager.start()
        self.request_queue = self.manager.request()
        self.response_queue = self.manager.response()

        self.logger.info(
            "Orchestrator is initialized.\n\n"
            + "\t\tListening on port %d\n"
            + "\t\tAccepting requests on the queue '%s'\n"
            + "\t\tPublishing responses on the queue '%s'\n",
            ORCHESTRATOR_PORT,
            INPUT_QUEUE_NAME,
            OUTPUT_QUEUE_NAME,
        )

    def test(self):
        self.request_queue.put(["Adam is a human. John is a boy."])

    def process_requests(self):
        """
        Continouosly process requests in the request queue and publish responses to the response queue.

        A request is a list of strings (typically paragraphs).
        A response is a list of json objects that represent a question.
        """

        self.logger.info("Processing requests...")
        while True:
            # This thread will block here until there's something in the queue.
            req = self.request_queue.get()
            self.logger.info("Acquired input: %s", req)

            # Short-circuit invalid input
            if req is None or len(req) == 0:
                logger.error("Invalid input, no questions generated")
                self.response_queue.put([])
                continue

            response = self.generate_questions(req)
            self.response_queue.put(response)

    def generate_questions(self, paragraphs):
        text = "\n".join(paragraphs)

        # resolve co-refs: she -> Beyonce
        self.logger.info("Resolving co-refs")
        # text = self.coreNLP.coref(sentences=text)

        # generate questions by replacing entities in sentences.
        questions = []
        for sent in self.coreNLP.sents(text):
            for entity in sent["entitymentions"]:
                question = {}
                question["prompt"] = self.sentence_str(sent).replace(
                    entity["text"], "_____"
                )
                question["answer"] = entity["text"]
                question["options"] = self.gensim.most_similar(entity["text"].split())                
                if len(question["options"]) >= 4:
                    questions.append(question)

        self.logger.info("done")      
        return questions

    def sentence_str(self, sentence):
        return fix_punctuation(" ".join([t["word"] for t in sentence["tokens"]]))


if __name__ == "__main__":
    o = Orchestrator()
    o.init()
    o.test()
    o.process_requests()
