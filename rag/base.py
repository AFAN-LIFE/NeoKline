import faiss
import numpy as np
from uuid import uuid4
import streamlit as st
from typing import Dict, List, Optional
from rag.embedding import netease_youdao_embedding

EMBEDDING_DIM = 768

class UserKnowledgeBase:

    @staticmethod
    def add_document(
            chunks: List[Dict],
            embedding_fn=netease_youdao_embedding
    ):
        # 处理文档块
        vectors = []
        metadata = []
        error_msg_list = []
        for chunk in chunks:
            status, emb, msg = embedding_fn(chunk["text"])
            if status == 'failed':
                error_msg_list.append(msg)
                continue
            chunk_uuid = uuid4().int & ((1 << 63) - 1)  # 将UUID转为63位正整数
            vectors.append(emb)
            metadata.append({
                "chunk_id": chunk_uuid,
                "text": chunk["text"],  # 存储原始文本
                "source_file": chunk["metadata"]["source_file"],
                "create_time": chunk["metadata"]["create_time"]
            })
        # 更新索引和元数据
        if vectors:
            # 合并向量数据
            vectors_array = np.array(vectors, dtype='float32')
            index = faiss.IndexIDMap(faiss.IndexFlatL2(EMBEDDING_DIM))
            ids_array = np.array([item['chunk_id'] for item in metadata], dtype=np.int64)
            index.add_with_ids(vectors_array, ids_array)
            # 返回信息
            success_ratio = len(vectors) / len(chunks)
            if success_ratio == 1:
                st.session_state.rag_faiss_index = index
                st.session_state.rag_meta_data = metadata
                return 'success', None, '全部获取完毕'
            else:
                return 'success', None, f'获取成功率为{int(success_ratio * 100)}%，失败信息有{error_msg_list}'
        else:
            return 'failed', None, f'全部获取失败，失败信息有{error_msg_list}'

    @staticmethod
    def search(
            query: str,
            k: int,
            embedding_fn=netease_youdao_embedding,
    ) -> List[Dict]:
        """
        多场景检索：
        1. 指定user_name和topic：精确检索用户某主题
        2. 仅指定user_name：检索用户所有文档
        3. 都不指定：全局检索（需管理员权限）
        """
        if st.session_state.rag_meta_data == []:
            st.error('当前无知识保存，请到“知识库管理”上传知识')
            st.stop()

        # 生成查询向量
        status, query_emb, msg = embedding_fn(query)
        if status == 'failed':
            raise ValueError(f"Embedding失败: {msg}")
        index:faiss.IndexIDMap = st.session_state.rag_faiss_index
        status, query_emb, _ = embedding_fn(query)
        D, I = index.search(
            np.array([query_emb], dtype='float32'), k
        )
        metadata = st.session_state.rag_meta_data
        metaid2content = {i['chunk_id']: i for i in metadata}
        return [{
            "text": metaid2content[i]["text"],
            "score": float(D[0][j]),
            "source": metaid2content[i]["source_file"],
        } for j, i in enumerate(I[0]) if i >= 0]