from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/healthz")
def healthz():
  return "ok", 200

if __name__ == "__main__":
  port = int(os.getenv("PORT", 8080))
  app.run(host="0.0.0.0", port=port)
