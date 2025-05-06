import requests
from config import SILICON_FLOW_TOKEN
def netease_youdao_embedding(text, SK_CODE=SILICON_FLOW_TOKEN):
    headers = {
        "Authorization": f"Bearer {SK_CODE}",
        "Content-Type": "application/json"
    }
    url = "https://api.siliconflow.cn/v1/embeddings"
    payload = {
        "model": "netease-youdao/bce-embedding-base_v1",
        "input": text,
        "encoding_format": "float"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        embedding = response.json()['data'][0]['embedding']
        return 'suceess', embedding, 'embedding成功'
    else:
        return 'failed', 0, response.text