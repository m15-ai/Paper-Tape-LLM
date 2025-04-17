# 🟢 Teletype Paper Tape LLM

A retro-futuristic terminal interface that simulates a 1979 Teletype Model 33 ASR — powered by modern LLMs via Ollama. Generates animated, audio-punched paper tape output for your prompts. Powered on/off with sound effects and glowing LEDs.

## 🔧 Features

- 🔌 Power switch (with startup/shutdown sounds)
  - Vintage POWER button with startup/shutdown SFX + glow
  - **Screen shake** when turning on or off (retro current surge effect)
- 🎧 Clicky punch sounds and motor hum synced to movement
- 📟 Paper tape scrolls in real-time with ASCII output
- 🟣 LLM selector (Qwen, TinyDolphin, Granite3-MoE)
- 💡 LED indicators for KSR (keyboard) / ASR (tape) / LLM / JAM status LEDs
- 🔔 EOL BELL support (ASCII `BEL` shown + ding audio)
  - `BEL` glyph shown visually on tape
- 📜 ASCII accurate PNG rendering of punched tape (matplotlib)

- 🧠 LLM integration (multi-model via Ollama API)
  - Dropdown LLM selector (locked while power is ON)
  - Models supported: `qwen2.5:0.5b`, `tinydolphin`, `granite3-moe`
  - System prompt identifies the LLM as a **Teletype Model 33 ASR (1979)**
  - Multiple models run locally with fast, lightweight footprint

- 📠 Realistic paper tape animation with ASCII hole punching
  - PNG images rendered by `matplotlib`
  - Proper header/footer hex codes (#FF, #00)


## Requirements

- Python 3
- Flask
- Matplotlib
- Ollama with supported models (`qwen2.5:0.5b`, `tinydolphin`, etc.)

## Setup

1. **Clone the repo**
2. Install dependencies:

```bash
pip install flask matplotlib requests
```

## Demo

![screenshot](screenshot.png)

## Setup

### 1. Run Ollama locally

Install [Ollama](https://ollama.com) and pull one or more models:

```bash
ollama pull qwen2.5:0.5b
ollama pull tinydolphin
ollama pull granite3-moe:1b
```

### 2. Start the Flask server

```
python3 papertape_server.py
```

### 3. Serve the HTML page

Use any web server (e.g., Apache, Nginx, or Python HTTP):

```
python3 -m http.server
```

## Notes

- Tested on desktop and mobile
- Models run offline — no external API calls
- TAPE JAM if > 16 words
- Audio quirks on mobile are handled with clone cleanup and failsafes

## License

MIT — for the retro hacker in all of us.

