import pika, json, os
import pandas as pd
from consumer import mysql

# kd_graph = { 0: 'x', 1: 'y'}
# kd_recent_tickets = { 0: 'txId', 1: 'user', 2: 'date', 3: 'priority'}
# kd_recent_rating = { 0: 'intime', 1: 'expired', 2: 'position'}
# kd_tickets = {0: 'id', 1: 'number', 2: 'customer', 3: 'summary', 4: 'status', 5: 'priority', 6: 'assignee', 7: 'dep'}
# kd_ReturnFaqList = { 0: 'header', 1: 'descr'}
# kd_rating = { 0: 'uID', 1: 'user', 2: 'koef', 3: 'zone' }
# kd_PersRating = { 0: 'return', 1: 'expired', 2: 'taken', 3: 'frod', 4: 'intime' }

def merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

def replace_keys(old_dict, key_dict):
    new_dict = { }
    for key in old_dict.keys():
        new_key = key_dict.get(key, key)
        if isinstance(old_dict[key], dict):
            new_dict[new_key] = replace_keys(old_dict[key], key_dict)
        else:
            new_dict[new_key] = old_dict[key]
    return new_dict

def dash(uid):
    
    kd = { 0: 'x', 1: 'y'}

    result = {
        "ticketNum": "none",
        "workTicketNum":  "none",
        "closedTicketNum": "none",
        "activeTicketNum":  "none"
        }
    

    cur = mysql.connect().cursor()
    res = cur.execute(
        "SELECT info_srv_db.ReturnNumberOfClaimsPerUser(%s), info_srv_db.ReturnNumberOfWorkStatusClaimsPerUser(%s), info_srv_db.ReturnNumberOfClaimsPerUserCurrMonth(%s), info_srv_db.ReturnNumberOfActiveClaimsPerDep(%s);", (uid, uid, uid, uid) 
    ) 

    if res > 0:

        user_row = cur.fetchone()

        result["ticketNum"] = user_row[0]
        result["workTicketNum"] = user_row[1]
        result["closedTicketNum"] = user_row[2]
        result["activeTicketNum"] = user_row[3]
        print(" [x] Got ticketNum, workTicketNum, closedTicketNum, activeTicketNum")
    
    cur.callproc('ReturnNumberOfClosedTicketsByDepEachMonth', [uid])

    df_sql_data = pd.DataFrame(cur.fetchall())

    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnNumberOfClosedTicketsByDepEachMonth" : data}
        result = merge(result, data)
    else: 
        data = {"ReturnNumberOfClosedTicketsByDepEachMonth" : "none"}
        result = merge(result, data)
        return result 
    
    cur.callproc('ReturnNumberOfClosedTicketsByUserEachMonth', [uid])

    df_sql_data = pd.DataFrame(cur.fetchall())
    
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnNumberOfClosedTicketsByUserEachMonth" : data}
        result = merge(result, data)
        
    else: 
        data = {"ReturnNumberOfClosedTicketsByUserEachMonth" : "none"}
        result = merge(result, data)
        return result 
    
    cur.callproc('ReturnNumberOfCreatedTicketsByDepEachMonth', [uid])

    df_sql_data = pd.DataFrame(cur.fetchall())
    
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnNumberOfCreatedTicketsByDepEachMonth" : data}
        result = merge(result, data) 
    else: 
        data = {"ReturnNumberOfCreatedTicketsByDepEachMonth" : "none"}
        result = merge(result, data)
        return result 
    
    res = cur.execute(
        "SELECT info_srv_db.ReturnNumberOfTicketsByDep(%s);", (uid) 
    ) 

    if res > 0:
        data = {"ReturnNumberOfTicketsByDep": "none"}
        user_row = cur.fetchone()
        data["ReturnNumberOfTicketsByDep"] = user_row[0]
        result = merge(result, data) 
    
    cur.callproc('ReturnLastMonthTicketsByDep', [uid])

    df_sql_data = pd.DataFrame(cur.fetchall())
    
    kd = { 0: 'txId', 1: 'user', 2: 'date', 3: 'priority'}

    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnLastMonthTicketsByDep" : data}
        result = merge(result, data) 
    else: 
        data = {"ReturnLastMonthTicketsByDep" : "none"}
        result = merge(result, data)
        return result 
    
    cur.callproc('ReturnLastMonthRatingData', [uid])

    df_sql_data = pd.DataFrame(cur.fetchall())
    
    kd = { 0: 'intime', 1: 'expired', 2: 'position'}

    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnLastMonthRatingData" : data}
        result = merge(result, data) 
        return json.dumps(result) 
    else: 
        data = {"ReturnLastMonthRatingData" : "none"}
        result = merge(result, data)
        return result 
    
def tickets(uid, role):
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = {0: 'id', 1: 'number', 2: 'customer', 3: 'summary', 4: 'status', 5: 'priority', 6: 'assignee', 7: 'dep'}

    match role:
        case "admin":
            cur.callproc('ReturnAllTickets')
            df_sql_data = pd.DataFrame(cur.fetchall())
            if not df_sql_data.empty:
                data = df_sql_data.to_dict('index')
                data = replace_keys(data, kd)
                data = { "ReturnAllTickets" : data}
                result = merge(result, data)
                return json.dumps(result) 
            else: 
                data = {"ReturnAllTickets" : "none"}
                result = merge(result, data)
                return result 
        case "worker":
            cur.callproc('ReturnAllTicketsByExecutor', [uid])
            df_sql_data = pd.DataFrame(cur.fetchall())
            if not df_sql_data.empty:
                data = df_sql_data.to_dict('index')
                data = replace_keys(data, kd)
                data = { "ReturnAllTicketsByExecutor" : data}
                result = merge(result, data)
                return json.dumps(result) 
            else: 
                data = {"ReturnAllTicketsByExecutor" : "none"}
                result = merge(result, data)
                return result 
        case "user":
            cur.callproc('ReturnAllTicketsByInitiator', [uid])
            df_sql_data = pd.DataFrame(cur.fetchall())
            if not df_sql_data.empty:
                data = df_sql_data.to_dict('index')
                data = replace_keys(data, kd)
                data = { "ReturnAllTicketsByInitiator" : data}
                result = merge(result, data)
                return json.dumps(result) 
            else: 
                data = {"ReturnAllTicketsByInitiator" : "none"}
                result = merge(result, data)
                return result 
            
def faq():
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = { 0: 'header', 1: 'descr'}

    cur.callproc('ReturnFaqList')
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnFaqList" : data}
        result = merge(result, data)
        return json.dumps(result) 
    else: 
        data = {"ReturnFaqList" : "none"}
        result = merge(result, data)
        return result 
    
def rating(uid):
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = { 0: 'uID', 1: 'user', 2: 'koef', 3: 'zone' }

    cur.callproc('ReturnCurrRatingList')
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnCurrRatingList" : data}
        result = merge(result, data)
    else: 
        data = {"ReturnCurrRatingList" : "none"}
        result = merge(result, data)
        return result 
    
    cur.callproc('ReturnOldRatingList')
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnOldRatingList" : data}
        result = merge(result, data)
    else: 
        data = {"ReturnOldRatingList" : "none"}
        result = merge(result, data)
        return result 
    
    kd = { 0: 'return', 1: 'expired', 2: 'taken', 3: 'frod', 4: 'intime' }

    cur.callproc('ReturnRatingStatByUser', [uid])
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnRatingStatByUser" : data}
        result = merge(result, data)
        return json.dumps(result) 
    else: 
        data = {"ReturnRatingStatByUser" : "none"}
        result = merge(result, data)
        return result 
    
def profile(uid):
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = { 0: 'name', 1: 'position', 2: 'email', 3: 'phone', 4: 'role', 5: 'dep', 6: 'status' }

    cur.callproc('ReturnUserData', [uid])
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnUserData" : data}
        result = merge(result, data)
        return json.dumps(result) 
    else: 
        data = {"ReturnUserData" : "none"}
        result = merge(result, data)
        return result 
    
def users():
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = { 0: 'id', 1: 'internal_num', 2: 'name', 3: 'dep', 4: 'position', 5: 'isVerified', 6: 'status' }

    cur.callproc('ReturnListOfAllUsers')
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnListOfAllUsers" : data}
        result = merge(result, data)
        return json.dumps(result) 
    else: 
        data = {"ReturnListOfAllUsers" : "none"}
        result = merge(result, data)
        return result 
    
def roles():
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = { 0: 'role', 1: 'kol' }

    cur.callproc('ReturnListOfRoles')
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnListOfRoles" : data}
        result = merge(result, data)
        return json.dumps(result) 
    else: 
        data = {"ReturnListOfRoles" : "none"}
        result = merge(result, data)
        return result 
    
def deps():
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = { 0: 'dep', 1: 'kol' }

    cur.callproc('ReturnListOfDeps')
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnListOfDeps" : data}
        result = merge(result, data)
        return json.dumps(result) 
    else: 
        data = {"ReturnListOfDeps" : "none"}
        result = merge(result, data)
        return result 
    
def statuses():
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = { 0: 'id', 1: 'status' }

    cur.callproc('ReturnAllStatuses')
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnAllStatuses" : data}
        result = merge(result, data)
        return json.dumps(result) 
    else: 
        data = {"ReturnAllStatuses" : "none"}
        result = merge(result, data)
        return result 
    
def priorities():
    
    result = {}
    
    cur = mysql.connect().cursor()

    kd = { 0: 'id', 1: 'priority' }

    cur.callproc('ReturnListOfPriorities')
    df_sql_data = pd.DataFrame(cur.fetchall())
    if not df_sql_data.empty:
        data = df_sql_data.to_dict('index')
        data = replace_keys(data, kd)
        data = { "ReturnListOfPriorities" : data}
        result = merge(result, data)
        return json.dumps(result) 
    else: 
        data = {"ReturnListOfPriorities" : "none"}
        result = merge(result, data)
        return result 