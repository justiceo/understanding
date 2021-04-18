
import logging
import re


def get_logger(name=__name__):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


# TODO: combine these into one, simple | fails for
# "\"I voted for Obama\", she said. He was born in (2016) but [18]. It's not true?"
pre_space = re.compile(r"\s([.,\)\]?])")
post_space = re.compile(r"([\[(])\s")
quotation_space = re.compile(r"(\")\s(.*?)\s(\")")
thin_quote_space = re.compile(r"\s('s)")
dash_space = re.compile(r"\s(-)\s")


def fix_punctuation(text):
    # Replace ( 2018 ) with ( 2018)
    text = pre_space.sub(r'\1', text)

    # Replace ( 2018 ) with (2018 )
    text = post_space.sub(r'\1', text)

    text = quotation_space.sub(r'\1\2\3', text)

    text = thin_quote_space.sub(r'\1', text)

    text = dash_space.sub(r'\1', text)
    
    return text


# Returns true if number is of the form \d*[st|nd|rd|th], crash or false otherwise.
# See explanation at https://codegolf.stackexchange.com/a/162322
isOrdinalNum = lambda v:'hsnrhhhhhh'[(v[-4:-3]!='1')*int(v[-3])]in v