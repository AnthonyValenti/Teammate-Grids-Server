import sqlite3
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

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

def getRandomPlayerPair():
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    solution=[]
    query = """
        SELECT name
        FROM playerNames
        ORDER BY RANDOM()
        LIMIT 2;
        """
    while len(solution)<8:
        result=cursor.execute(query).fetchall()
        pair=[]
        for name in result:
            pair.append(name[0])
        solution = getSolution(pair[0],pair[1])
    return pair,solution
    


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


# This endpoint takes 3 player names, [0] is the player on the row [1] is player on the col, [2] is the users guess
@app.post("/validate")
def validate_answer(player_list: PlayerList):
    if checkAnswer(player_list.playerNames[0],player_list.playerNames[2]) and checkAnswer(player_list.playerNames[1],player_list.playerNames[2]):
        return{"msg": "correct",
               "solution": getSolution(player_list.playerNames[0],player_list.playerNames[1])
               }
    else:
        return{"msg": "incorrect",
                "solution": getSolution(player_list.playerNames[0],player_list.playerNames[1])

                }
    
# This endpoint will return the row player names and col player names to be used for the game
# It will only return names in which a possible answer exists
@app.get("/playerNames")
def get_player_names():
    result1=getRandomPlayerPair()
    result2=getRandomPlayerPair()
    pair1,solution1=result1
    pair2,solution2=result2
    return {"pairs": (pair1,pair2),
            "solution":(solution1,solution2)
            }
