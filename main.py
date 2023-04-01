import discord
from discord.ext import commands
import json
import random

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "!!", help_command=None, intents = intents)
token = ""

list_language = ("anglais", "en", "allemand", "de", "espagnol", "es")
dict_num_personne = {"1" : "1iere personne du singulier de", "2" : "2ieme personne du singulier de", "3" : "3eme personne du singulier de", "4" : "1iere personne du pluriel de", "5" : "2ieme personne du pluriel de", "6" : "3ieme personne du pluriel de"}

def get_json(lang) -> dict:
    with open(f'/home/antoine/Desktop/revisions/db.json', "r") as file:
        return json.load(file)[lang]

@client.command()
async def start(ctx, lang = None):
    def checkMessageAnswer(message):
        return message.author == ctx.message.author and ctx.channel == message.channel and message.content.startswith("!!!")
    def checkMessage(message):
        return message.author == ctx.message.author and ctx.channel == message.channel
    if lang is None:
        await ctx.send("Quel langue veux-tu réviser?\n- anglais\n- espagnol\n- allemand")
        try:
            message = await client.wait_for("message", timeout = 60, check = checkMessage)
        except:
            return
        lang = message.content
    if lang not in list_language:
        await ctx.send("Langue invalide.")
        return
    if lang in ("anglais", "allemand", "espagnol"):
        lang = {"anglais": "en", "allemand": "de", "espagnol": "es"}[lang]

    list_exos = []
    data = get_json(lang)
    for exo in data.items():
        list_exos.append(f"- {len(list_exos) + 1} : {exo[0]}")
    list_exos = '\n'.join(list_exos)
    await ctx.send(f"Quel exercice veux-tu choisir (entre le numéro)?\n{list_exos}")
    try:
        message = await client.wait_for("message", timeout = 60, check = checkMessage)
    except:
        return
    if not message.content.isdigit():
        await ctx.send("Tu n'as pas renseigné l'index d'un exercice.")
        return
    
    exo = int(message.content)
    if exo > len(data) or exo <= 0:
        await ctx.send("Index inexistant")
        return
    name, exo = list(data.items())[exo-1][0], list(data.items())[exo-1][1]
    score = 0
    if exo["type"] == "trad":
        words = random.sample(exo["words"], len(exo["words"]))
        for word in words:
            w = random.randint(0, 1)
            resp = word[int(not w)]
            embed = discord.Embed(title = f"**{name}** ({score}/{len(exo['words'])})", description = f"traduction de {word[w]}:")
            await ctx.send(embed = embed)
            try:
                message = await client.wait_for("message", timeout = 30, check = checkMessageAnswer)
                if message.content == resp:
                    score += 1
                else:
                    await ctx.send(f"faux ({resp})")
            except:
                return
        await ctx.send(f"tu as {score} point")
    
    elif exo["type"] == f"trad-{lang}":
        words = random.sample(exo["words"], len(exo["words"]))
        for word in words:
            resp = word[1]
            embed = discord.Embed(title = f"**{name}** ({words.index(word)}/{len(exo['words'])})", description = f"traduction de __**{word[0]}**__:")
            embed.set_footer(text = f"score : {score}/{len(exo['words'])}")
            await ctx.send(embed = embed)
            try:
                message = await client.wait_for("message", timeout = 30, check = checkMessageAnswer)
                message.content = message.content[3:]
                if (isinstance(resp, list) and message.content.lower() in resp) or (type(resp) == str and message.content.lower() == resp):
                    score += 1
                    if isinstance(resp, list):
                        resp.remove(message.content.lower())
                        await ctx.send(f"il y avait aussi comme réponse possible :\n{resp}")
                else:
                    await ctx.send(f"faux ({resp})")
            except:
                await ctx.send(f"temps écoulé ({resp})")
        await ctx.send(f"tu as {score} point")

    elif exo["type"] == f"conj":
        words = random.sample(exo["words"], len(exo["words"]))
        for word in words:
            num = str(random.randint(1, 6))
            resp = word[2][num]
            embed = discord.Embed(title = f"**{name}** ({words.index(word)}/{len(exo['words'])})", description = f"conjugasion : {dict_num_personne[num]} __**{word[random.randint(0, 1)]}**__:")
            embed.set_footer(text = f"score : {score}/{len(exo['words'])}")
            await ctx.send(embed = embed)
            try:
                message = await client.wait_for("message", timeout = 45, check = checkMessageAnswer)
                message.content = message.content[3:]
                if (type(resp) == list and message.content in resp) or (type(resp) == str and message.content == resp):
                    score += 1
                else:
                    await ctx.send(f"faux ({resp})")
            except:
                await ctx.send(f"temps écoulé ({resp})")
        await ctx.send(f"tu as {score} point")
    
@client.event
async def on_command_error(ctx, error): #gestion global des erreurs
	if isinstance(error, commands.CommandNotFound):
		pass
	elif isinstance(error, commands.CheckFailure):
		pass
	elif isinstance(error, commands.MissingRequiredArgument):
		pass
	else:
		print(error)

client.run(token)
