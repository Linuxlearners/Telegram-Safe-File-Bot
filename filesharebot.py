import os
import sys
import asyncio
import threading
import uuid
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ================= AUTO INSTALL =================
def ensure_package(import_name, install_name):
    try:
        __import__(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])

ensure_package("telegram", "python-telegram-bot")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= DEFAULT SETTINGS =================
DEFAULT_BOT_TOKEN = "YOUR_BOT_TOKEN"
DEFAULT_ADMIN_IDS = "123456789"
DEFAULT_SECURITY_MODE = "Custom"  # "Any" or "Custom"

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ITEMS_PER_PAGE = 15

# Safe Tree Limits
MAX_TREE_DEPTH = 3
MAX_TREE_LINES = 300
TELEGRAM_MSG_LIMIT = 3500

BOT_TOKEN = None
SHARED_FOLDER = None
AUTHORIZED_USERS_LIST = []
SECURITY_MODE = "Any"
USER_FILE_MAP = {}

# ================= SAFE TREE =================
def build_tree_safe(path, prefix="", depth=0, lines=None):
    if lines is None:
        lines = []

    if depth > MAX_TREE_DEPTH or len(lines) > MAX_TREE_LINES:
        return lines

    try:
        items = sorted(os.listdir(path))
    except Exception:
        return lines

    for index, item in enumerate(items):
        if len(lines) > MAX_TREE_LINES:
            break

        full_path = os.path.join(path, item)
        connector = "┗ " if index == len(items) - 1 else "┣ "
        next_prefix = "   " if index == len(items) - 1 else "┃  "

        if os.path.isdir(full_path):
            lines.append(f"{prefix}{connector}📂 {item}")
            build_tree_safe(full_path, prefix + next_prefix, depth + 1, lines)
        else:
            lines.append(f"{prefix}{connector}📄 {item}")

    return lines

async def send_tree(update):
    root_name = os.path.basename(SHARED_FOLDER)
    lines = [f"📂 {root_name}"]
    lines.extend(build_tree_safe(SHARED_FOLDER))

    if len(lines) >= MAX_TREE_LINES:
        lines.append("⚠ Showing partial tree (safe mode enabled)")

    tree_text = "\n".join(lines)

    for i in range(0, len(tree_text), TELEGRAM_MSG_LIMIT):
        await update.message.reply_text(tree_text[i:i + TELEGRAM_MSG_LIMIT])

# ================= PAGINATED KEYBOARD =================
def build_keyboard(user_id, current_path, page=0):
    if user_id not in USER_FILE_MAP:
        USER_FILE_MAP[user_id] = {}

    keyboard = []

    try:
        items = sorted(os.listdir(current_path))
    except Exception:
        items = []

    total_pages = (len(items) - 1) // ITEMS_PER_PAGE + 1 if items else 1
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = items[start:end]

    # Back button
    if os.path.abspath(current_path) != os.path.abspath(SHARED_FOLDER):
        parent = os.path.dirname(current_path)
        back_id = str(uuid.uuid4())[:8]
        USER_FILE_MAP[user_id][back_id] = parent
        keyboard.append(
            [InlineKeyboardButton("⬆ Back", callback_data=f"DIR|{back_id}|0")]
        )

    for item in page_items:
        full_path = os.path.join(current_path, item)
        short_id = str(uuid.uuid4())[:8]
        USER_FILE_MAP[user_id][short_id] = full_path

        if os.path.isdir(full_path):
            keyboard.append(
                [InlineKeyboardButton(f"📁 {item}/", callback_data=f"DIR|{short_id}|0")]
            )
        else:
            size_mb = round(os.path.getsize(full_path) / (1024 * 1024), 2)
            keyboard.append(
                [InlineKeyboardButton(
                    f"📄 {item} ({size_mb}MB)",
                    callback_data=f"FILE|{short_id}|0"
                )]
            )

    # Pagination buttons
    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton("⬅ Prev", callback_data=f"PAGE|{current_path}|{page-1}")
        )
    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton("Next ➡", callback_data=f"PAGE|{current_path}|{page+1}")
        )
    if nav:
        keyboard.append(nav)

    return InlineKeyboardMarkup(keyboard)

# ================= BOT HANDLERS =================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if SECURITY_MODE == "Custom" and user_id not in AUTHORIZED_USERS_LIST:
        await update.message.reply_text(f"❌ Access Denied\nYour ID: {user_id}")
        return

    await send_tree(update)

    markup = build_keyboard(user_id, SHARED_FOLDER, 0)
    await update.message.reply_text(
        "📁 Navigation: Browse folders below",
        reply_markup=markup
    )

async def handle_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if SECURITY_MODE == "Custom" and user_id not in AUTHORIZED_USERS_LIST:
        await query.answer("Unauthorized", show_alert=True)
        return

    data = query.data.split("|")
    action = data[0]

    if action == "PAGE":
        path = data[1]
        page = int(data[2])
        markup = build_keyboard(user_id, path, page)
        await query.edit_message_reply_markup(reply_markup=markup)
        return

    short_id = data[1]
    target = USER_FILE_MAP.get(user_id, {}).get(short_id)

    if not target or not os.path.exists(target):
        await query.answer("Not found", show_alert=True)
        return

    if action == "FILE":
        file_size = os.path.getsize(target)
        if file_size > MAX_FILE_SIZE:
            await query.answer("File exceeds 50MB limit", show_alert=True)
            return

        msg = await query.message.reply_text("Uploading...")

        try:
            with open(target, "rb") as f:
                await query.message.reply_document(
                    f,
                    read_timeout=300,
                    write_timeout=300,
                    connect_timeout=60,
                )
            await msg.edit_text("Upload complete ✅")
        except Exception as e:
            await msg.edit_text(f"Upload failed ❌\n{str(e)}")

    elif action == "DIR":
        markup = build_keyboard(user_id, target, 0)
        await query.edit_message_text(
            f"📂 {os.path.basename(target)}",
            reply_markup=markup
        )

# ================= BOT START =================
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .connect_timeout(60)
        .read_timeout(300)
        .write_timeout(300)
        .pool_timeout(60)
        .build()
    )

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(handle_click))

    app.run_polling(drop_pending_updates=True)

# ================= GUI =================
def start_bot():
    global BOT_TOKEN, SHARED_FOLDER, AUTHORIZED_USERS_LIST, SECURITY_MODE

    BOT_TOKEN = token_entry.get().strip()
    SHARED_FOLDER = folder_label.cget("text")
    SECURITY_MODE = security_var.get()

    if not BOT_TOKEN or not os.path.isdir(SHARED_FOLDER):
        messagebox.showerror("Error", "Check token and folder.")
        return

    if SECURITY_MODE == "Custom":
        try:
            AUTHORIZED_USERS_LIST = [
                int(x.strip())
                for x in userid_entry.get().split(",")
                if x.strip()
            ]
        except:
            messagebox.showerror("Error", "Invalid User ID format.")
            return

    start_btn.config(state="disabled")
    stop_btn.config(state="normal")
    status_label.config(text="Bot Running ✅", foreground="green")

    threading.Thread(target=run_bot, daemon=True).start()

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_label.config(text=folder)

# GUI Window
root = tk.Tk()
root.title("Telegram Safe File Bot")
root.geometry("500x550")

ttk.Label(root, text="Bot Token:").pack(pady=5)
token_entry = ttk.Entry(root, width=60)
token_entry.insert(0, DEFAULT_BOT_TOKEN)
token_entry.pack()

ttk.Label(root, text="Security Mode:").pack(pady=5)
security_var = tk.StringVar(value=DEFAULT_SECURITY_MODE)

frame = ttk.Frame(root)
frame.pack()
ttk.Radiobutton(frame, text="Public", variable=security_var, value="Any").pack(side="left", padx=10)
ttk.Radiobutton(frame, text="Private", variable=security_var, value="Custom").pack(side="left", padx=10)

ttk.Label(root, text="Admin User IDs (comma separated):").pack(pady=5)
userid_entry = ttk.Entry(root, width=45)
userid_entry.insert(0, DEFAULT_ADMIN_IDS)
userid_entry.pack()

ttk.Button(root, text="Select Shared Folder", command=choose_folder).pack(pady=10)
folder_label = ttk.Label(root, text="Select folder", wraplength=450)
folder_label.pack()

start_btn = ttk.Button(root, text="START BOT", command=start_bot)
start_btn.pack(pady=20)

stop_btn = ttk.Button(root, text="STOP & EXIT", command=lambda: os._exit(0))
stop_btn.pack()

status_label = ttk.Label(root, text="Bot Offline ❌", foreground="red")
status_label.pack(pady=10)

root.mainloop()