import random
import math

def create_card(id, name, cost, type, value, desc, status=None):
    return {
        'id': id,
        'name': name,
        'cost': cost,
        'type': type,
        'value': value,
        'desc': desc,
        'status': status
    }

def generate_deck():
    deck = []
    cid = 1000
    for _ in range(4):
        deck.append(create_card(cid, "Strike", 1, "attack", 6, "Deal 6 DMG"))
        cid += 1
    for _ in range(3):
        deck.append(create_card(cid, "Shield", 1, "block", 5, "Gain 5 Armor"))
        cid += 1
    
    deck.append(create_card(cid, "Virus", 1, "debuff", 3, "Apply 3 Glitch", "glitch"))
    cid += 1
    deck.append(create_card(cid, "DDoS", 2, "debuff", 2, "Apply 2 Lag", "lag"))
    cid += 1
    deck.append(create_card(cid, "Hack", 2, "special", 8, "Deal 8 DMG + Heal 2"))
    cid += 1
    deck.append(create_card(cid, "Overclock", 0, "buff", 2, "Gain 2 Energy"))
    cid += 1
    
    random.shuffle(deck)
    return deck

def get_enemy_by_level(level):
    if level == 1:
        return {'name': 'Security Drone', 'hp': 40, 'max_hp': 40, 'armor': 0, 'status': {'glitch': 0, 'lag': 0}}
    elif level == 2:
        return {'name': 'Neon Thug', 'hp': 60, 'max_hp': 60, 'armor': 0, 'status': {'glitch': 0, 'lag': 0}}
    elif level == 3:
        return {'name': 'Elite Mecha', 'hp': 90, 'max_hp': 90, 'armor': 15, 'status': {'glitch': 0, 'lag': 0}}
    elif level == 4:
        return {'name': 'The Mainframe', 'hp': 150, 'max_hp': 150, 'armor': 30, 'status': {'glitch': 0, 'lag': 0}}
    return None

def get_enemy_intent(enemy_name):
    if enemy_name == 'Security Drone':
        actions = [
            {'type': 'attack', 'value': 5, 'desc': 'Zapper (5 DMG)'},
            {'type': 'defend', 'value': 5, 'desc': 'Harden (5 Armor)'}
        ]
    elif enemy_name == 'Neon Thug':
        actions = [
            {'type': 'attack', 'value': 8, 'desc': 'Pipe Smash (8 DMG)'},
            {'type': 'attack', 'value': 4, 'desc': 'Shiv (4 DMG)'},
            {'type': 'defend', 'value': 8, 'desc': 'Block (8 Armor)'}
        ]
    elif enemy_name == 'Elite Mecha':
        actions = [
            {'type': 'attack', 'value': 12, 'desc': 'Railgun (12 DMG)'},
            {'type': 'defend', 'value': 15, 'desc': 'Energy Shield (15 Armor)'},
            {'type': 'buff', 'value': 0, 'desc': 'Targeting...'}
        ]
    elif enemy_name == 'The Mainframe':
        actions = [
            {'type': 'attack', 'value': 15, 'desc': 'Delete.exe (15 DMG)'},
            {'type': 'attack', 'value': 5, 'desc': 'Ping (5 DMG x 3)'},
            {'type': 'defend', 'value': 20, 'desc': 'Firewall Max (20 Armor)'}
        ]
    else:
        actions = [{'type': 'attack', 'value': 1, 'desc': 'Error'}]
        
    return random.choice(actions)

def process_draw(deck, hand, discard, count):
    for _ in range(count):
        if not deck:
            if not discard: break
            deck = discard[:]
            discard = []
            random.shuffle(deck)
        
        if deck:
            hand.append(deck.pop(0))
            
    return deck, hand, discard
