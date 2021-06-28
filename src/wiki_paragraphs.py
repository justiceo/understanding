# Usage: python3 -i wiki_paragraphas.py
# Usage: python3 wiki_paragraphs.py --url=https://en.wikipedia.org/wiki/Oxygen > data/oxygen.txt
import os
import json
import re
from utils import get_logger


logger = get_logger(__name__)


def raw_text(url):
    data = os.popen("""curl -X GET http://localhost:9300  -d '{"url": "$URL"}'""".replace("$URL", url))
    return json.load(data)


def paragraphs_remote(url):
    # If error, return empty list.
    text = raw_text(url)
    if text is None:
        return []

    # Remove references from wikis.
    if "wikipedia.org/wiki" in url:
        text = re.sub(r"\[\d+\]", "", text)

    # Split into paragraphs.
    return text.split("\n\n")

