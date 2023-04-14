import pika, json, os
from consumer import mysql

def start(uid):
    
    cur = mysql.connect().cursor()
    res = cur.execute(
        "SELECT info_srv_db.ReturnNumberOfClaimsPerUser(%s), info_srv_db.ReturnNumberOfWorkStatusClaimsPerUser(%s), info_srv_db.ReturnNumberOfClaimsPerUserCurrMonth(%s), info_srv_db.ReturnNumberOfActiveClaimsPerDep(%s);", (uid, uid, uid, uid) 
    ) 

    if res > 0:

        user_row = cur.fetchone()

        result = {
            "NumberOfClaimsPerUser": user_row[0],
            "NumberOfWorkStatusClaimsPerUser": user_row[0],
            "NumberOfClaimsPerUserCurrMonth": user_row[0],
            "NumberOfActiveClaimsPerDep": user_row[0],
        }

        return result 
    else: 
        result = {
            "tickets": "none"
        }

        return result 