import os
import time
import re
import base64
import requests
import uuid
import argparse
import logging
from datetime import datetime
from tqdm import tqdm

import moondream as md
from PIL import Image
from dotenv import load_dotenv

# Qdrant and embedding imports
import qdrant_client
from qdrant_client import models, QdrantClient
from qdrant_client.http import models as qdrant_models
import tiktoken
import markdown  # if needed for further markdown processing
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer  # For embeddings

# LangChain text splitters
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# ------------------------------
# Load environment variables
load_dotenv()
# ------------------------------

# ----- CONFIGURATION -----
# Datalab API
DATALAB_API_KEY = os.environ.get("DATALAB_API_KEY")
DATALAB_MARKER_URL = os.environ.get("DATALAB_MARKER_URL")

# Moondream API key is loaded from .env
MOONDREAM_API_KEY = os.environ.get("MOONDREAM_API_KEY")
qdrant_url = os.environ.get("QDRANT_URL")
qdrant_api_key = os.environ.get("QDRANT_API_KEY")

# Directories for document processing
INPUT_DIR = "input_dir"  # where your PDFs are stored
RESULTS_DIR = "results"  # intermediate results (images, etc.)
FINAL_RESULTS_DIR = "final_results"  # final markdown files

# Polling parameters for Datalab API
MAX_POLLS = 300
POLL_INTERVAL = 3  # seconds

# Initialize Moondream API model
model = md.vl(api_key=MOONDREAM_API_KEY)

# ------------------------------
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ------------------------------
# Datalab/Moondream processing functions
def generate_description_for_image(image_path, figure_caption=""):
    """
    Load an image, encode it with Moondream, and get a description.
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
    """Call the Datalab marker API to convert a document into markdown and extract images."""
    with open(file_path, "rb") as f:
        files = {
            "file": (os.path.basename(file_path), f, "application/pdf")  # Adjust mime type if needed
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
    """Save base64-encoded images from the API response to disk."""
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
    Replace image placeholders with Moondream-generated descriptions.
    For each image markdown (e.g., ![](_page_0_Figure_14.jpeg)), look for a caption 
    (the next non-empty line starting with "Figure"). Then replace with:
       - A third-level heading (###) for the figure title (or "No Title" if missing)
       - A fourth-level heading (#### Image Description:) with the generated description.
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
            # Look ahead for a caption: the next non-empty line starting with "Figure"
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip().startswith("Figure"):
                caption = lines[j].strip()
                i = j  # Skip the caption line from output
            # Look up image path
            image_path = saved_images.get(image_filename)
            if image_path:
                try:
                    description = generate_description_for_image(image_path, caption)
                except Exception as e:
                    description = f"Error generating description: {e}"
            else:
                description = "Image file not found."
            title_text = caption if caption else "No Title"
            block_text = f"### {title_text}\n\n#### Image Description:\n{description}\n"
            processed_lines.append(block_text)
        else:
            processed_lines.append(line)
        i += 1
    return "\n".join(processed_lines)

def process_documents():
    """
    Process each file in INPUT_DIR:
      - Convert the document using Datalab marker API
      - Save extracted images
      - Process markdown (replace image blocks)
      - Save final markdown into FINAL_RESULTS_DIR with filename starting with "final_"
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FINAL_RESULTS_DIR, exist_ok=True)
    
    for filename in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, filename)
        if os.path.isfile(file_path):
            logger.info(f"Processing {filename}...")
            try:
                data = call_datalab_marker(file_path)
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                continue
            
            markdown_text = data.get("markdown", "")
            images_dict = data.get("images", {})
            base_name, _ = os.path.splitext(filename)
            images_folder = os.path.join(RESULTS_DIR, f"{base_name}_images")
            saved_images = save_extracted_images(images_dict, images_folder)
            logger.info(f"Saved {len(saved_images)} images to {images_folder}")
            
            final_markdown = process_markdown(markdown_text, saved_images)
            output_markdown_path = os.path.join(FINAL_RESULTS_DIR, f"final_{base_name}.md")
            with open(output_markdown_path, "w", encoding="utf-8") as md_file:
                md_file.write(final_markdown)
            logger.info(f"Final markdown for {filename} saved to {output_markdown_path}\n")

# ------------------------------
# Hierarchical Chunking and Qdrant Upsertion
# Constants for chunking
EMBEDDING_DIMENSIONS = 1024  
TOKENIZER = tiktoken.get_encoding("cl100k_base")  # For token counting

class HierarchicalChunker:
    def __init__(
        self,
        embedding_model: SentenceTransformer,
        qdrant_client: QdrantClient,
        collection_name: str,
        session_id: str,
        max_chunk_size: int = 1024,
        chunk_overlap: int = 200,
        top_level_max_size: int = 3072,
    ):
        self.embedding_model = embedding_model
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.session_id = session_id
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_level_max_size = top_level_max_size

        self._ensure_collection()

    def _ensure_collection(self):
        """Create the collection if it doesn't exist."""
        try:
            _ = self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} already exists")
        except Exception:
            logger.info(f"Creating collection {self.collection_name}")
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=EMBEDDING_DIMENSIONS,
                    distance=qdrant_models.Distance.COSINE,
                ),
                metadata_config=qdrant_models.MetadataConfig(
                    indexed_fields=["session_id", "document_id", "chunk_type", "heading_path"]
                )
            )

    def _count_tokens(self, text: str) -> int:
        return len(TOKENIZER.encode(text))

    def _get_embedding(self, text: str):
        try:
            embedding = self.embedding_model.encode(text)
            if hasattr(embedding, "tolist"):
                embedding = embedding.tolist()
            if len(embedding) != EMBEDDING_DIMENSIONS:
                logger.error(f"Unexpected embedding dimension: {len(embedding)}. Expected: {EMBEDDING_DIMENSIONS}")
                return None
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None

    def process_document(self, filepath: str, document_id: str = None):
        document_id = document_id or str(uuid.uuid4())
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False
        )
        header_docs = markdown_splitter.split_text(content)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.max_chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        all_chunks = []
        for doc in header_docs:
            splits = text_splitter.split_text(doc.page_content)
            for s in splits:
                chunk = {
                    "text": s,
                    "metadata": {
                        **doc.metadata,
                        "document_id": document_id,
                        "filepath": filepath
                    }
                }
                all_chunks.append(chunk)

        document_chunk = {
            "text": content[:2048],
            "metadata": {
                "document_id": document_id,
                "session_id": self.session_id,
                "filepath": filepath,
                "chunk_type": "document",
                "heading_path": os.path.basename(filepath)
            }
        }
        all_chunks.append(document_chunk)
        return all_chunks

    def index_chunks(self, chunks):
        points = []
        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk["text"])
            if embedding is None:
                logger.error(f"Skipping chunk {i} due to embedding error")
                continue
            point = qdrant_models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={**chunk["metadata"], "text": chunk["text"]}
            )
            points.append(point)
        batch_size = 100
        total_indexed = 0
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            total_indexed += len(batch)
            logger.info(f"Indexed {len(batch)} chunks")
        return total_indexed

    def process_directory(self, directory_path: str):
        total_points = 0
        file_count = 0
        for root, _, files in os.walk(directory_path):
            markdown_files = [f for f in files if f.endswith('.md')]
            for file in tqdm(markdown_files, desc="Processing markdown files"):
                filepath = os.path.join(root, file)
                logger.info(f"Processing {filepath}")
                document_id = f"{self.session_id}_{os.path.relpath(filepath, directory_path)}"
                chunks = self.process_document(filepath, document_id)
                num_points = self.index_chunks(chunks)
                total_points += num_points
                file_count += 1
                logger.info(f"Finished processing {filepath}. Indexed {num_points} points.")
        logger.info(f"Finished processing directory '{directory_path}'. Total files processed: {file_count}. Total points indexed: {total_points}.")

# ------------------------------
# Main execution
def main():
    # Step 1: Process documents via Datalab/Moondream pipeline
    process_documents()

    # Step 2: Hierarchical chunking & upsertion into Qdrant
    # Qdrant configuration (update these as needed)
    
    collection_name = "qgen_md"
    session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    max_chunk_size = 1024
    chunk_overlap = 200
    top_level_max_size = 2048
    # Use the final markdown files directory as input for chunking/upsertion
    input_dir_for_chunking = FINAL_RESULTS_DIR

    logger.info(f"Using session ID: {session_id}")

    # Initialize SentenceTransformer embedding model
    embedding_model = SentenceTransformer("dunzhang/stella_en_1.5B_v5", trust_remote_code=True).to("cpu")

    # Initialize Qdrant client
    qdrant_client_instance = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key
    )

    # Create HierarchicalChunker and process the directory
    chunker = HierarchicalChunker(
        embedding_model=embedding_model,
        qdrant_client=qdrant_client_instance,
        collection_name=collection_name,
        session_id=session_id,
        max_chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
        top_level_max_size=top_level_max_size
    )
    chunker.process_directory(input_dir_for_chunking)
    logger.info("Indexing complete.")

if __name__ == "__main__":
    main()
