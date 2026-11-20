import asyncio
import os

import discord
import requests
from discord.ext import commands

from index import get_ibb_metro_datasets


COMMAND_PREFIX = "!"
TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
startup_notified = False


@bot.event
async def on_ready():
    global startup_notified
    print(f"{bot.user} olarak giriş yapıldı.")

    if startup_notified:
        return

    startup_notified = True
    for guild in bot.guilds:
        channel = guild.system_channel
        if channel is None:
            print(f"{guild.name}: Sistem kanalı ayarlanmamış; bildirim gönderilmedi.")
            continue

        try:
            await channel.send(f"{bot.user} başlatıldı ve çevrimiçi.")
        except discord.Forbidden:
            print(f"{guild.name}: Sistem kanalına mesaj gönderme izni yok.")
        except discord.HTTPException as error:
            print(f"{guild.name}: Başlatma bildirimi gönderilemedi: {error}")


@bot.command()
async def ping(ctx):
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f"Pong! {latency_ms} ms")


@bot.command()
async def merhaba(ctx):
    await ctx.send(f"Merhaba {ctx.author.mention}!")
@bot.command()
async def metro(ctx):
    try:
        metro_lines = await asyncio.to_thread(get_ibb_metro_datasets)
    except requests.exceptions.Timeout:
        await ctx.send("İBB veri sunucusu zaman aşımına uğradı. Biraz sonra tekrar dene.")
        return
    except requests.exceptions.RequestException as error:
        print(f"İBB metro verisi alınamadı: {error}")
        await ctx.send("İBB metro verisi şu anda alınamıyor. Daha sonra tekrar dene.")
        return
    except (KeyError, ValueError) as error:
        print(f"İBB metro verisi beklenmeyen formatta: {error}")
        await ctx.send("İBB metro verisi beklenmeyen bir formatta geldi.")
        return

    if metro_lines:
        response_message = "İBB Metro Hatları:\n"
        for line in metro_lines:
            response_message += f"- {line['name']}: {line['url']}\n"
        await ctx.send(response_message)
    else:
        await ctx.send("Metro hatları verisi alınamadı.")

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN ortam değişkeni tanımlı değil.")

    bot.run(TOKEN)