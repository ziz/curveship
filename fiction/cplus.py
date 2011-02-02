"""Cloak of Darkness Plus

An augmentation of Roger Firth's Cloak of Darkness (1999) in Curveship,
an interactive fiction development system by Nick Montfort."""

__author__ = 'Nick Montfort (extending a game by Roger Firth)'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

from item_model import Actor, Thing, Room, Substance
from action_model import Modify, Sense
import can

import fiction.cloak

discourse = fiction.cloak.discourse
discourse['metadata']['title'] = 'Cloak of Darkness Plus'
discourse['metadata']['people'] = [
    ('augmented and implemented in Curveship by', 'Nick Montfort'),
    ('original game by', 'Roger Firth')]

initial_actions = fiction.cloak.initial_actions


class Lamp(Thing):
    '@lamp is the only instance.'

    def react(self, _, basis):
        'Increase/decrease the light emitted when turned on/off.'
        actions = []
        if (basis.modify and basis.direct == str(self) and 
            basis.feature == 'on'):
            # If turned on, make it glow; otherwise, have it stop glowing.
            if basis.new_value:
                actions.append(Modify('light', basis.agent,
                                      direct=str(self), feature='glow',
                                      new=0.6, salience=0.1))
            else:
                actions.append(Modify('extinguish', basis.agent,
                                      direct=str(self), feature='glow',
                                      new=0.0, salience=0.1))
        return actions


class Waver(Actor):
    '@mime is the only instance.'

    def __init__(self, tag, **keywords):
        self.waves_next_turn = True
        self.angry = False
        Actor.__init__(self, tag, **keywords)

    def act(self, command_map, concept):
        actions = []
        self.waves_next_turn = not self.waves_next_turn
        if self.waves_next_turn and not self.angry:
            actions.append(self.do_command('wave', command_map, concept))
        return actions


items = fiction.cloak.items + [

    Substance('@water',
        called='water',
        referring='clear |',
        qualities=['drink', 'liquid'],
        consumable=True,
        sight='clear water',
        taste="nothing unpleasant"),

    Waver('@mime in @foyer',
        article='a',
        called='(dazed) mime',
        referring='oblivious strange | greeter character',
        allowed=can.possess_things_and_wear_cloak,
        qualities=['person', 'man'],
        gender='male',
        sight="""

        [here] [is/1/v] a strange character who [seem/1/v] almost completely
        oblivious to everything""",
        start=50),

    Thing('@bottle in @foyer',
        article='a',
        called='(clear) (glass) bottle',
        open=False,
        transparent=True,
        vessel='@water',
        sight='a clear glass bottle, currently [open/@bottle/a]',
        touch="smooth glass"),

    Thing('@ticket of @person',
        article='a',
        called='ticket',
        referring='opera |',
        sight="""

        [@ticket/ordinary/s] [read/v] "VALID FOR A NIGHT AT THE OPERA UNLESS
        IT RAINS"

        """),

    Thing('@massive_sack in @foyer',
        article='a',
        called='(plain) massive sack',
        referring='massive | bag sack',
        allowed=can.contain_and_support_any_item,
        sight='a plain sack, totally massive',
        open=True),

    Thing('@large_sack in @foyer',
        article='a',
        called='(plain) large sack',
        referring='large | bag sack',
        allowed=can.contain_any_thing,
        sight='a plain sack, quite large',
        open=True),

    Lamp('@lamp in @cloakroom',
        article='a',
        called='(shiny) (brass) (carbide) lamp',
        referring='| lantern light',
        qualities=['device', 'metal'],
        on=False,
        flame=True,
        sight="""

        [@lamp/nifty/s] [here] [is/v] the kind often used for illuminating caves

        [@lamp/s] [is/v] shiny and [glow/@lamp/a]
        """)]
