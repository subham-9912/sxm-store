from flask import Flask, render_template, url_for, session, redirect
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = "SUBHAM_X_MOD_786"  # Isse aap change kar sakte hain
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
oauth = OAuth(app)

# --- DATABASE MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    avatar = db.Column(db.String(200))

# --- DISCORD OAUTH SETUP ---
discord = oauth.register(
    name='discord',
    client_id='1497147817288929400', # Aapki ID
    client_secret='yxo0WXWUz2WHwV2PCwYvlwYHxU7P5R_R', # Aapka Secret
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    api_base_url='https://discord.com/api/',
    client_kwargs={'scope': 'identify email'},
)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    # Orihost par ye automatically detect kar lega redirect URI
    redirect_uri = url_for('auth', _external=True)
    return discord.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = discord.authorize_access_token()
    resp = discord.get('users/@me')
    profile = resp.json()
    
    # User Profile Data
    d_id = profile['id']
    name = profile['username']
    email = profile.get('email')
    avatar_url = f"https://cdn.discordapp.com/avatars/{d_id}/{profile['avatar']}.png"

    # Database mein check karein agar user naya hai toh save karein
    user = User.query.filter_by(discord_id=d_id).first()
    if not user:
        user = User(discord_id=d_id, username=name, email=email, avatar=avatar_url)
        db.session.add(user)
        db.session.commit()

    # Session mein data save karein
    session['user'] = {
        'name': name,
        'id': d_id,
        'avatar': avatar_url
    }
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# --- START SERVER ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Render automatically port assign karta hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)