import random 
import json 
import pickle
import numpy as np

import nltk

from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

from asyncio.windows_events import NULL
import discord
from discord.ext import commands
import wikipedia
from urllib import parse, request
import re
import youtube_dl
import os

lemmatizer = WordNetLemmatizer()

intents = json.loads(open ('intents.json').read().encode("utf-8").decode("utf-8"))

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.model')

def clean_up_setence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]

    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_setence(sentence)
    bag = [0] * len(words)
    for sentence_word in sentence_words:
        for i, word in enumerate(words):
            if word == sentence_word:
                bag[i] = 1

    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]

    ERROR_TRESHOLD = 0.25
    results = [[i,r] for i, r in enumerate(res) if r > ERROR_TRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

bot = commands.Bot(command_prefix='>', description="This is a Helper Bot")


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def suma(ctx, numOne: int, numTwo: int):
    await ctx.send(f'La respuesta es: {numOne + numTwo}')


@bot.command()
async def resta(ctx, numOne: int, numTwo: int):
    await ctx.send(f'La respuesta es: {numOne - numTwo}')


@bot.command()
async def multiplica(ctx, numOne: int, numTwo: int):
    await ctx.send(f'La respuesta es: {numOne * numTwo}')


@bot.command()
async def divide(ctx, numOne: int, numTwo: int):
    if numOne == 0 or numTwo == 0:
        await ctx.send('No puedo dividir un numero entre 0')
    else:
        await ctx.send(f'La respuesta es: {numOne / numTwo}')


@bot.command()
async def descargar(ctx, url : str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    await ctx.send('Se ha descargado la canción satisfactoriamente')


@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command()
async def busca(ctx, question, question2 = ''):
    wikipedia.set_lang("es")
    if question2:
        result = wikipedia.summary(f'{question} {question2}', sentences=1)
    else: 
        result = wikipedia.summary(f'{question}', sentences=1)
    await ctx.send(result)
   

@bot.listen()
async def on_message(message):
    if message.author == bot.user or '>' in message.content.lower():
        return
    ints = predict_class(message.content)
    res = get_response(ints, intents)
    await message.channel.send(res)

@bot.event
async def on_ready():
    print('Bot is ready')

while True: 
    bot.run('ODU1NTYyODM3ODk1MTUxNjQ2.YM0S_A.yqiJnVdE4mBSafZfnJwN07HxOno')
