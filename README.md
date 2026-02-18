# infinity-player
# ♾️ Infinity AI - The Ultimate Primary Source Aggregator

<div align="center">

![Version](https://img.shields.io/badge/Version-7.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)
![NVIDIA NIM](https://img.shields.io/badge/AI-NVIDIA%20NIM-76b900.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

**"Stop watching the noise. Start listening to the source."**

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration) • [Usage](#-usage)

</div>

---

## 📖 Introduction

**Infinity AI** is a self-hosted, intelligent media archival system designed for researchers, developers, and deep learners.

In an era of algorithmic noise, Infinity AI acts as your **Autonomous Research Agent**. It executes massive concurrent searches across the web, uses **Large Language Models (LLMs)** to filter out clickbait and commentary, and delivers a pure, ad-free stream of **Primary Sources** (Interviews, Keynotes, Lectures, and Documentaries).

## ✨ Features

### 🧠 AI-Powered "Truth Shield"
The core engine uses **NVIDIA NIM (Llama-3)**, **OpenAI**, or **DeepSeek** to semantically analyze video metadata.
- **Sentiment Analysis:** Instantly rejects "Reaction", "Gossip", and "Clickbait" content.
- **Source Verification:** Prioritizes official channels (e.g., Stanford, TED, YC) and primary speakers.
- **Context Generation:** Generates real-time AI insights and summaries for each video.

### 🌊 Massive "Funnel" Architecture
- **Wide Net:** Scans **1,000+** candidates per search session using concurrent probing.
- **Heuristic Pre-filter:** Python-based regex engine instantly eliminates 90% of junk data (Shorts, TikToks).
- **Deep Verification:** The top candidates are sent to the LLM for final "Quality Assurance".

### 📽️ Cinema-Grade Experience
- **System-Level Proxy:** Bypasses browser CORS and 403 restrictions for seamless playback.
- **Floating Mini-Window:** A draggable, glass-morphism Picture-in-Picture mode for multitasking.
- **High Fidelity:** Forces **1080p MP4** streams with full seek/scrub support.
- **Offline Capable:** One-click download to save content locally.

### 🤖 Autonomous Persistence
- **Auto-Pilot:** Background scheduler wakes up every 24 hours to hunt for new content automatically.
- **Smart Resume:** Remembers your playback position across sessions. Close the tab, come back tomorrow, and resume exactly where you left off.

---

## 🛠️ Tech Stack

*   **Core:** Python 3.10+
*   **Web Framework:** FastAPI + Uvicorn (Asynchronous)
*   **AI Engine:** OpenAI SDK (Compatible with NVIDIA NIM, DeepSeek, SiliconFlow)
*   **Scraping:** yt-dlp (Custom configured for metadata extraction)
*   **Database:** SQLite3
*   **Frontend:** Vanilla JS + Tailwind CSS (Zero-build architecture)
*   **Networking:** HTTPX (SOCKS/HTTP Proxy support)

---

## ⚡ Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/infinity-ai.git
cd infinity-ai

### 2. Environment Setup (Recommended)
```bash
conda create -n infinity python=3.10
conda activate infinity

### 3. Install Dependencies
```bash
pip install -r requirements.txt

or
```bash
pip install fastapi uvicorn yt-dlp openai apscheduler jinja2 requests httpx[socks]

### 4. Run Application
```bash
python main.py

Access at: http://localhost:8000

