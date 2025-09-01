# banglish_embedding.py
"""
Provides BanglishBertEmbedder for Bangla, Banglish, and English embeddings using csebuetnlp/banglishbert.
"""
from transformers import AutoModel, AutoTokenizer
from normalizer import normalize
import torch
import numpy as np

class BanglishBertEmbedder:
    def __init__(self, model_name="csebuetnlp/banglishbert", device=None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.model.eval()

    def embed(self, texts):
        """
        texts: list of str
        Returns: list of numpy arrays (embeddings)
        """
        if isinstance(texts, str):
            texts = [texts]
        embeddings = []
        with torch.no_grad():
            for text in texts:
                norm_text = normalize(text)
                inputs = self.tokenizer(norm_text, return_tensors="pt", truncation=True, max_length=256)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.model(**inputs)
                # Mean pooling over token embeddings (excluding special tokens)
                last_hidden = outputs.last_hidden_state.squeeze(0)
                attn_mask = inputs['attention_mask'].squeeze(0)
                valid_idx = attn_mask.nonzero(as_tuple=True)[0]
                if len(valid_idx) > 2:
                    # Exclude [CLS] and [SEP] tokens
                    valid_idx = valid_idx[1:-1]
                vecs = last_hidden[valid_idx]
                pooled = vecs.mean(dim=0).cpu().numpy()
                embeddings.append(pooled)
        return embeddings
