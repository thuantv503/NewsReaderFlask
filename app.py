from flask import Flask, redirect, url_for, render_template, request, session
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Cấu hình OAuth
oauth = OAuth(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  

# Cấu hình OAuth cho Google
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_params=None,
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
)


class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email


# Mock database
users = {}


@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth')
def authorize():
    token = google.authorize_access_token()
    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()
    user = User(id=user_info['sub'], name=user_info['name'], email=user_info['email'])
    users[user.id] = user
    login_user(user)
    return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def fetch_news(query, page=1, page_size=20):
    params = {
        'q': query,
        'apiKey': '46d8e2a191654c13ba334d36510a3a9f',
        'page': page,
        'pageSize': page_size
    }
    response = requests.get('https://newsapi.org/v2/everything', params=params)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_bbc_news(page=1, page_size=20, sources='bbc-news'):
    params = {
        'apiKey': '46d8e2a191654c13ba334d36510a3a9f',
        'page': page,
        'pageSize': page_size,
        'sources': sources
    }
    response = requests.get('https://newsapi.org/v2/everything', params=params)
    if response.status_code == 200:
        return response.json()
    return None


@app.route('/home', methods=['GET', 'POST'])
@login_required
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
