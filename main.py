from flask import Flask, request

app = Flask(__name__)

@app.route("/variants")
def variant_api():
    pass

if __name__ == '__main__':
    app.run("127.0.0.1", 8000)