'Rules for what can be a child of an item for use in fictions.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

def have_any_item(link, tag, world):
    'Mainly to turn off checking in non-interactive plots, not for IF.'
    return True

def not_have_items(link, tag, world):
    'The default; most items are not containers.'
    return False

def have_only_things(tag, link, world):
    'The item being checked and all its descendants must be Things.'
    for i in [tag] + world.descendants(tag):
        if not (world.item[i].thing or world.item[i].substance):
            return False
    return True

def possess_any_item(_, link, __):
    return link == 'of'

def permit_any_item(_, link, __):
    return link == 'through'

def contain_any_item(_, link, __):
    return link == 'in'

def contain_and_support_any_item(_, link, __):
    return link in ['in', 'on']

def contain_permit_and_have_parts(_, link, __):
    return link in ['in', 'part_of', 'through']

def possess_any_thing(tag, link, world):
    return link == 'of' and have_only_things(tag, link, world)

def possess_and_wear_any_thing(tag, link, world):
    return link in ['of', 'on'] and have_only_things(tag, link, world)

def contain_any_thing(tag, link, world):
    return link == 'in' and have_only_things(tag, link, world)

def contain_and_support_things(tag, link, world):
    return link in ['in', 'on'] and have_only_things(tag, link, world)

