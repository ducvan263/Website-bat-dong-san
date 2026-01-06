import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from models.Property import Property
from services.property_service import PropertyService

class EmbeddingService:
    # model = SentenceTransformer("intfloat/multilingual-e5-base")
    index = None
    ids = []

    @staticmethod
    def build_index():
        properties = Property.query.filter(
            Property.status.in_(["selling", "renting"])
        ).all()

        texts = [PropertyService.property_to_text(p) for p in properties]
        EmbeddingService.ids = [p.id for p in properties]

        embeddings = EmbeddingService.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True
        )

        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(np.array(embeddings))

        EmbeddingService.index = index

    @staticmethod
    def search(query, k=5):
        q_emb = EmbeddingService.model.encode(
            [query],
            normalize_embeddings=True
        )
        _, idx = EmbeddingService.index.search(np.array(q_emb), k)
        return [EmbeddingService.ids[i] for i in idx[0]]
