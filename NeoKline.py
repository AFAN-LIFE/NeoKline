import streamlit as st

st.image('assets/logo-gray.png')
st.markdown('**NeoKline是开源免费的形态学分析平台，提供K线可视化及用户自主发起的DeepSeek AI交互功能。**')
st.caption("""
**技术透明声明**：本平台代码完全开源在 [GitHub](https://github.com/AFAN-LIFE/NeoKline)，\
通过自动化CI/CD流程部署于[Streamlit云服务器](http://neokline.streamlit.app/)。所有处理逻辑均可审计。
""")
st.markdown('''## 🚨合规声明及风险提示

本平台严格遵循中国证监会《关于加强对利用"荐股软件"从事证券投资咨询业务监管的暂行规定》（以下简称规定），郑重声明：
- 不提供任何具体证券品种的投资分析意见或价格走势预测；
- 不推荐具体证券投资品种；
- 不提示具体证券买卖时机；
- 不输出任何形式的证券投资建议。  

根据监管要求，本平台明确不属于"荐股软件"范畴，并建立多重合规保障机制：
- 所有AI生成内容均为用户指令驱动，系统不预设任何投资建议模型；
- 全界面动态风险提示覆盖，大模型底层强制植入合规约束（system角色设定）；
- **特别声明**：因DeepSeek大模型可能存在生成幻觉（Hallucination），若用户通过技术手段绕过平台合规限制，导致输出内容违反《规定》，相关责任由用户自行承担，与本平台无关。

🚨**风险提示**：
- ⚠️ **数据特性说明**：所有分析结论均基于历史数据回溯，不构成任何投资依据  
- ⚠️ **用户责任声明**：使用者需独立承担投资决策风险及后果  
- ⚠️ **系统边界声明**：严禁通过任何技术手段规避平台合规限制  
''')

st.markdown('''## 📚 相关资料
- ♨️（2万阅读）[250323：5分钟教会你用DeepSeek进行形态学分析](https://mp.weixin.qq.com/s/yR0qJitlvSB27Uz1KNvN_w))
- ♨️ [250409：TA-Lib生成MACD/布林带，DeepSeek形态分析升级版](https://mp.weixin.qq.com/s/mE0USsmClWipNol-wYLlbA)
''')

st.markdown('''## ✨ 交流分享
欢迎把本平台分享给你的朋友们，如想加入平台交流群，或有定制开发需求，欢迎微信联系：afan-life
''')
st.image('assets/contact.jpg')

