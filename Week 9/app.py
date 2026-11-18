from flask import Flask
from blueprint.api_v1 import bp as v1_bp
from blueprint.api_v2 import bp as v2_bp

app = Flask(__name__)
app.json.ensure_ascii = False   # để tiếng Việt không bị escape thành \u...

app.register_blueprint(v1_bp, url_prefix="/api/v1/users")
app.register_blueprint(v2_bp, url_prefix="/api/v2/users")

if __name__ == "__main__":
    app.run(debug=True)