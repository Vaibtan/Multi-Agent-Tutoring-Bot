#!/usr/bin/env python
import argparse
import concurrent.futures as cf
import json
import pathlib
import sys
from dataclasses import dataclass
from hashlib import sha256
from typing import List, Sequence

import redis
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_milvus import Milvus
from pydantic import BaseModel, Field, PositiveInt, validate_call
from tqdm import tqdm


class Settings(BaseModel):
    host: str = Field("localhost", description = "Milvus host")
    PORT: PositiveInt = 19530
    math_collection: str = Field("math_kb", description = "data for math")
    physics_collection: str = Field("physics_kb", description = "data for physics")
    embed_model: str = Field("all-mpnet-base-v2", description = "SBERT model")
    CHUNK_SIZE: PositiveInt = 500
    CHUNK_OVERLAP: PositiveInt = 75
    MAX_WORKERS: PositiveInt = 4
    redis_url: str | None = Field(None, description = "redis://host:port/0")
    REDIS_TTL_SEC: PositiveInt = 7 * 24 * 3600

config = Settings.model_validate({})

def sha(text: str) -> str: return sha256(text.encode("utf-8")).hexdigest()

@dataclass
class Embedder:
    # cached embed --> vector lookups via Redis
    model_name: str
    redis_client: redis.Redis | None = None
    TTL_SEC: int = 0
    
    def __post_init__(self) -> None:
        self.model = HuggingFaceEmbeddings(model_name = self.model_name)
        if self.redis_client is None and config.redis_url: \
            self.redis_client = redis.from_url(config.redis_url)
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        if not self.redis_client: return self.model.embed_documents(texts)
        vectors: List[List[float]] = []
        missing: list[int] = [] 
        keys = [f"{self.model_name}:{sha(t)}" for t in texts]
        raw = self.redis_client.mget(keys)
        for i, vec_json in enumerate(raw): # type: ignore
            if vec_json is None: missing.append(i); vectors.append([])
            else: vectors.append(json.loads(vec_json))
        if missing:
            new_vecs = self.model.embed_documents([texts[i] for i in missing])
            for idx, vec in zip(missing, new_vecs, strict = True):
                vectors[idx] = vec
                self.redis_client.set(keys[idx], json.dumps(vec), ex = self.TTL_SEC)
        return vectors

@validate_call
def split_pdf(pdf_path: pathlib.Path, subject: str) -> List[Document]:
    loader = PyMuPDFLoader(str(pdf_path))
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size = config.CHUNK_SIZE,\
        chunk_overlap = config.CHUNK_OVERLAP)
    chunks: List[Document] = splitter.split_documents(pages)
    for c in chunks: c.metadata.update({ "subject": subject, "file_name": pdf_path.name })
    return chunks

def parallel_load(pdf_files: Sequence[pathlib.Path], subject: str) -> List[Document]:
    all_docs: List[Document] = []
    with cf.ThreadPoolExecutor(max_workers = config.MAX_WORKERS) as pool:
        futures = {pool.submit(split_pdf, p, subject): p for p in pdf_files}
        for f in tqdm(cf.as_completed(futures), total = len(futures), desc = "Parsing PDFs"):
            all_docs.extend(f.result())
    return all_docs

def create_vector_store(collection: str) -> Milvus:
    embedder = HuggingFaceEmbeddings(model_name = config.embed_model)
    store = Milvus(collection_name = collection, \
        connection_args = { "host": config.host, "port": config.PORT }, \
            embedding_function = embedder, drop_old = True)
    return store

@validate_call
def build_knowledge_base(pdf_dir: pathlib.Path, subject: str) -> Milvus:
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {pdf_dir}")

    docs = parallel_load(pdf_files, subject)
    collection_name = config.math_collection if subject == "math" else config.physics_collection
    store = create_vector_store(collection_name)
    store.add_documents(docs)
    print(
        f"✅  {len(docs):,} chunks embedded → Milvus collection '{collection_name}' "
        f"@ {config.host}:{config.PORT}"
    )
    return store

def cli() -> None:
    parser = argparse.ArgumentParser(description="Build Math/Physics KB in Milvus.")
    parser.add_argument("--subject", choices = ("math", "physics"), \
        required = True, help  ="Target subject")
    parser.add_argument("--pdf-dir", type = pathlib.Path, required = True, \
        help = "Directory containing PDF files")
    args = parser.parse_args()
    build_knowledge_base(args.pdf_dir, args.subject)

if __name__ == "__main__":
    try: cli()
    except Exception as exc: print(f"❌  KB build failed: {exc}", file = sys.stderr); sys.exit(1)
