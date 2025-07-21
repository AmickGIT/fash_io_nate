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

def test_text_embedder():
    """
    Tests the TextEmbedder class by encoding a sample text
    and verifying the output embedding's properties.
    """
    print("Initializing TextEmbedder...")
    embedder = TextEmbedder()
    print("TextEmbedder initialized.")

    sample_text = "Green tops"
    print(f"\nEncoding text: '{sample_text}'")

    embedding = embedder.encode(sample_text)

    print(f"Embedding shape: {embedding.shape}")
    assert embedding.shape == (768,), f"Expected shape (768,), but got {embedding.shape}"

    print(f"Embedding dtype: {embedding.dtype}")
    assert embedding.dtype == np.float32, f"Expected dtype float32, but got {embedding.dtype}"

    print("Embedding (first 5 values):", embedding[:5])
    print("\nTest passed!")

if __name__ == "__main__":
    test_text_embedder()