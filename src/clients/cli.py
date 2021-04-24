from multiprocessing.managers import BaseManager
import argparse
import os.path
from shutil import which
import json
import validators

QG_PORT = 9200


class Cli:
    """
    Command-line interface for generating questions.

    Setup:
        - `pip3 install validators`
        - `npm i -g unfluff`

    Usage:
        python3 cli.py --input=https://en.wikipedia.org/wiki/Beyonc%C3%A9
    """

    def __init__(self, args):
        self.args = args
        if args.input_type == "automatic":
            if os.path.isfile(args.input):
                args.input_type = "file"
            elif validators.url(args.input):
                args.input_type = "url"
            else:
                args.input_type = "text"

        self.input_fn_dict = {
            "text": self.get_text_input,
            "file": self.get_local_file_input,
            "url": self.get_url_input,
        }

        self.manager = BaseManager(
            address=("localhost", QG_PORT), authkey=b"random auth"
        )
        self.manager.connect()
        print("Connected to process on port: " + str(QG_PORT))

    def gen_questions(self):
        print("input: ", self.extract_text())
        (requests_queue, response_queue) = self.get_queues()
        requests_queue.put(self.extract_text())
        return response_queue.get()

    def get_queues(self):
        BaseManager.register("requests")
        BaseManager.register("responses")

        return (self.manager.requests(), self.manager.responses())

    def extract_text(self):
        return self.input_fn_dict[self.args.input_type]()

    def get_text_input(self):
        return self.args.input

    def get_url_input(self):
        url = self.args.input
        if not self.can_fetch_url():
            return None
        data = os.popen('curl -s "{url}" | unfluff'.format(url=url))
        text = json.load(data)["text"]

        # Split into paragraphs.
        return text.split("\n\n")

    def get_local_file_input(self):
        file_name = self.args.input
        with open(file_name, "r") as file:
            data = file.read()

        # Split into paragraphs.
        return data.split("\n\n")

    def can_fetch_url(self):
        """Check whether curl and unfluffly is on PATH and marked as executable."""
        if which("curl") is None:
            raise RuntimeError("Install curl")
            return False

        if which("unfluff") is None:
            raise RuntimeError("Install the node package unfluff")
            return False

        return True


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A command-line entry point to the question generation models"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="The raw text input to the program or a URI to it",
    )
    parser.add_argument(
        "--input_type",
        required=False,
        default="automatic",
        choices=["text", "file", "url", "automatic"],
        help="The type of data passed to the input param. 'automatic' mode would default to text if --input cannot be parsed as URL or local file path.",
    )

    c = Cli(parser.parse_args())
    print(c.gen_questions())
