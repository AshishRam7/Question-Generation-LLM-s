import os
import time
import re
import base64
import requests
import moondream as md
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

DATALAB_API_KEY = os.environ.get("DATALAB_API_KEY")
DATALAB_MARKER_URL = os.environ.get("DATALAB_MARKER_URL")
MOONDREAM_API_KEY = os.environ.get("MOONDREAM_API_KEY")

# Directories
INPUT_DIR = "input_dir"
RESULTS_DIR = "results"
FINAL_RESULTS_DIR = "final_results"

# Polling parameters for Datalab API
MAX_POLLS = 300
POLL_INTERVAL = 3  # seconds

# Moondream API model configuration
model = md.vl(api_key=MOONDREAM_API_KEY)

def generate_description_for_image(image_path, figure_caption=""):
    """
    Load an image from the provided path, encode it using the Moondream API,
    and query for a description that is based on the provided figure caption.
    """
    image = Image.open(image_path)
    encoded_image = model.encode_image(image)
    query_text = (
        f"Describe the key technical findings in this figure/visualization "
        f"captioned: {figure_caption} using natural language. Illustrate and mention trends, "
        f"patterns, and numerical values that can be observed. Provide a scientific/academic styled short, "
        f"single paragraph summary that is highly insightful in context of the document."
    )
    response = model.query(encoded_image, query_text)
    description = response.get("answer", "No description available.")
    return description

def call_datalab_marker(file_path):
    """Call Datalab marker endpoint to convert the file into markdown and extract images."""
    with open(file_path, "rb") as f:
        files = {
            "file": (os.path.basename(file_path), f, "application/pdf")  # adjust mime type if needed
        }
        form_data = {
            "langs": (None, "English"),
            "force_ocr": (None, False),
            "paginate": (None, False),
            "output_format": (None, "markdown"),
            "use_llm": (None, False),
            "strip_existing_ocr": (None, False),
            "disable_image_extraction": (None, False)
        }
        headers = {"X-Api-Key": DATALAB_API_KEY}
        response = requests.post(DATALAB_MARKER_URL, files=files, data=form_data, headers=headers)
    data = response.json()
    if not data.get("success"):
        raise Exception(f"Datalab API error: {data.get('error')}")
    
    # Poll for the results
    check_url = data["request_check_url"]
    for _ in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        poll_resp = requests.get(check_url, headers=headers)
        poll_data = poll_resp.json()
        if poll_data.get("status") == "complete":
            return poll_data
    raise TimeoutError("Polling timed out waiting for Datalab processing to complete.")

def save_extracted_images(images_dict, images_folder):
    """Decode and save base64 encoded images to the images_folder.
       Returns a mapping from image filename to saved file path."""
    os.makedirs(images_folder, exist_ok=True)
    saved_files = {}
    for img_name, b64_data in images_dict.items():
        image_data = base64.b64decode(b64_data)
        image_path = os.path.join(images_folder, img_name)
        with open(image_path, "wb") as img_file:
            img_file.write(image_data)
        saved_files[img_name] = image_path
    return saved_files

def process_markdown(markdown_text, saved_images):
    """
    Process the markdown text to replace image placeholders with Moondream-generated descriptions.
    
    It scans the markdown line-by-line looking for image markdown lines (e.g.: 
       ![](_page_0_Figure_14.jpeg)
    If the next non-empty line starts with "Figure", that line is treated as the caption.
    Then the image markdown (and its caption, if present) is replaced by a block that contains:
      - A third-level heading (###) for the figure title.
      - A fourth-level heading (#### Image Description:) followed by the generated description.
    """
    lines = markdown_text.splitlines()
    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^!\[.*\]\((.*?)\)$", line.strip())
        if m:
            image_filename = m.group(1)
            caption = ""
            # Look ahead for a caption: next non-empty line starting with "Figure"
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip().startswith("Figure"):
                caption = lines[j].strip()
                i = j  # Skip the caption line
            # Look up the image file path from saved_images mapping
            image_path = saved_images.get(image_filename)
            if image_path:
                try:
                    description = generate_description_for_image(image_path, caption)
                except Exception as e:
                    description = f"Error generating description: {e}"
            else:
                description = "Image file not found."
            # Determine title: if caption exists, use it; else "No Title"
            title_text = caption if caption else ""
            # Format the replacement block with markdown headers:
            block_text = f"### {title_text}\n\n#### Figure Description:\n{description}\n"
            processed_lines.append(block_text)
        else:
            processed_lines.append(line)
        i += 1
    return "\n".join(processed_lines)

# ----- MAIN SCRIPT -----
def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FINAL_RESULTS_DIR, exist_ok=True)
    
    # Process each file in the input directory.
    for filename in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, filename)
        if os.path.isfile(file_path):
            print(f"Processing {filename}...")
            
            try:
                # Call Datalab marker API to convert the document to markdown
                data = call_datalab_marker(file_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
            
            # Extract markdown and images from the API response
            markdown_text = data.get("markdown", "")
            images_dict = data.get("images", {})
            
            # Create an images folder inside results for this file
            base_name, _ = os.path.splitext(filename)
            images_folder = os.path.join(RESULTS_DIR, f"{base_name}_images")
            saved_images = save_extracted_images(images_dict, images_folder)
            print(f"Saved {len(saved_images)} images to {images_folder}")
            
            # Process markdown: replace image placeholders with formatted Moondream descriptions.
            final_markdown = process_markdown(markdown_text, saved_images)
            
            # Save final markdown to final_results folder with file name starting with final_
            output_markdown_path = os.path.join(FINAL_RESULTS_DIR, f"final_{base_name}.md")
            with open(output_markdown_path, "w", encoding="utf-8") as md_file:
                md_file.write(final_markdown)
            print(f"Final markdown for {filename} saved to {output_markdown_path}\n")

if __name__ == "__main__":
    main()
