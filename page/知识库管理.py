import time
import streamlit as st
from rag.chunk import chunk_document
from rag.base import UserKnowledgeBase
from tools.callback import botton_callback

st.markdown("# 📈 知识库管理")

if 'rag_meta_data' not in st.session_state:
    st.session_state.rag_meta_data = []
if 'rag_faiss_index' not in st.session_state:
    st.session_state.rag_faiss_index = None
if 'rag_cache_name' not in st.session_state:
    st.session_state.rag_cache_name = ""

if ('rag_meta_data' not in st.session_state) or (st.session_state.rag_meta_data == []):
    st.badge('当前无知识库，请上传文档文件', color='orange')
else:
    st.badge(f'当前知识库已有{len(st.session_state.rag_meta_data)}个知识块，点击下方查看', color='green')
    with st.expander('查看知识库切块文档'):
        st.write(st.session_state.rag_meta_data)

if st.session_state.get("authentication_status") is None:
    st.badge('请登录后再上传文档！', color='orange')
else:
    st.markdown('由于计算存储资源限制，在线版仅支持上传**1篇文档**，并仅抽取**前10000字**（切成20块用于智能匹配），更高定制需求请到首页联系AFAN')
total_file = st.file_uploader("请上传文档文件，会替换原有知识库知识", type={'docx', 'pdf', 'txt'},
                              on_change=botton_callback, args=('知识库文档上传', ),
                              disabled= st.session_state.get("authentication_status") is None)
if total_file is not None:
    if total_file.name == st.session_state.rag_cache_name:
        st.badge('当前文档已存入知识库，请替换文档或直接进入股票分析界面使用', color='orange')
        st.stop()
    else:
        st.session_state.rag_cache_name = total_file.name
    chunks = chunk_document(total_file, total_file.name)
    st.badge('文件读取成功，正在存入知识库...')
    status, data, msg = UserKnowledgeBase.add_document(chunks[:20])
    if status == 'success':
        st.success(msg)
        st.badge('3秒钟之后自动刷新页面...')
        time.sleep(3)
        st.rerun()
    else:
        st.error(msg)
        st.stop()
