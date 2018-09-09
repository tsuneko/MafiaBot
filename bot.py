import discord
from discord.ext import commands
import asyncio
import time
import random
import math

debug = False

random.seed()

f = open("login.txt",mode='r')
loginDetails = {}
for line in f.readlines():
    if '=' in line:
        tokens = line.split('=')
        loginDetails[tokens[0]] = tokens[1].rstrip()

version = "0.9.9"
token = loginDetails["token"]
prefix = loginDetails["prefix"]

bot = commands.Bot(command_prefix = prefix)
bot.remove_command("help")

players = {}
gameInfo = {
    "open": False,
    "channel": None,
    "mafia_channel": None,
    "state": "Lobby",
    "player_count": 0,
}

emotes = {"A":"\U0001f1e6","B":"\U0001f1e7","C":"\U0001f1e8","D":"\U0001f1e9","E":"\U0001f1ea","F":"\U0001f1eb","G":"\U0001f1ec",
            "H":"\U0001f1ed","I":"\U0001f1ee","J":"\U0001f1ef","K":"\U0001f1f0","L":"\U0001f1f1","M":"\U0001f1f2","N":"\U0001f1f3",
            "O":"\U0001f1f4","P":"\U0001f1f5","Q":"\U0001f1f6","R":"\U0001f1f7","S":"\U0001f1f8","T":"\U0001f1f9","U":"\U0001f1fa",
            "V":"\U0001f1fb","W":"\U0001f1fc","X":"\U0001f1fd","Y":"\U0001f1fe","Z":"\U0001f1ff", "Confirm": "\U0001f52a"}

teamFormats = {
    5: "2C 1M 1S 1D",
    6: "2C 2M 1S 1D",
    7: "2C 2M 1S 1D 1J",
    8: "3C 2M 1S 1D 1J",
    9: "3C 2M 1S 1D 1J 1H",
    10: "3C 3M 1S 1D 1J 1H",
    11: "4C 3M 1S 1D 1J 1H",
    12: "5C 3M 1S 1D 1J 1H"
}

roleNames = {
    "C" : "Civilian",
    "M" : "Mafia",
    "S" : "Detective",
    "D" : "Doctor",
    "J" : "Joker",
    "H" : "Hooker",
    "Spectator" : "Spectator"
}

mafiaIDs = []

print("TsunBot v."+version+" started!")

@bot.command(pass_context = True)
async def userinfo(context, user:discord.User=None):
    if user == None:
        user = context.message.author
    await bot.say(user.name + " [" + user.id +"]")

@bot.command(pass_context = True)
async def channelinfo(context):
	if context.message.channel.is_private:
		await bot.say("Channel Info: Private Message to " + context.message.author.name + " [" + content.message.author.id + "]")
	else:
		await bot.say("Channel Info: Server [" + context.message.server.name + "] #" + context.message.channel.name + " [" + context.message.channel.id + "]")

@bot.command(pass_context = True)
async def join(context):
    if gameInfo["open"] == False:
        return
    if context.message.author in players:
        return
    if context.message.author in players:
        return

    await bot.edit_channel_permissions(gameInfo["channel"], context.message.author, discord.PermissionOverwrite(read_messages=True))
    
    players[context.message.author] = {"Role": "Spectator", "Status": "Dead"}
    await bot.send_message(gameInfo["channel"], "New Player: " + context.message.author.name + " added!")
    
    gameInfo["player_count"] += 1
    await bot.change_presence(game=discord.Game(name="Mafia ["+str(gameInfo["player_count"])+"]"))

@bot.command(pass_context = True)
async def leave(context):
    if gameInfo["open"] == False:
        return
    if context.message.author not in players:
        return
    players.pop(context.message.author)

    await bot.delete_channel_permissions(gameInfo["channel"], context.message.author)
    await bot.send_message(gameInfo["channel"], "Player: " + context.message.author.name + " has left.")

    gameInfo["player_count"] -= 1
    await bot.change_presence(game=discord.Game(name="Mafia ["+str(gameInfo["player_count"])+"]"))

@bot.command(pass_context = True)
async def add(context, user:discord.User=None):
    if gameInfo["open"] == False:
        return
    if user == None:
        return
    if user in players:
        return

    await bot.edit_channel_permissions(gameInfo["channel"], user, discord.PermissionOverwrite(read_messages=True))
    
    players[user] = {"Role": "Spectator", "Status": "Dead"}
    await bot.send_message(gameInfo["channel"], "New Player: " + user.name + " added!")
    
    gameInfo["player_count"] += 1
    await bot.change_presence(game=discord.Game(name="Mafia ["+str(gameInfo["player_count"])+"]"))

    
@bot.command(pass_context = True)
async def kick(context, user:discord.User=None):
    if gameInfo["open"] == False:
        return
    if user == None:
        return
    if user not in players:
        return
    players.pop(user)

    await bot.delete_channel_permissions(gameInfo["channel"], user)
    await bot.send_message(gameInfo["channel"], "Player: " + user.name + " has been kicked.")

    gameInfo["player_count"] -= 1
    await bot.change_presence(game=discord.Game(name="Mafia ["+str(gameInfo["player_count"])+"]"))
    

@bot.command(pass_context = True)
async def open(context):
    mafiaLobby = await bot.say("The Mafia Lobby has been opened! Type " + prefix + "join to join.")

    gameInfo["open"] = True
    gameInfo["channel"] = await bot.create_channel(context.message.server, "mafia-general", discord.ChannelPermissions(context.message.server.default_role, discord.PermissionOverwrite(read_messages=False)))
    gameInfo["mafia_channel"] = await bot.create_channel(context.message.server, "mafia-private", discord.ChannelPermissions(context.message.server.default_role, discord.PermissionOverwrite(read_messages=False)))
    gameInfo["state"] = "Lobby"
    gameInfo["player_count"] = 0

    await bot.move_channel(gameInfo["channel"], 0)
    await bot.move_channel(gameInfo["mafia_channel"], 1)

    await bot.change_presence(game=discord.Game(name="Mafia [Lobby]"))

    players = {}

@bot.command(pass_context = True)
async def fixchat(context):
	if (gameInfo["open"] == True):
	    await bot.move_channel(gameInfo["channel"], 0)
	    await bot.move_channel(gameInfo["mafia_channel"], 1)

@bot.command(pass_context = True)
async def close(context):
    gameInfo["open"] = False

    players = {}
    mafiaIDs = []

    await bot.delete_channel(gameInfo["channel"])
    await bot.delete_channel(gameInfo["mafia_channel"])
    await bot.change_presence(game=discord.Game(name="idle"))
    
@bot.command(pass_context = True)
async def start(context):
    random.seed()
    
    if gameInfo["open"] and gameInfo["state"] == "Lobby" and gameInfo["player_count"] >= 5:
        gameInfo["state"] = "Game"
    else:
        return
    
    await bot.send_message(gameInfo["channel"], "Game Starting with " + str(gameInfo["player_count"]) + " players!")
    await bot.change_presence(game=discord.Game(name="Mafia ["+str(gameInfo["player_count"])+"]"))

    # organise players into teams etc
    playerList = []
    for p in players:
        playerList.append(p)
    random.shuffle(playerList)

    mafiaIDs = []
    
    playerIndex = 0
    gameInfo["format"] = teamFormats[gameInfo["player_count"]]
    for token in gameInfo["format"].split():
        for _ in range(int(token[0])):
            players[playerList[playerIndex]]["Role"] = token[1]
            players[playerList[playerIndex]]["Status"] = "Alive"
            print("Assigned " + playerList[playerIndex].name + " to team: " + token[1])
            await bot.send_message(playerList[playerIndex], "Your role is: " + roleNames[token[1]])
            if token[1] == "M":
                mafiaIDs.append(playerList[playerIndex])
            else:
                if token[1] == "S":
                    detectiveID = playerList[playerIndex]
                elif token[1] == "D":
                    doctorID = playerList[playerIndex]
                elif token[1] == "H":
                    hookerID = playerList[playerIndex]
            playerIndex += 1

    await bot.send_message(gameInfo["mafia_channel"], "Please use this private text channel to communicate with each other.")
    
    for mafiaPlayer in mafiaIDs:
        await bot.edit_channel_permissions(gameInfo["mafia_channel"], mafiaPlayer, discord.PermissionOverwrite(read_messages=True))
    
    gameInfo["turn"] = 1
    gameInfo["time"] = "Night"
    
    while(gameInfo["state"] == "Game"):
        print(gameInfo["time"] + " " + str(gameInfo["turn"]))
        await bot.send_message(gameInfo["channel"], gameInfo["time"] + " " + str(gameInfo["turn"]))

        jokerWin = False

        if (gameInfo["time"] == "Day"):
            # vote lynch
            dayEvents = []
            
            participants = {}
            options = []
            votedParticipants = 0
            totalParticipants = 0
            participantNames = []
            participantIDs = []
            
            for p in players:
                if players[p]["Status"] == "Alive":
                    participants[p] = 0
                    participantIDs.append(p)
                    participantNames.append(p.name)
                    totalParticipants += 1
                    options.append(p.name)

            validReacts = {}
            for i in range(len(options)):
                options[i] = emotes[chr(ord("A")+i)] + " " + options[i]
                validReacts[emotes[chr(ord("A")+i)]] = i+1

            dayMessage = await bot.send_message(gameInfo["channel"], "Vote to lynch a player:\n"+"\n".join(options))

            for i in range(len(options)):
                await bot.add_reaction(dayMessage, emotes[chr(ord("A")+i)])
            
            voteInfo = await bot.send_message(gameInfo["channel"], "Waiting for votes from: " + ', '.join(participantNames))

            while (votedParticipants < totalParticipants):
                reaction = await bot.wait_for_reaction(message = dayMessage)
                if reaction.user == bot.user:
                    continue
                if reaction.user not in participants or reaction.reaction.emoji not in validReacts or reaction.user == participantIDs[validReacts[reaction.reaction.emoji]-1]:
                    await bot.remove_reaction(dayMessage, reaction.reaction.emoji, reaction.user)
                else:
                    if reaction.user.name not in participantNames:
                        participants[reaction.user] = validReacts[reaction.reaction.emoji]
                        print(reaction.user.name + " voted for: " + participantIDs[validReacts[reaction.reaction.emoji]-1].name)
                    else:
                        participantNames.remove(reaction.user.name)
                        participants[reaction.user] = validReacts[reaction.reaction.emoji]
                        print(reaction.user.name + " voted for: " + participantIDs[validReacts[reaction.reaction.emoji]-1].name)
                        await bot.edit_message(voteInfo, "Waiting for votes from: " + ' '.join(participantNames))
                        votedParticipants += 1
                    await bot.remove_reaction(dayMessage, reaction.reaction.emoji, reaction.user)

            await bot.delete_message(voteInfo)

            voteCounts = {}
            for p in participants:
                if participants[p] not in voteCounts:
                    voteCounts[participants[p]] = 1
                else:
                    voteCounts[participants[p]] += 1

            maxVote = 0
            voteWinners = []
            for v in voteCounts:
                if (voteCounts[v] > maxVote):
                    maxVote = voteCounts[v]
                    voteWinners = [v]
                elif (voteCounts[v] == maxVote):
                    voteWinners.append(v)

            if (len(voteWinners) > 1):
                dayEvents.append("As there was a tie for the max vote, the selected player will be chosen randomly.")
                random.shuffle(voteWinners)

            selectedPlayer = participantIDs[voteWinners[0]-1]
            dayEvents.append(selectedPlayer.name + " was voted off (role: " + roleNames[players[selectedPlayer]["Role"]] + "). Please say your last words.")

            narrateConfirm = True
            confirmEmote = emotes["Confirm"]
            dayEventMessage = await bot.send_message(gameInfo["channel"], "\n".join(dayEvents))
            await bot.add_reaction(dayEventMessage, confirmEmote)
            await bot.delete_message(dayMessage)

            while (narrateConfirm == True):
                reaction = await bot.wait_for_reaction(message = dayEventMessage)
                if reaction.user == bot.user:
                    continue
                if reaction.user != selectedPlayer or reaction.reaction.emoji != confirmEmote:
                    await bot.remove_reaction(dayEventMessage, reaction.reaction.emoji, reaction.user)
                else:
                    await bot.remove_reaction(dayEventMessage, reaction.reaction.emoji, reaction.user)
                    await bot.remove_reaction(dayEventMessage, reaction.reaction.emoji, bot.user)
                    narrateConfirm = False
            
            players[selectedPlayer]["Status"] = "Dead"
            await bot.send_message(selectedPlayer, "You have been voted off.")
            
            if players[selectedPlayer]["Role"] == "J":
                jokerWin = True

            gameInfo["time"] = "Night"
        else:
            # mafia kill
            nightMessage = await bot.send_message(gameInfo["channel"], "Mafia are deciding on a player to kill.")
            nightEvents = []

            participants = {}
            options = []
            votedParticipants = 0
            totalParticipants = 0
            participantIDs = []
            participantNames = []
            
            for p in players:
                if players[p]["Status"] == "Alive":
                    options.append(p.name)
                    participantIDs.append(p)
                    if players[p]["Role"] == "M":
                        participants[p] = 0
                        totalParticipants += 1
                        participantNames.append(p.name)

            validReacts = {}
            for i in range(len(options)):
                options[i] = emotes[chr(ord("A")+i)] + " " + options[i]
                validReacts[emotes[chr(ord("A")+i)]] = i+1

            mafiaMessage = await bot.send_message(gameInfo["mafia_channel"], "Vote to kill a player:\n"+"\n".join(options))

            for i in range(len(options)):
                await bot.add_reaction(mafiaMessage, emotes[chr(ord("A")+i)])

            voteInfo = await bot.send_message(gameInfo["mafia_channel"], "Waiting for votes from: " + ', '.join(participantNames))

            while (votedParticipants < totalParticipants):
                reaction = await bot.wait_for_reaction(message = mafiaMessage)
                if reaction.user == bot.user:
                    continue
                if reaction.user not in participants or reaction.reaction.emoji not in validReacts or reaction.user == participantIDs[validReacts[reaction.reaction.emoji]-1]:
                    await bot.remove_reaction(mafiaMessage, reaction.reaction.emoji, reaction.user)
                else:
                    if reaction.user.name not in participantNames:
                        participants[reaction.user] = validReacts[reaction.reaction.emoji]
                        print(reaction.user.name + " voted for: " + participantIDs[validReacts[reaction.reaction.emoji]-1].name)
                    else:
                        participantNames.remove(reaction.user.name)
                        participants[reaction.user] = validReacts[reaction.reaction.emoji]
                        await bot.edit_message(voteInfo, "Waiting for votes from: " + ' '.join(participantNames))
                        votedParticipants += 1
                        print(reaction.user.name + " voted for: " + participantIDs[validReacts[reaction.reaction.emoji]-1].name)
                    await bot.remove_reaction(mafiaMessage, reaction.reaction.emoji, reaction.user)

            await bot.delete_message(voteInfo)

            voteCounts = {}
            for p in participants:
                if participants[p] not in voteCounts:
                    voteCounts[participants[p]] = 1
                else:
                    voteCounts[participants[p]] += 1

            maxVote = 0
            voteWinners = []
            for v in voteCounts:
                if (voteCounts[v] > maxVote):
                    maxVote = voteCounts[v]
                    voteWinners = [v]
                elif (voteCounts[v] == maxVote):
                    voteWinners.append(v)

            if (len(voteWinners) > 1):
                random.shuffle(voteWinners)

            mafiaSelected = participantIDs[voteWinners[0]-1]
            await bot.delete_message(mafiaMessage)

            # check special roles
            detectiveAlive = False
            doctorAlive = False
            hookerAlive = False
            doctorSelected = None
            hookerSelected = None
            
            alivePlayers = []
            for p in players:
                if players[p]["Status"] == "Alive":
                    alivePlayers.append(p)
                    if players[p]["Role"] == "S":
                        detectiveAlive = True
                    elif players[p]["Role"] == "D":
                        doctorAlive = True
                    elif players[p]["Role"] == "H":
                        hookerAlive = True

            if detectiveAlive:
                await bot.edit_message(nightMessage, "The Detective is deciding on a player to investigate.")

                optionsIDs = []
                options = []
                for p in players:
                    if players[p]["Status"] == "Alive":
                        options.append(p.name)
                        optionsIDs.append(p)

                validReacts = {}
                
                for i in range(len(options)):
                    options[i] = emotes[chr(ord("A")+i)] + " " + options[i]
                    validReacts[emotes[chr(ord("A")+i)]] = i+1

                votes = await bot.send_message(detectiveID, "Please select a player to investigate:\n"+"\n".join(options))

                for i in range(len(options)):
                    await bot.add_reaction(votes, emotes[chr(ord("A")+i)])

                hasVoted = False

                while (hasVoted == False):
                    reaction = await bot.wait_for_reaction(message = votes)
                    if reaction.user == bot.user:
                        continue
                    if reaction.reaction.emoji in validReacts and reaction.user == detectiveID and reaction.user != optionsIDs[validReacts[reaction.reaction.emoji]-1]:
                        voteWinner = validReacts[reaction.reaction.emoji]
                        hasVoted = True

                detectiveSelected = optionsIDs[voteWinner-1]
                if players[detectiveSelected]["Role"] != "M":
                    team = "Civilian"
                else:
                    team = "Mafia"
                await bot.send_message(detectiveID, detectiveSelected.name + "'s team is: " + team)

                await bot.delete_message(votes)

            if doctorAlive:
                await bot.edit_message(nightMessage, "The Doctor is deciding on a player to save.")

                optionsIDs = []
                options = []
                for p in players:
                    if players[p]["Status"] == "Alive":
                        options.append(p.name)
                        optionsIDs.append(p)

                validReacts = {}
                
                for i in range(len(options)):
                    options[i] = emotes[chr(ord("A")+i)] + " " + options[i]
                    validReacts[emotes[chr(ord("A")+i)]] = i+1

                votes = await bot.send_message(doctorID, "Please select a player to save:\n"+"\n".join(options))

                for i in range(len(options)):
                    await bot.add_reaction(votes, emotes[chr(ord("A")+i)])

                hasVoted = False

                while (hasVoted == False):
                    reaction = await bot.wait_for_reaction(message = votes)
                    if reaction.user == bot.user:
                        continue
                    if reaction.reaction.emoji in validReacts and reaction.user == doctorID and reaction.user != optionsIDs[validReacts[reaction.reaction.emoji]-1]:
                        voteWinner = validReacts[reaction.reaction.emoji]
                        hasVoted = True

                await bot.delete_message(votes)

                doctorSelected = optionsIDs[voteWinner-1]

            if hookerAlive:
                await bot.edit_message(nightMessage, "The Hooker is deciding on a player to sleep with.")

                optionsIDs = []
                options = []
                for p in players:
                    if players[p]["Status"] == "Alive":
                        options.append(p.name)
                        optionsIDs.append(p)

                validReacts = {}
                
                for i in range(len(options)):
                    options[i] = emotes[chr(ord("A")+i)] + " " + options[i]
                    validReacts[emotes[chr(ord("A")+i)]] = i+1

                votes = await bot.send_message(hookerID, "Please select a player to save:\n"+"\n".join(options))

                for i in range(len(options)):
                    await bot.add_reaction(votes, emotes[chr(ord("A")+i)])

                hasVoted = False

                while (hasVoted == False):
                    reaction = await bot.wait_for_reaction(message = votes)
                    if reaction.user == bot.user:
                        continue
                    if reaction.reaction.emoji in validReacts and reaction.user == hookerID and reaction.user != optionsIDs[validReacts[reaction.reaction.emoji]-1]:
                        voteWinner = validReacts[reaction.reaction.emoji]
                        hasVoted = True

                await bot.delete_message(votes)

                hookerSelected = optionsIDs[voteWinner-1]
                
                if players[hookerSelected]["Role"] == "M":
                    nightEvents.append("The Mafia were having sexy time and were too busy to kill anyone.")
                    mafiaSelected = None
                elif players[hookerSelected]["Role"] == "D":
                    nightEvents.append("The Doctor was having sexy time and couldn't save anyone.")
                    doctorSelected = None

            random.shuffle(alivePlayers)
            narrateConfirm = False
            confirmEmote = emotes["Confirm"]
            
            if doctorSelected != None and doctorSelected == mafiaSelected:
                nightEvents.append("The Doctor was able to save " + mafiaSelected.name + " from being killed by the mafia. " + alivePlayers[0].name + " please narrate.")
                narrateConfirm = True
                await bot.add_reaction(nightMessage, confirmEmote)
            else:
                if mafiaSelected != None:
                    alivePlayers.remove(mafiaSelected)
                    players[mafiaSelected]["Status"] = "Dead"
                    await bot.send_message(mafiaSelected, "You have been killed by the mafia.")
                    nightEvents.append(mafiaSelected.name + " was killed by the mafia (role: " + roleNames[players[mafiaSelected]["Role"]] + "). " + alivePlayers[0].name + " please narrate.")
                    narrateConfirm = True
                    await bot.add_reaction(nightMessage, confirmEmote)

            await bot.edit_message(nightMessage, "\n".join(nightEvents))

            while (narrateConfirm == True):
                reaction = await bot.wait_for_reaction(message = nightMessage)
                if reaction.user == bot.user:
                    continue
                if reaction.user != alivePlayers[0] or reaction.reaction.emoji != confirmEmote:
                    await bot.remove_reaction(nightMessage, reaction.reaction.emoji, reaction.user)
                else:
                    await bot.remove_reaction(nightMessage, reaction.reaction.emoji, reaction.user)
                    await bot.remove_reaction(nightMessage, reaction.reaction.emoji, bot.user)
                    narrateConfirm = False

            gameInfo["time"] = "Day"
            gameInfo["turn"] += 1

        # check if game is over (count alive player roles)

        if jokerWin:
            await bot.send_message(gameInfo["channel"], "The Joker Wins!")
            gameInfo["state"] = "Lobby"
        else:
            civCount = 0
            mafiaCount = 0
            specialsCount = 0
            
            for p in players:
                if players[p]["Status"] == "Alive":
                    team = players[p]["Role"]
                    if team == "C" :
                        civCount += 1
                    elif team == "M":
                        mafiaCount += 1
                    elif team == "J" or team == "S" or team == "D" or team == "H":
                        specialsCount += 1

            if (mafiaCount >= civCount and specialsCount == 0) or (mafiaCount == 1 and specialsCount == 1 and civCount == 0):
                await bot.send_message(gameInfo["channel"], "The Mafia Win!")
                gameInfo["state"] = "Lobby"
            elif mafiaCount == 0:
                await bot.send_message(gameInfo["channel"], "The Civilians Win!")
                gameInfo["state"] = "Lobby"
    for mafiaPlayer in mafiaIDs:
        await bot.edit_channel_permissions(gameInfo["mafia_channel"], mafiaPlayer, discord.PermissionOverwrite(read_messages=False))

    messages =[]
    async for x in bot.logs_from(gameInfo["mafia_channel"], 99):
        messages.append(x)
    try:
        await bot.delete_messages(messages)
    except:
        print("start(): Failed to bulk delete messages")
        
    await bot.change_presence(game=discord.Game(name="Mafia [Lobby]"))
                    
@bot.command(pass_context = True)
async def end(context):
    if gameInfo["open"] == False:
        return
    gameInfo["state"] = "Lobby"
    for mafiaPlayer in mafiaIDs:
        await bot.edit_channel_permissions(gameInfo["mafia_channel"], mafiaPlayer, discord.PermissionOverwrite(read_messages=False))
    messages =[]
    async for x in bot.logs_from(gameInfo["mafia_channel"], 99):
        messages.append(x)
    try:
        await bot.delete_messages(messages)
    except:
        print("end(): Failed to bulk delete messages")

@bot.command(pass_context = True)
async def ping(context): # Replies "Pong!" with the ping of the bot.
    start = time.time() #Gets the time before the message
    msg = await bot.say("Pong!") #Says the message
    end = time.time() #Gets the time after the message
    await bot.edit_message(msg, "Pong! " + str(math.ceil((end-start)*1000)) + "ms")

@bot.command(pass_context = True)
async def clean(context):
    async for x in bot.logs_from(context.message.channel, limit = 100):
        if x.content.startswith(prefix) or x.author == bot.user:
            await bot.delete_message(x)
			
@bot.command(pass_context = True)
async def exitprogram(context):
	quit()
	
@bot.command(pass_context = True)
async def rules(context):
	await bot.say("Rules```" + 
		"Mafia is split into two main teams: the Civilians and the Mafia\n" + 
		"The Civilians win by killing off all the Mafia, and vice versa\n" + 
		"\n" +
		"At the start of the game, each player is given a role:\n" + 
		"Civilian: Normie plebian with no special functions\n" + 
		"Mafia: Try to kill all non-Mafia to win the game\n" +
		"Detective: Can investigate one player every night to check if they are Mafia or not\n" +
		"Doctor: Can save on player every night from potential death by Mafia\n" +
		"Joker: Special role which wins if voted off in the Day phase\n" +
		"Hooker: Can choose a player to interrupt during the Night phase (Mafia cannot kill if one of their members is chosen, Doctor cannot save if chosen)\n" +
		"\n" +
		"The game has two phases: Night and Day\n" +
		"During the Night phase, special roles will be able to choose players to perform an action on\n"+
		"During the Day phase, all players will vote to kill a player who they believe is the Mafia\n" +
		"These phases will alternate and the game will keep playing until one of the two main teams has won\n" +
		"\n" +
		"Through this Bot, voting is performed by clicking on the Discord Reactions\n"
		"```")


@bot.command(pass_context = True)
async def help(context):
	await bot.say("Command List```" +
		"Admin\n" + 
		prefix + "open: Sets up the mafia lobby.\n" +
		prefix + "close: Removes the mafia lobby.\n" +
		prefix + "fixchat: Re-positions chat channel positions in the case of discord desync.\n" +
                prefix + "clean: Deletes recent messages sent by the bot or commands issued by other users.\n" +
		"Users\n" + 
		prefix + "join: Joins the mafia lobby.\n" +
		prefix + "leave: Leaves the mafia lobby.\n" +
		prefix + "add @user: Forces @user to join the mafia lobby.\n" +
		prefix + "kick @user: Forces @user to leave the mafia lobby.\n" + 
		"Game\n" + 
		prefix + "start: Starts the game of mafia.\n" +
		prefix + "end: Stops the game of mafia.\n" +
		prefix + "rules: Displays the rules of mafia in active channel.\n" +
		"Tools\n" +
                prefix + "help: Displays this message in active channel.\n" +
		prefix + "ping: Finds total bot latency to irc server (send and receive).\n" +
		prefix + "userinfo (optional @user): Displays ClientIDs of either sender or @user.\n" +
		prefix + "channelinfo: Displays ChannelIDs of active channel.\n"
		+ "```")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.is_private:
        return
    if debug:
        print(message.content)
    if (message.content.startswith(prefix)):
        await bot.process_commands(message)
        try:
            await bot.delete_message(message)
        except:
            print("Unknown Message")

@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "["+bot.user.id+"]")
    await bot.change_presence(game=discord.Game(name="idle"))

bot.run(token,bot=False)
