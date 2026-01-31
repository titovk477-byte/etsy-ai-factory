from flask import Flask, render_template
from flask_cors import CORS
from pathlib import Path
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return {"status": "ok", "app": "EtsyAIFactory v3.0"}

if __name__ == '__main__':
    Path('logs').mkdir(exist_ok=True)
    Path('output').mkdir(exist_ok=True)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
