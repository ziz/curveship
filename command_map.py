'Translate commands, from user input or elsewhere, to Actions.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

from action_model import Behave, Configure, Modify, Sense

def check_for_metonymy(tag, concept):
    if hasattr(concept.item[concept.item[tag].parent], 'vessel'):
        tag = concept.item[tag].parent
    return tag

def burn(agent, tokens, _):
    'to consume with fire; to reduce to ashes by means of heat or fire'
    return Modify('burn', agent,
                  direct=tokens[1], feature='burnt', old=False, new=True)

def close(agent, tokens, concept):
    'to stop an opening; to shut; as, to close the eyes; to close a door'
    to_be_closed = check_for_metonymy(tokens[1], concept)
    return Modify('close', agent,
                  direct=to_be_closed, feature='open', old=True, new=False)

def drink(agent, tokens, _):
    'to swallow a specific liquid, as, to drink water'
    return Behave('drink', agent, direct=tokens[1])

def drink_it_from(agent, tokens, _):
    'to swallow a specific liquid from a vessel or source'
    return Behave('drink', agent,
                  template='[agent/s] [drink/v] [direct/o] from [indirect/o]',
                  direct=tokens[1], indirect=tokens[2])

def drink_from(agent, tokens, concept):
    'to swallow from a vessel or source'
    if len(concept.item[tokens[1]].children) > 0:
        (_, direct) = concept.item[tokens[1]].children[0]
    else:
        direct = '@cosmos'
    return Behave('drink', agent,
                  template='[agent/s] [drink/v] from [indirect/o]',
                  direct=direct, indirect=tokens[1])

def doff(agent, tokens, _):
    'to strip; to divest; to undress'
    return Configure('doff', agent,
                     template='[agent/s] [take/v] off [direct/o]',
                     direct=tokens[1], old=('on', agent), new=('of', agent))

def drop(agent, tokens, concept):
    'to let go; to set aside; to have done with; to let fall to the ground'
    to_be_dropped = check_for_metonymy(tokens[1], concept)
    room = str(concept.room_of(to_be_dropped))
    return Configure('drop', agent,
                     template=['[agent/s] [relinquish/v] [direct/o]',
                               '[agent/s] [set/v] [direct/o] down'],
                     direct=to_be_dropped, new=('in', room))

def eat(agent, tokens, _):
    'to chew and swallow as food; to devour'
    return Behave('eat', agent, direct=tokens[1])

def enter(agent, tokens, concept):
    'to go into something, such as a compartment or door'
    link = 'in'
    if concept.item[tokens[1]].door:
        link = 'through'
    return Configure('enter', agent,
                     template='[agent/s] [enter/v] [indirect/o]',
                     direct=agent, new=(link, tokens[1]))

def extinguish(agent, tokens, concept):
    'to quench; to put out, as a light or fire'
    if hasattr(concept.item[tokens[1]], 'lit'):
        feature = 'lit'
    else:
        feature = 'on'
    return Modify('extinguish', agent,
                  direct=tokens[1], feature=feature, old=True, new=False)

def feed(agent, tokens, _):
    'to give food to; to supply with nourishment'
    return Configure('feed', agent,
                     template='[agent/s] [feed/v] [direct/o] to [indirect/s]',
                     direct=tokens[1], old=('of', agent), new=('of', tokens[2]))

def fill_with(agent, tokens, _):
    'to make full with a substance; to supply with as much as can be contained'
    [new_parent, substance] = tokens[1:3]
    return Configure('fill', agent,
                     template='[agent/s] [fill/v] [indirect/o] with ' + 
                              '[direct/o]',
                     direct=substance, new=('in', new_parent))

def fill_from(agent, tokens, concept):
    'to make full from a source or vessel'
    [vessel, source] = tokens[1:3]
    if len(concept.item[source].children) > 0:
        (_, direct) = concept.item[source].children[0]
    else:
        direct = '@cosmos'
    return Configure('fill', agent,
                     template='[agent/s] [fill/v] [indirect/o] from [' + 
                              source + '/o]',
                     direct=direct, old=('in', source), new=('in', vessel))

def fill_with_from(agent, tokens, _):
    'to make full with a substance from a source or vessel'
    [vessel, substance, source] = tokens[1:4]
    return Configure('fill', agent,
                     template='[agent/s] [fill/v] [indirect/o] with ' + 
                              '[direct/o] from [' + source + '/o]',
                     direct=substance, old=('in', source), new=('in', vessel))

def free(agent, tokens, concept):
    'to bring out from confinement'
    tokens.append(concept.item[tokens[1]].parent)
    return free_from(agent, tokens, concept)

def free_from(agent, tokens, concept):
    'to bring out from some specified compartment'
    [direct, container] = tokens[1:3]
    link = 'in'
    if (container in concept.item and 
        concept.item[container] == concept.item[direct].parent):
        link = concept.item[direct].link
    room_tag = str(concept.room_of(agent))
    template = '[agent/s] [free/v] [direct/o] from [' + container + '/o]'
    return Configure('free', agent,
                     template=template, direct=direct,
                     old=(link, container), new=('in', room_tag))

def freeze(agent, _, __):
    'to halt; to stop moving as if congealed by cold'
    return Behave('freeze', agent,
                  template='[agent/s] [stand/v] very still')

def give(agent, tokens, concept):
    'to yield possesion of; to deliver over, as property'
    to_be_given = check_for_metonymy(tokens[1], concept)
    return Configure('give', agent,
                     template='[agent/s] [give/v] [direct/o] to [indirect/o]',
                     direct=to_be_given, old=('of', agent),
                     new=('of', tokens[2]))

def illuminate(agent, tokens, concept):
    'to make light; to supply with light; to brighten'
    if hasattr(concept.item[tokens[1]], 'lit'):
        feature = 'lit'
    else:
        feature = 'on'
    return Modify('illuminate', agent,
                  direct=tokens[1], feature=feature, old=False, new=True)

def inventory(agent, tokens, concept):
    "to make an inventory of one's own possessions"
    return look_at(agent, tokens + [agent], concept)

def kick(agent, tokens, _):
    'to strike, thrust, or hit violently with the foot'
    return Behave('kick', agent, direct=tokens[1], force=0.5)

def leave(agent, tokens, _):
    'to pass from one place to another on foot at a normal pace'
    return Behave('leave', agent,
                  template='[agent/s] [head/v] [direction]',
                  direct=agent, direction=tokens[1])

def leave_from(agent, tokens, concept):
    'to bring oneself out of some location'
    link = 'in'
    if (tokens[1] in concept.item and 
        concept.item[tokens[1]] == concept.item[agent].parent):
        link = concept.item[agent].link
    room_tag = str(concept.room_of(agent))
    template = '[agent/s] [get/v] out of [' + tokens[1] + '/o]'
    return Configure('depart', agent,
                     template=template, direct=agent,
                     old=(link, tokens[1]), new=('in', room_tag))

def listen(agent, tokens, concept):
    'to give close attention with the purpose of hearing; to hearken'
    tokens.append(str(concept.room_of(agent)))
    action = listen_to(agent, tokens, concept)
    action.representation = '[agent/s] [listen/v]'
    return action

def listen_to(agent, tokens, _):
    'to give close attention to something specified with the purpose of hearing'
    return Sense('hear', agent,
                 template='[agent/s] [listen/v] to [direct/o]',
                 direct=tokens[1], modality='hearing')

def lock(agent, tokens, _):
    'to fasten with a lock, or as with a lock; to make fast; as, to lock a door'
    return Modify('lock', agent,
                  direct=tokens[1], feature='locked', old=False, new=True)

def look(agent, tokens, concept):
    'to examine the surrounding room or compartment'
    tokens.append(str(concept.compartment_of(agent)))
    action = look_at(agent, tokens, concept)
    action.representation = '[agent/s] [look/v] around'
    return action

def look_at(agent, tokens, _):
    'to inspect something carefully, visually'
    return Sense('examine', agent,
                 template='[agent/s] [look/v] at [direct/o]',
                 modality='sight', direct=tokens[1])

def pour_in(agent, tokens, _):
    'to cause a substance to flow in a stream into somewhere'
    [substance, vessel] = tokens[1:3]
    return Configure('pour', agent,
                     template='[agent/s] [pour/v] [direct/o] into [indirect/o]',
                     direct=substance, new=('in', vessel))

def pour_in_from(agent, tokens, _):
    'to cause a substance to flow from somewhere into somewhere else'
    [substance, source, vessel] = tokens[1:4]
    return Configure('pour', agent,
                     template='[agent/s] [pour/v] [direct/o] into [indirect/o]',
                     direct=substance, old=('in', source), new=('in', vessel))

def pour_on(agent, tokens, _):
    'to cause a substance to flow in a stream onto something'
    [substance, vessel] = tokens[1:3]
    return Configure('pour', agent,
                     template='[agent/s] [pour/v] [direct/o] onto [indirect/o]',
                     direct=substance, new=('on', vessel))

def pour_on_from(agent, tokens, _):
    'to cause a substance to flow from somewhere onto something'
    [substance, source, vessel] = tokens[1:4]
    return Configure('pour', agent,
                     template='[agent/s] [pour/v] [direct/o] onto [indirect/o]',
                     direct=substance, old=('in', source), new=('on', vessel))

def press(agent, tokens, _):
    'to exert pressure or force upon'
    return Behave('press', agent, direct=tokens[1])

def put_in(agent, tokens, _):
    'to bring to a position or place; to place; to lay; to set'
    return Configure('put', agent,
                     template='[agent/s] [put/v] [direct/o] in [indirect/o]',
                     direct=tokens[1], new=('in', tokens[2]))

def put_on(agent, tokens, _):
    'to bring to a position or place; to place; to lay; to set'
    return Configure('put', agent,
                     template='[agent/s] [put/v] [direct/o] on [indirect/o]',
                     direct=tokens[1], new=('on', tokens[2]))

def read(agent, tokens, concept):
    'to take in the sense of, as of language, by interpreting characters'
    return look_at(agent, tokens, concept)

def remove(agent, tokens, concept):
    'to bring out of some location'
    tokens.append(concept.item[tokens[1]].parent)
    return remove_from(agent, tokens, concept)

def remove_from(agent, tokens, concept):
    'to bring out of some location'
    [direct, container] = tokens[1:3]
    if (direct == agent):
        return free_from(agent, tokens, concept)
    link = 'in'
    if (container in concept.item and 
        concept.item[container] == concept.item[direct].parent):
        link = concept.item[direct].link
    template = '[agent/s] [remove/v] [direct/o] from [' + container + '/o]'
    return Configure('remove', agent,
                     template=template, direct=direct,
                     old=(link, container), new=('of', agent))

def smell(agent, tokens, concept):
    'to percieve generally by the sense of smell'
    tokens.append(str(concept.room_of(agent)))
    action = smell_of(agent, tokens, concept)
    action.representation = '[agent/s] [sniff/v] around'
    return action

def smell_of(agent, tokens, _):
    'to percieve something by the sense of smell'
    return Sense('smell', agent,
                 template='[agent/s] [smell/v] [direct/o]',
                 direct=tokens[1], modality='smell')

def take(agent, tokens, concept):
    "to get into one's hold or possession; to procure; to seize and carry away"
    to_be_taken = check_for_metonymy(tokens[1], concept)
    return Configure('take', agent,
                     template='[agent/s] [pick/v] [direct/o] up',
                     direct=to_be_taken, new=('of', agent))

def taste(agent, tokens, _):
    'to percieve by the sense of taste, by sampling a small bit'
    return Sense('taste', agent,
                 template='[agent/s] [taste/v] [direct/o]',
                 direct=tokens[1], modality='taste')

def shake(agent, tokens, _):
    'to cause to move with quick or violent vibrations; to make to tremble'
    return Behave('shake', agent,
                  template='[agent/s] [shake/v] [direct/o]',
                  direct=tokens[1])

def shake_at(agent, tokens, _):
    'to cause to move with quick or violent vibrations at something'
    return Behave('shake', agent,
                  template='[agent/s] [shake/v] [indirect/o] at [direct/o]',
                  indirect=tokens[1], target=tokens[2])

def strike(agent, tokens, _):
    'to touch or hit with force, with the hand; to smite'
    return Behave('strike', agent, direct=tokens[1], force=0.4)

def strike_with(agent, tokens, _):
    'to touch or hit with force, with an instrument; to smite'
    return Behave('strike', agent,
                  template='[agent/s] [strike/v] [direct/o] with [indirect/o]',
                  direct=tokens[1], indirect=tokens[2], force=0.4)

def tell(agent, tokens, _):
    'to utter or recite to one or more people; to say'
    said = ' '.join(tokens[2:])
    return Behave('tell', agent,
                  template='[agent/s] [say/v] [utterance] to [direct/o]',
                  utterance=said, target=tokens[1])

def throw(agent, tokens, concept):
    'to fling, cast, or hurl with a certain whirling motion of the arm'
    item = concept.item[tokens[1]]
    new_place = str(concept.room_of(agent))
    return Configure('throw', agent,
                     template='[agent/s] [toss/v] [direct/s] up',
                     direct=tokens[1], old=(item.link, item.parent),
                     new=('through', new_place))

def toggle(agent, tokens, concept):
    'to switch from one state to the other possible state'
    if concept.item[tokens[1]].on:
        return turn_off(agent, tokens, concept)
    else:
        return turn_on(agent, tokens, concept)

def touch(agent, tokens, _):
    'to come in contact with; to extend the hand so as to reach and feel'
    return Sense('touch', agent, direct=tokens[1], modality='touch')

def touch_with(agent, tokens, _):
    'to come in contact with; to extend an object so as to reach'
    return Behave('touch', agent,
                  template='[agent/s] [touch/v] [direct/o] with [indirect/o]',
                  direct=tokens[1], indirect=tokens[2])

def turn_off(agent, tokens, _):
    'to deactivate; to switch something from an active state to an inactive one'
    return Modify('deactivate', agent,
                  template='[agent/s] [turn/v] [direct/o] off',
                  direct=tokens[1], feature='on', old=True, new=False)

def turn_on(agent, tokens, _):
    'to activate; to switch something from an inactive state to an active one'
    return Modify('activate', agent,
                  template='[agent/s] [turn/v] [direct/o] on',
                  direct=tokens[1], feature='on', old=False, new=True)

def turn_to(agent, tokens, _):
    'to rotate; to revolve; to make to face differently'
    return Modify('rotate', agent,
                  template='[agent/s] [turn/v] [direct/o] to ' + tokens[2],
                  direct=tokens[1], feature='setting', new=int(tokens[2]))

def open_up(agent, tokens, concept):
    """to make or set open; to render free of access

    Since 'open' is a builtin function, this one is called 'open_up.'"""    
    to_be_opened = check_for_metonymy(tokens[1], concept)
    return Modify('open', agent,
                  direct=to_be_opened, feature='open', old=False, new=True)

def open_with(agent, tokens, world):
    'to attempt to make or set open using a tool; to render free of access'
    if (hasattr(world.item[tokens[1]], 'locked') and 
        world.item[tokens[1]].locked):
        return Modify('unlock', agent,
                      direct=tokens[1], feature='locked', old=True, new=False)
    return Modify('open', agent,
                  template='[agent/s] [open/v] [direct/o] using [' + tokens[2] +
                  '/o]', direct=tokens[1], indirect=tokens[2], feature='open',
                  old=False, new=True)

def unlock(agent, tokens, _):
    'to unfasten, as what is locked; as, to unlock a door or a chest'
    return Modify('unlock', agent,
                  direct=tokens[1], feature='locked', old=True, new=False)

def utter(agent, tokens, _):
    'to speak; to pronounce (to no one in particular)'
    said = ' '.join(tokens[1:])
    return Behave('say', agent, 
                  template='[agent/s] [say/v] [utterance]', utterance=said)

def wait(agent, _, __):
    'to remain idle'
    return Behave('wait', agent)

def wander(agent, _, __):
    'to ramble here and there without any certain course; to rove'
    return Behave('wander', agent,
             template='[agent/s] [wander/v] around, staying in the same area',
             direct=agent)

def wave(agent, _, __):
    'to move the hands one way and the other'
    return Behave('wave', agent)

def wave_at(agent, tokens, _):
    'to gesture at someone by moving the hands'
    return Behave('wave', agent,
                  template='[agent/s] [wave/v] at [direct/o]',
                  target=tokens[1])

def wear(agent, tokens, _):
    'to carry or bear upon the person, as an article of clothing, etc.'
    return Configure('wear', agent,
                     template='[agent/s] [put/v] [direct/o] on',
                     direct=tokens[1], old=('of', agent), new=('on', agent))

