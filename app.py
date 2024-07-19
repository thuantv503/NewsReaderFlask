from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = '46d8e2a191654c13ba334d36510a3a9f'
BASE_URL = 'https://newsapi.org/v2/everything'

def fetch_news(query, page=1, page_size=20):
    params = {
        'q': query,
        'apiKey': API_KEY,
        'page': page,
        'pageSize': page_size
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_bbc_news(page=1, page_size=20, sources='bbc-news'):
    params = {
        'apiKey': API_KEY,
        'page': page,
        'pageSize': page_size,
        'sources': sources
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        keyword = request.form.get('keyword')
        articles = []
        if keyword:
            news_data = fetch_news(keyword)
            if news_data:
                articles = news_data.get('articles', [])
        return render_template('home.html', all_articles=articles, keyword=keyword)
    else:
        articles = []
        bbc_news_data = fetch_bbc_news()
        if bbc_news_data:
            articles = bbc_news_data.get('articles', [])
        return render_template('home.html', all_headlines=articles)

if __name__ == '__main__':
    app.run(debug=True)