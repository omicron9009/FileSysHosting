from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import shutil

app = Flask(__name__)

# Set the root directory for file storage
ROOT_DIR = ROOT_DIR = os.path.abspath("root_folder")
ROOT_DIR = "C:\\Users\\jadit\\OneDrive\\Desktop\\SIT\\SITnovate\\RepoManager"
# Ensure the root directory exists
if not os.path.exists(ROOT_DIR):
    os.makedirs(ROOT_DIR)

@app.route("/")
def home():
    """ Serve the main HTML page """
    return render_template("index.html")

@app.route("/list", methods=["GET"])
def list_files():
    """ List all files and directories in the given path """
    path = request.args.get("path", "")
    abs_path = os.path.join(ROOT_DIR, path)

    if not os.path.exists(abs_path):
        return jsonify({"error": "Path does not exist"}), 404

    items = []
    for item in os.listdir(abs_path):
        item_path = os.path.join(abs_path, item)
        items.append({
            "name": item,
            "is_directory": os.path.isdir(item_path),
            "path": os.path.relpath(item_path, ROOT_DIR)
        })

    return jsonify(items)

@app.route("/create", methods=["POST"])
def create_item():
    """ Create a new file or directory """
    data = request.json
    name = data.get("name")
    item_type = data.get("type")  # "file" or "directory"
    path = data.get("path", "")

    if not name or not item_type:
        return jsonify({"error": "Name and type are required"}), 400

    abs_path = os.path.join(ROOT_DIR, path, name)

    if os.path.exists(abs_path):
        return jsonify({"error": "File or directory already exists"}), 400

    try:
        if item_type == "directory":
            os.makedirs(abs_path)
        elif item_type == "file":
            with open(abs_path, "w") as f:
                f.write("")  # Create an empty file
        else:
            return jsonify({"error": "Invalid type"}), 400

        return jsonify({"message": f"{item_type} created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete", methods=["POST"])
def delete_item():
    """ Delete a file or directory """
    data = request.json
    path = data.get("path")

    if not path:
        return jsonify({"error": "Path is required"}), 400

    abs_path = os.path.join(ROOT_DIR, path)

    if not os.path.exists(abs_path):
        return jsonify({"error": "File or directory does not exist"}), 404

    try:
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)  # Delete directory and contents
        else:
            os.remove(abs_path)  # Delete file

        return jsonify({"message": "Deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/rename", methods=["POST"])
def rename_item():
    """ Rename a file or directory """
    data = request.json
    old_path = data.get("old_path")
    new_name = data.get("new_name")

    if not old_path or not new_name:
        return jsonify({"error": "Old path and new name are required"}), 400

    old_abs_path = os.path.join(ROOT_DIR, old_path)
    new_abs_path = os.path.join(os.path.dirname(old_abs_path), new_name)

    if not os.path.exists(old_abs_path):
        return jsonify({"error": "File or directory does not exist"}), 404

    if os.path.exists(new_abs_path):
        return jsonify({"error": "A file or directory with the new name already exists"}), 400

    try:
        os.rename(old_abs_path, new_abs_path)
        return jsonify({"message": "Renamed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/read", methods=["GET"])
def read_file():
    """ Read the content of a file """
    path = request.args.get("path")

    if not path:
        return jsonify({"error": "Path is required"}), 400

    abs_path = os.path.join(ROOT_DIR, path)

    if not os.path.exists(abs_path) or os.path.isdir(abs_path):
        return jsonify({"error": "File does not exist or is a directory"}), 404

    try:
        with open(abs_path, "r") as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/write", methods=["POST"])
def write_file():
    """ Write content to a file """
    data = request.json
    path = data.get("path")
    content = data.get("content", "")

    if not path:
        return jsonify({"error": "Path is required"}), 400

    abs_path = os.path.join(ROOT_DIR, path)

    if not os.path.exists(abs_path) or os.path.isdir(abs_path):
        return jsonify({"error": "File does not exist or is a directory"}), 404

    try:
        with open(abs_path, "w") as f:
            f.write(content)
        return jsonify({"message": "File updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download_file():
    """ Download a file """

    path = request.args.get("path")
    print(path)
    if not path:
        return jsonify({"error": "Path is required"}), 400

    abs_path = os.path.join(ROOT_DIR, path)

    if not os.path.exists(abs_path) or os.path.isdir(abs_path):
        return jsonify({"error": "File does not exist or is a directory"}), 404

    return send_from_directory(ROOT_DIR, path, as_attachment=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    """ Upload a file to the server """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    path = request.form.get("path", "")

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    save_path = os.path.join(ROOT_DIR, path, file.filename)

    try:
        file.save(save_path)
        return jsonify({"message": "File uploaded successfully", "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="192.168.0.129", port=5000, debug=True)
