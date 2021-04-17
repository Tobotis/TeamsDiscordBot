import discord
import random

alphabet_emojis = [
    "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸",
    "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"
]


# Game Class
# noinspection PyUnresolvedReferences
class Game:
    def __init__(self):  # Constructor of game class
        self.category = None  # Category of the game (GAME [Name of the game])
        self.game_manager = None  # Game manager text channel
        self.admin = None  # User who created the game
        self.players = []  # List of all users in the game in the format [user, users voice channel before the game]
        self.team_count = 5  # Number of teams which are playing
        self.game_manager_embed = None  # Embed of game manager (graphical overview)
        self.team_manager_embed = None
        self.random_teams = False  # True if the players should be in random teams, after the start of the game
        self.team_voice_channels = []  # List of all voice channels in the category of the current game
        self.running = False  # True if the game begins
        self.teams = []

    async def setup(self, message):  # Takes a message and creates/setups the game
        self.category = await message.guild.create_category(
            "GAME " + message.content[11:])  # Create the game category with the name => GAME [Name of the game]
        self.game_manager = await self.category.create_text_channel(
            "GameManager")  # Create the game manager text channel (Channel for game settings)
        self.admin = message.author  # The author of the initial message becomes the admin of the game
        self.players.append([self.admin, message.author.voice.channel if message.author.voice is not None else None])  # The admin is added in the players list
        self.update_teams()
        self.add_player_to_teams(self.admin)
        await self.rebuild_game_manager()  # Display the game manager embed in the game manager text channel
        await self.rebuild_team_manager()

    async def handle_message(self, message):  # Takes a message and applies its content to the game
        if message.channel == self.game_manager:  # Check if the message is from the correct channel (only messages
            # in the game manager are accepted)
            if message.author == self.admin:
                if message.content.startswith(
                        "!endGame"):  # Check if the message is the !endGame command => the game should end
                    await self.end_game()  # End the game
                if message.content.startswith(
                        "!startGame"):  # Check if the message is the !startGame command => the game should start
                    await self.start_game()  # Start the game
            elif message.content.startswith("!endGame") or message.content.startswith("!startGame"):
                await message.channel.send(":x: You don't have the permission to start/end the game :x:")
            if message.content.startswith("!team "):
                answer = await self.change_team(message.author, message.content[6:])
                if answer is not None:
                    await message.channel.send(answer)

    async def change_team(self, user, team_string):
        try:
            team_number = int(team_string)
            if 1 > team_number or team_number > self.team_count:
                return "Please use a valid team."
            for team in self.teams:
                if user in team:
                    team.remove(user)
                    break
            else:
                return "You aren't a player in this game."
            self.teams[team_number - 1].append(user)
            await self.team_manager_embed.edit(embed=self.get_team_manager_embed())
        except:
            return "Please use a valid number."

    async def handle_reaction(self, reaction, user):  # Takes a reaction and the associated user and applies it to the game manager
        if reaction.message.channel == self.game_manager and user != client.user:  # Check if the reaction is in the
            # correct channel (only reactions in the game manager are accepted) and if the user is not the bot itself
            if reaction.message == self.game_manager_embed and user == self.admin:
                if reaction.emoji == "⬆️":  # Check if the reaction is the :arrow_up: emoji
                    self.team_count += 1  # Increase the team count
                if reaction.emoji == "⬇️" and self.team_count > 1:  # Check if the reaction is the :arrow_down: emoji
                    self.team_count -= 1  # Decrease the team count

                self.update_teams()

                if reaction.emoji == "🎰":  # Check if the reaction ist the :slot_machine: emoji
                    self.random_teams = not self.random_teams  # Toggle the randomized teams
                    await self.rebuild_game_manager()
                    if self.random_teams:
                        await self.rebuild_team_manager(hide=True)
                    else:
                        await self.rebuild_team_manager()
                elif not self.random_teams:
                    await self.team_manager_embed.edit(embed=self.get_team_manager_embed())
                    await self.game_manager_embed.edit(embed=self.get_game_manager_embed())  # Update the game manager embed => the new changes are
                    # displayed
                    await self.game_manager_embed.clear_reactions()  # Clear the reactions => the users can make a new
                    # reaction
                    await self.add_reactions_to_game_manager_embed()  # Add the default reactions to the embed
            elif reaction.message == self.game_manager_embed:
                await reaction.message.channel.send(":x: You don't have the permission to change settings :x:")



    async def start_game(self):  # Start the game
        if self.running:  # Check if the game is already running
            return
        if self.random_teams:  # Check if the game should start with random teams
            self.teams = []
            for j in range(self.team_count):
                self.teams.append([])
            players = self.players.copy()  # Make a copy of the player list, to shuffle it
            random.shuffle(players)  # Randomize the player list
            team = 0
            for i in range(len(players)):
                self.teams[team].append(self.players[i][0])
                if team < self.team_count - 1:
                    team += 1
                else:
                    team = 0
        print(self.teams)

        for i in range(self.team_count):  # Iterate through all the teams
            vc = await self.category.create_voice_channel("Team " + str(i + 1))  # Create a voice channel for the team with name Team [team index]
            self.team_voice_channels.append(vc)  # Add the voice channel into the voice channel list

        for i in range(len(self.teams)):
            team = self.teams[i]
            for player in team:
                try:
                    await player.move_to(self.team_voice_channels[i])
                except:
                    pass

        self.running = True  # Set the game running

    async def end_game(self):  # Ends and deletes the game
        for player in self.players:  # Iterate through all the players
            await player[0].move_to(
                player[1])  # Move the player to his former voice channel (if its None, the player disconnects)
        for channel in self.category.channels:  # Iterate through all the channels in the game category
            await channel.delete()  # Delete the channel
        await self.category.delete()  # Delete the whole category
        games.remove(self)  # Remove the game from the current games

    async def rebuild_game_manager(self):  # Displays the game manager embed
        if self.game_manager_embed is not None:  # Check if the old game manager embed should be deleted
            # and if there is an old one existing
            await self.game_manager_embed.delete()  # Delete the game manager embed
            self.game_manager_embed = None
        message = await self.game_manager.send(
            embed=self.get_game_manager_embed())  # Send the new embed in the game manager channel

        self.game_manager_embed = message  # Set the new game manager embed

        await self.add_reactions_to_game_manager_embed()  # Add the default reactions to the embed

    async def rebuild_team_manager(self, hide=False):
        if self.team_manager_embed is not None:
            await self.team_manager_embed.delete()
            self.team_manager_embed = None
        if hide:
            return

        message = await self.game_manager.send(embed=self.get_team_manager_embed())
        self.team_manager_embed = message

    async def add_reactions_to_game_manager_embed(
            self):  # Add the default reactions to the embed, so its easier for the user to react
        await self.game_manager_embed.add_reaction("⬆️")
        await self.game_manager_embed.add_reaction("⬇️")
        await self.game_manager_embed.add_reaction("🎰")

    def get_game_manager_embed(self):  # Get the game manager embed
        # Set the embed
        embed = discord.Embed(title="Game Management", colour=discord.Colour(0xd02e1c))
        embed.set_footer(text="Answer by reacting to this message")
        embed.add_field(name="Teams", value=str(self.team_count), inline=True)
        embed.add_field(name="Players", value=str(len(self.players)), inline=True)
        embed.add_field(name="Random Teams :slot_machine:", value=":white_check_mark: " if self.random_teams else ":x:",
                        inline=True)
        return embed  # Return the embed

    def get_team_manager_embed(self):
        embed = discord.Embed(title="Team Management", colour=discord.Colour(0xd02e1c))
        embed.set_footer(text="Change team with: !team [number]")

        for j in range(len(self.teams)):
            team = self.teams[j]
            string = "\u200b"
            if len(team) > 0:
                string = str(team[0].display_name) + "\t"
                for i in range(1, len(team)):
                    string += str(team[i].display_name) + "\n"
            embed.add_field(name="Team " + str(j + 1), value="```" + string + "```")
        return embed

    def update_teams(self):
        while len(self.teams) < self.team_count:
            self.teams.append([])
        while len(self.teams) > self.team_count:
            last_team = self.teams.pop(-1)
            for player in last_team:
                self.add_player_to_teams(player)

    def add_player_to_teams(self, player):
        team_length = []
        for i in range(len(self.teams)):
            team_length.append(len(self.teams[i]))
        self.teams[team_length.index(min(team_length))].append(player)


games = []  # Keeps track of all games which are running


async def create_game(message):  # Create a new game
    name = str(message.content)[12:]  # Take the name of the game
    already_used = False  # True if the name is already in use
    for game in games:  # Iterate through all the current games
        if name.upper() == game.category.name.upper()[6:]:  # Check if the name is the same
            already_used = True  # The name is already in use
    if len(str(message.content).replace(" ", "")) < 12:  # Check if there is even a game name
        await message.channel.send("No valid !startGame command: !startGame [game title]")  # Send an explanation
    elif already_used:  # Check if the name is already in use
        await message.channel.send("The name is already in use :slight_frown:")  # Send an explanation
    else:  # Create a new game
        game = Game()  # Instantiate a new Game
        games.append(game)  # Add it in the list of the current games
        await game.setup(message)  # Setup the game


async def join_game(message):  # Join a game
    name = message.content[10:]  # Get the name of the game
    for game in games:  # Iterate through all the current games
        if name.upper() == game.category.name.upper()[
                           6:]:  # Check if the name in the message is the same as the game name
            if message.author not in game.players:  # Check if the joining user is not already in the game
                game.players.append([message.author,
                                     message.author.voice.channel if message.author.voice is not None else None])  # Add the user to the players
                game.add_player_to_teams(message.author)
                await game.game_manager.send(
                    str(
                        message.author.display_name) + " joined the game. Have fun! Be nice!")  # Send a announcement in the game manager channel
                await game.rebuild_game_manager()  # Rebuild the game manager embed and delete the old one
                if game.random_teams:
                    await game.rebuild_team_manager(hide=True)
                else:
                    await game.rebuild_team_manager()
                break
            else:  # The user is already in the game
                await message.channel.send("You are currently a player in this game.")  # Send an explanation
                break
    else:  # There is no game wit the name
        await message.channel.send("No game found with name: " + name.upper())  # Send an explanation


# The main Bot/Client class (inherits from the discord.client)
# noinspection PyMethodMayBeStatic
class Client(discord.Client):
    async def on_ready(self):  # The bot is running
        print("Bot initialized...")
        guilds = client.guilds  # Get all the guilds/server of the bot
        for guild in guilds:  # Iterate through all the guilds
            cat_channels = guild.categories  # Get all the categories of this guild
            for cat_channel in cat_channels:  # Iterate through all the categories in the guild
                if cat_channel.name.startswith("GAME "):  # Check if the category is a GAME
                    for channel in cat_channel.channels:  # Iterate through all the channels in this category
                        await channel.delete()  # Delete the channel
                    await cat_channel.delete()  # Delete the category

    async def on_message(self, message):  # There is a message
        if message.author == client.user:  # Check if the author of the message is the bot itself
            return
        if message.content.startswith(
                "!createGame "):  # Check if the message is the !createGame command => a game should be created
            await create_game(message)  # Create a game

        if message.content.startswith(
                "!joinGame "):  # Check if the message is the !join command => the author wants to join a game
            await join_game(message)  # Join a game

        for game in games:  # Iterate through all the games
            if message.channel.category == game.category:  # Check if the message is in the category of the game
                await game.handle_message(message)  # Handle the message of a specific game

    async def on_reaction_add(self, reaction, user):  # There is a reaction
        for game in games:  # Iterate through all the games
            if reaction.message.channel.category == game.category:  # Check if the reaction is in the category of the
                # game
                await game.handle_reaction(reaction, user)  # Handle the reaction of a specific game


client = Client()  # Instantiate the client
client.run("ODMyMjE3MzIyOTgyNDczNzk4.YHgkxw.f2TwACwDW2qxSOuzJtXrOwnuGYI")  # Run the client

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
