#!/usr/bin/env python3
from flask import Flask, request, jsonify
import shutil
import datetime as dt
import os
import sys
import base64
import re
from gptpdf import parse_pdf

app = Flask(__name__)


def encode_image_to_base64(image_path):
    """Encode a PNG image to a Base64 string."""
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_encoded_data = base64.b64encode(image_data)
        return base64_encoded_data.decode("utf-8")


def replace_png_with_base64(markdown_file_path, output_file_path):
    """Replace PNG image references in a Markdown file with Base64 strings."""
    # Read the content of the markdown file
    with open(markdown_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Regular expression to find PNG images
    png_pattern = r"!\[.*?\]\((.*?\.png)\)"

    def replace_with_base64(match):
        image_path = match.group(1)

        # Check if the image file exists
        if os.path.exists(image_path):
            base64_string = encode_image_to_base64(image_path)
            return f"![Image]({base64_string})"
        else:
            print(f"Warning: File {image_path} does not exist.")
            return match.group(0)  # Return the original markdown if file not found

    # Replace all PNG image references with Base64 strings
    updated_content = re.sub(png_pattern, replace_with_base64, content)

    # Write the updated content to the output file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(updated_content)


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
    # print(api_key)

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
            api_key=api_key,
        )
        return jsonify({"markdown": file.filename}), 200
        # return jsonify({"markdown": markdown_content}), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500
        sys.exit(1)

    # remove the folder
    # shutil.rmtree(upload_folder)

    # return jsonify({"filename": file.filename}), 200


if __name__ == "__main__":
    app.run(debug=True)
