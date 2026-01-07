# Termux Instagram Bot 2026 🤖📱

A professional, interactive Instagram automation bot designed **specifically for Termux on Android**.

**Developed With ❤️ By 📸 [@rithikvinayak_](https://instagram.com/rithikvinayak_)**

## ✨ Key Features

### 🎯 **Bot Liker & Commenter**
*   **Advanced Targeting**: Interact with posts based on:
    *   **Hashtags** (Recent/Top)
    *   **Locations** (City/Place)
    *   **Followers** of a specific user
    *   **Followings** of a specific user
*   **Human Simulation**: Randomized delays and sleep cycles to avoid detection.

### 👀 **Story Watcher**
*   **Mass Watch**: Automatically view stories from your feed or specific targets.
*   **Auto-Like**: Option to like every story you watch.

### 🛡️ **Security & Stability**
*   **Anti-Ban**: Saves sessions/cookies locally.
*   **Robust**: Handles API errors, network issues, and 2FA challenges gracefully.

---

## 🚀 Installation Guide (Termux)

Open your Termux app and run these commands:

### 1. Install Dependencies
```bash
pkg update && pkg upgrade -y
pkg install python git rust binutils pkg-config libjpeg-turbo -y
```

### 2. Clone Repository
```bash
git clone https://github.com/rithikclicks/Termux-Instagram-Bot-2026.git
cd Termux-Instagram-Bot-2026
```

### 3. Install Python Libraries
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Bot! 🏁
```bash
python rithik.py
```

---

## 🎮 How to Use

1.  **Login**: Use **Option 5 ("Config")** -> **Edit Credentials** to login safely.
    *   *Supports 2FA (SMS/Authenticator).*
2.  **Configure Services**:
    *   **[1] Bot Liker**: Set your target (e.g., `#viral`, `@competitor`) and speed.
    *   **[2] Bot Commenter**: Add your custom comments list.
    *   **[3] Story Watcher**: Turn on "Like Stories" for extra engagement.
3.  **Start Protection**: Select **Option 4 (Start Bot)** to begin the automation loop.
4.  **Stop**: Press `Ctrl + C` to exit.

---

## ⚠️ Safety Warning
*   **Start Slow**: Use higher delays (e.g., 60-120 seconds) on day 1.
*   *This tool is for educational purposes.*

## 📝 License
Proprietary. Unauthorized distribution is prohibited.
