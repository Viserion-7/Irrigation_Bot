import os
import telebot
import requests
import json
import csv
import cred
botRunning=True
bot = telebot.TeleBot(cred.apitok)

def csvExport(data):

    filename = "movie.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(data)
        csvfile.close()
    
def getmovie(name):
    movieName=name.strip("/movie ")
    urlData=requests.get(f"http://www.omdbapi.com/?apikey={bot}="+movieName)
    
    global fields
    fields=urlData.json()
    title,year,rating,photo=fields["Title"],fields["Year"],fields["imdbRating"],fields["Poster"]
    output=f'{photo}\nTitle:{title}\nYear:{year}\nimDbRating:{rating}'
    return output

@bot.message_handler(commands=['start', 'hello'])
def greet(message):
    global botRunning
    botRunning = True
    bot.reply_to(
        message, 'Hello there! I am a bot that will show movie information for you and export it in a CSV file.\n\n')
    
@bot.message_handler(commands=['stop', 'bye'])
def goodbye(message):
    global botRunning
    botRunning = False
    bot.reply_to(message, 'Bye!\nHave a good time')
    


@bot.message_handler(func=lambda message: botRunning, commands=['help'])
def helpProvider(message):
    bot.reply_to(message, '1.0 You can use \"/movie MOVIE_NAME\" command to get the details of a particular movie. For eg: \"/movie The Shawshank Redemption\"\n\n2.0. You can use \"/export\" command to export all the movie data in CSV format.\n\n3.0. You can use \"/stop\" or the command \"/bye\" to stop the bot.')


@bot.message_handler(func=lambda message: botRunning, commands=['movie'])
def getMovie(message):
    bot.reply_to(message, 'Getting movie info...')
    out=getmovie(message.text)
    bot.reply_to(message,out)
  
@bot.message_handler(func=lambda message: botRunning, commands=['export'])
def getList(message):
    filename = "movie.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([fields["Title"],fields["Year"],fields["Ratings"][0]["Value"]])
        csvfile.close()
    bot.reply_to(message, 'Generating file...')
    file= open("movie.csv","r")
    bot.send_document(message.chat.id,file)
    file.close()

@bot.message_handler(func=lambda message: botRunning)
def default(message):
    bot.reply_to(message, 'I did not understand '+'\N{confused face}')
    
bot.infinity_polling()
