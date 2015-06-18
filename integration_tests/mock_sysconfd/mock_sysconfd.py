from flask import Flask, request

app = Flask(__name__)


@app.route("/exec_request_handlers", methods=["GET", "POST"])
def exec_request_handlers():
    print request.method, request.url, request.data
    return ''


@app.route("/delete_voicemail", methods=["GET", "POST"])
def delete_voicemail():
    print request.method, request.url, request.data
    return ''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8668)
