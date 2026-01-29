import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# 🔐 Apna Bot Token yaha daalo
BOT_TOKEN ="8452924134:AAGqqVp4_3GWFclIXkEv1ydvSQLdk60fuxY"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 YouTube Video Downloader Bot!\n\n"
        "YouTube video URL bhejo, main video download kar ke bhej dunga!\n"
        "📱 Mobile + 💻 Desktop dono support karta hai."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    status_msg = await update.message.reply_text("⏳ Video download ho rahi hai...")

    try:
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': '%(title)s.%(ext)s',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')

        video_file = f"{title}.mp4" if os.path.exists(f"{title}.mp4") else f"{title}.webm"

        if os.path.exists(video_file):
            size_mb = os.path.getsize(video_file) / (1024 * 1024)

            if size_mb <= 50:
                with open(video_file, 'rb') as video:
                    await update.message.reply_video(
                        video=video,
                        caption=f"✅ Downloaded: {title}\n📁 Size: {round(size_mb, 2)} MB"
                    )
            else:
                await status_msg.edit_text("❌ File 50MB se badi hai. Audio bhej raha hun...")
                await send_audio(update, url)

            os.remove(video_file)
        else:
            await status_msg.edit_text("❌ Video download nahi hui.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}\nValid YouTube URL bhejo!")

async def send_audio(update: Update, url: str):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')

        audio_file = f"{title}.mp3"

        if os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    caption=f"🎵 Audio: {title}"
                )
            os.remove(audio_file)

    except:
        pass

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
