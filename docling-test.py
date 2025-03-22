from docling.document_converter import DocumentConverter
import os

# Use a local relative path for the input file
source = "content\BFS_notespdf.pdf"  # replace with your local file path
converter = DocumentConverter()
result = converter.convert(source)
markdown_output = result.document.export_to_markdown()
print(markdown_output)

# Extract the base filename without the extension
base_filename = os.path.basename(source)
name_without_ext, _ = os.path.splitext(base_filename)
output_filename = f"{name_without_ext}_md.md"

# Ensure the /results directory exists
os.makedirs("results", exist_ok=True)

# Define the full output path and write the markdown content
output_file_path = os.path.join("results", output_filename)
with open(output_file_path, "w", encoding="utf-8") as f:
    f.write(markdown_output)

print(f"Markdown file saved to {output_file_path}")
