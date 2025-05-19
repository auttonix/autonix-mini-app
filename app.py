from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/wallet')
def wallet():
    return render_template('wallet.html')

@app.route('/invest')
def invest():
    return render_template('invest.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

def start_app_bot():
    """Starts the bot and the Flask app."""
    print("🚀 Starting the App Bot...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)