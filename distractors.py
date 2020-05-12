from flair.data import Sentence
from flair.models import SequenceTagger
import flair.datasets
from flair.data import MultiCorpus
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

# TODO
# Train a chemistry/science NER since NER can be used for both answer generation and distractor generation.
# Input to this script should be a context string and output should be all the NEs.
# spacy has an optimal module for generating sentences from long texts. https://spacy.io/api/sentencizer
# 
st = StanfordNERTagger('./stanford-ner/english.muc.7class.distsim.crf.ser.gz',
                       './stanford-ner/stanford-ner-3.9.2.jar', 'utf-8')

text = 'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.'
text = "Back in 2017, there were 2010 elements on the 11th floor. Diatomic oxygen gas constitutes 20.8% of the Earth's atmosphere."

tokenized_text = word_tokenize(text)
nltk_classified_text = st.tag(tokenized_text)


# wnut_17 = flair.datasets.WNUT_17()
# wikiner_en = flair.datasets.WIKINER_ENGLISH()

# # make a multi corpus consisting of two UDs
# multi_corpus = MultiCorpus([wnut_17, wikiner_en])

# make a sentence
sentence = Sentence(text)

# load the NER tagger
tagger = SequenceTagger.load('multi-ner-fast')

# run NER over sentence
tagger.predict(sentence)


print("Sentence: ", sentence)
print("Stanford NER: ", nltk_classified_text)
print('Flair: ')

# iterate over entities and print
for entity in sentence.get_spans('ner'):
    print(entity)
