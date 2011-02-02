'The Simulated Bank Robbery, a story (not an IF) for telling via Curveship.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

from item_model import Actor, Room, Thing
from action_model import Behave, Configure, Sense
import can

discourse = {
    'metadata': {
         'title': 'The Simulated Bank Robbery'},
    'spin':
    {'commanded': '@robber', 'focalizer': '@robber', 'narratee': None,
     'time_words': False, 'room_name_headings': False}}

READ_SLIPS = Behave('read', '@teller', direct='@slips')
SNOOZE = Behave('snooze', '@guard',
    template='[agent/s] [snooze/ing/v]')
COUNT_SLIPS = Behave('count', '@teller', direct='@slips')
DON_MASK = Configure('wear', '@robber', direct='@mask', new=('on', '@robber'),
    template='[agent/s] [put/v] on [direct/o]')
TYPE = Behave('type', '@teller')
PLAY = Behave('play', '@teller',
    template="[agent/s] [play/v] Solitaire a bit on [agent's] computer")
ROBBER_TO_LOBBY = Behave('leave', '@robber',
    template='[agent/s] [leave/v] the street',
    direct='@robber', direction='in')
WAVE = Behave('wave', '@teller', target='@robber',
    template='[agent/s] [wave/v] to [direct/o]')
BRANDISH = Behave('brandish', '@robber', target='@teller', indirect='@fake_gun',
    template='[agent/s] [brandish/v] [indirect/o] at [direct/o]')
LAUGH = Behave('laugh', '@teller')
WAKE = Behave('wake', '@guard')
SEE_ROBBER = Sense('see', '@guard', direct='@robber', modality='sight')
GUARD_TO_LOBBY = Behave('leave', '@guard',
    template='[agent/s] [leave/v] the guard post',
    direct='@guard', direction='out')
BAG_FAKE = Configure('put', '@teller', direct='@fake_money', new=('in', '@bag'),
    template='[agent/s] [put/v] [direct/o] in [@bag/o]')
TURN = Behave('turn', '@robber', target='@guard',
    template = '[agent/s] [turn/v] to [direct/o]')
SHOOT_1 = Behave('shoot', '@guard', target='@robber',
    template='[agent/s] [shoot/v] [direct/o] in the chest')
SHOOT_2 = Behave('shoot', '@guard', target='@robber',
    template='[agent/s] [shoot/v] [direct/o] in the chest')
FALL = Behave('fall', '@robber')
DIE = Behave('die', '@robber')
CRY = Behave('cry', '@teller')

# Uncomment this line to have Curveship exit after narrating CRY.
# CRY.final = True

initial_actions = [READ_SLIPS, SNOOZE, TYPE, DON_MASK, COUNT_SLIPS, PLAY,
                   ROBBER_TO_LOBBY, WAVE, BRANDISH, LAUGH, WAKE, SEE_ROBBER,
                   GUARD_TO_LOBBY, BAG_FAKE, TURN, SHOOT_1, SHOOT_2,
                   FALL, DIE, CRY]

items = [
    Room('@vestibule',
        article='the',
        called='vestibule',
        exits={},
        view={'@lobby': (0.8, 'out in the lobby')}),

    Room('@lobby',
        article='the',
        called='lobby',
        exits={'out': '@street', 'in': '@guard_post'},
        view={'@vestibule': (0.6, 'inside the vestibule')}),

    Room('@guard_post',
        article='the',
        called='guard post',
        exits={'out': '@lobby'},
        view={'@lobby': (0.8, 'through the one-way mirror')}),

    Room('@street',
        article='the',
        called='street outside the bank',
        exits={'in': '@lobby'}),

    Actor('@teller in @vestibule',
        article='the',
        called='bank teller',
        gender='female',
        allowed=can.have_any_item),

    Actor('@robber in @street',
        article='the',
        called='twitchy man',
        gender='male',
        allowed=can.have_any_item),

    Actor('@guard in @guard_post',
        article='the',
        called='burly guard',
        gender='male',
        allowed=can.have_any_item),

    Thing('@slips in @vestibule',
        article='some',
        called='deposit slips'),

    Thing('@fake_money in @vestibule',
        article='some',
        prominence=0.3,
        called='fake money'),

    Thing('@bag in @vestibule',
        article='a',
        called='black bag',
        allowed=can.have_any_item),

    Thing('@mask of @robber',
        article='a',
        called='Dora the Explorer mask'),

    Thing('@fake_gun of @robber',
        article='a',
        called='gun-shaped object'),

    Thing('@pistol of @guard',
        article='a',
        called='pistol')
]

