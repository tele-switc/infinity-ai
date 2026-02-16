# infinity-ai
♾️ Infinity AI - The Ultimate Primary Source Aggregator

Infinity AI is a self-hosted, AI-powered media intelligence system designed to cut through the noise of modern content algorithms. It autonomously scans thousands of videos, uses Large Language Models (LLMs) to filter out clickbait, commentary, and reaction content, and delivers a pure stream of Primary Sources (Interviews, Keynotes, Lectures, and Documentaries).

✨ Why Infinity AI?

YouTube and social media are flooded with "YouTuber talks about X" content. Finding the original 3-hour interview or the raw keynote speech is becoming increasingly difficult.

Infinity AI solves this by acting as your personal research agent.

🚀 Key Features

🧠 AI-Powered Verification (The Truth Shield)

Uses NVIDIA NIM (Llama-3), OpenAI, or DeepSeek to semantically analyze video metadata.

Distinguishes between Elon Musk speaking vs. A random guy analyzing Elon Musk.

Automatically rejects reaction videos, gossip, and short clips (< 5 mins).

🌊 Massive Scale "Funnel" Scraping

Wide Net: Scans 1,000+ candidates per search using concurrent probing.

Heuristic Pre-filter: Python-based regex engine instantly kills 90% of junk data.

AI Verdict: The remaining high-quality candidates are sent to the LLM for final verification.

📽️ Cinema-Grade Streaming

System-Level Proxy: Bypasses browser CORS and 403 restrictions.

High Fidelity: Forces 1080p MP4 streams with full seek/scrub support.

No Ads: Direct stream piping means zero interruptions.

🖥️ Floating "Mini-Mode"

A beautiful, draggable Picture-in-Picture window.

Watch your content in the corner while browsing the massive archive list simultaneously.

Glassmorphism UI: Modern, dark-themed aesthetic with smooth animations.

🤖 Autonomous Persistence

SQLite Database: Saves every verified video. It remembers what you watched.

Auto-Pilot: A background scheduler wakes up every 24 hours to hunt for new content automatically.

Smart Resume: Close the browser, come back tomorrow, and resume exactly where you left off.

🛠️ Tech Stack

Core: Python 3.10+

API Framework: FastAPI + Uvicorn (Asynchronous)

AI Engine: OpenAI SDK (Compatible with NVIDIA NIM, DeepSeek, SiliconFlow)

Scraping: yt-dlp (Custom configured for metadata extraction)

Database: SQLite3

Frontend: Vanilla JS + Tailwind CSS (No build steps required, extremely fast)

Networking: HTTPX (with SOCKS proxy support)

⚡ Quick Start
1. Clone the Repository
code
Bash
download
content_copy
expand_less
git clone https://github.com/yourusername/infinity-ai.git
cd infinity-ai
2. Create Environment (Recommended)
code
Bash
download
content_copy
expand_less
conda create -n infinity python=3.10
conda activate infinity
3. Install Dependencies
code
Bash
download
content_copy
expand_less
pip install -r requirements.txt
# OR manually:
pip install fastapi uvicorn yt-dlp openai apscheduler jinja2 requests httpx[socks]
4. Run the System
code
Bash
download
content_copy
expand_less
python main.py

Access the dashboard at: http://localhost:8000

⚙️ Configuration

Infinity AI comes with a built-in Graphical Setup Wizard. You don't need to edit config files manually.

Launch the App: Open your browser to http://localhost:8000.

Setup Screen: If no API key is found, you will be redirected to the setup page.

Select Provider:

NVIDIA NIM (Recommended): Best for Llama-3-70B reliability.

OpenAI / DeepSeek: Fully supported.

SiliconFlow: Supported for Qwen models.

Proxy Settings (Important):

If you are behind a firewall or use a VPN (e.g., Clash, V2Ray), enter your proxy URL in the settings (e.g., http://127.0.0.1:7890) to avoid connection errors.

🖥️ User Interface Guide
The Search Mode

Type a subject name (e.g., "Sam Altman"). The system will initiate a massive concurrent scan, filtering hundreds of videos in seconds.

The Player (Cinema Mode)

List Panel: Shows AI-verified sources on the right.

AI Reason: Hover over a video to see why the AI selected it.

Mini-Mode: Click the button in the top-right of the player to shrink it into a floating window.

The Floating Window

Draggable: Grab the top handle to move it anywhere.

Responsive: The list expands to full width, allowing you to manage the database while watching.

🤝 Contributing

Contributions are welcome! Whether it's adding new AI providers, improving the UI, or optimizing the scraper.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📜 License

Distributed under the MIT License. See LICENSE for more information.
