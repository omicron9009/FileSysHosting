import os
from flask import Flask, request, send_from_directory, render_template_string

# Configuration
NAS_STORAGE = "nas_storage"
os.makedirs(NAS_STORAGE, exist_ok=True)

app = Flask(__name__, static_folder=NAS_STORAGE)

# HTML template for uploading and accessing files
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NAS Simulator</title>
</head>
<body>
    <h1>NAS Simulator - File Hosting</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>
    <h2>Stored Files:</h2>
    <ul>
        {% for file in files %}
        <li><a href="/files/{{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/")
def index():
    files = os.listdir(NAS_STORAGE)
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part"
    
    file = request.files["file"]
    if file.filename == "":
        return "No selected file"

    file.save(os.path.join(NAS_STORAGE, file.filename))
    return "File uploaded successfully! <a href='/'>Go back</a>"

@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(NAS_STORAGE, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
