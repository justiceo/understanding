
import argparse
import os
import time
from nltk.tree import Tree
from corenlp_parser import CoreNLPParser
import re
import gensim.downloader as api

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=False,
                    default='data/sample_input2.txt',
                    help="Plain text file with text for generating questions.")
parser.add_argument("--output", required=False,
                    default='data/sample_out.text',
                    help="File to write JSON list of questions")

args = parser.parse_args()
# For more on gensim models see https://github.com/RaRe-Technologies/gensim-data
print("loading model...")
model = api.load("fasttext-wiki-news-subwords-300")
space_regex = re.compile(r"\( ", re.IGNORECASE)


def get_input():
    with open(args.input, 'r') as file:
        data = file.read()

    # TODO: consider apply white-space fix.
    # ' '.join(data.split())
    return data


def sentence_str(sentence):
    if "parse" in sentence:
        # This call is expensive ~10seconds! But if we already have it, it's accurate.
        return " ".join(Tree.fromstring(sentence["parse"]).leaves())
    else:
        combined = " ".join([t["word"] for t in sentence["tokens"]])
        # TODO: fix unnecessary spaces with regex replace.
        # combined = space_regex.sub("\(", combined)
        return combined


def get_similar_entities(target, entities):
    options = []

    if target["ner"] in ["DATE", "ORDINAL", "CARDINAL", "NUMBER"]:
        return get_similar_entities_cosine(target)

    for ent in entities:
        if len(options) >= 4:
            return options

        et = ent["text"].title()
        tt = target["text"].title()
        en = ent["ner"]
        tn = target["ner"]
        if en == tn and et not in tt and tt not in et and et not in options:
            options.append(et)
    return options


def get_similar_entities_cosine(target, count=5):
    try:
        closestWords = model.similar_by_word(word=target["text"], topn=count)
    except:
        return []

    topN = list(map(lambda x: x[0], closestWords))[0:count]

    odd_one = model.doesnt_match(topN)
    print("\nodd one: ", odd_one)

    return topN


def run():
    start = time.time()

    # get input text.
    text = get_input()
    # text = "John lived in America. He is married."

    # parse text using CoreNLP Server.
    parser = CoreNLPParser(sentences=text)
    print("parsed text...", time.time() - start)

    # get flat list of entities without Os.
    entities = parser.ent_flat()
    print("entities: ", parser.ent_tags())

    # generate questions by replacing entities in sentences.
    questions = []
    for sent in parser.sents():
        for entity in sent["entitymentions"]:
            question = {}
            question["prompt"] = sentence_str(
                sent).replace(entity["text"], "_____")
            question["answer"] = entity["text"]
            question["options"] = get_similar_entities(entity, entities)
            questions.append(question)
            print(question["prompt"])
            print(question["answer"])
            print(question["options"])

    # TODO: score the prompt, answer and options.

    print("Done...", time.time() - start)


run()
