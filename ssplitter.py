
def split(sentence):
    processors = []
    sntcs = [sentence] # TODO: call parse here to mention multiple sentences are split and tree generated.
    for p in processors:
        sntcs = p(sntcs)
    return  ". ".join(sntcs)

def and_processor(sent_tree):
    pass
    return sent_tree