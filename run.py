
import argparse
import os
import time
from nltk.tree import Tree
from corenlp_parser import CoreNLPParser
import re
import gensim.downloader as api
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=False,
                    default='data/sample_input.txt',
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
        return get_similar_numeric(target)

    return get_similar_other(target)


def get_similar_numeric(target, count=5):
    try:
        closestWords = model.similar_by_word(word=target["text"], topn=count)
    except:
        return []

    topN = list(map(lambda x: x[0], closestWords))

    # Make the odd item the last item.
    odd_one = model.doesnt_match(topN)
    topN.remove(odd_one)
    topN.append(odd_one)

    return topN


def get_similar_other(target, count=5, debug=False):
    terms = target["text"].split()
    if debug:
        print("terms: ", terms)
    try:
        closestWords = model.most_similar(positive=terms, topn=count*10)
    except:
        if debug:
            print("error getting most_similar")
        return []

    closestWords = list(map(lambda x: x[0], closestWords))
    if debug:
        print("closestWords: ", closestWords, " terms: ", terms)

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

    if debug:
        print("unique after LSC: ", unique_options, " terms: ", terms)

    # Remove terms from options
    for t in terms:
        unique_options.remove(t)

    return unique_options


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

    print("Done...", time.time() - start)


# run()
