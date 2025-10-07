import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm

SCHEMA_FILE = Path("AE_Json_Schema.json")
COLLECTION_NAME = "ae_schema"
EMBED_MODEL = "all-MiniLM-L6-v2"

def extract_chunks(schema: dict):
    """
    Convert a large schema into semantically meaningful chunks.
    Groups elements by high-level type names or component definitions.
    """
    chunks = []

    def recurse(obj, prefix="root"):
        if isinstance(obj, dict):
            for k, v in obj.items():
                key_path = f"{prefix}.{k}"
                if isinstance(v, (dict, list)):
                    recurse(v, key_path)
                else:
                    chunks.append(f"{key_path}: {v}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                recurse(item, f"{prefix}[{i}]")
    
    if "elements_details" in schema:
        for name, details in schema["elements_details"].items():
            text = f"Schema element: {name}\nDetails:\n{json.dumps(details, indent=2)}"
            chunks.append(text)

    if "global_types" in schema:
        for t in schema["global_types"]:
            chunks.append(f"Global type: {t}")

    recurse(schema, "schema")
    return chunks


def main():
    print("Building ChromaDB index...")
    client = chromadb.PersistentClient(path="./chroma_db")

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(COLLECTION_NAME)
    model = SentenceTransformer(EMBED_MODEL)

    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    chunks = extract_chunks(schema)

    print(f"Extracted {len(chunks)} schema chunks, encoding...")
    embeddings = model.encode(chunks, batch_size=32, show_progress_bar=True)

    print("Indexing into ChromaDB...")
    for i in tqdm(range(0, len(chunks), 64), desc="Indexing Chunks"):
        batch = chunks[i:i + 64]
        collection.add(
            ids=[str(i + j) for j in range(len(batch))],
            embeddings=embeddings[i:i + len(batch)].tolist(),
            documents=batch
        )

    print(f"Indexed {len(chunks)} schema chunks into {COLLECTION_NAME}")

if __name__ == "__main__":
    main()
