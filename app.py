from flask import Flask
from config import Config

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY


@app.route("/")
def home():
    return "Welcome to Skill Analyzer & Job Finder"


if __name__ == "__main__":
    app.run(debug=True)