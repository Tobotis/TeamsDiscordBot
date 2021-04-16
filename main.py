
import discord

class Client(discord.Client):
    async def on_ready(self):
        print("Bot initialized...")

client = Client()
client.run("ODMyMjE3MzIyOTgyNDczNzk4.YHgkxw.f2TwACwDW2qxSOuzJtXrOwnuGYI")