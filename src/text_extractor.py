# Usage: python3 -i text_extractor.py
# Usage: python3 text_extractor.py --uri=https://en.wikipedia.org/wiki/Oxygen > data/oxygen.txt
import os
import textract
import wget


# For more on downloading a file - https://www.tutorialspoint.com/downloading-files-from-web-using-python
def download_file(url):
    print("Downloading ", url)
    try:
        filename = wget.download(url, out="/tmp")
    except ValueError as e:
        print("\nError downloading file ", e)
        return ""

    # If file has no extension, give it .html for text extraction purposes.
    if "." not in filename:
        os.rename(filename, filename + ".html")
        return filename + ".html"

    return filename

def extract_text(filename):
    print("Extracting text from ", filename)
    return textract.process(filename)

def maybe_download_and_extract_text(uri):
    if os.path.isfile(uri):
        return extract_text(uri)
    else:
        filename = download_file(uri)
        if filename != "":
            text = extract_text(filename)
            os.remove(filename)
            return text
        else:
            raise ValueError("No file to extract text from.")    

def extract_paragraphs(uri):
    text = maybe_download_and_extract_text(uri)
    return text.decode("utf-8").split("\n\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True,
                        help="The path to the file containing the data.")
    
    args = parser.parse_args()
    print(extract_paragraphs(args.uri))

