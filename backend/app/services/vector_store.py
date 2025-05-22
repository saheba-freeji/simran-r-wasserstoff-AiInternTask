from typing import List, Dict, Any
import numpy as np
import faiss
import os
import json
import pickle
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, persist_directory: str = "data/vectorstore"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize sentence transformer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize or load FAISS index
        self.index_path = os.path.join(persist_directory, "faiss.index")
        self.metadata_path = os.path.join(persist_directory, "metadata.pkl")
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(384)  # 384 is the dimension of the embeddings
            self.metadata = {}
    
    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Add a document to the vector store"""
        # Get embedding
        embedding = self.model.encode([content])[0]
        
        # Add to FAISS index
        self.index.add(np.array([embedding]).astype('float32'))
        
        # Store metadata
        self.metadata[doc_id] = {
            "metadata": metadata,
            "index": self.index.ntotal - 1
        }
        
        # Save to disk
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        # Get query embedding
        query_vector = self.model.encode([query])[0]
        
        # Search in FAISS
        distances, indices = self.index.search(
            np.array([query_vector]).astype('float32'), 
            k=n_results
        )
        
        # Get results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            # Find document ID for this index
            doc_id = None
            doc_metadata = None
            for id_, data in self.metadata.items():
                if data["index"] == idx:
                    doc_id = id_
                    doc_metadata = data["metadata"]
                    break
            
            if doc_id:
                results.append({
                    "id": doc_id,
                    "metadata": doc_metadata,
                    "distance": float(distance)
                })
        
        return results
