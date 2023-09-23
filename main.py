import sqlite3
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import random
import datetime


app = FastAPI()

def createDB():
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    with open('teammateGrid.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()


class User(BaseModel):
    username: str
    password: str

class Player(BaseModel):
    name: str

class Score(BaseModel):
    username: str
    score: int

createDB()

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

def playedTogethor(player1,player2):
    query = """
    SELECT *
    FROM skaters20to22
    WHERE ? IN (column1, column2, column3, column4, column5, column6, column7, column8, column9, column10, column11, column12, column13, column14, column15, column16, column17, column18, column19);
    """
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    result=cursor.execute(query,(player1,)).fetchall()
    conn.close()
    for row in result:
        if player2 in row:
            return True
    return False

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
        ORDER BY RANDOM();
        """
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    result=cursor.execute(query,(player,)).fetchone()
    conn.close()
    if result is None:
        getRandomPlayedWith(player)
    resultList = list(result)
    random.shuffle(resultList)
    resultList.remove(player)
    name=resultList[0]
    return(name)
        



  
  
  
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

def generateNames():
    player0=getRandomPlayer()
    player1=getRandomPlayedWith(player0)
    player2=getRandomPlayedWith(player1)
    player3=getRandomPlayedWith(player2)
    if None in [player0, player1, player2, player3]:
        return generateNames()  
    names = [player0, player1, player2, player3]
    if len(names) != len(set(names)):
        return generateNames()
    if any(name is None for name in names):
        return generateNames()  
    return names

# This endpoint will return the row player names and col player names to be used for the game
# It will only return names in which a possible answer exists
@app.get("/playerNames")
def get_player_names():
    players=generateNames()
    return {
            "rowPlayer1": players[0],
            "colPlayer1": players[1],
            "rowPlayer2": players[2],
            "colPlayer2": players[3],
            "solution0_0":getSolution(players[0],players[1]),
            "solution0_1":getSolution(players[0],players[3]),
            "solution1_0":getSolution(players[1],players[2]),
            "solution1_1":getSolution(players[2],players[3]),

            }
@app.post("/login")
def user_login(user: User):
    query = """
        SELECT *
        FROM users
        WHERE username = ?
        AND password = ?;
        """
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    result=cursor.execute(query,(user.username,user.password)).fetchone()
    conn.close()
    if result is not None and str(result[0])==str(user.username) and str(result[1])==str(user.password):
        return{
            "msg":"ok",
            "user":user.username
            }
    return{
        "msg":"failed"
        }

@app.post("/register")
def user_register(user: User):
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    msg=""
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?);", (user.username, user.password))
        conn.commit()
        msg="ok"
    except sqlite3.IntegrityError:
        msg="failed"
    except Exception as e:
        msg="failed"
    finally:
        conn.close()    
        return{
            "msg": msg,
            "user": user.username
        }
    
#This function will get what quartile a player is in based on points, this will be used to determine a score multiplier
@app.post("/points")
def get_points(player: Player):
    query = """
    WITH QuartileData AS (
    SELECT
        name,
        points,
        NTILE(4) OVER (ORDER BY points) AS Quartile
    FROM
        playerNames
    )

    SELECT
    name,
    Quartile
    FROM
    QuartileData
    WHERE
    name = ?;
    """
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    result=cursor.execute(query,(player.name,)).fetchone()[1]
    mult = 4
    if(result ==4):
        mult=1
    if(result ==3):
        mult=2
    if(result == 2):
        mult =3 
    return {"mult":mult}

@app.post("/savePoints")
def save_points(scores: Score):
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    msg=""
    try:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO scores (username, score, date) VALUES (?, ?, ?);", (scores.username, scores.score, date ))
        conn.commit()
        msg="ok"
    except sqlite3.IntegrityError:
        msg="failed"
    except Exception as e:
        msg="failed"
    finally:
        conn.close()    
        return{
            "msg": msg,
            "user": scores.username,
            "score": scores.score,
            "date": date,
        }
    
@app.post("/scores")
def get_user_scores(user: Player):
    query = """
    SELECT * from scores
    where username = ?;
    """
    conn = sqlite3.connect('teammateGrid.db')
    cursor = conn.cursor()
    result=cursor.execute(query,(user.name,)).fetchall()
    return {"scores": result}

@app.post("/validate")
def check_solution(player1: Player, player2: Player):
    return getSolution(player1,player2)