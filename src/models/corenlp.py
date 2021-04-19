import json
import requests
from ports import CORE_NLP_PORT


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
        self.url = "http://localhost:" + port
        self.session = requests.Session()
        return False

    def ner(self, sentences, encoding="utf8"):
        """
        Returns a sentences with their NER tags.
        """

        return self.for_annotators(sentences, "ner", encoding)

    def coref(self, sentences, encoding="utf8"):
        """
        TODO: Remove the implementation details below.
        """
        tagged_data = self.for_annotators(sentences, "dcoref", encoding)
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

        return paragraph

    def for_annotators(self, sentences, annotators, encoding, timeout=60):
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
