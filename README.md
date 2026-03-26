# amino_tools

> Advanced automation toolkit for Aminoapps with enhanced security and performance.

## Features

- Spam messages to chats, wikis, walls and blogs
- Retrieve chat IDs (public & joined)
- Fake coin transfer display
- Spam system messages
- Spam chat join & leave notifications
- Invite online users to a chat
- Like recent blogs
- Follow / unfollow online users
- Bulk publish blogs and wikis

## Installation

### Termux

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git
git clone https://github.com/vraestoren/amino_tools
cd amino_tools
pip install -r requirements.txt
python main.py
```

### Linux / Windows

```bash
git clone https://github.com/vraestoren/amino_tools
cd amino_tools
pip install -r requirements.txt
python main.py
```

## Requirements

```
amino.py
tabulate
```

## Usage

Run `main.py` and follow the prompts then login with your Amino email and password, pick a community, then choose a tool from the menu.
