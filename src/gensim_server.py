# Usage: python3 gensim_server.py
from multiprocessing.managers import BaseManager
import queue
import gensim.downloader as api
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from utils import *


# For more on gensim models see https://github.com/RaRe-Technologies/gensim-data
def most_similar(count=10, model_name="glove-wiki-gigaword-50", port=9100):
    logger = get_logger()
    logger.info("initializing process to serve model %s", model_name)
    model = api.load(model_name)
    logger.info("loaded model %s", model_name)

    terms_queue = queue.Queue()
    similarities_queue = queue.Queue()
    BaseManager.register("terms_queue", callable=lambda: terms_queue)
    BaseManager.register("similarities_queue",
                         callable=lambda: similarities_queue)
    m = BaseManager(address=("", port), authkey=b"random auth")
    m.start()

    shared_terms_queue = m.terms_queue()
    shared_similarities_queue = m.similarities_queue()

    logger.info("process is ready")
    while True:
        # This operation is blocking.
        terms = shared_terms_queue.get()

        # Short-circuit invalid input
        if terms is None or len(terms) == 0:
            logger.error("terms is null or empty")
            shared_similarities_queue.put([])
            continue

        try:
            closestWords = model.most_similar(positive=terms, topn=count*10)
        except KeyError as e:
            logger.error(e)
            shared_similarities_queue.put([])
            continue

        closestWords = list(map(lambda x: x[0], closestWords))

        # Returns true if Longest Common Substring between x, y is longer than half the length of either.
        # TODO: Update to use a fuzzymatcher - https://pypi.org/project/fuzzywuzzy/
        # (Beyonce, BeyBey) => true
        # (Beyonce, yonce) => true
        # (Beyonce, Jay-Z) => false
        def is_reasonable_lcs(x, y): return SequenceMatcher(
            None, x, y).find_longest_match(0, len(x), 0, len(y))[2] <= min(len(x), len(y))/2 and fuzz.ratio(x, y) < 80

        def is_unique(arr, e):
            e_lower = e.lower()
            for x in arr:
                if not is_reasonable_lcs(x.lower(), e_lower):
                    return False
            return True
        # equivalent_lambda = lambda arr, e: len([x for x in arr if not is_reasonable_lcs(x.lower(),e.lower())]) > 0

        # Perform Longest Common Substring search over options with limit.
        unique_options = terms.copy()
        for x in closestWords:
            if len(unique_options) >= count + len(terms):
                break
            if is_unique(unique_options, x):
                unique_options.append(x)

        logger.debug("unique after LSC: %s, terms: %s ", unique_options, terms)

        # Remove terms from options
        for t in terms:
            unique_options.remove(t)

        shared_similarities_queue.put(unique_options)


if __name__ == "__main__":
    most_similar()
