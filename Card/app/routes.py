from flask import Blueprint, render_template, session, jsonify, request
from .game_logic import generate_deck, get_enemy_intent, process_draw, get_enemy_by_level
import math

main = Blueprint('main', __name__)

@main.route('/')
def index():
    session.clear()
    session['player'] = {'hp': 50, 'max_hp': 50, 'energy': 3, 'max_energy': 3, 'armor': 0}
    session['level'] = 1
    
    enemy = get_enemy_by_level(1)
    session['enemy'] = enemy
    
    session['deck'] = generate_deck()
    session['hand'] = []
    session['discard'] = []
    session['enemy_intent'] = get_enemy_intent(enemy['name'])
    session['game_over'] = False
    session['result'] = ''
    session['log'] = ["System Initialized.", "Floor 1: Security Drone detected."]
    
    deck, hand, discard = process_draw(session['deck'], session['hand'], session['discard'], 5)
    session['deck'] = deck
    session['hand'] = hand
    session['discard'] = discard
    
    session.modified = True 
    return render_template('index.html')

@main.route('/play_card', methods=['POST'])
def play_card():
    if session.get('game_over'): return jsonify(get_state())

    card_id = request.json.get('card_id')
    hand = session['hand']
    player = session['player']
    enemy = session['enemy']
    discard = session['discard']
    
    played_index = -1
    for i, c in enumerate(hand):
        if c['id'] == card_id:
            played_index = i
            break
            
    if played_index != -1:
        played = hand[played_index]
        
        if player['energy'] >= played['cost']:
            player['energy'] -= played['cost']
            hand.pop(played_index)
            discard.append(played)
            
            if played['type'] == 'attack':
                dmg = played['value']
                if enemy['armor'] > 0:
                    blocked = min(enemy['armor'], dmg)
                    enemy['armor'] -= blocked
                    dmg -= blocked
                enemy['hp'] -= dmg
                session['log'].insert(0, f"Used {played['name']} for {played['value']} DMG")
                
                if played['name'] == 'Hack':
                    player['hp'] = min(player['max_hp'], player['hp'] + 2)

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
                if st == 'glitch' and played['value'] > 0:
                    enemy['hp'] -= 2

            if enemy['hp'] <= 0:
                enemy['hp'] = 0
                handle_enemy_death(session)

            session['hand'] = hand
            session['discard'] = discard
            session['player'] = player
            session['enemy'] = enemy
            session.modified = True 

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
        enemy['hp'] = 0
        handle_enemy_death(session)
        session.modified = True
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
        player['hp'] = 0
        session['game_over'] = True
        session['result'] = 'DEFEAT'
        session['log'].insert(0, "CRITICAL FAILURE")

    player['energy'] = player['max_energy']
    player['armor'] = 0
    enemy['armor'] = 0
    
    deck, hand, discard = process_draw(session['deck'], session['hand'], session['discard'], 5)
    session['deck'] = deck
    session['hand'] = hand
    session['discard'] = discard
    
    session['enemy_intent'] = get_enemy_intent(enemy['name'])
    session['player'] = player
    session['enemy'] = enemy
    session.modified = True 
    
    return jsonify(get_state())

def handle_enemy_death(session):
    next_level = session['level'] + 1
    new_enemy = get_enemy_by_level(next_level)
    
    session['log'].insert(0, f"TARGET DESTROYED. Healing 10 HP.")
    session['player']['hp'] = min(session['player']['max_hp'], session['player']['hp'] + 10)
    
    if new_enemy:
        session['level'] = next_level
        session['enemy'] = new_enemy
        session['enemy_intent'] = get_enemy_intent(new_enemy['name'])
        session['player']['energy'] = session['player']['max_energy']
        session['player']['armor'] = 0
        
        session['discard'].extend(session['hand'])
        session['hand'] = []
        deck, hand, discard = process_draw(session['deck'], session['hand'], session['discard'], 5)
        session['deck'] = deck
        session['hand'] = hand
        session['discard'] = discard
        
        session['log'].insert(0, f"Approaching Floor {next_level}: {new_enemy['name']}")
    else:
        session['game_over'] = True
        session['result'] = 'VICTORY'
        session['log'].insert(0, "ALL THREATS NEUTRALIZED.")

def get_state():
    return {
        'player': session['player'],
        'enemy': session['enemy'],
        'hand': session['hand'],
        'deck_count': len(session['deck']),
        'discard_count': len(session['discard']),
        'enemy_intent': session['enemy_intent'],
        'game_over': session['game_over'],
        'result': session.get('result', ''),
        'level': session['level'],
        'log': session['log'][:5]
    }
