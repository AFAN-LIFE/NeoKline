import streamlit as st

def single_content_qa(content):
    img_path = content['img'][0]['value']
    with st.container(border=True):
        j1, j2, j3 = st.columns([2, 2, 2])
        j2.image('assets/deepseek.png')
        # 添加风险提示
        st.warning("""
        **风险提示**：
        - 以下内容由DeepSeek AI生成，仅供参考，不代表本平台观点
        - 所有分析均基于历史数据，不构成投资建议
        - 使用者需自行承担决策风险
        - 禁止尝试通过特殊指令获取投资建议
        """)
        base_system = st.text_area('系统预设，用户无法更改',  '''🚨你现在是一名资深的股票分析师，请根据这张图以及用户的提问进行分析，但请注意不要违反中国证监会《关于加强对利用"荐股软件"从事证券投资咨询业务监管的暂行规定》，包括：
- 不提供任何具体证券品种的投资分析意见或价格走势预测；
- 不推荐具体证券投资品种；
- 不提示具体证券买卖时机；
- 不输出任何形式的证券投资建议。''', disabled=True)
        i1, i2 = st.columns([4, 1])
        extra_info = i1.text_area('请填写您对当前结果的问题或对场景的补充描述，让DeepSeek帮你分析！',
                                  value='分析一下这个图的形态学走势')
        if i2.button('问答交流'):
            single_img_one_round_qa_view(base_system, img_path, extra_info)

def single_img_one_round_qa_view(system, img_path, extra_info):
    from llm.siliconflow import get_stream_dsvl2_response
    from llm.siliconflow import image_to_base64_from_buffer

    img_base64 = image_to_base64_from_buffer(img_path)
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "text": system,
                    "type": "text"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "image_url": {
                        "detail": "auto",
                        "url": f"data:image/png;base64,{img_base64}"  # 使用 Base64 编码的shap图片
                    },
                    "type": "image_url"
                },
                {
                    "text": f"{extra_info}",
                    "type": "text"
                }
            ]
        }
    ]
    with st.expander('DeepSeek分析结果', expanded=True):
        st.write_stream(get_stream_dsvl2_response(messages))