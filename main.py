import asyncio
import logging
import subprocess
import shutil
import sqlite3
import json
import requests
import os
import httpx
import re
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, WebSocket, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
import yt_dlp
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("InfinityCore")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ==========================================
# 1. 数据库与配置
# ==========================================
DB_NAME = "infinity_max.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            title TEXT,
            duration INTEGER,
            thumbnail TEXT,
            channel TEXT,
            ai_reason TEXT,
            added_at TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_setting(key, default=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def save_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

class ConfigRequest(BaseModel):
    provider: str
    api_key: str
    model: str
    base_url: str = None
    proxy: str = None

# ==========================================
# 2. API 与网络层
# ==========================================

def create_http_client(proxy_url: str = None):
    if proxy_url and proxy_url.strip():
        return httpx.Client(proxies=proxy_url, verify=False, timeout=30.0)
    else:
        return httpx.Client(trust_env=False, timeout=30.0)

@app.get("/api/config")
def get_config():
    key = get_setting("api_key", "")
    return {
        "is_configured": bool(key),
        "provider": get_setting("provider", "openai"),
        "model": get_setting("model", "gpt-4o"),
        "base_url": get_setting("base_url", "https://api.openai.com/v1"),
        "proxy": get_setting("proxy", ""),
        "masked_key": f"{key[:3]}...{key[-4:]}" if len(key) > 8 else ""
    }

@app.post("/api/config")
def update_config(config: ConfigRequest):
    base_url = config.base_url
    if not base_url:
        if config.provider == "openai": base_url = "https://api.openai.com/v1"
        elif config.provider == "deepseek": base_url = "https://api.deepseek.com"
        elif config.provider == "nvidia": base_url = "https://integrate.api.nvidia.com/v1"
        elif config.provider == "siliconflow": base_url = "https://api.siliconflow.cn/v1"

    try:
        http_client = create_http_client(config.proxy)
        client = OpenAI(api_key=config.api_key, base_url=base_url, http_client=http_client)
        client.chat.completions.create(model=config.model, messages=[{"role": "user", "content": "Hi"}], max_tokens=1)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    save_setting("provider", config.provider)
    save_setting("api_key", config.api_key)
    save_setting("model", config.model)
    save_setting("base_url", base_url)
    save_setting("proxy", config.proxy or "")
    
    return {"status": "success"}

# ==========================================
# 3. 漏斗式抓取逻辑 (The Funnel)
# ==========================================

def get_scraper_opts():
    return {
        'quiet': True,
        'extract_flat': True, # 极速模式：必须开启，否则抓1000条会超时
        'ignoreerrors': True,
        'no_warnings': True,
        'socket_timeout': 15,
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    }

# --- 层级 1: 启发式过滤 (本地 Python 极速过滤) ---
def heuristic_filter(entry, query_parts):
    """
    不需要 AI，用简单的规则瞬间杀掉 90% 的垃圾视频
    """
    title = entry.get('title', '').lower()
    duration = entry.get('duration') or 0
    
    # 1. 标题必须包含查询词的一部分 (e.g. 搜 Elon Musk，标题必须有 Elon 或 Musk)
    if not any(part in title for part in query_parts):
        return False

    # 2. 垃圾词黑名单
    banned = ["reaction", "react", "gameplay", "walkthrough", "short", "#shorts", "tiktok", "reel", "funny moments", "compilation"]
    if any(b in title for b in banned):
        return False

    # 3. 时长过滤：小于 300秒 (5分钟) 的直接丢弃
    # 真正的访谈演讲通常都很长
    if duration < 300:
        return False
        
    return True

# --- 层级 2: AI 深度鉴别 ---
def verify_with_ai(video_metadata, query_person):
    api_key = get_setting("api_key")
    if not api_key: return True, "AI Skipped"
    
    client = OpenAI(
        api_key=api_key, 
        base_url=get_setting("base_url"), 
        http_client=create_http_client(get_setting("proxy"))
    )
    
    prompt = f"""
    Role: Senior Content Editor.
    Goal: Identify PRIMARY SOURCE videos of "{query_person}".
    
    Criteria for VALID:
    - Full Interviews, Keynote Speeches, Lectures, Fireside Chats, Documentaries.
    - The person is speaking directly for the majority of the time.
    
    Criteria for INVALID:
    - 3rd party commentary/analysis (e.g. "Why he is wrong").
    - News reports ABOUT the person.
    - Reaction videos.
    - Clickbait/Gossip.

    Video: "{video_metadata['title']}" by "{video_metadata['channel']}" ({int(video_metadata['duration']/60)} mins).
    
    Output JSON ONLY: {{"valid": true/false, "reason": "max 5 words"}}
    """

    try:
        completion = client.chat.completions.create(
            model=get_setting("model"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, # 零温度，追求精准
            max_tokens=60,
            response_format={"type": "json_object"}
        )
        res = json.loads(completion.choices[0].message.content)
        return res.get('valid', False), res.get('reason', 'AI Verified')
    except Exception as e:
        logger.error(f"AI Check Error: {e}")
        return True, "AI Bypass (Error)"

async def fetch_process(websocket, query):
    if not get_setting("api_key"):
        await websocket.send_json({"status": "error", "msg": "⚠️ Please configure API Key first."})
        return

    # 1. 构建海量搜索矩阵 (年份 + 关键词)
    # 这样可以突破 YouTube 单次搜索 50 条的限制，达到 1000+
    current_year = datetime.now().year
    years = range(current_year, current_year - 5, -1) # 最近5年
    
    search_matrix = []
    
    # 核心词
    core_types = ["full interview", "keynote speech", "documentary", "fireside chat", "lecture"]
    
    # 组合生成: "Elon Musk full interview 2024", "Elon Musk keynote 2023"...
    for t in core_types:
        # 不带年份 (搜相关度)
        search_matrix.append(f"{query} {t}")
        # 带年份 (搜新近度)
        for y in years:
            search_matrix.append(f"{query} {t} {y}")

    total_tasks = len(search_matrix)
    await websocket.send_json({"status": "log", "msg": f"🌐 启动广域扫描矩阵: {total_tasks} 个并发探针..."})

    # 2. 并发执行抓取
    raw_candidates = []
    seen_ids = set()
    query_parts = query.lower().split()
    
    # 限制并发数为 5，防止被 YouTube 封 IP
    semaphore = asyncio.Semaphore(5)

    async def fetch_worker(term):
        async with semaphore:
            try:
                # 每个探针抓 40 条
                data = await asyncio.to_thread(yt_dlp.YoutubeDL(get_scraper_opts()).extract_info, f"ytsearch40:{term}", download=False)
                return data.get('entries', [])
            except: return []

    results = await asyncio.gather(*[fetch_worker(term) for term in search_matrix])
    
    # 3. 展平并执行 层级 1 (启发式过滤)
    for batch in results:
        if not batch: continue
        for entry in batch:
            if not entry: continue
            vid = entry['id']
            if vid in seen_ids: continue
            
            # Heuristic Filter
            if heuristic_filter(entry, query_parts):
                seen_ids.add(vid)
                raw_candidates.append({
                    'id': vid,
                    'title': entry['title'],
                    'channel': entry.get('uploader'),
                    'duration': entry.get('duration'),
                    'thumbnail': entry.get('thumbnail')
                })

    await websocket.send_json({"status": "log", "msg": f"⚡ 初筛完成: 从 {len(seen_ids)}+ 条原始数据中保留 {len(raw_candidates)} 条潜力视频..."})

    # 4. 执行 层级 2 (AI 过滤)
    # 为了省钱和速度，如果初筛结果太多，只取前 60 个给 AI
    ai_candidates = raw_candidates[:60] 
    final_list = []
    
    await websocket.send_json({"status": "log", "msg": f"🧠 AI 正在深度鉴别 {len(ai_candidates)} 个目标..."})

    for vid in ai_candidates:
        valid, reason = verify_with_ai(vid, query)
        if valid:
            vid['ai_reason'] = reason
            if not vid.get('thumbnail'): vid['thumbnail'] = f"https://img.youtube.com/vi/{vid['id']}/hqdefault.jpg"
            save_video_to_db(vid)
            final_list.append(vid)

    await websocket.send_json({"status": "done", "msg": f"✅ 收录 {len(final_list)} 个神级资源 (已过滤 {len(seen_ids) - len(final_list)} 个杂项)", "data": final_list})

def save_video_to_db(v):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO videos (id, title, duration, thumbnail, channel, ai_reason, added_at) VALUES (?,?,?,?,?,?,?)', 
              (v['id'], v['title'], v['duration'], v['thumbnail'], v['channel'], v['ai_reason'], datetime.now()))
    conn.commit()
    conn.close()

# 路由部分保持不变...
def get_real_url(vid):
    try:
        cmd = ["yt-dlp", "-g", "-f", "best[ext=mp4]", f"https://www.youtube.com/watch?v={vid}"]
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    except: return None

@app.get("/api/stream/{vid}")
async def proxy_stream(vid: str, request: Request):
    url = get_real_url(vid)
    if not url: return Response(status_code=404)
    headers = {"User-Agent": "Mozilla/5.0"}
    if request.headers.get("range"): headers["Range"] = request.headers.get("range")
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=20)
        resp_h = {"Accept-Ranges": "bytes", "Content-Type": "video/mp4"}
        for k in ["Content-Length", "Content-Range"]: 
            if k in r.headers: resp_h[k] = r.headers[k]
        return StreamingResponse(r.iter_content(chunk_size=1024*1024), status_code=r.status_code, headers=resp_h, media_type="video/mp4")
    except: return Response(status_code=502)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        await fetch_process(websocket, data.get("query"))
    except: await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
