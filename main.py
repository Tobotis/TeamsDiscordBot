import discord


class Client(discord.Client):
    async def on_ready(self):
        print("Bot initialized...")

    async def on_message(self, message):
        if message.author == client.user:
            return
        await message.channel.send("Message received.")


client = Client()
client.run("ODMyMjE3MzIyOTgyNDczNzk4.YHgkxw.f2TwACwDW2qxSOuzJtXrOwnuGYI")
