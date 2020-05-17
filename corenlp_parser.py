# -*- coding: utf-8 -*-
# Interface to the CoreNLP REST API.
#
# Adapted from https://www.nltk.org/_modules/nltk/parse/corenlp.html
import json


class CoreNLPParser():
    """Interface to the CoreNLP Parser."""

    def __init__(self, sentences=None, url="http://localhost:9000", encoding="utf8"):
        import requests

        self.url = url
        self.encoding = encoding
        self.session = requests.Session()
        self.tagged_data = self.api_call(sentences)

    def api_call(self, data, timeout=60):
        default_properties = {
            "outputFormat": "json",
            "annotators": "tokenize,ssplit,ner",
            # "annotators": "tokenize,pos,lemma,ssplit,parse,pos,ner,dcoref",
        }

        response = self.session.post(
            self.url,
            params={"properties": json.dumps(default_properties)},
            data=data.encode(self.encoding),
            timeout=timeout,
        )

        response.raise_for_status()
        return response.json()

    def ent_tags(self):
        entities = [ent for ent_group in self.ents()
                    for ent in ent_group if ent["ner"] != "O"]
        return [(e["text"], e["ner"]) for e in entities]

    def ents(self):
        return [
            [t for t in tagged_sentence["entitymentions"]]
            for tagged_sentence in self.tagged_data["sentences"]
        ]

    def sents(self):
        return self.tagged_data["sentences"]
