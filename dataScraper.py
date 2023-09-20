import requests
import csv

"""
This code scrapes the NHL API and gets the players that played in each regualar season game
I write the list of players that played for a team in a game to a single row in a CSV file
I can then use this CSV file to determine if a group of players have played togethor 
by checking if their names occur on the same row at least once in the file.
"""

rosterList=list()
for i in range(1, 1313):  # Start from 1 and go up to 1313 for 2021-2023 and up to 869 for 2020 because shorented season
    gameId = str(i).zfill(4)
    print(i)
    response = requests.get('https://statsapi.web.nhl.com/api/v1/game/202202{}/boxscore'.format(gameId)).json()
    homeRoster=list()
    awayRoster=list()
    for id in response['teams']['away']['skaters']:
        if id not in response['teams']['away']['scratches']:
            awayRoster.append(response['teams']['away']['players']["ID"+str(id)]['person']['fullName'])
    for id in response['teams']['home']['skaters']:
        if id not in response['teams']['home']['scratches']:
            homeRoster.append(response['teams']['home']['players']["ID"+str(id)]['person']['fullName'])
    for id in response['teams']['away']['goalies']:
        awayRoster.append(response['teams']['away']['players']["ID"+str(id)]['person']['fullName'])
    for id in response['teams']['home']['goalies']:
        homeRoster.append(response['teams']['home']['players']["ID"+str(id)]['person']['fullName'])
    rosterList.append(awayRoster)
    rosterList.append(homeRoster)
with open('2022Season.csv', mode="w", newline="") as file:
    csv_writer = csv.writer(file)
    for row in rosterList:
        csv_writer.writerow(row)