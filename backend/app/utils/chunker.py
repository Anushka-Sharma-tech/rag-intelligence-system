from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict

def chunk_documents(pages: List[Dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
    """
    Split document pages into overlapping chunks.
    RecursiveCharacterTextSplitter tries \n\n, then \n, then ". ", then " "
    to find natural split points — preserving semantic integrity.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = []
    for page_data in pages:
        texts = splitter.split_text(page_data["text"])
        for i, text in enumerate(texts):
            chunks.append({
                "text": text,
                "page": page_data.get("page"),
                "source": page_data["source"],
                "chunk_index": i
            })
    return chunks