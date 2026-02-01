from flask import Flask, render_template, request
from flask_cors import CORS
from pathlib import Path
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/callback')
def callback():
    code = request.args.get('code', '')
    html = '<html><head><title>OAuth Callback</title></head>'
    html += '<body style="font-family: Arial; text-align: center; padding: 50px;">'
    html += '<h1>Authorization Successful!</h1>'
    html += '<p>Your authorization code:</p>'
    html += '<code style="background: #f0f0f0; padding: 10px;">' + code + '</code>'
    html += '<p>You can close this window.</p>'
    html += '</body></html>'
    return html

@app.route('/api/health')
def health():
    return {"status": "ok", "app": "KK Style Automator v3.0"}

if __name__ == '__main__':
    Path('logs').mkdir(exist_ok=True)
    Path('output').mkdir(exist_ok=True)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
