import logging
from abc import ABC, abstractmethod

from openai import OpenAI
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt, wait_random_exponential

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class BaseEmbeddingModel(ABC):
    @abstractmethod
    def create_embedding(self, text):
        pass


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, model="text-embedding-ada-002"):
        self.client = OpenAI()
        self.model = model

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def create_embedding(self, text):
        text = text.replace("\n", " ")
        return (
            self.client.embeddings.create(input=[text], model=self.model)
            .data[0]
            .embedding
        )


class SBertEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, model_name="sentence-transformers/multi-qa-mpnet-base-cos-v1"):
        self.model = SentenceTransformer(model_name)

    def create_embedding(self, text):
        return self.model.encode(text)

from clova_interface import BaseClovaInterface
class ClovaEmbeddingModel(BaseClovaInterface, BaseEmbeddingModel):
    def __init__(self):
        super().__init__()
    
    def create_embedding(self, text):
        resp = self.embed_text(text, embedding_type="clir-sts-dolphin")
        if resp=="Error":
            raise Exception("Embedding error occured")
        else:
            return resp['embedding']

from FlagEmbedding import BGEM3FlagModel
class BGEM3EmbeddingModel(BaseEmbeddingModel):
    def __init__(self):
        self.model = BGEM3FlagModel('BAAI/bge-m3',  use_fp16=True) 
    
    def create_embedding(self, text):
        return self.model.encode(text)['dense_vecs']