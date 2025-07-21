from sentence_transformers import SentenceTransformer
import numpy as np

EMBEDDING_MODEL_NAME = 'all-mpnet-base-v2'

class TextEmbedder:
    def __init__(self):
        """
        Initializes the TextEmbedder by loading the SentenceTransformer model.
        """
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def encode(self, text: str) -> np.ndarray:
        """
        Encodes a single string of text into a 768-dimension embedding.

        Args:
            text: The input string to encode.

        Returns:
            A numpy array of shape (768,) with dtype float32.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype('float32')