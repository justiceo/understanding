import argparse
from models.corenlp import CoreNLP
from models.gensim import Gensim
from text_extractor import extract_paragraphs
from wiki_paragraphs import paragraphs_remote
from utils import get_logger
from utils import fix_punctuation
from bottle import route, run, template, request, response
from json import dumps

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    required=False,
    default="../data/beyonce.txt",
    help="Plain text file with text for generating questions.",
)
parser.add_argument(
    "--output",
    required=False,
    default="data/sample_out.text",
    help="File to write JSON list of questions",
)
args = parser.parse_args()
logger = get_logger(__name__)
coreNLP = CoreNLP()
coreNLP.init()
gensim = Gensim()
gensim.init()


def sentence_str(sentence):
    return fix_punctuation(" ".join([t["word"] for t in sentence["tokens"]]))


def get_similar_entities(target):
    # TODO: Update to differentiate numericals.
    return gensim.most_similar(target["text"].split())


def resolve_corefs(text):
    # resolve co-references (the time grows at least exponentially with text length)
    return coreNLP.coref(sentences=text)


def trim_text(text):
    # remove text that doesn't add much to essence, in this case 10% of input text.
    return text  # summarize(text, ratio=0.9)


def run_models(input=args.input):
    logger.info("starting the whole shebang.")

    # get input text.
    paragraphs = paragraphs_remote(input)
    text = "\n".join(paragraphs[0:2])
    logger.info("acquired input: ")
    print("input: ", text)

    # resolve co-refs: she -> Beyonce
    text = resolve_corefs(text)
    logger.info("resolved co-refs")

    text = trim_text(text)
    logger.info("trimmed text")

    # generate questions by replacing entities in sentences.
    questions = []
    for sent in coreNLP.sents(text):
        for entity in sent["entitymentions"]:
            question = {}
            question["prompt"] = sentence_str(sent).replace(entity["text"], "_____")
            question["answer"] = entity["text"]
            question["options"] = get_similar_entities(entity)
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

    logger.info("done")
    return questions

@route('/')
def index():
    logger.info("Received new request", request)
    url = request.query.url
    questions = run_models(url)
    response.content_type = 'application/json'
    return dumps(questions)




if __name__ == "__main__":
    logger.info("initializing web")
    run(host='0.0.0.0', port=9200, debug=True, reloader=True)
