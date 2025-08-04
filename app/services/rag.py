from dotenv import load_dotenv
import logging

from app.utils import RAG_AGENT_SYSTEM_PROMPT
from app.services.vector_store_service import (
    supabase,
    openai_client,
    get_embedding
)

load_dotenv()

async def retrieve_relevant_pdf_chunks(user_query: str, source_file: str = "") -> str:
    embedding = await get_embedding(user_query)

    result = supabase.rpc(
        'match_pdf_chunks',
        {
            'query_embedding': embedding,
            'match_count': 3,
            'source': source_file
        }
    ).execute()

    if not result.data:
        return "No relevant chunks found."

    result = "\n\n------\n\n".join([
        f"{r['content']}" for r in result.data
    ])

    return result


async def answer_query(user_query: str, source_file: str) -> str:
    try:
        context = await retrieve_relevant_pdf_chunks(user_query, source_file)

        prompt = f"Retrieved Chunks: {context}. \n User Query: {user_query}."

        response = await openai_client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=[
                {"role": "system", "content": RAG_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        return content
    except Exception as e:
        logging.error(f"Error getting title and summary: {e}")
