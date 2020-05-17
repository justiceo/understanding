
import argparse
import os
import time
from nltk.tree import Tree
from corenlp_parser import CoreNLPParser
import re


parser = argparse.ArgumentParser()
parser.add_argument("--input", required=False,
                    default='data/sample_input2.txt',
                    help="Plain text file with text for generating questions.")
parser.add_argument("--output", required=False,
                    default='data/sample_out.text',
                    help="File to write JSON list of questions")


args = parser.parse_args()


def get_input():
    with open(args.input, 'r') as file:
        data = file.read()

    # TODO: consider apply white-space fix.
    # ' '.join(data.split())
    return data

space_regex = re.compile(r"\( ", re.IGNORECASE)
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


# def group_tags(tags):
#     out = []
#     for tag in tags:
#         if len(out) == 0:
#             out.append(tag)
#             continue

#         last = out.pop()
#         if tag["ner"] == last["ner"]:
#             # TODO: Might important: Merge tags carefully, respecting indices, and confidences.
#             last["text"] = " ".join([last["text"], tag["text"]])
#             last["characterOffsetEnd"] = tag["characterOffsetEnd"]
#             out.append(last)
#         else:
#             out.extend([last, tag])
#     return out
    
def run():
    start = time.time()

    # get input text.
    text = get_input()
    # text = "John lived in America. He is married."

    # parse text using CoreNLP Server.
    parser = CoreNLPParser(sentences=text)
    print("parsed text...", time.time() - start)

    # flatten the list and remove Os for easy search
    entities = [ent for ent_group in parser.ents() for ent in ent_group if ent["ner"] != "O"]
    print("entities: ", [(e["text"], e["ner"]) for e in entities])

    # generate questions by replacing entities in sentences.
    questions = []
    for sent in parser.sents():
        for entity in sent["entitymentions"]:
            question = {}
            question["prompt"] = sentence_str(sent).replace(entity["text"], "_____")
            question["answer"] = entity["text"].title()
            question["options"] = get_similar_entities(entity, entities)
            questions.append(question)
            print("\n\n", question)

    # TODO: score the prompt, answer and options.

    print("Done...", time.time() - start)

run()