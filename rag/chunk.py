import hashlib
from datetime import datetime
from typing import List, Dict, Union, BinaryIO
from pathlib import Path


def chunk_document(file_stream: Union[BinaryIO, bytes], file_name: str, chunk_size=600, overlap=100) -> \
List[Dict]:
    """处理文件流并返回分块结果"""
    # 根据文件扩展名选择解析器
    ext = Path(file_name).suffix.lower()
    text = ""

    if ext == '.pdf':
        import pdfplumber
        text = ''
        if isinstance(file_stream, bytes):
            import io
            file_stream = io.BytesIO(file_stream)

        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                text += page.extract_text()

    elif ext == '.docx':
        from docx import Document
        if isinstance(file_stream, bytes):
            import io
            file_stream = io.BytesIO(file_stream)

        text = "\n".join([para.text for para in Document(file_stream).paragraphs])

    elif ext == '.txt':
        if isinstance(file_stream, bytes):
            text = file_stream.decode('utf-8')
        else:
            text = file_stream.read().decode('utf-8')

    else:
        raise ValueError(f"不支持的文件类型: {ext}")

    # 分块处理
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunk_id = hashlib.md5(f"{file_name}_{i}".encode()).hexdigest()

        chunks.append({
            "id": chunk_id,
            "text": chunk,
            "metadata": {
                "chunk_index": i,
                "source_file": file_name,  # 使用文件名而不是路径
                "create_time": datetime.now().isoformat()
            }
        })

    return chunks