# Usage: python3 -i wiki_paragraphas.py
# Usage: python3 wiki_paragraphs.py --url=https://en.wikipedia.org/wiki/Oxygen > data/oxygen.txt
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

def paragraphs_local(file_name):
    with open(file_name, 'r') as file:
        data = file.read()

    return data.split("\n\n")

def paragraphs(url):
    # If error, return empty list.
    text = raw_text(url)
    if text is None:
        return []

    # Remove references from wikis.
    if "wikipedia.org/wiki" in url:
        text = re.sub(r"\[\d+\]", "", text)

    # Split into paragraphs.
    return text.split("\n\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True,
                        help="The URL to wiki page.")
    parser.add_argument("--output", required=False,
                        help="File to write text output")

    args = parser.parse_args()
    ps = paragraphs(args.url)
    out = "\n\n".join(ps)
    if args.output is not None:
        with open(args.output, "w") as outfile:
            outfile.write(out)
    else:
        print(out)
