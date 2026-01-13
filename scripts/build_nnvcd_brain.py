import pandas as pd
import requests
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# 1. CONFIGURATION - The "Source of Truth"
HDX_URL = "https://data.humdata.org/dataset/nigeria-acled-conflict-data"
# Note: In a real agentic workflow, the agent would scrape the page to find the 
# latest weekly CSV download link. Here is the logic:
CSV_URL = "https://export.acleddata.com/api/read/csv?limit=0&country=Nigeria"  # Example API endpoint

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.beads', 'brain_data')
INDEX_PATH = os.path.join(OUTPUT_DIR, "nnvcd_acled_brain.index")
MAP_PATH = os.path.join(OUTPUT_DIR, "nnvcd_knowledge_map.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_nnvcd_brain():
    print("--- Phase 1: Ingesting ACLED Knowledge ---")
    # Download the dataset
    try:
        df = pd.read_csv(CSV_URL)
    except Exception as e:
        print(f"Error downloading data: {e}")
        return
    
    # 2. THE "BEAD" TRANSFORMATION (Cleaning & Normalization)
    # We combine columns into a single "Contextual String" for the AI to read
    df['brain_input'] = df.apply(lambda x: 
        f"Event: {x['event_type']} ({x['sub_event_type']}) in {x['location']}, {x['admin1']}. "
        f"Actors: {x['actor1']} vs {x.get('actor2', 'N/A')}. "
        f"Fatalities: {x['fatalities']}. Notes: {x.get('notes', 'N/A')}", axis=1)

    print(f"Processed {len(df)} historical conflict events.")

    # 3. VECTORIZATION (Generating the Skillset)
    print("--- Phase 2: Generating Vector Embeddings ---")
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and fast
    embeddings = model.encode(df['brain_input'].tolist(), show_progress_bar=True)

    # 4. INDEXING (Creating the Working Memory)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    # Save the 'Brain' for the App to use
    faiss.write_index(index, INDEX_PATH)
    df[['event_id_cnty', 'brain_input']].to_csv(MAP_PATH, index=False)
    
    print(f"Success: NNVCD Brain is now trained with ACLED patterns. Index saved at {INDEX_PATH}")

if __name__ == "__main__":
    build_nnvcd_brain()
