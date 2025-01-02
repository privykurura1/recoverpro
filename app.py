import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins (adjust for production)

# Define supported file extensions
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.flv']
DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.xls', '.ppt']

# Helper function to scan files
def scan_deleted_files(storage_path):
    """
    Scans the specified storage path for files with supported extensions.
    :param storage_path: Path to scan for files.
    :return: List of recovered file metadata.
    """
    recovered_files = []
    print(f"Scanning path: {storage_path}")  # Debugging

    if not os.path.exists(storage_path):
        print(f"Path does not exist: {storage_path}")  # Debugging
        return []

    for root, dirs, files in os.walk(storage_path):
        for file in files:
            if len(recovered_files) >= 50:
                break
            if any(file.endswith(ext) for ext in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + DOCUMENT_EXTENSIONS):
                file_path = os.path.join(root, file)
                try:
                    recovered_files.append({
                        "name": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path)
                    })
                except Exception as e:
                    print(f"Error accessing file {file}: {str(e)}")
    print(f"Found {len(recovered_files)} files.")
    return recovered_files


@app.route('/scan', methods=['GET'])
def scan_files():
    """
    API endpoint to scan files in a specified path.
    :return: JSON response with file metadata.
    """
    storage_path = request.args.get('path')
    if not storage_path:
        return jsonify({"error": "Storage path is required."}), 400

    if not os.path.exists(storage_path):
        return jsonify({"error": f"Path '{storage_path}' does not exist."}), 400

    files = scan_deleted_files(storage_path)
    return jsonify({"files": files})


@app.route('/recover', methods=['POST'])
def recover_file():
    """
    API endpoint to recover a specified file.
    :return: JSON response with recovery status.
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided."}), 400

    file_path = data.get('file_path')

    # Check if the file exists
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": f"File '{file_path}' does not exist."}), 400

    try:
        # Return the file path to the client (Android app will handle recovery)
        return jsonify({"status": "success", "file_path": file_path})

    except Exception as e:
        print(f"Error recovering file: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)  # Adjust port if needed
