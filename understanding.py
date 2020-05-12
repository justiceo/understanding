# For setup guide see https://github.com/ExplorerFreda/self-attentive-parser
# For primer on different question types in English grammar, see https://preply.com/en/blog/2014/11/13/types-of-questions-in-english
# or https://www.grammarbank.com/question-types.html
import benepar
from nltk.tree import *

def IsSentenceOrClause(n):
    return n.label() == 'S'


# ========= #
# Base Tags #
# ========= #

# e.g. "happy" in "chickens are happy"
adjective_phrase = lambda n: n.label() == 'ADJP'

# e.g. "through" in "driving through"
adverb_phrase = lambda n: n.label() == 'ADVP'

# e.g. "a" in "Tobi is a boy"
determiner = lambda n: n.label()  == 'DT'

# e.g. "over" in "I jumped over the fence"
preposition = lambda n: n.label() == 'IN'

# e.g. "hello" in "hello hello"
injection = lambda n: n.label() == 'INTJ'

# e.g. "happy" in "chickens are happy"
adjective = lambda n: n.label() == 'JJ'

# e.g. "boy" in "Tobi is a boy"
singular_noun = lambda n: n.label()  == 'NN'

noun_phrase = lambda n: n.label() == 'NP'

# e.g. "Tobi" in the sentence "Tobi is a boy"
singular_proper_noun = lambda n: n.label() == 'NNP'

# e.g. "Nigerians" in the sentence "Nigerians are bold."
plural_proper_noun = lambda n: n.label() == 'NNPS'

# e.g. "over the fence" in "I jumped over the fence"
prepositional_phrase = lambda n: n.label() == 'PP'

# e.g. "'s" in "the dog's fur is soft"
possessive_ending = lambda n: n.label() == 'POS'

# e.g. "we" in "We are coming"
personal_pronoun = lambda n: n.label() == 'PRP'

# e.g. "Which of these is a president?"
wh_question = lambda n: n.label() == 'SBARQ'

# e.g. "is a president" in "Which of these is a president?"
wh_question_main_clause = lambda n: n.label() == 'SQ'

# e.g. "through" in "driving through"
adverb = lambda n: n.label() == 'RB'

# e.g. "hello" in "hello hello"
uh = lambda n: n.label() == 'UH'

# e.g. "start" in "started"
verb_base_form = lambda n: n.label() == 'VB'

# e.g. "jumped" in "I jumped over the fence"
verb_past_tense = lambda n: n.label() == 'VBD'

# e.g. "coming" in "We are coming"
verb_present_participle = lambda n: n.label() == 'VBG'

# e.g. "entitled" in "The song entitled home"
verb_past_participle = lambda n: n.label() == 'VBN'

# e.g. "are" in "We are coming"
singular_present_verb_non_3p = lambda n: n.label() == 'VBP'

# e.g. "is" in "Tobi is a boy"
singular_present_verb_3p = lambda n: n.label() == 'VBZ'

# e.g. "is a boy" in "Tobi is a boy"
verb_phrase = lambda n: n.label() == 'VP'

# e.g. "Which of these" in "Which of these is a president?"
wh_question_phrase = lambda n: n.label() == 'WHNP'

# e.g. "Which" in "Which of these is a president?"
wh_determiner = lambda n: n.label() == 'WDT'

# e.g. "What" in "What is obama's height?"
wh_pronoun = lambda n: n.label() == 'WP'

# e.g. "?" in "Which of these is a president?"
puntuation_mark = lambda n: n.label() == '.'

# ============ #
# Derived tags #
# ============ #

# TODO: Add utility function for promoting single children to their parents and vice-versa. 

def is_direct_question(query):
    return wh_question(query);


def traverse(t):
    try:
        t.label()
        print(" ".join(t.leaves()))
    except AttributeError:
        return
    print(t)
    

parser = benepar.Parser("benepar_en2")
tree = parser.parse("in what way")
print(tree)
print("is direct question", is_direct_question(tree))
print(traverse(tree))

# failing cases: "Would you be there", "Do you know him", "Can you find the rope"
