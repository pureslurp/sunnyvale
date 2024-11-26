team_abbrev = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "LV", "PHI", "PIT", "LAC", "SF", "SEA", "LAR", "TB", "TEN", "WAS"]

manager_eff = {
    "Jon Gruden" : 0.863,
    "Im and the Gems" : 0.927,
    "Liver King III" : 0.893,
    "Miles Long" : 0.871,
    "Flavortown" : 0.827,
    "EZ DubZ" : 0.862,
    "Njigba’s in Paris" : 0.839,
    "Kamalas Hairy Clit" : 0.839,
    "Pitter Patter" : 0.891,
    "Gales" : 0.916,
    "A Nu Start" : 0.834,
    "ELC3" : 0.869
}

schedule = {
    'week13' : [['Im and the Gems', 'Miles Long'],
                ['EZ DubZ', 'Pitter Patter'],
                ['Jon Gruden', 'ELC3'],
                ['A Nu Start', 'Gales'],
                ['Flavortown', "Njigba’s in Paris"],
                ['Kamalas Hairy Clit', "Liver King III"]],
    'week14' : [['Im and the Gems', "Jon Gruden"],
                ['EZ DubZ', "Njigba’s in Paris"],
                ['A Nu Start', 'Kamalas Hairy Clit'],
                ['Miles Long', 'Liver King III'],
                ['Flavortown', "Gales"],
                ['Pitter Patter', 'ELC3']],
    'week15' : [["Im and the Gems", "Liver King III"],
                ['EZ DubZ', 'Gales'],
                ['Jon Gruden', 'Pitter Patter'],
                ['A Nu Start', 'Miles Long'],
                ['Flavortown', 'Kamalas Hairy Clit'],
                ["Njigba’s in Paris", 'ELC3']]
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