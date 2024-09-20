from flask import Flask, request, jsonify
import shutil
import datetime as dt
import os

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload_file():
    print("Request files:", request.files)  # Debugging line
    print("Request form:", request.form)  # Debugging line
    # check if the post request has the file part
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400

    file = request.files["file"]
    api_token = request.form.get("api_token")

    # check if the api_token is provided
    if not api_token:
        return jsonify({"error": "no api token provided"}), 400

    # if the user does not select a file, the browser submits an empty file without a filename
    if file.filename == "":
        return jsonify({"error": "no selected file"}), 400

    # check if the file is a PDF
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "only PDF files are allowed"}), 400

    # check if the file size is less than 50MB
    if len(file.read()) > 50 * 1024 * 1024:
        return jsonify({"error": "file size exceeds 50MB"}), 400

    # Reset file pointer to the beginning after reading its size
    file.seek(0)

    # save the file to the server
    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_folder = os.path.join(
        "upload", f"{timestamp}_{os.path.splitext(file.filename)[0]}"
    )
    print(upload_folder)
    os.makedirs(
        upload_folder, exist_ok=True
    )  # Create the directory if it doesn't exist
    file.save(os.path.join(upload_folder, file.filename))

    # remove the folder
    shutil.rmtree(upload_folder)

    return jsonify({"filename": file.filename}), 200


if __name__ == "__main__":
    app.run(debug=True)
