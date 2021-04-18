#bin/bash

# Install poetry
which poetry || pip3 install poetry

# Install project dependencies
poetry install

# Install Java if it doesn't exist.
which java || sudo apt install default-jre

# Download and unpack the JAR files.
if [ ! -d "./stanford-corenlp" ]
then
    mkdir stanford-corenlp
    wget http://nlp.stanford.edu/software/stanford-corenlp-latest.zip
    unzip stanford-corenlp-latest.zip -d stanford-corenlp
    rm stanford-corenlp-latest.zip
fi

# Set the classpath.
cd stanford-corenlp
for file in `find . -name "*.jar"`; do 
    export CLASSPATH="$CLASSPATH:`realpath $file`"; 
done