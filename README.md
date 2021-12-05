# Question Generator

## Getting Started
1. Install (Docker Desktop)[https://docs.docker.com/desktop/] - This installs docker engine, docker compose (and other things).
2. Run `docker-compose up`
3. Navigate to `localhost:9200/?url=https://en.wikipedia.org/wiki/Drake_(musician)`

## Development
1. Download and install latest python3 (min is 3.9) - https://www.python.org/downloads/
2. Install app dependencies `python3 -m pip install -r requirements.txt`
3. Run sanity tests `pytest`.
4. Start the server `python3 run.py`

## Goal with pubsub

For more see https://docs.google.com/document/d/1TbYPE_LL6M6N-kCAICvx8QjqPd9-q9KS8GUwTiOcurs/edit

```
publisher = pubsub.publisher("url")
pubsub.transform("url", "text", textract)
pubsub.transform("text", "paragraph", splitter)
pubsub.transform("paragraph", "answer", answerExtractor) // answer and prompt need to be together
pubsub.transform(["paragraph", "answer"], "prompt", promptGenerator)
pubsub.transform(["answer", "text"], "options", optionsGenerator)
pubsub.transform(["prompt", "options"], "question", questionGenerator)
pubsub.transform(["answer", "prompt", "options"], "answeredAuestion", answeredQuestionGenerator)
pubsub.collector(["question", "text"], "questionsArray", questionsCollector)
pubsub.tranform("questionsArray", "rankedQuestionsArray", questionRanker)
pubsub.subscribe("question", print)
publisher.send("http://www.google.com")

// for multiple topics, the first parent key is used for joining.
// e.g. for optionsGenerator, for every "answer", we access the "text" output.  

// for collectingTransform - we wait until all outputs are available.
// e.g. for questionCollector, we collect each question until the questionGenerator is done. And pair with text.
```

See RxPy and Jina for more on this.