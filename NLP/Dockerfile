# Alpine Linux with OpenJDK JRE
FROM openjdk:8-jre-alpine

COPY . .
RUN wget http://nlp.stanford.edu/software/stanford-corenlp-latest.zip	
RUN unzip stanford-corenlp-latest.zip
WORKDIR stanford-corenlp-latest/stanford-corenlp-4.2.0
EXPOSE 9000
RUN java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
