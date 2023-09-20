import sqlite3
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:19006",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# will receive a list containing of 3 players to validate 
# playerNames[0] will be the player on the row
# playerNames[1] will be the player on the col
# playerNames[2] will be the users entered answer
class PlayerList(BaseModel):
    playerNames: List[str]


def getPlayerQuery():
    query = """
    SELECT *
    FROM skaters20to22
    WHERE ? IN (column1, column2, column3, column4, column5, column6, column7, column8, column9, column10, column11, column12, column13, column14, column15, column16, column17, column18, column19)
    AND ? IN (column1, column2, column3, column4, column5, column6, column7, column8, column9, column10, column11, column12, column13, column14, column15, column16, column17, column18, column19)
    ;
    """
    return query

def getPlayedWithQuery():
    query = """
    SELECT *
    FROM skaters20to22
    WHERE ? IN (column1, column2, column3, column4, column5, column6, column7, column8, column9, column10, column11, column12, column13, column14, column15, column16, column17, column18, column19);
    """
    return query


def getRandomPlayer():
    query = """
    SELECT name
    FROM playerNames
    ORDER BY RANDOM()
    LIMIT 1;
    """
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    result=cursor.execute(query).fetchone()
    conn.close()
    name = result[0]
    return(name)
    
def getRandomPlayedWith(player):
    query = """
        SELECT *
        FROM skaters20to22
        WHERE ? IN (column1, column2, column3, column4, column5, column6, column7, column8, column9, column10, column11, column12, column13, column14, column15, column16, column17, column18, column19)
        ORDER BY RANDOM()
        LIMIT 1;
        """
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    result=cursor.execute(query,(player,)).fetchone()
    conn.close()
    resultList = list(result)
    random.shuffle(resultList)
    resultList.remove(player)
    name=resultList[0]
    return(name)
        


def checkAnswer(player1,player2):
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    results =[]
    cursor.execute(getPlayerQuery(),(player1,player2))
    result=cursor.fetchone()
    conn.close()
    if result is not None:
        results.append(result)
    if not results:
        return False
    else:
        return True
    
def getSolution(rowPlayer,colPlayer):
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    cursor.execute(getPlayedWithQuery(),(rowPlayer,))
    result=cursor.fetchall()
    playedWithRowPlayer=[]
    for row in result:
        for name in row:
            if name not in playedWithRowPlayer:
                playedWithRowPlayer.append(name)
    cursor.execute(getPlayedWithQuery(),(colPlayer,))
    result=cursor.fetchall()
    playedWithColPlayer=[]
    for row in result:
        for name in row:
            if name not in playedWithColPlayer:
                playedWithColPlayer.append(name)
    conn.close()
    intersection = [item for item in playedWithColPlayer if item in playedWithRowPlayer]
    intersection = list(filter(None, intersection))
    return intersection

 
# This endpoint will return the row player names and col player names to be used for the game
# It will only return names in which a possible answer exists
@app.get("/playerNames")
def get_player_names():
    player0=getRandomPlayer()
    player1=getRandomPlayedWith(player0)
    player2=getRandomPlayedWith(player1)
    player3=getRandomPlayedWith(player2)
    return {
            "rowPlayer1": player0,
            "colPlayer1": player1,
            "rowPlayer2": player2,
            "colPlayer2": player3,
            "solution0_0":getSolution(player0,player1),
            "solution0_1":getSolution(player0,player3),
            "solution1_0":getSolution(player1,player2),
            "solution1_1":getSolution(player2,player3),

            }
