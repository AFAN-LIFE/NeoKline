import base64
import requests, json
from config import SILICON_FLOW_TOKEN

# https://cloud.siliconflow.cn/models
sk = SILICON_FLOW_TOKEN

def image_to_base64_from_buffer(img_buffer):
    # 直接从 BytesIO 缓冲区获取 Base64 编码
    img_buffer.seek(0)  # 确保指针在开头
    return base64.b64encode(img_buffer.getvalue()).decode("utf-8")

def get_stream_dsvl2_response(messages, **kwargs):
    """
    调用硅基流动的流式 API
    """
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-ai/deepseek-vl2",
        "stream": True,
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "stop": [],
        "messages": messages
    }
    # 发送请求并流式获取响应
    response = requests.post(url, json=payload, headers=headers, stream=True, verify=False)
    if response.status_code != 200:
        raise Exception(f"API 请求失败，状态码：{response.status_code}，错误信息：{response.text}")

    # 逐行读取流式响应
    for chunk in response.iter_lines():
        if chunk:
            # 解析 JSON 数据
            chunk_str = chunk.decode("utf-8").strip()
            if chunk_str.startswith("data:"):
                chunk_data = chunk_str[5:].strip()  # 去掉 "data: " 前缀
                if chunk_data == "[DONE]":  # 流式结束标志
                    break
                try:
                    chunk_json = json.loads(chunk_data)
                    content = chunk_json["choices"][0]["delta"].get("content", "")
                    print(content)
                    yield content
                except json.JSONDecodeError:
                    continue