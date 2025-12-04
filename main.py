from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import ollama
import json
import sys

# 初始化 APP
app = FastAPI(title="AIoT 智能中控系统")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- 1. 定义数据结构 ---
class ChatRequest(BaseModel):
    command: str  

# --- 2. 定义系统提示词  ---
SYSTEM_PROMPT = """
你是一个智能家居控制中枢。你的唯一任务是将用户的自然语言转化为 JSON 控制指令。
不要输出任何闲聊内容，只输出 JSON。

可用设备：
- light (灯)
- fan (风扇)
- ac (空调)

输出格式示例：
{"device": "light", "action": "on"}
{"device": "ac", "action": "26C"}
"""

# --- 3. 核心接口 ---
@app.post("/api/control")
async def control_home(request: ChatRequest):
    print(f"📡 收到前端指令: {request.command}")
    
    try:
        # 调用 Ollama 大模型
        response = ollama.chat(model='deepseek-r1:8b', messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': request.command},
        ])
        
        ai_raw_reply = response['message']['content']
        print(f"🧠 AI 原始思考: {ai_raw_reply}")

        # 清洗数据
        clean_json = ai_raw_reply.replace("```json", "").replace("```", "").strip()
        
        # 解析 JSON
        action_data = json.loads(clean_json)
        
        
        # 模拟硬件控制
        feedback = ""
        if action_data['device'] == 'light' and action_data['action'] == 'on':
            feedback = "执行成功：已为您开启客厅主灯 💡"
        elif action_data['device'] == 'fan' and action_data['action'] == 'off':
            feedback = "执行成功：风扇已停止运转 💨"
        else:
            feedback = f"指令已发送：设备 {action_data['device']} -> {action_data['action']}"
            
        return {
            "status": "success",
            "user_input": request.command,
            "parsed_action": action_data,
            "message": feedback
        }

    except json.JSONDecodeError:
        print("❌ JSON 解析失败，AI 可能走神了")
        return {
            "status": "error",
            "message": "AI 没听懂，请再说具体一点",
            "raw_response": ai_raw_reply
        }
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 启动服务
    print(">>> 🟢 AIoT 中枢正在启动...")
    uvicorn.run(app, host="0.0.0.0", port=8000)