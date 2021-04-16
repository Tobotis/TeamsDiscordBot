import discord


class Game:
    def __init__(self):
        self.category = None
        self.game_manager = None
        self.admin = None
        self.players = []

    async def setup(self, message):
        self.category = await message.guild.create_category("GAME " + message.content[11:])
        self.game_manager = await self.category.create_text_channel("GameManager")
        self.admin = message.author
        self.players.append(self.admin)

    async def handle_message(self, message):
        if message.channel == self.game_manager:
            if message.content.startswith("!endGame"):
                for channel in self.category.channels:
                    await channel.delete()
                await self.category.delete()
                games.remove(self)


games = []


async def start_game(message):
    name = str(message.content)[12:]
    already_used = False
    for game in games:
        if name.upper() == game.category.name.upper()[5:]:
            already_used = True
    if len(str(message.content).replace(" ", "")) < 12:
        await message.channel.send("No valid !startGame command: !startGame [game title]")
    elif already_used:
        await message.channel.send("The name is already in use :slight_frown:")
    else:
        game = Game()
        games.append(game)
        await game.setup(message)


async def join_game(message):
    name = message.content[10:]
    for game in games:
        if name.upper() == game.category.name.upper()[5:]:
            if message.author not in game.players:
                game.players.append(message.author)
                await game.game_manager.send(str(message.author).split("#")[0] + " joined the game. Have fun! Be nice!")
            else:
                await message.channel.send("You currently are a player in this game.")
    else:
        await message.channel.send("No game found with name: " + name.upper())

class Client(discord.Client):
    async def on_ready(self):
        print("Bot initialized...")

    async def on_message(self, message):
        if message.author == client.user:
            return
        if message.content.startswith("!createGame"):
            await start_game(message)

        if message.content.startswith("!joinGame"):
            await join_game(message)

        for game in games:
            if message.channel.category == game.category:
                await game.handle_message(message)

        # await message.channel.send("Message received.")


client = Client()
client.run("ODMyMjE3MzIyOTgyNDczNzk4.YHgkxw.f2TwACwDW2qxSOuzJtXrOwnuGYI")
