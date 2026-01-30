from flask import Flask, render_template, session, jsonify, request
import random

app = Flask(__name__)
app.secret_key = 'cyber_deck_key_777'


def create_card(name, cost, type, value, description):
    return {
        'id': random.randint(1000, 9999),
        'name': name,
        'cost': cost,
        'type': type,
        'value': value,
        'desc': description
    }


def generate_starter_deck():
    deck = []
    for _ in range(5):
        deck.append(create_card("Strike", 1, "attack", 6, "Deal 6 DMG"))
    for _ in range(4):
        deck.append(create_card("Shield", 1, "block", 5, "Gain 5 Armor"))
    deck.append(create_card("Hack", 2, "special", 10, "Deal 10 DMG + Heal 2"))
    deck.append(create_card("Overclock", 0, "buff", 2, "Gain 2 Energy"))
    random.shuffle(deck)
    return deck


def get_enemy_action():
    actions = [
        {'type': 'attack', 'value': 10, 'desc': 'Charging Laser (10 DMG)'},
        {'type': 'attack', 'value': 15, 'desc': 'Heavy Smash (15 DMG)'},
        {'type': 'defend', 'value': 10, 'desc': 'Firewall (Gain 10 Armor)'},
        {'type': 'buff', 'value': 0, 'desc': 'Scanning (No Action)'}
    ]
    return random.choice(actions)


def draw_cards(count):
    deck = session['deck']
    hand = session['hand']
    discard = session['discard']

    for _ in range(count):
        if len(deck) == 0:
            if len(discard) == 0:
                break
            deck = discard[:]
            discard = []
            random.shuffle(deck)

        if len(deck) > 0:
            hand.append(deck.pop(0))

    session['deck'] = deck
    session['hand'] = hand
    session['discard'] = discard


@app.route('/')
def index():
    session.clear()

    session['player'] = {'hp': 50, 'max_hp': 50, 'energy': 3, 'max_energy': 3, 'armor': 0}
    session['enemy'] = {'name': 'Cyber-Lich', 'hp': 80, 'max_hp': 80, 'armor': 0}

    session['deck'] = generate_starter_deck()
    session['hand'] = []
    session['discard'] = []

    session['enemy_intent'] = get_enemy_action()
    session['game_over'] = False
    session['log'] = ["System Initialized.", "Enemy detected."]

    draw_cards(5)

    return render_template('index.html')


@app.route('/play_card', methods=['POST'])
def play_card():
    if session['game_over']:
        return jsonify(get_state())

    card_id = request.json.get('card_id')
    hand = session['hand']
    player = session['player']
    enemy = session['enemy']
    discard = session['discard']

    card_index = -1
    played_card = None

    for i, card in enumerate(hand):
        if card['id'] == card_id:
            card_index = i
            played_card = card
            break

    if played_card and player['energy'] >= played_card['cost']:
        player['energy'] -= played_card['cost']
        hand.pop(card_index)
        discard.append(played_card)

        if played_card['type'] == 'attack':
            dmg = played_card['value']
            if enemy['armor'] > 0:
                blocked = min(enemy['armor'], dmg)
                enemy['armor'] -= blocked
                dmg -= blocked
            enemy['hp'] -= dmg
            session['log'].insert(0, f"Used {played_card['name']} for {played_card['value']} DMG")

            if played_card['name'] == 'Hack':
                player['hp'] = min(player['max_hp'], player['hp'] + 2)

        elif played_card['type'] == 'block':
            player['armor'] += played_card['value']
            session['log'].insert(0, f"Used {played_card['name']}, gained {played_card['value']} Armor")

        elif played_card['type'] == 'buff':
            player['energy'] += played_card['value']
            session['log'].insert(0, f"Used {played_card['name']}, energy surged!")

        if enemy['hp'] <= 0:
            enemy['hp'] = 0
            session['game_over'] = True
            session['log'].insert(0, "TARGET ELIMINATED.")

    session['player'] = player
    session['enemy'] = enemy
    session['hand'] = hand
    session['discard'] = discard

    return jsonify(get_state())


@app.route('/end_turn', methods=['POST'])
def end_turn():
    if session['game_over']:
        return jsonify(get_state())

    player = session['player']
    enemy = session['enemy']
    discard = session['discard']
    hand = session['hand']

    discard.extend(hand)
    session['hand'] = []
    session['discard'] = discard

    intent = session['enemy_intent']

    if intent['type'] == 'attack':
        dmg = intent['value']
        if player['armor'] > 0:
            blocked = min(player['armor'], dmg)
            player['armor'] -= blocked
            dmg -= blocked
        player['hp'] -= dmg
        session['log'].insert(0, f"Enemy hit you for {dmg} DMG!")

    elif intent['type'] == 'defend':
        enemy['armor'] += intent['value']
        session['log'].insert(0, "Enemy reinforced shields.")

    if player['hp'] <= 0:
        player['hp'] = 0
        session['game_over'] = True
        session['log'].insert(0, "CRITICAL SYSTEM FAILURE.")

    player['energy'] = player['max_energy']
    player['armor'] = 0
    enemy['armor'] = 0

    session['player'] = player
    session['enemy'] = enemy

    if not session['game_over']:
        session['enemy_intent'] = get_enemy_action()
        draw_cards(5)

    return jsonify(get_state())


def get_state():
    return {
        'player': session['player'],
        'enemy': session['enemy'],
        'hand': session['hand'],
        'deck_count': len(session['deck']),
        'discard_count': len(session['discard']),
        'enemy_intent': session['enemy_intent'],
        'game_over': session['game_over'],
        'log': session['log'][:5]
    }


if __name__ == '__main__':
    app.run(debug=True, port=5004)