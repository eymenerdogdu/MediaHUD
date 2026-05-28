# MediaHUD

<p align="center">
  <img src="[https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue?style=flat-for-the-badge](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue?style=flat-for-the-badge)" alt="Platform Compatibility">
  <img src="[https://img.shields.io/badge/Framework-PyQt5-green?style=flat-for-the-badge](https://img.shields.io/badge/Framework-PyQt5-green?style=flat-for-the-badge)" alt="PyQt5">
  <img src="[https://img.shields.io/badge/License-MIT-yellow?style=flat-for-the-badge](https://img.shields.io/badge/License-MIT-yellow?style=flat-for-the-badge)" alt="License">
</p>

<pre>
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ┌────┐                                                     ║
║   │   ─┐    MediaHUD :: CrossPlatform Media Indicator        ║
║   │   ─┘    Designed & Engineered by Eymen ERDOĞDU           ║
║   └────┘    github.com/eymenerdogdu                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
</pre>

**MediaHUD** is a lightweight, frameless, and modern **cross-platform media indicator** that hooks into your operating system's native APIs to monitor background audio and media playback. It does not play audio files natively; instead, it acts as a sleek HUD panel and remote proxy to display and control status from active system media players.

## ✨ Features

- 🖥️ **Cross-Platform:** Native integration via DBus/MPRIS on Linux and WinRT/GlobalSystemMediaTransportControls on Windows.
- 🎨 **Minimalist Design:** Frameless, compact 380x105px interface that can be freely dragged anywhere on your desktop.
- 📌 **Always on Top:** Stays persistent over other application windows (`WindowStaysOnTopHint`) for instant widget access.
- 📜 **Dynamic Text Scrolling:** Automatically scrolls long track titles smoothly without breaking the layout.
- 🖼️ **Smart Album Art:** Seamlessly processes cover art from Spotify or local media sources (Supports both local `file://` protocols and Web URLs).
- 🎛️ **Universal Control:** Bridges Play/Pause, Previous, and Next commands directly back to the active source player.

## 🚀 Installation

Ensure you have **Python 3.x** and **PyQt5** installed on your machine. Follow the steps below according to your specific operating system to resolve the necessary backend dependencies:

### 1. Base Framework Dependency
`pip install PyQt5`

### 2. Platform-Specific Backends

#### 🐧 On Linux:
To interact with the system-wide messaging bus (`DBus`):
`pip install dbus-python`

#### 🪟 On Windows:
To handle asynchronous requests sent to the Windows Media Control Manager (`WinRT`):
`pip install winrt-Windows.Media.Control`

## 💻 Usage

Clone this repository or grab the raw source code, then spin it up via your command-line interface:
`python media_hud.py`

- **Drag & Move:** Hold down your mouse left-click anywhere on the interface to reposition the HUD panel.
- **Window Controls:** Minimize to the taskbar or terminate the process using the custom-styled top-right button utilities.

## 📄 License

This project is licensed under the terms of the [MIT](LICENSE) license.
