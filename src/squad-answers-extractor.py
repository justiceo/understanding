import json
import re
import sys
import pandas as pd
import benepar
from progress.bar import Bar
from nltk.tree import *

# Would not match:
# Quoted text, e.g. A in "The first letter in the alphabet is 'A'."
# Partial text, e.g. alpha in "The first letter in the alphabet is 'A'."
# Case-insentitive text, e.g. First in "The first letter in the alphabet is 'A'."
# Unicode text, e.g. \u2013 (long hypen 1716-1718) in "It lasted between 1716\u20131718."


def get_sentence(context_str, answer_text, answer_start):
    # address an edge case where answer text is first word.
    context_str = " " + context_str
    try:
        matches = re.finditer(
            rf"[^.?!]*(?<=[.?\s!]){answer_text}(?=[\s.?!])[^.?!]*[.?!]", context_str, re.IGNORECASE)
    except:
        matches = []
        return None
    for match in matches:
        if match.start() <= answer_start and match.end() >= answer_start + len(answer_text):
            return match.group().strip()
    return None


# x = get_sentence(
#     "Dorsey was born and raised in St. Louis, Missouri the son of Tim and Marcia (née Smith) Dorsey.", "Dorsey", 34)
# print(x)
# exit()

with open("data/squad-train-tiny-v2.0.json", "r") as read_file:
    data = json.load(read_file)['data']

# get senteces
print("generating sentences dense with answers...")
bar = Bar('Gen top sentences', max=70000)
sents = []
for section in data:
    for paragraph in section['paragraphs']:
        for question in paragraph['qas']:
            for answer in question['answers']:
                x = get_sentence(
                    paragraph['context'], answer['text'], answer['answer_start'])
                if x is not None:
                    sents.append(x)
                    bar.next()
bar.finish()
print("# sentences", len(sents))
df = pd.DataFrame(data=sents, columns=['sentence'])
answer_count = len(df)
df = df['sentence'].value_counts().reset_index(name='count')
df.columns = ['sentence', 'count']
df = df.sort_values('count', ascending=False)
# remove sentences that have fewer than 5 associated answers.
df = df[df['count'] > 8]
top_sents = df['sentence'].values.tolist()
print("top sents length: ", len(top_sents))


# Create the map context -> answer text -> answer_start
# Avoids too many answer duplicates.
print("extracting answer, sentence pairs...")
bar = Bar('Extract answers+sentences', max=answer_count)
whole_map = {}
for section in data:
    for paragraph in section['paragraphs']:
        context = paragraph['context']
        whole_map[context] = {}
        questions = paragraph['qas']
        for question in questions:
            for answer in question['answers']:
                s = get_sentence(
                    context, answer['text'], answer['answer_start'])
                if s is None:
                    continue
                # Temporary: Do not include non-popular sentences.
                if s not in top_sents:
                    continue
                if s not in whole_map.keys():
                    whole_map[s] = {}
                print("adding answer: ", answer['text'])
                whole_map[s][answer['text']] = answer['answer_start']
                bar.next()
bar.finish()

# Go through the map and for each answer, trim down the context
answers_with_context = []
print("loading model...")
parser = benepar.Parser("benepar_en2")
bar = Bar('Processing', max=len(whole_map))
for context_str, answers in whole_map.items():
    # get constituency parsing of text
    try:
        tmp_tree = parser.parse(context_str)
    except ValueError:
        # TODO: figure out a way to parse long sentences.
        continue

    context_tree = ParentedTree.convert(tmp_tree)
    for answer_text, start in answers.items():
        # if answer occurs multiple time in context, skip to avoid confusion
        if context_str.count(answer_text) != 1:
            print("skipping answer: ", answer_text)
            continue

        # find a node in context_tree that contains answer wholly.
        for st in context_tree.subtrees(lambda t: " ".join(t.leaves()) == answer_text):
            labels = {"text": answer_text, "is_answer": True,
                      "label": st.label(), "root_label": st.root().label()}

            if st.parent() is not None:
                labels['parent_label'] = st.parent().label()
                if st.parent().parent() is not None:
                    labels['grand_parent_label'] = st.parent().parent().label()
                else:
                    labels['grand_parent_label'] = None
            else:
                labels['parent_label'] = None

            if st.left_sibling() is not None:
                labels['left_sibling_label'] = st.left_sibling().label()
                if st.left_sibling().left_sibling() is not None:
                    labels['left_left_sibling_label'] = st.left_sibling(
                    ).left_sibling().label()
                else:
                    labels['left_left_sibling_label'] = None
            else:
                labels['left_sibling_label'] = None

            if st.right_sibling() is not None:
                labels['right_sibling_label'] = st.right_sibling().label()
                if st.right_sibling().right_sibling() is not None:
                    labels['right_right_sibling_label'] = st.right_sibling(
                    ).right_sibling().label()
                else:
                    labels['right_right_sibling_label'] = None
            else:
                labels['right_sibling_label'] = None

            print("r adding answer: ", answer_text[:20])
            answers_with_context.append(labels)

    # Add other words in sentence.
    for st in context_tree.subtrees(lambda t: " ".join(t.leaves()) not in answers):
        answer_text = " ".join(st.leaves())
        labels = {"text": answer_text, "is_answer": False,
                  "label": st.label(), "root_label": st.root().label()}

        if st.parent() is not None:
            labels['parent_label'] = st.parent().label()
            if st.parent().parent() is not None:
                labels['grand_parent_label'] = st.parent().parent().label()
            else:
                labels['grand_parent_label'] = None
        else:
            labels['parent_label'] = None

        if st.left_sibling() is not None:
            labels['left_sibling_label'] = st.left_sibling().label()
            if st.left_sibling().left_sibling() is not None:
                labels['left_left_sibling_label'] = st.left_sibling(
                ).left_sibling().label()
            else:
                labels['left_left_sibling_label'] = None
        else:
            labels['left_sibling_label'] = None

        if st.right_sibling() is not None:
            labels['right_sibling_label'] = st.right_sibling().label()
            if st.right_sibling().right_sibling() is not None:
                labels['right_right_sibling_label'] = st.right_sibling(
                ).right_sibling().label()
            else:
                labels['right_right_sibling_label'] = None
        else:
            labels['right_sibling_label'] = None

        answers_with_context.append(labels)
    bar.next()

bar.finish()
print(answers_with_context[:1])
print(len(answers_with_context))


with open("data/squad-train-trimmed-v2.1.json", "w") as out:
    json.dump(answers_with_context, out)

print("done.")