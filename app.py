from flask import Flask, request, jsonify
import shutil
import datetime as dt
import os
import sys
from gptpdf import parse_pdf

app = Flask(__name__)


def pdf_to_markdown(pdf_path, api_key, output_dir):
    # Parse the PDF
    content, image_paths = parse_pdf(
        pdf_path, output_dir=output_dir, api_key=api_key, model="gpt-4o-mini"
    )

    # Create markdown content
    markdown_content = f"# {os.path.splitext(os.path.basename(pdf_path))[0]}\n\n"
    markdown_content += content

    # Add image references if any
    # if image_paths:
    #    markdown_content += "\n\n## Images\n"
    #    for i, image_path in enumerate(image_paths, 1):
    #        markdown_content += f"\n![Image {i}]({image_path})\n"

    return markdown_content


@app.route("/upload", methods=["POST"])
def upload_file():
    api_key = os.environ.get("OPENAI_API_KEY")

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

    try:
        markdown_content = pdf_to_markdown(
            os.path.join(upload_folder, file.filename),
            output_dir=upload_folder,
            api_key=api_token,
            model="gpt-4o-mini",
        )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

    # remove the folder
    # shutil.rmtree(upload_folder)

    # return jsonify({"filename": file.filename}), 200
    return jsonify({"markdown": markdown_content}), 200


if __name__ == "__main__":
    app.run(debug=True)
