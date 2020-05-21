from flair.data import Sentence
from flair.models import SequenceTagger
import flair.datasets
from flair.data import MultiCorpus
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from corenlp_parser import CoreNLPParser
import scispacy
import spacy
import time
from chemdataextractor import Document


# TODO
# Train a chemistry/science NER since NER can be used for both answer generation and distractor generation.
# Input to this script should be a context string and output should be all the NEs.
# spacy has an optimal module for generating sentences from long texts. https://spacy.io/api/sentencizer
# get wikidata using https://github.com/attardi/wikiextractor
# perform co-reference resolution on the text first using - https://github.com/facebookresearch/SpanBERT
# Wikipedia data dump download url - https://github.com/trycycle/wikipedia-downloader
# https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2

def group_tags(tags):
    out = []
    for tag in tags:
        if len(out) == 0:
            out.append(tag)
            continue

        last = out.pop()
        if tag[1] == last[1]:
            out.append((' '.join([last[0], tag[0]]), tag[1]))
        else:
            out.extend([last, tag])
    return out


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
    return [t for t in group_tags(classified) if t[1] != 'O']


def get_stanford_ner7(text):
    st7 = StanfordNERTagger('./stanford-ner/english.muc.7class.distsim.crf.ser.gz',
                            './stanford-ner/stanford-ner-3.9.2.jar', 'utf-8')
    tokenized_text = word_tokenize(text)
    st7_classified = st7.tag(tokenized_text)
    return [t for t in group_tags(st7_classified) if t[1] != 'O']


def get_stanford_ner(text):
    # Don't forget to start server in ~/code/stanford-nlp/ by running
    # java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
    # test with:
    # wget --post-data 'John Doe lives in America. The Earth's crust is red.' 'localhost:9000/?properties={"annotators": "tokenize,ssplit,ner,parse,dcoref", "outputFormat": "json"}' -O - > data/sample_out.json
    ner_tagger = CoreNLPParser(sentences=text)
    return ner_tagger.ent_tags()


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


def get_chem_data_extractor_ner(text):
    doc = Document(text)
    return doc.cems


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

    print("\nStanford NER: ", get_stanford_ner(text))
    print("Time taken: ", time.time() - start)
    start = time.time()

    print("\nChemDataExtractor: ", get_chem_data_extractor_ner(text))
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
A self-described \"modern-day feminist\", Beyonc\u00e9 creates songs that are often 
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

text7 = """
The modern human experience places a large emphasis upon the material world. From the
day of our birth to the day we die, we are frequently preoccupied with the world around
us. Whether struggling to feed ourselves, occupying ourselves with modern inventions,
interacting with other people or animals, or simply meditating on the air we breathe, our
attention is focused on different aspects of the material world. In fact only a handful of
disciplines—certain subsets of religion, philosophy, and abstract math—can be considered
completely unrelated to the material world. Everything else is somehow related to chemistry,
the scientific discipline which studies the properties, composition, and transformation of
matter.
Chemistry itself has a number of branches:
• Analytical chemistry seeks to determine the composition of substances.
• Biochemistry is the study of chemicals found in living things (such as DNA and proteins).
• Inorganic Chemistry studies substances that do not contain carbon.
• Organic chemistry studies carbon-based substances. Carbon, as described in more detail
in this book, has unique properties that allow it to make complex chemicals, including
those of living organisms. An entire field of chemistry is devoted to substances with this
element.
• Physical chemistry is the study of the physical properties of chemicals, 
which are characteristics that can be measured without changing the composition of the substance.
"""

# Stanford NER3 => Very precise
# Spacy SM => Very fast
# (Spacy SM intersected with Spacy LG) => Precise, rich and slow.

eval(text7)
