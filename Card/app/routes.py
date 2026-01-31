from flask import Blueprint, render_template, session, jsonify, request
from .game_logic import generate_deck, get_enemy_intent, draw_cards
import math

main = Blueprint('main', __name__)


@main.route('/')
def index():
    session.clear()
    session['player'] = {'hp': 50, 'max_hp': 50, 'energy': 3, 'max_energy': 3, 'armor': 0}
    session['enemy'] = {'name': 'Cyber-Lich', 'hp': 80, 'max_hp': 80, 'armor': 0, 'status': {'glitch': 0, 'lag': 0}}

    session['deck'] = generate_deck()
    session['hand'] = []
    session['discard'] = []
    session['enemy_intent'] = get_enemy_intent()
    session['game_over'] = False
    session['log'] = ["System Initialized.", "Enemy detected."]

    draw_cards(session, 5)
    return render_template('index.html')


@main.route('/play_card', methods=['POST'])
def play_card():
    if session.get('game_over'): return jsonify(get_state())

    card_id = request.json.get('card_id')
    hand = session['hand']
    player = session['player']
    enemy = session['enemy']

    played = next((c for c in hand if c['id'] == card_id), None)

    if played and player['energy'] >= played['cost']:
        player['energy'] -= played['cost']
        hand.remove(played)
        session['discard'].append(played)

        if played['type'] == 'attack':
            dmg = played['value']
            if enemy['armor'] > 0:
                blocked = min(enemy['armor'], dmg)
                enemy['armor'] -= blocked
                dmg -= blocked
            enemy['hp'] -= dmg
            session['log'].insert(0, f"Used {played['name']} for {played['value']} DMG")
            if played['name'] == 'Hack': player['hp'] = min(player['max_hp'], player['hp'] + 2)

        elif played['type'] == 'block':
            player['armor'] += played['value']
            session['log'].insert(0, f"Shields up! +{played['value']} Armor")

        elif played['type'] == 'buff':
            player['energy'] += played['value']
            session['log'].insert(0, "Energy Surged!")

        elif played['type'] == 'debuff':
            st = played['status']
            enemy['status'][st] += played['value']
            session['log'].insert(0, f"Applied {played['value']} {st.upper()}")
            if st == 'glitch': enemy['hp'] -= 2

        if enemy['hp'] <= 0:
            enemy['hp'] = 0
            session['game_over'] = True
            session['log'].insert(0, "TARGET ELIMINATED.")

    return jsonify(get_state())


@main.route('/end_turn', methods=['POST'])
def end_turn():
    if session.get('game_over'): return jsonify(get_state())

    player = session['player']
    enemy = session['enemy']

    session['discard'].extend(session['hand'])
    session['hand'] = []

    if enemy['status']['glitch'] > 0:
        dmg = enemy['status']['glitch']
        enemy['hp'] -= dmg
        enemy['status']['glitch'] -= 1
        session['log'].insert(0, f"Glitch dealt {dmg} DMG")

    if enemy['hp'] <= 0:
        session['game_over'] = True
        return jsonify(get_state())

    intent = session['enemy_intent']
    if intent['type'] == 'attack':
        dmg = intent['value']
        if enemy['status']['lag'] > 0:
            dmg = math.floor(dmg * 0.5)
            enemy['status']['lag'] -= 1
            session['log'].insert(0, "Lag Reduced DMG by 50%")

        if player['armor'] > 0:
            blocked = min(player['armor'], dmg)
            player['armor'] -= blocked
            dmg -= blocked
        player['hp'] -= dmg
        session['log'].insert(0, f"Enemy hit you for {dmg} DMG")

    elif intent['type'] == 'defend':
        enemy['armor'] += intent['value']
        session['log'].insert(0, "Enemy reinforced shields")

    if player['hp'] <= 0:
        session['game_over'] = True
        session['log'].insert(0, "CRITICAL FAILURE")

    player['energy'] = player['max_energy']
    player['armor'] = 0
    enemy['armor'] = 0
    session['enemy_intent'] = get_enemy_intent()
    draw_cards(session, 5)

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