from datetime import datetime, timedelta

def get_expiry_text(expiry: datetime):
    if (expiry < datetime.utcnow()):
        text = "expired"
    else:
        text = ""
        td = (expiry - datetime.utcnow())
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days > 0:
            text += f"{days}d "
        if hours > 0:
            text += f"{hours}h "
        if minutes > 0:
            text += f"{minutes}m" 
            
    return text.rstrip()
    