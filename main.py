import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8937174618:AAGb17sFAOUMH7uPaZtFFtSIEjMClyDXcIQ"

# Improved options to bypass TikTok/Instagram blocks
YDL_OPTIONS = {
    'format': 'best[ext=mp4]/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    # This part makes the bot look like a real browser:
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
}

async def download_video(url):
    """Downloads video and returns the file path."""
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        # This will extract info and download the file
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # Check for valid links
    sites = ["instagram.com", "tiktok.com", "youtube.com", "youtu.be", "vxtiktok.com"]
    if any(site in url for site in sites):
        status_msg = await update.message.reply_text("⏳ Processing link... Please wait.")
        
        try:
            file_path = await download_video(url)
            
            # Check file size (Telegram limit 50MB)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            if file_size_mb > 50:
                await status_msg.edit_text(f"❌ File too large ({round(file_size_mb, 1)}MB). Limit is 50MB.")
            else:
                await status_msg.edit_text("✅ Done! Sending...")
                with open(file_path, 'rb') as video:
                    await update.message.reply_video(video=video)
                await status_msg.delete()
            
            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
            
        except Exception as e:
            # If it still fails, suggest updating
            await status_msg.edit_text(f"❌ Error.\n\nTry again in a minute. If it fails again, the site might be blocking the bot.")
            print(f"Error details: {e}")
    else:
        # Not a link we handle
        pass

def main():
    print("Bot starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Running...")
    app.run_polling()

if __name__ == '__main__':
    main()