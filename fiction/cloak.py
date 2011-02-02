"""Cloak of Darkness

An implementation of Roger Firth's Cloak of Darkness (1999) in Curveship,
an interactive fiction development system by Nick Montfort."""

__author__ = 'Nick Montfort (based on a game by Roger Firth)'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

from item_model import Actor, Room, Thing
from action_model import Behave, Modify, Sense
import can
import when

discourse = {

    'metadata': {
        'title': 'Cloak of Darkness',
        'headline': 'A Basic IF Demonstration',
        'people': [('Curveship implementation by', 'Nick Montfort'),
                   ('original game by', 'Roger Firth')],
        'prologue': ''},

    'command_grammar': {
        'PUT_ON ACCESSIBLE ACCESSIBLE':
         ['put ACCESSIBLE onto ACCESSINLE',
          '(hang|put|place) ACCESSIBLE (up )?(atop|on|onto) ACCESSIBLE',
          '(hang|put)( up)? ACCESSIBLE (atop|on|onto) ACCESSIBLE']},

    'action_templates': [
        ('PUT new_link=on new_parent=@hook',
         '[agent/s] [hang/v] [direct/o] up on [indirect/o]')],

    'spin': {
        'focalizer': '@person',
        'commanded': '@person',
        'narratee': '@person',
        'known_directions': True}}

ARRIVE = Behave('arrive', '@person',
                template="""
                hurrying through the rainswept November night, [@person/s] 
                [are/v] glad to see the bright lights of the Opera House""",
                indirect='@foyer')
ARRIVE.after = """it [is/1/v] surprising that there [are/not/2/v] more people 
               about but, hey, what should [@person/s] expect in a cheap demo 
               game?"""

LOOK_AROUND = Sense('see', '@person', direct='@foyer', modality='sight')

initial_actions = [ARRIVE, LOOK_AROUND]

class ScrawledMessage(Thing):

    def __init__(self, tag, **keywords):
        self.intact = True
        Thing.__init__(self, tag, **keywords)

    def react(self, world, basis):
        actions = []
        if (basis.sense and basis.direct == '@message' and
            basis.modality == 'sight'):
            sigh =  Behave('sigh', basis.agent)
            sigh.final = True
            actions.append(sigh)
        return actions

    def react_to_failed(self, world, basis):
        actions = []
        if (basis.behave and basis.verb == 'leave' and self.intact):
            actions.append(Modify('trample', basis.agent,
                                  direct='@message', feature='intact',
                                  new=False, salience=0))
            sight = """
            the message, now little but a cipher of trampled sawdust, 
            [seem/1/v] to read: [begin-caps] [*/s] [lose/ed/v]"""
            actions.append(Modify('rewrite', basis.agent, 
                                  direct=str(self), feature='sight',
                                  new=sight, salience=0))
        return actions

def support_cloak(tag, link, world):
    return (tag, link) == ('@cloak', 'on')

def possess_things_and_wear_cloak(tag, link, world):
    return ((tag, link) == ('@cloak', 'on') or
            link == 'of' and can.have_only_things(tag, link, world))

can.support_cloak = support_cloak
can.possess_things_and_wear_cloak = possess_things_and_wear_cloak

def in_foyer(world):
    return str(world.room_of('@person')) == '@foyer'

when.in_foyer = in_foyer

items = [

    Actor('@person in @foyer',
        article='the',
        called='operagoer',
        referring='| operagoer',
        qualities=['person', 'woman'],
        allowed=can.possess_things_and_wear_cloak,
        gender='female',
        refuses=[
        ('behave LEAVE direct=@person way=north', when.in_foyer,
         """[*/s] [have/v] only just arrived, and besides, the weather
         outside [seem/1/v] to be getting worse"""),
        ('configure direct=@cloak new_parent=@foyer', when.always,
         """the floor [is/not/1/v] the best place to leave a smart cloak
         lying around""")],
        sight="""
        [*/s] [see/v] a typically nondescript character"""),

    Thing('@cloak on @person',
        article='a',
        called='(handsome) cloak (of darkness)',
        referring='black damp trimmed with satin smart soft sumptuous ' +
                  'velvet | cape',
        qualities=['clothing'],
        glow=-0.5,
        sight="""
        [@cloak/s] [is/v] of velvet trimmed with satin and [is/v] slightly
        spattered with raindrops

        [@cloak's] blackness [is/1/v] so deep that it [seem/1/v] to suck light
        from the room""",
        touch="""
        a material that [is/1/v] soft and sumptuous, despite being damp"""),

    Room('@foyer',
        article='the',
        called='(splendid) foyer (of the opera house)',
        referring='splendidly decorated red gold spacious | hall',
        exits={'south': '@bar', 'west': '@cloakroom'},
        sight="""
        [*/s] [see/v] [*/o] standing in a spacious hall, splendidly decorated
        in red and gold, with glittering chandeliers overhead

        the entrance from the street [is/1/v] to the north, and there [are/2/v]
        doorways south and west"""),

    Room('@cloakroom',
        article='a',
        called='(small) cloakroom',
        referring='cloak hat check | room check checkroom hatcheck',
        exits={'east':'@foyer'},
        sight="""
        [*/s] [see/v] that clearly, the walls of this small room were once
        lined with hooks, though [now] only one [remain/1/v]

        the exit [is/1/v] a door to the east"""),

    Thing('@hook part_of @cloakroom',
        article='a',
        called='(small) (brass) hook',
        referring='| peg',
        qualities=['metal'],
        allowed=can.support_cloak,
        sight="""
        [this] [is/v] just a small brass hook, screwed to the wall""",
        mention=False),

    Room('@bar',
        article='a',
        called='(empty) (foyer) bar',
        referring='rough rougher |',
        glow=0.4,
        exits={'north': '@foyer'},
        sight="""
        the bar, much rougher than [*/s] would have guessed after the opulence
        of the foyer to the north, [is/1/v] completely empty

        there [seem/1/v] to be some sort of message scrawled in the sawdust on
        the floor"""),

    ScrawledMessage('@message part_of @bar',
        article='a',
        called='(scrawled) message',
        referring='trampled | sawdust message floor scrawl',
        sight="""
        the message, neatly marked in the sawdust, [read/1/v]:
        [begin-caps] [*/s] [win/ed/v]""")]

