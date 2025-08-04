from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.utils import extract_text, save_file_from_url
from typing import List
import logging
import time
import os
import asyncio
from app.services.vector_store_service import process_and_store_document
from app.services.agent import pdf_ai_expert
from app.services.rag import answer_query
from app.utils import compute_sha256
from app.db.mongo import file_collection

hackrx_router = APIRouter()

class HackRxRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

@hackrx_router.post('/hackrx/run')
async def run_hackrx(
    payload: HackRxRequest,
    # token: str = Depends(verify_token)
):
    try:
        start_time = time.monotonic()
        logging.info(f"Input: {payload}")

        filepath, original_filename = await save_file_from_url(payload.documents)

        before_hash = time.monotonic()
        file_hash = await compute_sha256(filepath)
        after_hash = time.monotonic()
        
        logging.info(f"Time taken to hash: {(after_hash-before_hash):.2f} seconds")

        existing = await file_collection.find_one({"hash": file_hash})
        if existing:
            logging.info(f"File already processed: {existing['filename']}")
            filename = existing['filename']
        else:
            text = extract_text(filepath)
            await process_and_store_document(text, original_filename)
            await file_collection.insert_one({"hash": file_hash, "filename": original_filename})
            filename=original_filename
            logging.info("File Processed")

        
        # filename=original_filename

        # text = extract_text(filepath)
        # await process_and_store_document(text, original_filename)

        response = {"answers": []}
        response['answers'] = await asyncio.gather(*[
            answer_query(question, filename) for question in payload.questions
        ])
 
        logging.info(f"response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during processing.")
    
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            
        end_time = time.monotonic()
        duration = end_time - start_time
        logging.info(f"⏱️ Total response time: {duration:.2f} seconds")
