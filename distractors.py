from flair.data import Sentence
from flair.models import SequenceTagger
import flair.datasets
from flair.data import MultiCorpus
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import scispacy
import spacy
import time


# TODO
# Train a chemistry/science NER since NER can be used for both answer generation and distractor generation.
# Input to this script should be a context string and output should be all the NEs.
# spacy has an optimal module for generating sentences from long texts. https://spacy.io/api/sentencizer

def get_spacy_ner(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]


def get_spacy_ner_lg(text):
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]


def get_scispacy_ner(text):
    nlp = spacy.load("en_core_sci_sm")
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def get_scispacy_bc5_ner(text):
    nlp = spacy.load('en_ner_bc5cdr_md')
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]


def get_stanford_ner3(text):
    st3 = StanfordNERTagger('./stanford-ner/english.all.3class.distsim.crf.ser.gz',
                            './stanford-ner/stanford-ner-3.9.2.jar', 'utf-8')
    tokenized_text = word_tokenize(text)
    classified = st3.tag(tokenized_text)
    return [t for t in classified if t[1] != 'O']


def get_stanford_ner7(text):
    st7 = StanfordNERTagger('./stanford-ner/english.muc.7class.distsim.crf.ser.gz',
                            './stanford-ner/stanford-ner-3.9.2.jar', 'utf-8')
    tokenized_text = word_tokenize(text)
    st7_classified = st7.tag(tokenized_text)
    return [t for t in st7_classified if t[1] != 'O']


def get_flair_ner(text):
    # wnut_17 = flair.datasets.WNUT_17()
    # wikiner_en = flair.datasets.WIKINER_ENGLISH()

    # # make a multi corpus consisting of two UDs
    # multi_corpus = MultiCorpus([wnut_17, wikiner_en])

    # make a sentence
    sentence = Sentence(text)

    flair_tagger = SequenceTagger.load('multi-ner-fast')
    # run NER over sentence
    flair_tagger.predict(sentence)

    # iterate over entities and print
    return sentence.get_spans('ner')


def eval(text):
    print("\nSentence: ", text)
    start = time.time()

    print("\nFlair: ", get_flair_ner(text))
    print("Time taken: ", time.time() - start)
    start = time.time()

    print("\nSpacy: ", get_spacy_ner(text))
    print("Time taken: ", time.time() - start)
    start = time.time()

    print("\nSpacy Lg: ", get_spacy_ner_lg(text))
    print("Time taken: ", time.time() - start)
    start = time.time()

    print("\nSciSpacy: ", get_scispacy_ner(text))
    print("Time taken: ", time.time() - start)
    start = time.time()

    print("\nSciSpacy BC5: ", get_scispacy_bc5_ner(text))
    print("Time taken: ", time.time() - start)
    start = time.time()

    print("\nStanford NER3: ", get_stanford_ner3(text))
    print("Time taken: ", time.time() - start)
    start = time.time()

    print("\nStanford NER7: ", get_stanford_ner7(text))
    print("Time taken: ", time.time() - start)
    start = time.time()


text0 = 'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.'

text00 = "Back in 2017, there were 2010 elements on the 11th floor. Diatomic oxygen gas constitutes 20.8% of the Earth's atmosphere."

text1 = """
Mass is the measure of inertia. From a subatomic point of view, mass can also be understood
in terms of energy, but that does not concern us when dealing with chemistry. Mass for
particles, atoms, and molecules is not measured in grams, as with ordinary substances.
Instead, it is measured in atomic mass units, or amu. For more information about mass
and amu, read the previous chapters on properties of matter.
"""

text2 = """
If the enthalpy decreases during a chemical reaction, a corresponding amount of energy must
be released to the surroundings. Conversely, if the enthalpy increases during a reaction, a
corresponding amount of energy must be absorbed from the surroundings. This is simply
the Law of Conservation of Energy.
"""

text3 = """
The concentration of a solution is the measure of how much solute and solvent there is. A
solution is concentrated if it contains a large amount of solute, or dilute if contains a small
amount.
"""

text4 = """
Molarity is the number of moles of solute per liter of solution. It is abbreviated with the
symbol M, and is sometimes used as a unit of measurement, e.g. a 0.3 molar solution of HCl.
In that example, there would be 3 moles of HCl for every 10 liters of water (or whatever the
solvent was).
"""

text5 = """
"A self-described \"modern-day feminist\", Beyonc\u00e9 creates songs that are often
characterized by themes of love, relationships, and monogamy, as well as female sexuality and empowerment. 
On stage, her dynamic, highly choreographed performances have led to critics hailing 
her as one of the best entertainers in contemporary popular music. 
Throughout a career spanning 19 years, she has sold over 118 million records as a solo artist, and a further 60 million with Destiny's Child, making her one of the best-selling music artists of all time. 
She has won 20 Grammy Awards and is the most nominated woman in the award's history. The Recording Industry Association of America recognized her as the Top Certified Artist in America during the 2000s decade. 
In 2009, Billboard named her the Top Radio Songs Artist of the Decade, 
the Top Female Artist of the 2000s and their Artist of the Millennium in 2011. 
Time listed her among the 100 most influential people in the world in 2013 and 2014. 
Forbes magazine also listed her as the most powerful female musician of 2015.
"""

text6 = """
The Normans (Norman: Nourmands; French: Normands; Latin: Normanni) were the people who in 
the 10th and 11th centuries gave their name to Normandy, a region in France. 
They were descended from Norse (\"Norman\" comes from \"Norseman\") raiders and pirates from Denmark, 
Iceland and Norway who, under their leader Rollo, agreed to swear fealty to King Charles III of West Francia. 
Through generations of assimilation and mixing with the native Frankish and Roman-Gaulish populations, 
their descendants would gradually merge with the Carolingian-based cultures of West Francia. 
The distinct cultural and ethnic identity of the Normans emerged initially in the first half of the 10th century, 
and it continued to evolve over the succeeding centuries.
"""

# Stanford NER3 => Very precise
# Spacy SM => Very fast
# (Spacy SM intersected with Spacy LG) => Precise, rich and slow.

eval(text6)
