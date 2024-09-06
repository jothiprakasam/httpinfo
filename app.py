from flask import Flask, render_template, request
import socket
import ssl
from urllib.parse import urlparse

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form["url"]


        if not url.startswith("https://"):
            url = "https://" + url

        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        context = ssl.create_default_context()
        mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysock = context.wrap_socket(mysock, server_hostname=hostname)

        try:

            mysock.connect((hostname, 443))


            cmd = f'GET {parsed_url.path or "/"} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n'.encode()
            mysock.send(cmd)

            response = b""
            while True:
                data = mysock.recv(512)
                if len(data) < 1:
                    break
                response += data


            response_str = response.decode("utf-8", errors="ignore")
            headers, body = response_str.split("\r\n\r\n", 1)

        except Exception as e:
            return f"Error: {e}"

        finally:
            mysock.close()

        return render_template("index.html", headers=headers, body=body)
        # f"{body}"

    return render_template("index.html", headers=None, body=None)


if __name__ == "__main__":
    app.run(debug=True)
