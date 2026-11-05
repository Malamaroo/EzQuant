from flask import Flask, jsonify, request, render_template
from pathlib import Path

backend_dir = Path(__file__).parent
app_dir = backend_dir.parent
frontend_dir = app_dir / 'FrontEnd'

app = Flask(
    __name__,
    template_folder= str(frontend_dir),
    static_folder= str(frontend_dir),
    static_url_path= '/static'
)
    

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=8000, debug=True)
