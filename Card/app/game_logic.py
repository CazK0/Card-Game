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

    random.shuffle(deck)
    return deck


def get_enemy_intent():
    actions = [
        {'type': 'attack', 'value': 6, 'desc': 'Quick Beam (6 DMG)'},
        {'type': 'attack', 'value': 9, 'desc': 'Charged Shot (9 DMG)'},
        {'type': 'defend', 'value': 8, 'desc': 'Firewall (Gain 8 Armor)'},
        {'type': 'buff', 'value': 0, 'desc': 'Scanning (No Action)'}
    ]
    return random.choice(actions)


def draw_cards(session, count):
    deck = session['deck']
    hand = session['hand']
    discard = session['discard']

    for _ in range(count):
        if not deck:
            if not discard: break
            deck = discard[:]
            discard = []
            random.shuffle(deck)

        if deck:
            hand.append(deck.pop(0))

    session['deck'] = deck
    session['hand'] = hand
    session['discard'] = discard