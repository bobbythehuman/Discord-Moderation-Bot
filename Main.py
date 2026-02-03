import re
import datetime
import asyncio  # await asyncio.sleep(5)
# discord.py == 1.7.3
import discord
import sqlite3
from typing import Optional, Union, List, Dict, Any, Iterable
from discord.ext import commands
# discord-py-slash-command == 3.0.3
from discord_slash import (
    SlashCommand,
    SlashContext,
)
from discord_slash.utils.manage_commands import create_choice, create_option


TOKEN = ''

# Used for private or testing commands in specific guilds/ servers
PRIVATE_GUILD_IDS: List[int] = []


# for reference of option types
"""
SUB_COMMAND = 1
SUB_COMMAND_GROUP = 2
STRING = 3
INTEGER = 4
BOOLEAN = 5
USER = 6
CHANNEL = 7
ROLE = 8
MENTIONABLE = 9
FLOAT = 10
"""


class Users:
    def __init__(self, user: Union[discord.User, discord.Member]) -> None:
        userID = getattr(user, "id", None)
        userName = getattr(user, "name", None)
        if not userID or not userName:
            raise Exception("Invalid user provided")
        self.id = userID
        self.name = userName
        self.user = user
        self.warnings: List[Dict[str, Any]] = []

    def warn(
        self,
        givenBy: Union[discord.User, discord.Member, discord.ClientUser],
        reason: str,
        time: datetime.datetime,
    ) -> None:
        def myFunc(e: Dict[str, Any]) -> datetime.datetime:
            return e["time"]

        warning = {
            "id": len(self.warnings) + 1,
            "reason": reason,
            "time": time,
            "givenBy": givenBy,
        }
        self.warnings.append(warning)
        self.warnings.sort(key=myFunc, reverse=True)

    def check(self, msgCount: int, timeFrame: float) -> bool:
        convertedTimeFrame = datetime.timedelta(0, timeFrame, 0, 500)
        recent = self.warnings[0]
        last = self.warnings[msgCount - 1]
        total = recent["time"] - last["time"]
        if total <= convertedTimeFrame:
            return True
        else:
            return False

    def getWarnings(self) -> List[Dict[str, Any]]:
        return self.warnings

    def getName(self) -> str:
        return self.name


class Servers:
    def __init__(self, server: discord.Guild) -> None:
        self.id = server.id
        self.guild = server
        self.words: list[str] = [
            "fuck",
            "bitch",
            "cunt",
            "nigga",
            "bastard",
            "nigger",
            "shit",
            "retard",
        ]
        self.letters: dict[str, list[str]] = {
            "a": ["a", "A", "&", "@", "à", "á", "â", "ä", "æ", "ã", "å", "ā"],
            "b": ["b", "B", "8", "ß"],
            "c": ["c", "C", "ç", "ć", "č", "(", "k"],
            "d": ["d", "D"],
            "e": ["e", "E", "3", "è", "é", "ê", "ë", "ē", "ė", "ę"],
            "f": ["f", "F"],
            "g": ["g", "G", "9"],
            "h": ["h", "H"],
            "i": ["i", "I", "1", "î", "ï", "í", "ī", "į", "ì", "ł"],
            "j": ["j", "J"],
            "k": ["k", "K", "c"],
            "l": ["l", "L", "1", "ł"],
            "m": ["m", "M"],
            "n": ["n", "N", "ñ", "ń"],
            "o": ["o", "O", "0", "ô", "ö", "ò", "ó", "œ", "ø", "ō", "õ"],
            "p": ["p", "P"],
            "q": ["q", "Q"],
            "r": ["r", "R"],
            "s": ["s", "S", "5", "ś", "š"],
            "t": ["t", "T", "7"],
            "u": ["u", "U", "û", "ü", "ù", "ú", "ū"],
            "v": ["v", "V"],
            "w": ["w", "W", "ŵ"],
            "x": ["x", "X", "+"],
            "y": ["y", "Y", "ŷ"],
            "z": ["z", "Z", "ž", "ź", "ż"],
        }
        self.seperate: list[str] = [".", ","]
        self.users: list[Users] = []
        self.timeGap: str = "30m"
        self.warnCount: int = 3
        self.muteDuration: str = "10m"
        self.reportChannels: list = []
        self.requiredRoles: list = []
        self.channels: list = [server.channels]
        self.roles: list = [server.roles]

    ###
    def addWord(self, word: str) -> None:
        self.words.append(word)

    def getWords(self) -> list[str]:
        return self.words

    def removeWord(self, word: str) -> None:
        self.words.remove(word)

    ###
    def addSeperator(self, punc: str) -> None:
        self.seperate.append(punc)

    def getSeperator(self) -> list[str]:
        return self.seperate

    def removeSeperator(self, punc: str) -> None:
        self.seperate.remove(punc)

    ###
    def addLetter(self, letter: str, char: str) -> None:
        self.letters[letter].append(char)

    def getLetter(self, letter: str = "") -> dict[str, list[str]] | list[str]:
        if letter:
            return self.letters[letter]
        else:
            return self.letters

    def removeLetter(self, letter: str, char: str) -> None:
        self.letters[letter].remove(char)

    ###
    def addUser(self, user: Users) -> None:
        self.users.append(user)

    def getUsers(self) -> list[Users]:
        return self.users

    ###
    def addChannel(self, channel: discord.TextChannel) -> None:
        self.reportChannels.append(channel)

    def getChannels(self) -> list[discord.TextChannel]:
        return self.reportChannels

    def removeChannel(self, channel: discord.TextChannel) -> None:
        self.reportChannels.remove(channel)

    ###
    def addRole(self, role: discord.Role) -> None:
        self.requiredRoles.append(role)

    def getRoles(self) -> list[discord.Role]:
        return self.requiredRoles

    def removeRole(self, role: discord.Role) -> None:
        self.requiredRoles.remove(role)

    ###
    def updateMuteTime(self, time: str) -> None:
        self.muteDuration = time

    def getMuteTime(self) -> str:
        return self.muteDuration

    ###
    def updateWarnCount(self, count: int) -> None:
        self.warnCount = count

    def getWarnCount(self) -> int:
        return self.warnCount

    ###
    def updateTimeFrame(self, time: str) -> None:
        self.timeGap = time

    def getTimeFrame(self) -> str:
        return self.timeGap

    ####


###
class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", help_command=None)
        self.server = []
        self.conn = sqlite3.connect("guild_data.db")
        self.cursor = self.conn.cursor()
        slash = SlashCommand(self, sync_commands=True)

        @slash.slash(
            name="ping",
            description="Display bot ping",
            guild_ids=PRIVATE_GUILD_IDS
        )
        async def ping(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                return
            else:
                print("ping")
                await ctx.send(f"Client Latency: {round(self.latency * 1000)}")

        @slash.slash(
            name="server",
            description="Display server info",
            guild_ids=PRIVATE_GUILD_IDS)
        async def server(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                return
            else:
                for aServer in self.server:
                    print("--------------------------------------------------------")
                    print("id:", aServer.id)
                    print("word list:", aServer.getWords())
                    print("letter list:", aServer.getLetter())
                    print("seperator list:", aServer.getSeperator())
                    print("time gap:", aServer.timeGap)
                    print("warn count:", aServer.warnCount)
                    print("mute duration", aServer.muteDuration)
                    print("channels:", aServer.getChannels())
                    print("roles:", aServer.getRoles())
                    for user in aServer.getUsers():
                        print("---- user ----")
                        print(user.id)
                        print(user.name)
                        print(user.warnings)

                await ctx.send("done")

        @slash.slash(
            name="Sync_Commands",
            description="Sync slash commands",
            guild_ids=PRIVATE_GUILD_IDS,
        )
        async def syncCommand(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                await ctx.send("You cannot use this command")
                return
            else:
                await slash.sync_all_commands()
                await ctx.send(f"Commands synced!")

        #######################

        @slash.slash(
            name="Help",
            description="Gets the help menu",
            guild_ids=PRIVATE_GUILD_IDS,
        )
        async def help(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                return
            else:
                embed = discord.Embed(title="Help", color=0x17D4EE)
                embed.add_field(
                    name="/newWord <add/remove> <word>",
                    value="add a word that people cant say",
                    inline=True,
                )
                embed.add_field(
                    name="/displayWords",
                    value="display all words that is not allowed to be said",
                    inline=True,
                )
                embed.add_field(
                    name="/newLetter <add/remove> <letter> <character>",
                    value="Add a character to a letter list that people could replace",
                    inline=True,
                )
                embed.add_field(
                    name="/displayLetter <letter>",
                    value="display characters for all letter or a specific one",
                    inline=True,
                )
                embed.add_field(
                    name="/newSeperator <add/remove> <character>",
                    value="Add punctuation to which could be used to separates characters",
                    inline=True,
                )
                embed.add_field(
                    name="/displaySeperator",
                    value="display characters for all letter or a specific one",
                    inline=True,
                )
                embed.add_field(
                    name="/requiredRole <add/remove> <role>",
                    value="the required roles to be able to control everything",
                    inline=True,
                )
                embed.add_field(
                    name="/displayRoles",
                    value="display all roles that is considered admin roles",
                    inline=True,
                )
                embed.add_field(
                    name="/reportChannel <add/remove> <channel>",
                    value="A channel where everything is logged to",
                    inline=True,
                )
                embed.add_field(
                    name="/displayChannel",
                    value="display all channels that is currently being logged to",
                    inline=True,
                )
                embed.add_field(
                    name="/warn <user> <reason>", value="warns a user", inline=True
                )
                embed.add_field(
                    name="/warning <user>", value="check a users warnings", inline=True
                )
                embed.add_field(
                    name="/tempmute <user> <duration> <reason>",
                    value="mutes a user",
                    inline=True,
                )
                embed.add_field(
                    name="/defaultMute <time>",
                    value="How long the default mute duration is",
                    inline=True,
                )
                embed.add_field(
                    name="/warningCount <number>",
                    value="How how many warnings the user can receive before being muted",
                    inline=True,
                )
                embed.add_field(
                    name="/timeFrame <time>",
                    value="The time between the most recent warning and the 3rd warning",
                    inline=True,
                )
                embed.add_field(
                    name="/muteInfo", value="display info about muting", inline=True
                )

                await ctx.send(embed=embed)
                msg = """/newWord <add/remove> <word>
/displayWords
/newLetter <add/remove> <letter> <character>
/displayWords <letter>
/newSeperator <add/remove> <character>
/displaySeperator

/requiredRole <add/remove> <role>
/displayRoles
/reportChannel <add/remove> <channel>
/displayChannel

/warn <user> <reason>
/warning <user>
/tempmute <user> <duration> <reason>

/defaultMute <time>
/warningCount <number>
/timeFrame <time>
/muteInfo
                """

        ###############################################################
        @slash.slash(
            name="Warn",
            description="Warns a user",
            options=[
                create_option(
                    name="user",
                    description="Choose a user",
                    required=True,
                    option_type=6,
                ),
                create_option(
                    name="reason",
                    description="Reason for warning",
                    required=False,
                    option_type=3,
                ),
            ],
        )
        async def warn(
            ctx: SlashContext, user: discord.Member, reason: str = "No Reason"
        ) -> None:
            currentGuild = self.getGuild(ctx)
            author = ctx.author
            if author == self.user:
                return
            elif await self.validRoles(ctx, currentGuild):
                await self.warnCall(
                    ctx,
                    user,
                    author,
                    currentGuild,
                    reason,
                    datetime.datetime.now(),
                    None,
                    True,
                )

        @slash.slash(
            name="Warnings",
            description="Check a users warnings",
            options=[
                create_option(
                    name="user",
                    description="Choose a user",
                    required=False,
                    option_type=6,
                )
            ],
        )
        async def warnings(
            ctx: SlashContext,
            user: Optional[Union[discord.Member, discord.User]] = None,
        ) -> None:
            author = ctx.author

            if author == self.user:
                return
            else:
                if not user:
                    user = author

                if not user:
                    await ctx.send("User not found.")
                    return

                icon = getattr(user, "avatar_url", None)
                userID = getattr(user, "id", None)
                userName = getattr(user, "name", None)
                if not userID or not userName:
                    await ctx.send("Invalid user provided.")
                    return

                currentGuild = self.getGuild(ctx)
                User = self.getUser(currentGuild, user)
                embed = discord.Embed(color=0x007FFF)
                embed.set_author(name=f"[Warnings] {userName}", icon_url=icon)

                for x in User.getWarnings():
                    embed.add_field(
                        name="given by", value=x["givenBy"].mention, inline=True
                    )
                    embed.add_field(name="reason", value=x["reason"], inline=True)
                    embed.add_field(name="time", value=x["time"], inline=True)
                else:
                    embed.add_field(
                        name="No warnings found", value="User is clean!", inline=True
                    )

                await ctx.send(embed=embed)
                self.log(currentGuild, ctx.author, f"checked warnings for - [{userID}]")

        ##
        @slash.slash(
            name="Report_Channel",
            description="A channel where everything is logged to",
            options=[
                create_option(
                    name="option",
                    description="Add or remove option",
                    required=True,
                    option_type=3,
                    choices=[
                        create_choice(name="add", value="add"),
                        create_choice(name="remove", value="remove"),
                    ],
                ),
                create_option(
                    name="channel",
                    description="Choose a channel",
                    required=True,
                    option_type=7,
                ),
            ],
        )
        async def reportChannel(
            ctx: SlashContext, option: str, channel: discord.TextChannel
        ) -> None:
            currentGuild = self.getGuild(ctx)
            author = ctx.author
            if author == self.user:
                return
            elif await self.validRoles(ctx, currentGuild):
                sql_query = ""
                if option == "add":
                    if channel not in currentGuild.getChannels():
                        currentGuild.addChannel(channel)
                        self.log(
                            currentGuild,
                            author,
                            f"new log channel added - [{channel.id}]",
                        )
                        await ctx.send(f"[{channel}] channel has been added")
                        sql_query = f"""INSERT INTO PrivChannel (serverID,channel_ID) VALUES ('{currentGuild.id}','{channel.id}');"""
                    else:
                        await ctx.send("Channel already exist")
                elif option == "remove":
                    if channel in currentGuild.getChannels():
                        currentGuild.removeChannel(channel)
                        self.log(
                            currentGuild,
                            author,
                            f"new log channel removed - [{channel.id}]",
                        )
                        await ctx.send(f"[{channel}] channel has been removed")
                        sql_query = f"""DELETE FROM PrivChannel WHERE channel_ID='{channel.id}' AND serverID='{currentGuild.id}';"""
                    else:
                        await ctx.send("Channel doesnt exist")
                self.cursor.execute(sql_query)
                self.conn.commit()

        @slash.slash(
            name="Display_Channels",
            description="Display all channels that is currently being logged to",
        )
        async def displayChannel(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                embed = discord.Embed(title="[Channel list]", color=0x007FFF)
                count = 0
                for x in currentGuild.getChannels():
                    count += 1
                    embed.add_field(name=str(count), value=x, inline=True)
                self.log(currentGuild, ctx.author, "displayed all channels")
                await ctx.send(embed=embed)

        ##
        @commands.has_permissions(administrator=True)
        @slash.slash(
            name="Required_Role",
            description="The required roles to be able to control everything",
            options=[
                create_option(
                    name="option",
                    description="Add or remove option",
                    required=True,
                    option_type=3,
                    choices=[
                        create_choice(name="add", value="add"),
                        create_choice(name="remove", value="remove"),
                    ],
                ),
                create_option(
                    name="role",
                    description="Choose a role",
                    required=True,
                    option_type=8,
                ),
            ],
        )
        async def requiredRole(
            ctx: SlashContext, option: str, role: discord.Role
        ) -> None:
            currentGuild = self.getGuild(ctx)
            if ctx.author == self.user:
                return
            else:
                sql_query = ""
                if option == "add":
                    if role not in currentGuild.getRoles():
                        currentGuild.addRole(role)
                        self.log(
                            currentGuild, ctx.author, f"new role added - [{role.id}]"
                        )
                        await ctx.send(f"[{role.name}] role has been added")
                        sql_query = f"""INSERT INTO admin_role (serverID,role_ID) VALUES ('{currentGuild.id}','{role.id}');"""
                    else:
                        await ctx.send("Role already exist")
                elif option == "remove":
                    if role in currentGuild.getRoles():
                        currentGuild.removeRole(role)
                        self.log(
                            currentGuild, ctx.author, f"new role removed - [{role.id}]"
                        )
                        await ctx.send(f"[{role.name}] role has been removed")
                        sql_query = f"""DELETE FROM admin_role where role_ID = '{role.id}' AND serverID='{currentGuild.id}';"""
                    else:
                        await ctx.send("Role doesnt exist")
                self.cursor.execute(sql_query)
                self.conn.commit()

        @slash.slash(
            name="Display_Roles",
            description="Display all roles that is considered admin roles",
        )
        async def displayRoles(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                embed = discord.Embed(title="[Role list]", color=0x007FFF)
                count = 0
                for x in currentGuild.getRoles():
                    count += 1
                    embed.add_field(name=str(count), value=x, inline=True)
                self.log(currentGuild, ctx.author, "displayed all roles")
                await ctx.send(embed=embed)

        ###############################################################
        @slash.slash(
            name="New_Word",
            description="Add a word that people cant say",
            options=[
                create_option(
                    name="option",
                    description="Add or remove option",
                    required=True,
                    option_type=3,
                    choices=[
                        create_choice(name="add", value="add"),
                        create_choice(name="remove", value="remove"),
                    ],
                ),
                create_option(
                    name="word",
                    description="Choose a word",
                    required=True,
                    option_type=3,
                ),
            ],
        )
        async def newWord(ctx: SlashContext, option: str, word: str) -> None:
            currentGuild = self.getGuild(ctx)
            if ctx.author == self.user:
                return
            elif await self.validRoles(ctx, currentGuild):
                if option == "add":
                    if word not in currentGuild.getWords():
                        currentGuild.addWord(word)
                        await ctx.send(f"[{word}] has been added")
                        self.log(currentGuild, ctx.author, f"word added - [{word}]")
                        sql_query = f"""INSERT INTO word_list (serverID,word) VALUES ('{currentGuild.id}','{word}');"""
                        self.cursor.execute(sql_query)
                        self.conn.commit()
                    else:
                        await ctx.send("Word already exist")
                elif option == "remove":
                    if word in currentGuild.getWords():
                        currentGuild.removeWord(word)
                        await ctx.send(f"[{word}] has been removed")
                        self.log(currentGuild, ctx.author, f"word removed - [{word}]")
                        sql_query = f"""DELETE FROM word_list WHERE word='{word}' AND serverID='{currentGuild.id}';"""
                        self.cursor.execute(sql_query)
                        self.conn.commit()
                    else:
                        await ctx.send("Word doesnt exist")

        @slash.slash(
            name="Display_Words",
            description="Display all words that is not allowed to be said",
        )
        async def displayword(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                embed = discord.Embed(title="[Word list]", color=0x007FFF)
                count = 0
                for x in currentGuild.getWords():
                    count += 1
                    embed.add_field(name=str(count), value=x, inline=True)
                self.log(currentGuild, ctx.author, "displayed all words")
                await ctx.send(embed=embed)

        ###############################################################
        @slash.slash(
            name="New_Letter",
            description="Add a character to a letter list that people could replace",
            options=[
                create_option(
                    name="option",
                    description="Add or remove option",
                    required=True,
                    option_type=3,
                    choices=[
                        create_choice(name="add", value="add"),
                        create_choice(name="remove", value="remove"),
                    ],
                ),
                create_option(
                    name="letter",
                    description="Choose a letter",
                    required=True,
                    option_type=3,
                ),
                create_option(
                    name="char",
                    description="Choose a character",
                    required=True,
                    option_type=3,
                ),
            ],
        )
        async def newLetter(
            ctx: SlashContext, option: str, letter: str, char: str
        ) -> None:
            currentGuild = self.getGuild(ctx)
            if ctx.author == self.user:
                return
            elif await self.validRoles(ctx, currentGuild):
                if option == "add":
                    if char not in currentGuild.getLetter(letter):
                        currentGuild.addLetter(letter, char)
                        await ctx.send(f"[{char}] has been added to [{letter}]")
                        self.log(
                            currentGuild,
                            ctx.author,
                            f"new character [{char}] added to [{letter}]",
                        )
                        sql_query = f"""INSERT INTO letters_list (serverID,orig_Char,replacement) VALUES ('{currentGuild.id}','{letter}','{char}');"""
                        self.cursor.execute(sql_query)
                        self.conn.commit()
                    else:
                        await ctx.send("Letter already exist")
                elif option == "remove":
                    if char in currentGuild.getLetter(letter):
                        currentGuild.removeLetter(letter, char)
                        await ctx.send(f"[{char}] has been removed from [{letter}]")
                        self.log(
                            currentGuild,
                            ctx.author,
                            f"new character [{char}] removed from [{letter}]",
                        )
                        sql_query = f"""DELETE FROM letters_list WHERE orig_Char='{letter}' AND replacement='{char}' AND serverID='{currentGuild.id}';"""
                        self.cursor.execute(sql_query)
                        self.conn.commit()
                    else:
                        await ctx.send("Letter doesnt exist")

        @slash.slash(
            name="Display_Letters",
            description="Display characters for all letter or a specific one",
            options=[
                create_option(
                    name="letter",
                    description="Choose a letter",
                    required=False,
                    option_type=3,
                )
            ],
        )
        async def displayLetter(ctx: SlashContext, letter: str = "") -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                embed = discord.Embed(title="[Letter list]", color=0x007FFF)
                count = 0
                if letter:
                    for x in currentGuild.getLetter(letter):
                        count += 1
                        embed.add_field(name=str(count), value=x, inline=True)
                    await ctx.send(embed=embed)
                    self.log(
                        currentGuild,
                        ctx.author,
                        f"displayed all characters for [{letter}]",
                    )
                else:
                    for x in currentGuild.getLetter():
                        count += 1
                        embed.add_field(
                            name=str(count),
                            value=" - ".join(currentGuild.getLetter(x)),
                            inline=True,
                        )
                        if count == 13:
                            await ctx.send(embed=embed)
                            embed = discord.Embed(title="[Letter list]", color=0x007FFF)
                    await ctx.send(embed=embed)
                    self.log(
                        currentGuild,
                        ctx.author,
                        "displayed all characters for all letters",
                    )

        ###############################################################
        @slash.slash(
            name="New_Seperator",
            description="Add punctuation to which could be used to separates characters",
            options=[
                create_option(
                    name="option",
                    description="Add or remove option",
                    required=True,
                    option_type=3,
                    choices=[
                        create_choice(name="add", value="add"),
                        create_choice(name="remove", value="remove"),
                    ],
                ),
                create_option(
                    name="seperator",
                    description="Choose a seperator",
                    required=True,
                    option_type=3,
                ),
            ],
        )
        async def newSeperator(ctx: SlashContext, option: str, seperator: str) -> None:
            currentGuild = self.getGuild(ctx)
            if ctx.author == self.user:
                return
            elif await self.validRoles(ctx, currentGuild):
                if option == "add":
                    if seperator not in currentGuild.getSeperator():
                        currentGuild.addSeperator(seperator)
                        await ctx.send(f"[{seperator}] has been added")
                        self.log(
                            currentGuild, ctx.author, f"seperator added - [{seperator}]"
                        )
                        sql_query = f"""INSERT INTO separator_list (serverID,seperator) VALUES ('{currentGuild.id}','{seperator}');"""
                        self.cursor.execute(sql_query)
                        self.conn.commit()
                    else:
                        await ctx.send("Seperator already exist")
                elif option == "remove":
                    if seperator in currentGuild.getSeperator():
                        currentGuild.removeSeperator(seperator)
                        await ctx.send(f"[{seperator}] has been removed")
                        self.log(
                            currentGuild,
                            ctx.author,
                            f"seperator removed - [{seperator}]",
                        )
                        sql_query = f"""DELETE FROM separator_list WHERE seperator='{seperator}' AND serverID='{currentGuild.id}';"""
                        self.cursor.execute(sql_query)
                        self.conn.commit()
                    else:
                        await ctx.send("Seperator doesnt exist")

        @slash.slash(name="Display_Seperators", description="Display all separators")
        async def displaySeperator(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                embed = discord.Embed(title="[seperator list]", color=0x00FFFF)
                count = 0
                for x in currentGuild.getSeperator():
                    count += 1
                    embed.add_field(name=str(count), value=x, inline=True)
                await ctx.send(embed=embed)
                self.log(currentGuild, ctx.author, "displayed all separators")

        #################

        @slash.slash(name="Mute_Info", description="Display info about muting")
        async def muteInfo(ctx: SlashContext) -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                embed = discord.Embed(title="[Muting Info]", color=0x007FFF)
                embed.add_field(
                    name="Default Mute", value=currentGuild.getMuteTime(), inline=True
                )
                embed.add_field(
                    name="Warning Count", value=currentGuild.getWarnCount(), inline=True
                )
                embed.add_field(
                    name="Time Frame", value=currentGuild.getTimeFrame(), inline=True
                )
                await ctx.send(embed=embed)
                self.log(currentGuild, ctx.author, "displayed muting info")

        @slash.slash(
            name="Default_Mute",
            description="How long the default mute duration is",
            options=[
                create_option(
                    name="time",
                    description="Enter new time, example: 30m20s",
                    required=True,
                    option_type=3,
                )
            ],
        )
        async def DefaultMute(ctx: SlashContext, time: str) -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                currentGuild.updateMuteTime(time)
                sql_query = f"""UPDATE warn_operation SET mute_duration="{time}" WHERE serverID="{currentGuild.id}";"""
                self.cursor.execute(sql_query)
                self.conn.commit()
                await ctx.send(f"{time} is the new default mute duration")
                self.log(
                    currentGuild, ctx.author, f"Updated default mute time - [{time}]"
                )

        @slash.slash(
            name="Warning_Count",
            description="How how many warnings the user can receive before being muted",
            options=[
                create_option(
                    name="count",
                    description="Enter new count",
                    required=True,
                    option_type=3,
                )
            ],
        )
        async def WarningCount(ctx: SlashContext, count: Union[int, str]) -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                currentGuild.updateWarnCount(int(count))
                sql_query = f"""UPDATE warn_operation SET warn_count="{count}" WHERE serverID="{currentGuild.id}";"""
                self.cursor.execute(sql_query)
                self.conn.commit()
                await ctx.send(f"{count} is the new warning count")
                self.log(currentGuild, ctx.author, f"Updated warning count - [{count}]")

        @slash.slash(
            name="Time_Frame",
            description="The time between the most recent warning and the final warning",
            options=[
                create_option(
                    name="time",
                    description="Enter new time, example: 30m20s",
                    required=True,
                    option_type=3,
                )
            ],
        )
        async def timeFrame(ctx: SlashContext, time: str) -> None:
            if ctx.author == self.user:
                return
            else:
                currentGuild = self.getGuild(ctx)
                currentGuild.updateTimeFrame(time)
                sql_query = f"""UPDATE warn_operation SET warn_gap="{time}" WHERE serverID="{currentGuild.id}";"""
                self.cursor.execute(sql_query)
                self.conn.commit()
                await ctx.send(f"{time} is the new time frame")
                self.log(currentGuild, ctx.author, f"Updated time frame - [{time}]")

        ###############################################################
        @slash.slash(
            name="Temp_Mute",
            description="Mutes a user",
            options=[
                create_option(
                    name="member",
                    description="Choose a member",
                    required=True,
                    option_type=6,
                ),
                create_option(
                    name="duration",
                    description="Duration of mute",
                    required=True,
                    option_type=3,
                ),
                create_option(
                    name="reason",
                    description="Reason for mute",
                    required=False,
                    option_type=3,
                ),
            ],
        )
        async def tempmute(
            ctx: SlashContext,
            member: discord.User,
            duration: str,
            reason: str = "No Reason",
        ) -> None:
            currentGuild = self.getGuild(ctx)
            if ctx.author == self.user:
                return
            elif await self.validRoles(ctx, currentGuild):
                await self.mute(
                    ctx, currentGuild, member, ctx.author, duration, True, reason
                )

        @self.event
        async def on_message(message: discord.Message) -> None:
            if message.author == self.user:
                return
            else:
                msg = str(message.content.lower())
                currentGuild = self.getGuild(message)
                author = message.author

                self.getUser(currentGuild, author)

                for roles in currentGuild.getRoles():
                    if roles in message.author.roles:
                        return

                botUser = self.user
                if not isinstance(botUser, discord.ClientUser):
                    raise Exception("Bot user is not valid")

                wordstatus, word = self.compare(msg, currentGuild)
                if wordstatus:
                    await message.delete()
                    await self.warnCall(
                        message,
                        message.author,
                        botUser,
                        currentGuild,
                        "Language",
                        datetime.datetime.now(),
                        [message.channel, word, msg],
                    )
                await self.process_commands(message)

        ####################
        @self.event
        async def on_command_error(ctx: commands.Context, error: Exception) -> None:
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("Make sure you put the required arguments.")
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("Invalid command used.")
            if isinstance(error, commands.MissingPermissions):
                await ctx.send("Invalid permission.")
            else:
                print(f"!!![Error] - {error}!!!")
                await ctx.send("Error encountered.")

    @staticmethod
    async def on_connect() -> None:
        print("[LOGS] Connecting to discord!")

    async def on_ready(self) -> None:
        time = datetime.datetime.now()
        # print(datetime.timedelta(0,0,0,0,2,1))
        newtime = (time - datetime.timedelta(0, 0, 0, 0, 0, 1)).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
        if not isinstance(self.user, discord.ClientUser):
            raise Exception("Bot user is not valid")

        print(
            f"[LOGS] Logged in: {self.user.name}\n[LOGS] ID: {self.user.id}\n[LOGS] Time: {time}"
        )
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="your every message"
            )
        )
        activeservers = self.guilds
        # print(self.guilds)
        ###
        for server in activeservers:
            print(server.name)

            sql_query = f"""SELECT * FROM server
                            WHERE server_ID={server.id}"""
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            newServer = Servers(server)
            # print(newServer.id)
            self.server.append(newServer)

            if not results:
                sql_query = f"""INSERT INTO server (server_ID,name) VALUES ('{server.id}','{server.name}');"""
                self.cursor.execute(sql_query)
                self.conn.commit()

            sql_query = f"""SELECT * FROM word_list
                            WHERE serverID={server.id}"""
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            for words in results:
                newServer.addWord(words[1])
            # print("done word")

            sql_query = f"""SELECT orig_Char,replacement FROM 'letters_list'
                            WHERE serverID={server.id}"""
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            for letters in results:
                newServer.addLetter(letters[0], letters[1])
            # print("done letter")

            sql_query = f"""SELECT * FROM separator_list
                            WHERE serverID={server.id}"""
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            for seperator in results:
                newServer.addSeperator(seperator[1])
            # print("done separator")

            # print("start user")
            #            sql_query = (f'''SELECT user_ID,name,reason,given_by,date_given FROM 'user_list', 'warning_list'
            #                           WHERE user_list.serverID=warning_list.serverID and user_list.user_ID=warning_list.userID and warning_list.serverID={server.id} and warning_list.date_given>"{newtime}"''') ## problem
            #          #print(sql_query)
            #         self.cursor.execute(sql_query)
            #        results = self.cursor.fetchall()
            #       if results:
            #          #print(results)
            #         print(len(results))
            #        for user in results:
            #           #print(user)
            #          foundUser = await self.fetch_user(user[0])
            #         newUser = Users(foundUser)
            #        found = False
            #       for x in newServer.getUsers():
            #          if user[0] == x.id:
            #             newUser = self.getUser(newServer, foundUser)
            #            found = True
            #           print("old --",user,"----",x.name,x.id)
            #  if not found:
            #     print("new --",user,"----",newUser.name,newUser.id)
            #    newServer.addUser(newUser)
            # await self.warnCall("", foundUser, await self.fetch_user(user[3]), newServer, user[2],
            #                   datetime.datetime.strptime(user[4], "%Y-%m-%d %H:%M:%S.%f"), "", False, True)

            sql_query1 = f"""SELECT * FROM 'user_list'
                            WHERE serverID={server.id}"""
            self.cursor.execute(sql_query1)
            results1 = self.cursor.fetchall()
            if results1:
                for user in results1:
                    # print(user)
                    foundUser = await self.fetch_user(user[1])
                    newUser = Users(foundUser)
                    newServer.addUser(newUser)

                    sql_query2 = f'''SELECT * FROM 'warning_list' WHERE serverID={server.id} and userID={newUser.id} and date_given>"{newtime}"'''  # date_given>"{newtime}"
                    self.cursor.execute(sql_query2)
                    results2 = self.cursor.fetchall()
                    if results2:
                        for warnings in results2:
                            # print(warnings)
                            newUser.warn(
                                await self.fetch_user(warnings[3]),
                                warnings[2],
                                warnings[4],
                            )

            # print("done users")

            sql_query = f"""SELECT * FROM warn_operation
                            WHERE serverID={server.id}"""
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            if not results:
                sql_query = f"""INSERT INTO warn_operation (serverID,warn_count,mute_duration,warn_gap)
                                VALUES ({server.id},{newServer.getWarnCount()},"{newServer.getMuteTime()}","{newServer.getTimeFrame()}");"""
                self.cursor.execute(sql_query)
                self.conn.commit()
            else:
                newServer.updateWarnCount(results[0][1])
                newServer.updateMuteTime(results[0][2])
                newServer.updateTimeFrame(results[0][3])

            sql_query = f"""SELECT * FROM admin_role
                            WHERE serverID={server.id}"""
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            for role in results:
                foundRole = discord.utils.get(newServer.guild.roles, id=role[1])
                if foundRole:
                    newServer.addRole(foundRole)
                else:
                    print(f"[WARN] Role ID {role[1]} not found in server {server.id}")

            sql_query = f"""SELECT * FROM PrivChannel
                            WHERE serverID={server.id}"""
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            for channel in results:
                newChannel = await self.fetch_channel(channel[1])
                if newChannel and isinstance(newChannel, discord.TextChannel):
                    newServer.addChannel(newChannel)
                else:
                    print(
                        f"[WARN] Channel ID {channel[1]} not found in server {server.id} or wrong type was found"
                    )
            print("done server")
        ###
        print(
            f"[LOGS] Bot is ready!\n[LOGS] Ready in: {datetime.datetime.now() - time}"
        )

    @staticmethod
    async def on_resumed() -> None:
        print("\n[LOGS] Bot has resumed session!")

    ################
    # Format the word into regex
    @staticmethod
    def formating(word: str, server: Servers) -> str:
        temp = ""
        if not server.getSeperator():
            for x in word:
                temp = "%s[%s]+" % (temp, "".join(server.getLetter(x)))
        else:
            for x in word:
                temp = "%s[%s]*[%s]+" % (
                    temp,
                    "".join(server.getSeperator()),
                    "".join(server.getLetter(x)),
                )
            temp = "%s[%s]*" % (temp, "".join(server.getSeperator()))
        return temp

    # The main comparison function
    def compare(self, phrase: str, server: Servers) -> tuple[bool, str]:
        for x in server.getWords():
            my_regex = self.formating(x, server)
            regexp = re.search(rf"{my_regex}", phrase)
            if regexp:
                return True, x
        return False, ""

    def getGuild(self, context: Union[SlashContext, discord.Message]) -> Servers:
        for x in self.server:
            guild = context.guild
            if not isinstance(guild, discord.Guild):
                raise Exception("Guild not found")

            if x.id == guild.id:
                return x
        else:
            raise Exception("Guild not found")

    def getUser(
        self, server: Servers, user: Union[discord.User, discord.Member]
    ) -> Users:
        userID = getattr(user, "id", None)
        userName = getattr(user, "name", None)
        if not userID or not userName:
            raise Exception("User ID or name not found")

        for storedUser in server.getUsers():
            if storedUser.id == userID:
                return storedUser

        # user not found, create new one
        newUser = Users(user)
        server.addUser(newUser)
        sql_query = f"""INSERT INTO user_list (serverID, user_ID, name, is_muted) VALUES ('{server.id}','{userID}','{userName}','{False}');"""
        self.cursor.execute(sql_query)
        self.conn.commit()
        return newUser

    def toSecond(self, time: str) -> float:
        time = time.lower()
        second = 0
        newconvert = ""
        for x in time:
            if x not in ["w", "d", "h", "m", "s"]:
                newconvert = str(newconvert) + x
            else:
                if x == "w":
                    newconvert = int(newconvert) * 7
                    second += self.toSecond(str(newconvert) + "d")
                if x == "d":
                    newconvert = int(newconvert) * 24
                    second += self.toSecond(str(newconvert) + "h")
                if x == "h":
                    newconvert = int(newconvert) * 60
                    second += self.toSecond(str(newconvert) + "m")
                if x == "m":
                    newconvert = int(newconvert) * 60
                    second += self.toSecond(str(newconvert) + "s")
                if x == "s":
                    second += int(newconvert)
                newconvert = ""
        return second

    @staticmethod
    async def toChannel(
        ctx: Any,
        channels: Optional[Iterable[discord.TextChannel]],
        text: discord.Embed,
        reply: bool = False,
        extraMsg: str = "",
    ) -> None:
        for channel in channels or [ctx.channel]:
            if ctx.channel != channel:
                await channel.send(embed=text)
            if not extraMsg:
                print("not extra")
                if reply:
                    await ctx.send(embed=text)
                else:
                    await ctx.channel.send(embed=text)
            else:
                print("extra")
                await ctx.channel.send(extraMsg)

    @staticmethod
    async def validRoles(ctx: SlashContext, server: Servers) -> bool:
        if not isinstance(ctx.author, discord.Member):
            await ctx.send("You must be a member of the server to use this command.")
            return False
        for roles in ctx.author.roles:
            if roles in server.getRoles():
                return True
        await ctx.send("invalid permissions")
        return False

    @staticmethod
    def log(
        server: Servers,
        user: Union[discord.User, discord.ClientUser, discord.Member],
        text: str,
    ) -> None:
        print(f"[{server.id}]-[{user.display_name}] : {text}")

    async def mute(
        self,
        ctx: Any,
        server: Servers,
        member: Union[discord.User, discord.Member],
        fromMember: Union[discord.User, discord.Member, discord.ClientUser],
        duration: str,
        respond: bool = False,
        reason: str = "",
    ) -> None:

        icon = getattr(member, "avatar_url", None)
        memberID = getattr(member, "id", None)
        if not memberID:
            await ctx.send("Failed to mute: user ID not found.")
            return

        mutingEmbed = discord.Embed(color=0xFF0000)
        mutingEmbed.set_author(name=f"[Mute] {member}", icon_url=icon)
        mutingEmbed.add_field(name="User", value=member.mention, inline=True)
        mutingEmbed.add_field(name="Moderator", value=fromMember.mention, inline=True)
        mutingEmbed.add_field(name="Reason", value=reason, inline=True)
        mutingEmbed.add_field(name="Duration", value=duration, inline=False)

        unmutingEmbed = discord.Embed(color=0x00FF00)
        unmutingEmbed.set_author(name=f"[Unmute] {member}", icon_url=icon)
        unmutingEmbed.add_field(name="User", value=member.mention, inline=True)
        unmutingEmbed.add_field(name="Moderator", value=fromMember.mention, inline=True)

        # check if Muted role exist
        mutedRole = discord.utils.get(server.guild.roles, name="Muted")
        if not mutedRole:
            perms = discord.Permissions(
                send_messages=False, read_messages=True, read_message_history=True
            )
            # create Muted role and retreive it and set permissions
            await ctx.guild.create_role(name="Muted", permissions=perms)
            mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

            if not mutedRole:
                await ctx.send("Failed to create Muted role, please create it manually")
                return

            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    mutedRole, speak=False, send_messages=False
                )
                for x in range(1, 20):
                    try:
                        await mutedRole.edit(position=x)
                    except:
                        break
                for channels in server.channels[0]:
                    await channels.set_permissions(
                        mutedRole, speak=False, send_messages=False
                    )
                # only Members can be given roles
                if isinstance(member, discord.Member):
                    await member.add_roles(mutedRole)
                else:
                    await ctx.send("Failed to mute: user is not a server member.")
                    return
        else:
            time = self.toSecond(duration)

            if not isinstance(member, discord.Member):
                await ctx.send("Failed to mute: user is not a server member.")
                return

            await member.add_roles(mutedRole)
            await self.toChannel(ctx, server.getChannels(), mutingEmbed, respond)
            self.log(server, ctx.author, f"[{memberID}] muted for [{duration}]")

            await asyncio.sleep(time)

            try:
                await member.remove_roles(mutedRole)
            except:
                pass
            await self.toChannel(ctx, server.getChannels(), unmutingEmbed, respond)
            self.log(server, ctx.author, f"[{memberID}] has been unmuted")

    async def warnCall(
        self,
        ctx: Union[SlashContext, discord.Message],
        toUser: Union[discord.Member, discord.User],
        fromUser: Union[discord.Member, discord.User, discord.ClientUser],
        server: Servers,
        reason: str,
        time: datetime.datetime,
        more: Optional[List[Any]] = None,
        respond: bool = False,
    ) -> None:
        # print(ctx, toUser, fromUser, server, reason, time, more, ignore)
        user = self.getUser(server, toUser)
        embed = discord.Embed(color=0xEB9100)
        embed.set_author(
            name=f"[Warning] {toUser}", icon_url=getattr(toUser, "avatar_url", None)
        )
        embed.add_field(
            name="User", value=getattr(toUser, "mention", str(toUser)), inline=True
        )

        # ensure we have a from-user fallback and safe attribute access
        if fromUser is None:
            if self.user is None:
                raise Exception("Bot user is not valid")
            else:
                from_user_actual = self.user
        else:
            from_user_actual = fromUser
        # from_user_actual = fromUser if fromUser is not None else self.user
        from_user_mention = getattr(from_user_actual, "mention", str(from_user_actual))
        embed.add_field(name="Moderator", value=from_user_mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)

        if more is not None:
            embed.add_field(name="Channel", value=more[0], inline=False)
            embed.add_field(name="Message", value=more[2], inline=False)
            await self.toChannel(
                ctx, server.getChannels(), embed, respond, "You have been warned"
            )
            self.log(server, toUser, f"bad word [{more[1]}] in [{more[2]}]")
        else:
            await self.toChannel(ctx, server.getChannels(), embed, respond)
            self.log(
                server,
                from_user_actual,
                f"Warned [{user.id}] for [{reason}]",
            )

        # safe id extraction
        to_user_id = getattr(toUser, "id", 0)
        from_user_id = getattr(from_user_actual, "id", 0)
        sql_query = f"""INSERT INTO warning_list (serverID, userID,reason,given_by,date_given) VALUES ('{server.id}','{to_user_id}','{reason}','{from_user_id}','{time}');"""
        self.cursor.execute(sql_query)
        self.conn.commit()

        # ensure fromUser is not None for warn() call
        user.warn(from_user_actual, reason, time)
        if len(user.getWarnings()) >= server.getWarnCount():
            test = user.check(
                server.getWarnCount(), self.toSecond(server.getTimeFrame())
            )
            if test:
                await self.mute(
                    ctx,
                    server,
                    toUser,
                    from_user_actual,
                    server.getMuteTime(),
                    respond,
                    "language",
                )


bot = MyClient()
bot.run(TOKEN)
