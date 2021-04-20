import json
import requests
from ports import GENSIM_PORT


class Gensim:
    """
    Interface to interacting with Gensim Rest API.
    TODO: Dockerize https://github.com/alibugra/flask-gensim
    """

    def init(self, port=GENSIM_PORT):
        """
        Issues a call to the server with a hardcoded text, prints the return status.
        Returns true if server returned OK.
        """
        self.url = "http://localhost:" + port
        self.session = requests.Session()
        return False

    def most_similar(self, terms, timeout=60):
        """
        Returns words similar to the given terms.

        TODO: Provide caching at this level.
        """

        response = self.session.get(
            self.url,
            params={"terms": json.dumps(terms)},
            timeout=timeout,
        )

        response.raise_for_status()
        return response.json()
