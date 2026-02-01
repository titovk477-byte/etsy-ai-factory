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
    return f'''
    <html>
    <head><title>OAuth Callback</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>✅ Authorization Successful!</h1>
        <p>Your authorization code:</p>
        <code style="background: #f0f0f0; padding: 10px; display: block; margin: 20px;">{code}</code>
        <p>You can close this window.</p>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return {"status": "ok", "app": "KK Style Automator v3.0"}

if __name__ == '__main__':
    Path('logs').mkdir(exist_ok=True)
    Path('output').mkdir(exist_ok=True)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Шаг 4: Commit changes

### Шаг 5: Подожди 2-3 минуты (Render автоматически обновит)

---

### Проверь:
```
https://kk-style-app.onrender.com/callback
