# Setup

## Start CoreNLP server.
1. Download Stanford CoreNLP from - https://stanfordnlp.github.io/CoreNLP/download.html
2. Unzip the models jar inside the CoreNLP jar into Stanfod CoreNLP directory.
3. Start REPL with CoreNLP with `./corenlp.sh -annotators tokenize,ssplit,pos,depparse,lemma,ner,entitymentions,entitylink`
4. Start CoreNLPServer for API access using `java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000`
5. Install Poetry: `pip3 install poetry`
6. Install app dependencies: `poetry install`
7. Run tests `poetry run pytest`.

## Start GenSim server.
1. `$ poetry run python3 gensim_server.py`

## Run the script.
1. `$ poetry run python3 -i run.py`
2. `>>> run()`