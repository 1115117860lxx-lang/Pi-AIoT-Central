![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?style=flat&logo=vue.js&logoColor=white)
![Ollama](https://img.shields.io/badge/AI-Ollama-black?style=flat)
![Raspberry Pi](https://img.shields.io/badge/Hardware-Raspberry%20Pi%205-C51A4A?style=flat&logo=raspberrypi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

# Pi-AIoT-Central

#基于 Raspberry Pi 5 + NPU 的边缘计算私有化 AIoT 中控系统（架构篇）

#功能特性 (Features)：

✅ 离线大模型大脑： 集成 deepseek-r1:8b，无需联网即可理解自然语言。

阶段一（PC 仿真 / 逻辑验证）：

模型： DeepSeek-R1-8B

验证目的： 利用 R1 强大的思维链（CoT）能力，验证 System Prompt 对自然语言转 JSON 指令的准确率。实测复杂指令解析成功率达 99%。

阶段二（树莓派部署 / 落地优化）：

模型： Qwen2.5-1.5B (Int4 量化)

优化考量： 考虑到 Raspberry Pi 5 (8GB) 的内存限制及边缘端对实时性 (Real-time) 的极高要求。

最终效果： 理论上1.5B 模型在树莓派上推理速度可达 15+ Tokens/s，可实现了“毫秒级”的语音控制响应，且内存占用控制在 2GB 以内，为 NPU 视觉模块预留了充足资源。

✅ 数字孪生架构： 前后端分离设计，具备完整的 Web 仿真控制台。

✅ 结构化指令引擎： 独创 System Prompt，将自然语言 100% 转化为 JSON 控制协议。

阶段一（PC 仿真 / 逻辑验证）：

#后端逻辑的结果截图如下

<img width="512" height="224" alt="image" src="https://github.com/user-attachments/assets/540b4c77-a157-4b5f-b9cc-eab27117ba7f" />


#前端交互通结果截图如下

<img width="512" height="345" alt="image" src="https://github.com/user-attachments/assets/2bae4b7c-d307-44ff-a6ba-b61bf05bb3f6" />
