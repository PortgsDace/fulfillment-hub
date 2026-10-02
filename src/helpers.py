import datetime
from .constants import *

def calculate_sla_status(sla_deadline_str):
    if not sla_deadline_str:
        return "SAFE"
    
    try:
        sla = datetime.datetime.fromisoformat(sla_deadline_str)
        now = datetime.datetime.now()
        diff = (sla - now).total_seconds() / 3600 # hours
        
        if diff < 0:
            return "OVERDUE"
        elif diff < 0.5:
            return "URGENT"
        elif diff < 2.0:
            return "AT RISK"
        else:
            return "SAFE"
    except:
        return "SAFE"

def get_priority_score(order):
    score = 0
    if order.get('priority') == PRIORITY_URGENT:
        score += 100
        
    sla_status = calculate_sla_status(order.get('sla_deadline'))
    if sla_status == "OVERDUE":
        score += 50
    elif sla_status == "URGENT":
        score += 30
    elif sla_status == "AT RISK":
        score += 15
        
    return score
