from bottle import route, run, template
from bottle import request, response
from bottle import post, get, put, delete

import json

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
from utils import fix_punctuation

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
    return fix_punctuation(" ".join([t["word"] for t in sentence["tokens"]]))


def get_similar_entities(target):
    # TODO: Update to differentiate numericals.
    return most_similar(target["text"].split())


def resolve_corefs(text):
    # resolve co-references (the time grows at least exponentially with text length)
    corefParser = CoreNLPParser(sentences=text, annotators="dcoref")
    return corefParser.coref()



def trim_text(text):
    # remove text that doesn't add much to essence, in this case 10% of input text.
    return summarize(text, ratio=0.9)


def runn():
    logger.info("starting the whole shebang.")

    # get input text.
    paragraphs = paragraphs_local(args.input)
    text = "\n".join(paragraphs[0:2])
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

    # print("\n\n\n\nMore than 4 options:\n")
    # for q in [q for q in questions if len(q["options"]) >= 4]:
    #     print(q["prompt"])
    #     print(q["answer"])
    #     print(q["options"])

    # return questions

    # TODO: score the prompt, answer and options.

    logger.info("done")
    
    return questions


@route('/')
def index():
    return template('index.tpl')

@get('/generatedata')
def listing_handler():
    '''Handles name listing'''

    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache'
    return json.dumps({'data': runn()})
    

run(host='localhost', port=8080, debug=True)