import discord
from discord.ext import commands
import yt_dlp
import os

# আপনার টোকেনটি সরাসরি এনভায়রনমেন্ট থেকে নেওয়া হচ্ছে
TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True 
bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch', 
    'quiet': True
}

@bot.event
async def on_ready():
    # এটি বটের কমান্ডগুলোকে ডিসকর্ড সার্ভারের সাথে সিঙ্ক করবে
    await bot.tree.sync()
    print(f'Logged in as {bot.user} - কমান্ড সিঙ্ক হয়েছে!')

@bot.tree.command(name="play", description="গান বাজান")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    if not interaction.user.voice:
        await interaction.followup.send("প্রথমে একটি ভয়েস চ্যানেলে জয়েন করুন!")
        return

    channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        voice_client = await channel.connect()
    elif voice_client.channel != channel:
        await voice_client.move_to(channel)

    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url2 = info['url']

        player = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
        voice_client.play(player)
        await interaction.followup.send(f'বাজছে: {info.get("title")}')
    except Exception as e:
        await interaction.followup.send(f"গান বাজাতে সমস্যা হয়েছে: {e}")

bot.run(TOKEN)