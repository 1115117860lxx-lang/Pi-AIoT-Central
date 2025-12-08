# 🍓 Raspberry Pi 5 Offline Jarvis (AIoT Voice Assistant)

一个基于树莓派 5 的**完全离线**智能家居语音管家。它拥有本地大模型大脑，毫秒级响应速度，并能通过 GPIO 控制实体硬件。

## ✨ 特性
* **0 延迟**：使用 Vosk 离线语音识别，无需联网。
* **本地大脑**：集成 Ollama + Qwen2.5 (1.5B)，支持闲聊与指令控制。
* **硬件控制**：支持 LED 灯与风扇控制 (GPIO)。
* **鲁棒性**：内置规则引擎兜底，防止大模型幻觉导致控制失败。

## 🛠️ 硬件需求
* Raspberry Pi 5 (8GB 推荐)
* USB 麦克风 & 音箱
* LED 灯 (Pin 17)
* 风扇 (Pin 27)

## 📦 安装与运行

### 1. 环境配置
```bash
# 安装系统依赖
sudo apt install espeak espeak-ng python3-pyaudio libasound2-dev

# 安装 Python 库
pip install vosk pyaudio pyttsx3 requests RPi.GPIO

2. 下载模型
请下载 Vosk 中文模型 vosk-model-small-cn-0.22 并解压到项目根目录，重命名为 model。

3. 运行 Ollama
ollama serve
# 确保已拉取模型: ollama pull qwen2.5:1.5b

4. 启动 Jarvis
python jarvis.py
