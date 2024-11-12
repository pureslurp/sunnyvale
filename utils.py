team_abbrev = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "LV", "PHI", "PIT", "LAC", "SF", "SEA", "LAR", "TB", "TEN", "WAS"]

manager_eff = {
    "Jon Gruden" : 0.852,
    "Im and the Gems" : 0.929,
    "Liver King III" : 0.898,
    "Miles Long" : 0.882,
    "Flavortown" : 0.85,
    "EZ DubZ" : 0.847,
    "Njigba’s in Paris" : 0.822,
    "Kamalas Hairy Clit" : 0.872,
    "Pitter Patter" : 0.882,
    "Gales" : 0.903,
    "A Nu Start" : 0.823,
    "ELC3" : 0.857
}

def extract_position(text) -> str:
    '''function that extracts the position from Yahoo player html'''
    try:
        text = text.split(" - ")[1].split(" ")[0]
    except:
        pass
    return text

def extract_player_name(text) -> str:
    '''function that extracts the player name from the Yahoo player html'''
    text = str(text).split("-")[0].strip()
    if text[-2:].upper() in team_abbrev:
        player = text[:-2]
    elif text[-3:].upper() in team_abbrev:
        player = text[:-3]
    else:
        player = text
    return player

def extract_team(text) -> None | str:
    '''function that extracts the team name from the Yahoo player html'''
    text = str(text).split("-")[0].strip()
    if text[-2:].upper() in team_abbrev:
        return text[-2:].upper()
    elif text[-3:].upper() in team_abbrev:
        return text[-3:].upper()
    else:
        return None