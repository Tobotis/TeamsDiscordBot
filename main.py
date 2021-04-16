import discord
import random


class Game:
    def __init__(self):
        self.category = None
        self.game_manager = None
        self.admin = None
        self.players = []
        self.team_count = 2
        self.game_manager_embed = None
        self.random_teams = False
        self.team_voice_channels = []
        self.running = False

    async def setup(self, message):
        self.category = await message.guild.create_category("GAME " + message.content[11:])
        self.game_manager = await self.category.create_text_channel("GameManager")
        self.admin = message.author
        self.players.append([self.admin, message.author.voice.channel])
        await self.display_game_manager()

    async def handle_message(self, message):
        if message.channel == self.game_manager:
            if message.content.startswith("!endGame"):
                for player in self.players:
                    await player[0].move_to(player[1])
                for channel in self.category.channels:
                    await channel.delete()
                await self.category.delete()
                games.remove(self)
            if message.content.startswith("!startGame"):
                await self.start_game()

    async def handle_reaction(self, reaction, user):
        if reaction.message.channel == self.game_manager and user != client.user:
            if reaction.emoji == "⬆️":
                self.team_count += 1
            if reaction.emoji == "⬇️":
                self.team_count -= 1
            if reaction.emoji == "🎰":
                self.random_teams = not self.random_teams

            await self.game_manager_embed.edit(embed=self.get_embed())
            await self.game_manager_embed.clear_reactions()
            await self.add_reactions_to_embed()

    async def start_game(self):
        if self.running:
            return
        if self.random_teams:
            players = self.players.copy()
            random.shuffle(players)
            for i in range(self.team_count):
                vc = await self.category.create_voice_channel("Team " + str(i + 1))
                self.team_voice_channels.append(vc)
            team = 0
            for player in players:
                await player[0].move_to(self.team_voice_channels[team], reason="Game started")
                if team < self.team_count - 1:
                    team += 1
                else:
                    team = 0
        running = True

    async def display_game_manager(self, delete=False):
        if delete and self.game_manager_embed is not None:
            await self.game_manager_embed.delete()

        message = await self.game_manager.send(embed=self.get_embed())

        self.game_manager_embed = message

        await self.add_reactions_to_embed()

    def get_embed(self):
        embed = discord.Embed(title="Game Management", colour=discord.Colour(0xd02e1c))

        embed.set_footer(text="Answer by reacting to this message")

        embed.add_field(name="Teams", value=str(self.team_count), inline=True)
        embed.add_field(name="Players", value=str(len(self.players)), inline=True)
        embed.add_field(name="Random Teams :slot_machine:", value=":white_check_mark: " if self.random_teams else ":x:",
                        inline=True)
        return embed

    async def add_reactions_to_embed(self):
        await self.game_manager_embed.add_reaction("⬆️")
        await self.game_manager_embed.add_reaction("⬇️")
        await self.game_manager_embed.add_reaction("🎰")


games = []


async def create_game(message):
    name = str(message.content)[12:]
    already_used = False
    for game in games:
        if name.upper() == game.category.name.upper()[6:]:
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
        if name.upper() == game.category.name.upper()[6:]:
            if message.author not in game.players:
                game.players.append([message.author, message.author.voice.channel])
                await game.game_manager.send(
                    str(message.author).split("#")[0] + " joined the game. Have fun! Be nice!")
                await game.display_game_manager(delete=True)
                break
            else:
                await message.channel.send("You are currently a player in this game.")
                break
    else:
        await message.channel.send("No game found with name: " + name.upper())


class Client(discord.Client):
    async def on_ready(self):
        print("Bot initialized...")
        guilds = client.guilds
        for guild in guilds:
            cat_channels = guild.categories
            for cat_channel in cat_channels:
                if cat_channel.name.startswith("GAME "):
                    for channel in cat_channel.channels:
                        await channel.delete()
                    await cat_channel.delete()

    async def on_message(self, message):
        if message.author == client.user:
            return
        if message.content.startswith("!createGame "):
            await create_game(message)

        if message.content.startswith("!joinGame "):
            await join_game(message)

        for game in games:
            if message.channel.category == game.category:
                await game.handle_message(message)

    async def on_reaction_add(self, reaction, user):
        for game in games:
            if reaction.message.channel.category == game.category:
                await game.handle_reaction(reaction, user)


client = Client()
client.run("ODMyMjE3MzIyOTgyNDczNzk4.YHgkxw.f2TwACwDW2qxSOuzJtXrOwnuGYI")

'''{
  "embed": {
    "title": "Players",
    "color": 13643292,
    "fields": [
     
      {
        "name":"Team :one:",
        "value": "```Heiholf\tTobotis\nFridolin\nHannes```",
        "inline": true
      },
      {
        "name":"Team :two:",
        "value": "```Heiholf\tTobotis\nFridolin\nHannes```",
        "inline": true
      },
      {
        "name":"Team :three:",
        "value": "```Heiholf\tTobotis\nFridolin\nHannes```",
        "inline": true
      },
      {
        "name":"Team :four:",
        "value": "```Heiholf\tTobotis\nFridolin\nHannes```",
        "inline": true
      },
      {
        "name":"Team :five:",
        "value": "```Heiholf\tTobotis\nFridolin\nHannes```",
        "inline": true
      }
    ]
  }
}'''