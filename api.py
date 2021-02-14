import flask
from flask import request, jsonify
from newspaper import Article 
import requests
import json
from flask import Flask
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True


@app.route('/fact-check', methods=['POST'])
def factCheck():
    queryParams = request.args.to_dict()
    newsUrl = queryParams.get('newsUrl');
    article = Article(str(newsUrl), language='en')
    article.download()
    article.parse()
    articleTitle = article.title
    articleContent = article.text
    metaResponse = requests.get('https://api.urlmeta.org/?url='+newsUrl, headers={'Authorization': 'Basic dGhlc2FoYXJzaEBnbWFpbC5jb206a2FudmlYc3JIZFhhUk9SZk10RUQ='})
    metaJson = json.loads(metaResponse.content.decode('utf-8'))
    factCheckApiKey = 'AIzaSyCrV1SGkvPGgIKwV6xG_A4z0xZRZ7YgFBg'
    factCheckResponse = requests.get("https://factchecktools.googleapis.com/v1alpha1/claims:search", params={"query": articleTitle, "key": factCheckApiKey})
    if factCheckResponse.content == b'{}\n':
        fakeboxResponse = requests.post("http://localhost:8080/fakebox/check", json={'url': newsUrl, 'content': articleContent, 'title': articleTitle})
        fakeboxJson = json.loads(fakeboxResponse.content.decode('utf-8'))
        apiResponse = {"meta": metaJson, "articleTitle": articleTitle, "articleBias": fakeboxJson.get('content').get('decision'), "articleCategory": fakeboxJson.get('domain').get('category'), "articleContent": articleContent}
        return apiResponse
    factCheckJson = json.loads(factCheckResponse.content.decode('utf-8'))
    apiResponse = {"claim": factCheckJson.get('claims')[0], "meta": metaJson, "articleTitle": articleTitle, "articleContent": articleContent}
    return apiResponse

@app.route('/checkbook-invoice', methods=['POST'])
def createInvoice():
    queryParams = request.args.to_dict()
    name = queryParams.get('name')
    print(name)
    print(queryParams)
    recipient = queryParams.get('recipient')
    description = queryParams.get('description')
    amount = int(queryParams.get('amount'))
    response = requests.post("https://sandbox.checkbook.io/v3/invoice", json={'name': name, 'amount': amount, 'recipient': recipient, 'description': description}, headers={'Authorization': 'e08051a7be464444b608365c9a563e69:a15592731bd5139f57aaf44764f9c1bd'})
    print(response.content)
    responseJson = json.loads(response.content.decode('utf-8'))
    return responseJson

@app.route('/invoice', methods=['GET'])
def checkInvoice():
    queryParams = request.args.to_dict()
    invoiceId = queryParams.get('id')
    response = requests.get("https://sandbox.checkbook.io/v3/invoice/"+invoiceId, headers={'Authorization': 'e08051a7be464444b608365c9a563e69:a15592731bd5139f57aaf44764f9c1bd'})
    print(response.content)
    responseJson = json.loads(response.content.decode('utf-8'))
    return responseJson

@app.route('/', methods=['OPTIONS'])
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


app.run()