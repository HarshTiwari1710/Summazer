import pymongo
from flask import Flask, request, jsonify
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from firebase_admin import auth, credentials, initialize_app
import json
import requests

app = Flask(__name__)
# Initialize Firebase app
cred = credentials.Certificate('Key.json')
firebase_app = initialize_app(cred)

# Connect to the MongoDB server
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['text_summaries']
collection = db['summaries']


@app.route('/summarize', methods=['POST'])
def text_summarization():
    # Get the text from the request
    text = request.json['text']

    # Initialize the summarizer and parser
    summarizer = LexRankSummarizer()
    parser = PlaintextParser.from_string(text, Tokenizer('english'))

    # Generate a summary of the text using LexRank
    summary = summarizer(parser.document, sentences_count=3)

    # Join the summary sentences into a single string
    summary = ' '.join(str(sentence) for sentence in summary)

    # Store the summary in the MongoDB database
    document = {'text': text, 'summary': summary}
    collection.insert_one(document)

    # Return the summary in JSON format
    return jsonify({'summary': summary})

@app.route('/summaries', methods=['GET'])
def get_summaries():
    # Retrieve all documents from the MongoDB collection
    documents = collection.find()

    # Extract the text and summaries from the documents
    summaries = []
    for document in documents:
        summary = document['summary']
        text = document['text']
        summaries.append({'text': text, 'summary': summary})

    # Return the summaries with text in JSON format
    return jsonify({'summaries': summaries})

if __name__ == '__main__':
    app.run(debug=True)
