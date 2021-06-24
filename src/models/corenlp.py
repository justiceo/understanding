import json
import requests
from utils import fix_punctuation

CORE_NLP_PORT: int = 9000


class CoreNLP:
    """
    Interface to the CoreNLP REST API.
    Adapted from https://www.nltk.org/_modules/nltk/parse/corenlp.html
    """

    def init(self, port=CORE_NLP_PORT):
        """
        Issues a call to the server with a hardcoded text, prints the return status.
        Returns true if server returned OK.
        """
        self.url = "http://corenlp:" + str(port)
        self.session = requests.Session()
        return False

    def coref(self, sentences, encoding="utf8"):
        """

        FYI: Time grows at least exponentially with text length.
        TODO: Remove the implementation details below.
        """
        tagged_data = self.__for_annotators(sentences, "dcoref", encoding)
        corefs = tagged_data["corefs"]

        # Map corefs to { "representative_mention": [{"ref", "sent", "token"}]}
        # Map corefs to {(sentNum, startIndex): rep_mention }
        coref_map = {}
        for gid, group in corefs.items():
            rep_text = next(
                (
                    x["text"]
                    for x in group
                    if x["isRepresentativeMention"] and x["type"] != "PRONOMINAL"
                ),
                None,
            )
            if rep_text is None:
                continue
            coref_map.update(
                {
                    (m["sentNum"], m["startIndex"]): rep_text
                    for m in group
                    if m["endIndex"] - m["startIndex"] == 1
                }
            )

        # Create sentences list replace any replaceables.
        sents = [
            [
                coref_map.get((i + 1, token["index"]), token["originalText"])
                for token in sent["tokens"]
            ]
            for i, sent in enumerate(tagged_data["sentences"])
        ]

        # Rebuild sentence list into paragraph.
        paragraph = " ".join([" ".join(s) for s in sents])

        return fix_punctuation(paragraph)

    def sents(self, text):
        return self.__ner(text)["sentences"]

    def __ner(self, sentences, encoding="utf8"):
        """
        Returns a sentences with their NER tags.
        """

        return self.__for_annotators(sentences, "ner", encoding)

    def __for_annotators(self, sentences, annotators, encoding, timeout=60):
        """
        Returns senteces tagged by the given annotators.

        TODO: Provide caching at this level.
        """

        default_properties = {
            "outputFormat": "json",
            "annotators": annotators,
        }

        response = self.session.post(
            self.url,
            params={"properties": json.dumps(default_properties)},
            data=sentences.encode(encoding),
            timeout=timeout,
        )

        response.raise_for_status()
        return response.json()

    def __unused_ent_tags(self):
        return [(e["text"], e["ner"]) for e in self.__unused_ent_flat()]

    def __unused_ent_flat(self):
        return [
            ent
            for ent_group in self.__unused_ents()
            for ent in ent_group
            if ent["ner"] != "O"
        ]

    def __unused_ents(self):
        return [
            [t for t in tagged_sentence["entitymentions"]]
            for tagged_sentence in self.tagged_data["sentences"]
        ]
