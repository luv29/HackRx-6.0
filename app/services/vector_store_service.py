import os
import json
import fitz 
import asyncio
import logging
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from supabase import create_client, Client
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core import get_settings
settings = get_settings()

load_dotenv()

openai_client = AsyncOpenAI(
    api_key = settings.gemini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key
)

@dataclass
class ProcessedChunk:
    chunk_number: int
    title: str
    summary: str
    content: str
    embedding: List[float]
    source_file: str

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)

async def get_embedding(text: str) -> List[float]:
    try:
        response = await openai_client.embeddings.create(
            model="gemini-embedding-exp-03-07",
            dimensions=1536,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logging.error(f"Error getting embedding: {e}")
        return [0] * 1536

async def get_title_and_summary(chunk: str) -> Dict[str, str]:
    system_prompt = """You are an AI that extracts titles and summaries from documentation chunks.
    Return a JSON object with 'title' and 'summary' keys.
    For the title: If this seems like the start of a document, extract its title. If it's a middle chunk, derive a descriptive title.
    For the summary: Create a concise summary of the main points in this chunk.
    Keep both title and summary concise but informative."""

    try:
        response = await openai_client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Content:\n{chunk[:1000]}..."}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content

        parsed = json.loads(content)

        # If it's a list, just return the first item
        if isinstance(parsed, list):
            return parsed[0]
        return parsed

    except Exception as e:
        logging.error(f"Error getting title and summary: {e}")
        return {"title": "Error processing title", "summary": "Error processing summary"}

async def process_chunk(chunk: str, chunk_number: int, source_file: str) -> ProcessedChunk:
    extracted = await get_title_and_summary(chunk)
    embedding = await get_embedding(chunk)

    return ProcessedChunk(
        chunk_number=chunk_number,
        title=extracted["title"],
        summary=extracted["summary"],
        content=chunk,
        embedding=embedding,
        source_file=source_file
    )

async def insert_chunk(chunk: ProcessedChunk):
    try:
        data = {
            "chunk_number": chunk.chunk_number,
            "title": chunk.title,
            "summary": chunk.summary,
            "content": chunk.content,
            "embedding": chunk.embedding,
            "source_file": chunk.source_file
        }
        
        result = supabase.table("pdf_chunks").insert(data).execute()
        logging.info(f"Inserted chunk {chunk.chunk_number} from {chunk.source_file}")
        
        return result
    except Exception as e:
        logging.error(f"Error inserting chunk: {e}")
        return None

async def process_and_store_document(text: str, source_file: str):
    chunks = chunk_text(text)
    # for i, chunk in enumerate(chunks):
    #     pc = await process_chunk(chunk, i, source_file)
    #     await insert_chunk(pc)
    
    processed = await asyncio.gather(*[
        process_chunk(chunk, i, source_file) for i, chunk in enumerate(chunks)
    ])
    
    await asyncio.gather(*[insert_chunk(c) for c in processed])

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

async def main():
    pdf_path = "data/three.pdf"
    source_file = os.path.basename(pdf_path)

    text = extract_text_from_pdf(pdf_path)
    await process_and_store_document(text, source_file)

if __name__ == "__main__":
    asyncio.run(main())
