import flask
from flask import request, jsonify
from newspaper import Article 
import requests
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/fact-check', methods=['POST'])
def factCheck():
    queryParams = request.args.to_dict()
    print(queryParams);
    newsUrl = queryParams.get('newsUrl');
    article = Article(str(newsUrl), language='en')
    article.download()
    article.parse()
    articleTitle = article.title
    articleContent = article.text
    print(articleTitle)
    factCheckApiKey = 'YOUR_API_KEY'
    factCheckResponse = requests.get("https://factchecktools.googleapis.com/v1alpha1/claims:search", params={"query": articleTitle, "key": factCheckApiKey})
    print(factCheckResponse.content)
    if factCheckResponse.content == b'{}\n':
        print('jgjhvjgvghjvjh')
        fakeboxResponse = requests.post("http://localhost:8080/fakebox/check", json={'url': newsUrl, 'content': articleContent, 'title': articleTitle})
        fakeboxJson = json.loads(fakeboxResponse.content.decode('utf-8'))
        print(fakeboxJson)
        apiResponse = {"articleTitle": articleTitle, "articleBias": fakeboxJson.get('content').get('decision'), "articleCategory": fakeboxJson.get('domain').get('category')}
        return apiResponse
    return factCheckResponse.content

app.run()