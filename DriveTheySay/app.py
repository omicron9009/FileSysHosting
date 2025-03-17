from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './root_directory'
app.secret_key = 'supersecretkey'

# ✅ List files and folders
@app.route('/', defaults={'folder_path': ''}, strict_slashes=False)
@app.route('/folder/<path:folder_path>', strict_slashes=False)
def index(folder_path=''):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_path)
    if not os.path.exists(folder):
        flash('Folder not found!', 'error')
        return redirect(url_for('index'))

    items = sorted(os.listdir(folder))
    return render_template('index.html', items=items, current_path=folder_path)

# ✅ Upload file
@app.route('/upload', defaults={'folder_path': ''}, methods=['POST'], strict_slashes=False)
@app.route('/upload/<path:folder_path>', methods=['POST'], strict_slashes=False)
def upload_file(folder_path=''):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_path)
    if 'file' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('index', folder_path=folder_path))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('index', folder_path=folder_path))

    try:
        file.save(os.path.join(folder, file.filename))
        flash(f'File "{file.filename}" uploaded successfully!', 'success')
    except Exception as e:
        flash(f'Failed to upload file: {e}', 'error')

    return redirect(url_for('index', folder_path=folder_path))

# ✅ Create folder (optional path handling)
@app.route('/create_folder', defaults={'folder_path': ''}, methods=['POST'], strict_slashes=False)
@app.route('/create_folder/<path:folder_path>', methods=['POST'], strict_slashes=False)
def create_folder(folder_path=''):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_path)
    folder_name = request.form.get('folder_name')
    new_folder = os.path.join(folder, folder_name)

    if not os.path.exists(new_folder):
        try:
            os.makedirs(new_folder)
            flash(f'Folder "{folder_name}" created!', 'success')
        except Exception as e:
            flash(f'Failed to create folder: {e}', 'error')
    else:
        flash('Folder already exists!', 'warning')

    return redirect(url_for('index', folder_path=folder_path))

# ✅ Delete file or folder
@app.route('/delete/<path:item_path>', methods=['POST'], strict_slashes=False)
def delete_item(item_path):
    path = os.path.join(app.config['UPLOAD_FOLDER'], item_path)
    if os.path.exists(path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            flash(f'"{os.path.basename(path)}" deleted!', 'success')
        except Exception as e:
            flash(f'Failed to delete: {e}', 'error')
    else:
        flash('Item not found!', 'error')

    parent_folder = os.path.dirname(item_path)
    return redirect(url_for('index', folder_path=parent_folder))

# ✅ Rename file or folder
@app.route('/rename/<path:item_path>', methods=['POST'], strict_slashes=False)
def rename_item(item_path):
    old_path = os.path.join(app.config['UPLOAD_FOLDER'], item_path)
    new_name = request.form.get('new_name')
    new_path = os.path.join(os.path.dirname(old_path), new_name)

    if os.path.exists(old_path):
        try:
            os.rename(old_path, new_path)
            flash(f'Renamed to "{new_name}"!', 'success')
        except Exception as e:
            flash(f'Failed to rename: {e}', 'error')
    else:
        flash('Item not found!', 'error')

    parent_folder = os.path.dirname(item_path)
    return redirect(url_for('index', folder_path=parent_folder))

# ✅ Download file or folder
@app.route('/download/<path:item_path>', strict_slashes=False)
def download_item(item_path):
    path = os.path.join(app.config['UPLOAD_FOLDER'], item_path)
    if not os.path.exists(path):
        flash('Item not found!', 'error')
        return redirect(url_for('index', folder_path=os.path.dirname(item_path)))

    try:
        if os.path.isdir(path):
            shutil.make_archive(path, 'zip', path)
            path += '.zip'
        return send_from_directory(os.path.dirname(path), os.path.basename(path), as_attachment=True)
    except Exception as e:
        flash(f'Failed to download: {e}', 'error')
        return redirect(url_for('index', folder_path=os.path.dirname(item_path)))

# ✅ Search
@app.route('/search', methods=['GET'], strict_slashes=False)
def search():
    query = request.args.get('query', '')
    results = []
    base_dir = app.config['UPLOAD_FOLDER']

    if query:
        for root, dirs, files in os.walk(base_dir):
            for name in dirs + files:
                if query.lower() in name.lower():
                    relative_path = os.path.relpath(os.path.join(root, name), base_dir)
                    results.append(relative_path)

    if not results:
        flash('No results found!', 'info')

    return render_template('search_results.html', results=results, query=query)

# ✅ Create root directory if not present
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
