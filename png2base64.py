#!/usr/bin/env python3
import os
import sys
import base64
import re


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


# main function to be called from the command line
if __name__ == "__main__":
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    replace_png_with_base64(pdf_path, output_dir)
