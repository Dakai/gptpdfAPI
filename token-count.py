from token_count import TokenCount
import base64

from PIL import Image
import io
import base64


def compress_image(image_path, max_size):
    image = Image.open(image_path)
    width, height = image.size
    quality = 90  # Start with a high quality
    data_url = None

    while True:
        # Create a BytesIO object to save the image
        buffered = io.BytesIO()
        # Save the image as JPEG
        image.save(buffered, format="JPEG", quality=quality)
        data_url = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Check the size of the data URL
        if len(data_url) < max_size:
            break

        # Adjust quality or dimensions
        if quality > 10:  # Prevent too low quality
            quality -= 10
        else:
            width = int(width * 0.9)
            height = int(height * 0.9)
            image = image.resize((width, height), Image.ANTIALIAS)

    return f"data:image/jpeg;base64,{data_url}"


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# cli command to receive the image Path


# Path to your image
# image_path = "./Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
image_path = "./0_0.png"

# Getting the base64 string
# base64_image = encode_image(image_path)

compressed_image = compress_image(image_path, 262144)  # 262144 bytes = 256KB
# token_count = TokenCount(base64_image)

tc = TokenCount(model_name="gpt-3.5-turbo")
tokens = tc.num_tokens_from_string(compressed_image)
print(f"Tokens in the string: {tokens}")
