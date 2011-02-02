'Artmaking, a tiny demonstration game for Curveship.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'

from item_model import Actor, Room, Thing
from action_model import Modify, Sense
import can
import when

discourse = {
    'metadata': {
        'title': 'Artmaking',
        'headline': 'A very simple example',
        'people': [('by', 'Nick Montfort')],
        'prologue': 'Settle for nothing less than an artistic breakthrough.'},
    'spin':
    {'commanded': '@artist', 'focalizer': '@artist', 'narratee': '@artist'}}

initial_actions = [Sense('ogle', '@artist', direct='@studio', modality='sight')]

class Art(Thing):
    '@sculpture is the only instance.'

    def react(self, world, basis):
        'Win the game when smashed.'
        actions = []
        if (basis.verb in ['kick', 'strike'] and basis.direct == str(self)):
            damage = Modify('puncture', basis.agent, direct=str(self),
                            feature='intact', new=False)
            damage.after = """finally, a worthy contribution to the art world
            ... victory!"""
            damage.final = True
            actions = [damage]
        return actions

items = [
    Actor('@artist in @studio',
        article='the',
        called='artist',
        gender='female',
        allowed=can.possess_any_item,
        refuses=[('LEAVE way=(north|out)', when.always,
                 '[@artist/s] [have/v] work to do')]),

    Room('@studio',
        article='the',
        called='studio',
        exits={},
        sight='a bare studio space with a single exit, to the north'),

    Thing('@box in @studio',
        article='a',
        called='box',
        open=False,
        allowed=can.contain_and_support_things,
        sight='the medium-sized parcel [is/1/v] [open/@box/a]'),

    Art('@sculpture in @box',
        article='a',
        called='sculpture',
        intact=True,
        sight='a sculpture of a mountain, made to order in China')]

