import os
import torch
from collections import defaultdict
import numpy as np
from torch import cuda
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from transformers import DPRReader, GPT2LMHeadModel, RagRetriever, RagModel, RagSequenceForGeneration

BATCH_SIZE = 8

embed_model_id = 'sentence-transformers/all-MiniLM-l6-v2'
device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'
embed_model = HuggingFaceEmbeddings(
    model_name=embed_model_id,
    model_kwargs={'device': device},
    encode_kwargs={'device': device, 'batch_size': BATCH_SIZE}
)

retriever = DPRReader.from_pretrained("facebook/dpr-reader-single-nq")
retriever.to(device)
retriever.eval()

generator_model = GPT2LMHeadModel.from_pretrained("gpt2")
generator_model.to(device)
generator_model.eval()

rag_retriever = RagRetriever(
    retriever=retriever,
    generator=generator_model
)

rag_model = RagModel(
    retriever=rag_retriever,
    generator=generator_model
)
rag_model.to(device)
rag_model.eval()

rag_sequence_generator = RagSequenceForGeneration(
    model=rag_model,
    generator=generator_model,
    retriever=retriever
)
rag_sequence_generator.to(device)
rag_sequence_generator.eval()

question = "What is my clinical history?"
context = "Jacklynn is a 50 year old white female patient."
output = rag_sequence_generator(
    question,
    context,
    max_length=500,  
    num_return_sequences=1
)

print(output[0]["generated_text"])
