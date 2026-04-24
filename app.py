import os
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)

# Render ke Environment Variables se key uthane ke liye
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_for_local')

oauth = OAuth(app)

# Discord Setup
discord = oauth.register(
    name='discord',
    client_id=os.environ.get('DISCORD_CLIENT_ID'),
    client_secret=os.environ.get('DISCORD_CLIENT_SECRET'),
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    api_base_url='https://discord.com/api/',
    client_kwargs={'scope': 'identify email'},
)

# Google Setup
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/')
def index():
    return "Welcome to SXM Store! <a href='/login/discord'>Discord Login</a> | <a href='/login/google'>Google Login</a>"

@app.route('/login/<name>')
def login(name):
    client = oauth.create_client(name)
    # _external=True hona zaroori hai Render ke liye
    redirect_uri = url_for('auth', name=name, _external=True)
    return client.authorize_redirect(redirect_uri)

@app.route('/auth/<name>')
def auth(name):
    client = oauth.create_client(name)
    token = client.authorize_access_token()
    
    if name == 'google':
        user = client.get('userinfo').json()
    else:
        user = client.get('users/@me').json()
        
    session['user'] = user
    return f"Hello {user.get('username') or user.get('name')}, login successful!"

if __name__ == '__main__':
    # Render port dynamically assign karta hai, isliye ye line compulsory hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
