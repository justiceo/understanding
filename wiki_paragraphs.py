# Usage: python3 -i wiki_paragraphas.py
import os
import json
import re
import shutil
from shutil import which

def is_requirements_ok():
    """Check whether curl and unfluffly is on PATH and marked as executable."""
    if which("curl") is None:
        print("Install curl")
        return False

    if which("unfluff") is None:
        print("Install the node package unfluff")
        return False

    return True

def raw_text(url):
    if not is_requirements_ok():
        return None
    data = os.popen('curl -s "{url}" | unfluff'.format(url=url))
    return json.load(data)["text"]

def paragraphs(url):
    # If error, return empty list.
    text = raw_text(url)
    if text is None:
        return []

    # Remove references from wikis.
    if "wikipedia.org/wiki" in url:
        text = re.sub(r"\[\d+\]", "", text)

    # Split into paragraphs.
    return  text.split("\n\n")