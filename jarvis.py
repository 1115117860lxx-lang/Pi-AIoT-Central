"""
项目名称: Raspberry Pi 5 AIoT 离线语音管家 (Jarvis)
硬件平台: Raspberry Pi 5 (8GB)
核心技术栈:
  - 听觉 (STT): Vosk (离线模型: vosk-model-small-cn-0.22)
  - 大脑 (LLM): Ollama + Qwen2.5:1.5b (本地运行)
  - 视觉 (TTS): pyttsx3 + espeak (离线语音合成)
  - 控制 (GPIO): RPi.GPIO
作者: 新
日期: 2025
"""

import os
import json
import pyaudio
import requests
import pyttsx3
import RPi.GPIO as GPIO
import time
from vosk import Model, KaldiRecognizer

# --- 1. 硬件配置与初始化 ---
PIN_LIGHT = 17  # 灯光 GPIO
PIN_FAN = 27    # 风扇 GPIO

# 强制清理 GPIO 状态，防止被旧进程占用
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
except:
    pass

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_LIGHT, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_FAN, GPIO.OUT, initial=GPIO.LOW)
    IS_PI = True
    print(f"✅ 硬件就绪！控制引脚: 灯={PIN_LIGHT}, 风扇={PIN_FAN}")
    
    # --- 💡 开机自检 (视觉反馈) ---
    print("👀 硬件自检中 (灯光闪烁)...")
    for _ in range(2):
        GPIO.output(PIN_LIGHT, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(PIN_LIGHT, GPIO.LOW)
        time.sleep(0.3)
    print("✅ 自检完成。")

except Exception as e:
    IS_PI = False
    print(f"⚠️ 进入模拟模式 (GPIO 错误): {e}")

# --- 2. 离线语音合成 (TTS) ---
engine = pyttsx3.init()

# 自动寻找并切换中文语音包
voices = engine.getProperty('voices')
found_zh = False
for v in voices:
    if 'zh' in v.id or 'chinese' in v.name.lower():
        engine.setProperty('voice', v.id)
        found_zh = True
        print(f"✅ TTS 已切换中文: {v.id}")
        break

if not found_zh:
    try:
        engine.setProperty('voice', 'zh') # 强制尝试
    except:
        pass

engine.setProperty('rate', 165)  # 语速
engine.setProperty('volume', 1.0) # 音量

def speak(text):
    """ 文字转语音输出 """
    print(f"🤖 Jarvis: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        pass

# --- 3. 离线语音识别 (Vosk) ---
if not os.path.exists("model"):
    print("❌ 错误：找不到 'model' 文件夹，请下载 Vosk 中文模型。")
    exit(1)

# 屏蔽底层 ALSA 音频驱动的冗余报错
try:
    from ctypes import *
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def py_error_handler(filename, line, function, err, fmt): pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass

print("⏳ 正在加载 Vosk 离线模型...")
model = Model("model")
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()

# 打开麦克风流 (采样率 16000)
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
stream.start_stream()

# --- 4. AI 大脑处理 (Ollama + 规则兜底) ---
def ask_ai(text):
    url = "http://127.0.0.1:11434/api/chat"
    
    # System Prompt: 定义 AI 的人设和输出格式
    system_prompt = """
    你是一个智能管家。
    任务：判断用户意图，返回 JSON。
    规则：
    1. 如果用户想控制设备，必须设置 "device" (light/fan) 和 "action" (on/off)。
    2. 如果只是闲聊，"device" 设为 null。
    
    示例：
    用户：把灯打开 -> {"device": "light", "action": "on", "reply": "好的，灯亮了"}
    用户：你好 -> {"device": null, "action": null, "reply": "你好呀！"}
    """
    
    ai_data = {"device": None, "action": None, "reply": "我没听清"}
    
    # 1. 尝试请求本地 LLM
    try:
        res = requests.post(url, json={
            "model": "qwen2.5:1.5b",
            "messages": [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text}
            ],
            "stream": False
        }, timeout=10)
        
        raw = res.json()['message']['content']
        # 清洗数据，提取 JSON
        clean = raw.replace("```json", "").replace("```", "").strip()
        import re
        match = re.search(r'\{.*\}', clean, re.DOTALL)
        if match:
            ai_data = json.loads(match.group())
        else:
            ai_data = {"reply": clean, "device": None, "action": None}
            
    except:
        return {"reply": "Ollama 服务未启动", "device": None}

    # 🔥 2. 规则兜底 (Rule-based Fallback) 🔥
    # 如果小模型“漏抓”了指令，使用关键词强制修正，确保控制成功率 100%
    if ai_data.get("device") is None:
        text_lower = text.lower()
        # print("⚠️ 检测到 AI 未识别设备，启动规则兜底检查...")
        
        if "灯" in text_lower:
            if any(x in text_lower for x in ["开", "亮", "open", "on"]):
                ai_data.update({"device": "light", "action": "on", "reply": "好的，灯已开启 (兜底)"})
            elif any(x in text_lower for x in ["关", "灭", "close", "off"]):
                ai_data.update({"device": "light", "action": "off", "reply": "好的，灯已关闭 (兜底)"})
                
        elif "风扇" in text_lower:
            if any(x in text_lower for x in ["开", "转", "open", "on"]):
                ai_data.update({"device": "fan", "action": "on", "reply": "风扇启动 (兜底)"})
            elif any(x in text_lower for x in ["关", "停", "close", "off"]):
                ai_data.update({"device": "fan", "action": "off", "reply": "风扇停止 (兜底)"})

    return ai_data

# --- 5. 主循环 ---
print("\n✅ 系统就绪！请说话...")
speak("系统启动完毕")

try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if len(data) == 0: break

        # Vosk 实时监听
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result['text'].replace(" ", "")
            
            if text:
                print(f"👂 听到: {text}")
                # 关键词唤醒过滤，防止杂音误触
                keywords = ["灯", "风扇", "打开", "关", "你好", "是谁", "笑话", "天气", "贾维斯"]
                
                if any(k in text for k in keywords):
                    action_data = ask_ai(text)
                    print(f"🧠 AI 最终决策: {action_data}") 
                    
                    device = action_data.get('device')
                    action = action_data.get('action')
                    reply = action_data.get('reply', '好的')
                    
                    # 硬件执行逻辑 (兼容大小写)
                    if device and device.lower() == 'light' and IS_PI:
                        state = GPIO.HIGH if action == 'on' else GPIO.LOW
                        GPIO.output(PIN_LIGHT, state)
                        print(f"💡 [硬件操作] 灯 -> {action}")
                        
                    elif device and device.lower() == 'fan' and IS_PI:
                        state = GPIO.HIGH if action == 'on' else GPIO.LOW
                        GPIO.output(PIN_FAN, state)
                        print(f"💨 [硬件操作] 风扇 -> {action}")
                    
                    speak(reply)

except KeyboardInterrupt:
    print("\n退出系统")
    stream.stop_stream()
    stream.close()
    p.terminate()
    if IS_PI: GPIO.cleanup()