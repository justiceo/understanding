import gensim.downloader as api
import time
import nltk 
# for wordnet interface see https://www.nltk.org/howto/wordnet.html
from nltk.corpus import wordnet 

print("Loading model...")
start = time.time()
model = api.load("fasttext-wiki-news-subwords-300")
print("Loaded model... ", time.time() - start)

def get_similar(term, count=5):
    start = time.time()
    try:
        cosine_similar = model.most_similar(positive=[term], topn=count)
        cosine_similar = [x[0] for x in cosine_similar]
    except KeyError:
        cosine_similar = []

    print("Cosine similar: ", cosine_similar)
    print("Took: ", time.time() - start)
    start = time.time()

    # wordnet
    synonyms = [] 
    antonyms = [] 
    
    for syn in wordnet.synsets(term): 
        for l in syn.lemmas(): 
            synonyms.append(l.name()) 
            if l.antonyms(): 
                antonyms.append(l.antonyms()[0].name()) 
    
    print("\nSynonyms: ", set(synonyms)) 
    print("\nAntonyms: ", set(antonyms)) 
    print("Took: ", time.time() - start)

