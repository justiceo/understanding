
import argparse
import os
import time
from nltk.tree import Tree
from corenlp_parser import CoreNLPParser
import re
import gensim.downloader as api
from gensim.summarization.summarizer import summarize
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from wiki_paragraphs import paragraphs_local
from utils import *
from gensim_client import most_similar

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=False,
                    default='data/beyonce.txt',
                    help="Plain text file with text for generating questions.")
parser.add_argument("--output", required=False,
                    default='data/sample_out.text',
                    help="File to write JSON list of questions")
args = parser.parse_args()
logger = get_logger(__name__)

def sentence_str(sentence):
    if "parse" in sentence:
        # This call is expensive ~10seconds! But if we already have it, it's accurate.
        return " ".join(Tree.fromstring(sentence["parse"]).leaves())
    else:
        combined = " ".join([t["word"] for t in sentence["tokens"]])
        # TODO: fix unnecessary spaces with regex replace.
        # space_regex = re.compile(r"\( ", re.IGNORECASE)
        # combined = space_regex.sub("\(", combined)
        return combined


def get_similar_entities(target):
    # TODO: Update to differentiate numericals.
    return most_similar(target["text"].split())


def resolve_corefs(text):
    # resolve co-references (the time grows at least exponentially with text length)
    corefParser = CoreNLPParser(sentences=text, annotators="dcoref")
    corefParser.coref()
    
    # TODO: Update text.
    return text


def trim_text(text):
    # remove text that doesn't add much to essence, in this case 10% of input text.
    return summarize(text, ratio=0.9)


def run():
    logger.info("starting the whole shebang.")

    # get input text.
    paragraphs = paragraphs_local(args.input)
    text = paragraphs[0]
    logger.info("acquired input")

    # resolve co-refs: she -> Beyonce
    text = resolve_corefs(text)
    logger.info("resolved co-refs")

    text = trim_text(text)
    logger.info("trimmed text")

    # parse text using CoreNLP Server.
    parser = CoreNLPParser(sentences=text)
    logger.info("parsed text")

    # get flat list of entities without Os.
    entities = parser.ent_flat()
    logger.debug("entities: %s", parser.ent_tags())

    # generate questions by replacing entities in sentences.
    questions = []
    for sent in parser.sents():
        for entity in sent["entitymentions"]:
            question = {}
            question["prompt"] = sentence_str(
                sent).replace(entity["text"], "_____")
            question["answer"] = entity["text"]
            question["options"] = get_similar_entities(entity)
            questions.append(question)
            if len(question["options"]) >= 4:
                continue
            print(question["prompt"])
            print(question["answer"])
            print(question["options"])

    print("\n\n\n\nMore than 4 options:\n")
    for q in [q for q in questions if len(q["options"]) >= 4]:
        print(q["prompt"])
        print(q["answer"])
        print(q["options"])

    # TODO: score the prompt, answer and options.

    logger.info("done")


if __name__ == "__main__":
    logger.info("$ run()")
