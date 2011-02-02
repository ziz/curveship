'World and Concept classes for instantiaion by interactive fictions.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import copy
import operator

import can
import item_model

def check_for_reserved_tags(items):
    'Raise an error if a reserved tag, such as @cosmos, is in the list.'
    if '@cosmos' in items:
        raise StandardError('The tag "@cosmos" is reserved for the ' +
         'special item at the root of the item tree. Use a different ' +
         'tag for item now tagged "@cosmos".')
    if '@focalizer' in items:
        raise StandardError('The tag "@focalizer" is reserved for use ' +
         'in indicating the actor who is currently focalizing the ' +
         'narration. Use a different tag for item now tagged ' +
         '"@focalizer".')
    if '@commanded' in items:
        raise StandardError('The tag "@commanded" is reserved for use ' +
         'in indicating the actor who is currently being commanded. ' +
         'Use a different tag for item now tagged "@commanded".')


class WorldOrConcept(object):
    'Abstract base class for the World and for Concepts.'

    def __init__(self, item_list, actions):
        if self.__class__ == WorldOrConcept:
            raise StandardError('Attempt to instantiate abstract base ' +
                                'class world_model.WorldOrConcept')
        self.item = {}
        self.act = actions
        self.ticks = 0
        seen_tags = []
        # Construct the World's Item dictionary from the Item list:
        for item in item_list:
            if str(item) in seen_tags:
                raise StandardError('The tag "' + str(item) + '" is ' +
                 "given to more than one item in the fiction's code. " +
                 'Item tags must be unique.')
            seen_tags.append(str(item))
            self.item[str(item)] = item
        check_for_reserved_tags(self.item)

    def __str__(self):
        return str(self.act) + '\n' + str(self.item)

    def accessible(self, actor):
        'List all Items an Item can access.'
        if actor == '@cosmos':
            return self.item.keys()
        compartment = self.compartment_of(actor)
        tag_list = [str(compartment)]
        for (link, child) in compartment.children:
            if not link == 'on':
                tag_list += [child]
                tag_list += self.descendants(child, stop='closed')
        tag_list += compartment.shared + self.doors(str(compartment))
        accessible_list = []
        for tag in tag_list:
            if (not hasattr(self.item[tag], 'accessible') or 
                self.item[tag].accessible):
                accessible_list.append(tag)
        return accessible_list

    def ancestors(self, tag):
        'List all Items hierarchically above an Item.'
        items_above = []
        i = self.item[tag].parent
        while i is not None:
            items_above += [i]
            i = self.item[i].parent
        return items_above

    def compartment_of(self, tag):
        'Return the opaque compartment around the Item.'
        if tag == '@cosmos' or self.item[tag].room:
            return self.item[tag]
        compartment = self.item[self.item[tag].parent]
        while not (compartment.room or compartment.door or
                   str(compartment) == '@cosmos' or
                   (not compartment.transparent and
                    hasattr(compartment, 'open') and not compartment.open)):
        # Keep ascending to the next parent until we encounter either
        # (1) a room, (2) @cosmos, or (3) an opaque Item that has the "open" 
        # feature and is closed.
            compartment = self.item[compartment.parent]
        return compartment

    def respondents(self, action):
        """Return a list: the cosmos, the Room of the agent, (living) contents.

        These are all the Items that can prevent or react to an Action by
        the agent of the action. If the Item has an "alive" feature, it is only 
        added if alive is True.

        A special case: If the agent has congifured itself to new Room, the new
        room and (living) contents have a chance to respond, too."""
        tag_list = []
        tag_list.append('@cosmos')
        room = self.room_of(action.agent)
        if room is not None:
            tag_list.append(str(room))
            for tag in self.descendants(str(room)):
                if (not hasattr(self.item[tag], 'alive') or
                    self.item[tag].alive):
                    tag_list.append(tag)
        if action.configure and action.direct == action.agent:
            new_room = self.room_of(action.new_parent)
            if not room == new_room and new_room is not None:
                tag_list.append(str(new_room))
                for tag in self.descendants(str(new_room)):
                    if (not hasattr(self.item[tag], 'alive') or
                        self.item[tag].alive):
                        tag_list.append(tag)
        return tag_list

    def descendants(self, tag, stop='bottom'):
        """List all Items hierarchically under "tag".

        If stop='bottom', descend all the way. If stop='closed', go to down to
        closed children, but not inside those; for stop='opaque', stop at 
        opaque ones."""
        items_under = []
        if (stop == 'bottom' or
           (stop == 'closed' and (not hasattr(self.item[tag], 'open')
            or self.item[tag].open)) or
           (stop == 'opaque' and (not hasattr(self.item[tag], 'open')
            or self.item[tag].open or self.item[tag].transparent))):
            for (_, child) in self.item[tag].children:
                if child in self.item:
                    items_under += [child] + self.descendants(child, stop=stop)
        # If this is a room, include doors & shared things; otherwise [].
        return items_under + self.item[tag].shared + self.doors(tag)

    def has(self, category, tag):
        'Does the tag represent an Item of this category in this World/Concept?'
        return tag in self.item and getattr(self.item[tag], category)

    def room_of(self, tag):
        'If the Item exists and is in a Room, return the Room.'
        while (tag in self.item and not self.has('room', tag) and
            not self.has('door', tag) and not tag == '@cosmos'):
            tag = self.item[tag].parent
        if self.has('room', tag) or self.has('door', tag):
            return self.item[tag]
        return None

    def show_descendants(self, tag, padding=''):
        'Return the tree rooted at this Item.'
        if tag not in self.item:
            return ''
        link = ''
        if not tag == '@cosmos':
            link = self.item[tag].link
        string = (padding + tag + ': ' + self.item[tag].noun_phrase() +
                  ' [' + link + ']\n')
        for (_, child) in self.item[tag].children:
            string += self.show_descendants(child, padding + ('    '))
        return string

    def doors(self, tag):
        "Returns a list of the Item's Doors; [] if there are none."
        doors = []
        if tag in self.item and self.item[tag].room:
            for direction in self.item[tag].exits:
                leads_to = self.item[tag].exits[direction]
                if self.has('door', leads_to) and not leads_to in doors:
                    doors.append(leads_to)
        return doors


class Concept(WorldOrConcept):
    "An Actor's theory or model of the World, which can be used in telling."

    def __init__(self, item_list, actions, cosmos=None):
        self.changed = []
        WorldOrConcept.__init__(self, item_list, actions)
        if cosmos is None:
            cosmos = item_model.Actor('@cosmos', called='nature',
                                       allowed=can.have_any_item)
        self.item['@cosmos'] = cosmos
        for (tag, item) in self.item.items():
            if not tag == '@cosmos':
                self.item[item.parent].add_child(item.link, tag, True)


    def item_at(self, tag, time):
        'Return the Item from this moment in the Concept.'
        if tag not in self.item:
            return None
        item = self.item[tag]
        current = len(self.changed) - 1
        while current >= 0 and self.changed[current][0] > time:
            (_, changed_tag, old) = self.changed[current]
            if changed_tag == tag:
                item = old
            current -= 1
        return item

    def update_item(self, item, time):
        'After perception, change an Item within this Concept.'
        if str(item) in self.item:
            old = self.item[str(item)]
        else:
            old = None
        self.item[str(item)] = item
        self.changed.append((time, str(item), old))

    def roll_back_to(self, time):
        'Go back to a previous state of this Concept.'
        new_ids = []
        for action_id in self.act:
            new_ids.append((action_id, self.act[action_id].start))
        ids_times = sorted(new_ids, key=operator.itemgetter(1))
        while len(ids_times) > 0 and ids_times[-1][1] > time:
            (last_id, _) = ids_times.pop()
            self.act.pop(last_id)
        while len(self.changed) > 0 and self.changed[-1][0] > time:
            (_, tag, old) = self.changed.pop()
            if old is None:
                del self.item[tag]
            else:
                self.item[tag] = old

    def copy_at(self, time):
        'Return a new Concept based on this one, but from an earlier time.'
        new_concept = copy.deepcopy(self)
        new_concept.roll_back_to(time)
        return new_concept


def sight_culprit(prominence, view, lit):
    'Which of the three factors is mostly to blame for the lack of visibility?'
    if lit <= prominence and lit <= view:
        return 'enough_light'
    if view <= prominence and view <= lit:
        return 'good_enough_view'
    return 'item_prominent_enough'


class World(WorldOrConcept):
    'The simulated world; it has Items and Actions.'

    def __init__(self, fiction):
        self.running = True
        action_dict = {}
        for action in fiction.initial_actions:
            action.cause = 'initial_action'
            action_dict[action.id] = action
        self.concept = {}
        WorldOrConcept.__init__(self, fiction.items, action_dict)
        # Instantiate the needed amounts of Substance
        for substance in [i for i in fiction.items if i.substance]:
            parents = []
            for tag in self.item:
                if (hasattr(self.item[tag], 'source') and
                    self.item[tag].source == str(substance)):
                    parents.append(tag)
                elif hasattr(self.item[tag], 'vessel'):
                    if self.item[tag].vessel == str(substance):
                        # The amount should go into the vessel itself.
                        parents.append(tag)
                    else:
                        # The amount should become the child of the main
                        # Substance Item, which is of @cosmos. It's necessary
                        # to create one amount for each empty vessel (or
                        # vessel that is holding something else) since that 
                        # vessel might hold the Substance later.
                        parents.append(str(substance))
            tag_number = 1
            for parent in parents:
                new_item = copy.deepcopy(substance)
                new_item._tag += '_'  + str(tag_number)
                tag_number += 1
                new_item.link = 'in'
                new_item.parent = parent
                self.item[str(new_item)] = new_item
        if fiction.cosmos is None:
            fiction.cosmos = item_model.Actor('@cosmos', called='nature',
                                       allowed=can.have_any_item)
        self.item['@cosmos'] = fiction.cosmos
        for (tag, item) in self.item.items():
            if not tag == '@cosmos':
                self.item[item.parent].add_child(item.link, tag, True)


    def advance_clock(self, duration):
        'Move the time forward a specified number of ticks.'
        self.ticks += duration
        for actor in self.concept:
            self.concept[actor].ticks = self.ticks

    def back_up_clock(self, target_time):
        'Roll the time back to a particuar tick.'
        self.ticks = target_time
        for actor in self.concept:
            self.concept[actor].roll_back_to(self.ticks)

    def light_level(self, tag):
        "Determines the light level (not just glow) in the Item's compartment."
        compartment = self.compartment_of(tag)
        if compartment is None:
            return 0.0
        total = compartment.glow
        for (_, child) in compartment.children:
            total += self.light_within(child)
        return total

    def light_within(self, tag):
        'Returns the light illuminating an Item, inherently and within.'
        total = self.item[tag].glow # The inherent light coming from the item.
        for (link, child) in self.item[tag].children:
            if link == 'in':
            # For Items that are 'in', descend if open or transparent.
                if not hasattr(self.item[tag], 'open') or self.item[tag].open:
                    total += self.light_within(child)
                elif self.item[tag].transparent:
                    total += self.light_within(child)
            else:
                total += self.light_within(child)
        return total

    def prevents_sight(self, actor, tag):
        'Returns a reason (if there are any) that "actor" cannot see "tag".'
        if actor == '@cosmos':
        # @cosmos can see everything at all times.
            return None
        item_place = self.room_of(tag)
        actor_place = self.room_of(actor)
        if actor_place is None:
        # The Actor is "out of play" (of @cosmos), and cannot see anything.
            return 'actor_in_play'
        if (item_place is None and
            not tag in self.item[str(actor_place)].shared and
            not tag in self.doors(str(actor_place))):
        # The Item could be either a SharedThing or a Door if its Room is
        # None. If its Room is None and neither is the case, however, it 
        # must be "out of play."
            return 'item_in_play'
        compartment = self.compartment_of(actor)
        view_tags = []
        if not compartment == actor_place:
        # The Actor is is some sort of opaque compartment within a room.
        # Only Items within that compartment will be visible.
            view_tags = [str(compartment)]
            for (link, child) in compartment.children:
                if not link == 'on':
                    view_tags += [child] 
                    view_tags += self.descendants(child, stop='opaque')
        else:
        # Otherwise, list all the Items to which there is a line of sight
        # in the Actor's Room and in every Room that has a view from there.
            if self.item[str(actor_place)].door:
                rooms_visible = self.item[str(actor_place)].connects
            else:
                rooms_visible = actor_place.view.keys()
            for room_tag in [str(actor_place)] + rooms_visible:
                view_tags += ([room_tag] + 
                               self.descendants(room_tag, stop='opaque'))
        if tag not in view_tags:
            return 'line_of_sight'
        view = 1.0
        # Set the view to be perfect (1.0). This applies if the Actor and
        # Item are in the same Room, or if the Item is a SharedThing or Door
        # of the Actor's Room, or if the Actor is in a Door and the Item is
        # in a connecting Room.
        if actor_place.room and str(item_place) in actor_place.view:
        # If looking onto a Room in view, check how well it can be seen.
            (view, _) = actor_place.view[str(item_place)]
        lit = self.light_level(tag)
        if str(self.compartment_of(actor)) == tag:
        # The compartment itself is the one case where it's important to
        # get the interior light level. If the line of sight crosses the 
        # compartment, the light level doesn't matter; the item can't be seen.
        # If inside, the light level is computed within the compartment. But
        # the compartment itself has different "inside" and "outside" light
        # levels. Select an arbitrary child of the compartment (there must
        # be at least one, the Actor) and check the light level for that child.
            (_, child) = self.item[tag].children[0]
            lit = self.light_level(child)
        visibility = self.item[tag].prominence * view * lit
        if visibility >= 0.2:
        # 0.2 is the threshhold for seeing something.
        # An actor sees something that has prominence 0.5 and is in a room with
        #   view 0.5 under full light (1): 0.5 * 0.5 * 1 = 0.25 >= 0.2
        # An actor sees something that has prominece 1 and is in the same room
        #   even under very low (0.2) light: 1 * 1 * .02 = 0.2 >= 0.2
        # Something with prominence below 0.2 will never be visible to an actor
        #   in the current system.
        # Something with prominence 0.3 will be seen (under full light) in the
        #   same room but not from a room where the view is 0.6.
            return None
        # Assign blame to whichever value is smallest.
        return sight_culprit(self.item[tag].prominence, view, lit)

    def can_see(self, actor, tag):
        'Is the item identified by "tag" visible to "actor"?'
        return self.prevents_sight(actor, tag) is None

    def reset(self):
        'Revert the World and Concepts to their initial states.'
        self.undo(1)
        for actor in self.concept:
            self.concept[actor].roll_back_to(1)

    def set_concepts(self, actors):
        "Set initial information in all Actors' Concepts."
        for actor in self.item:
            if self.has('actor', actor) and not actor == '@cosmos':
                known_items = []
                for i in self.item:
                    if self.can_see(actor, i):
                        known_items.append(copy.deepcopy(self.item[i]))
                self.concept[actor] = Concept(known_items, {})
        for (actor, items, actions) in actors:
            self.concept[actor] = Concept(items, actions)
        cosmos_items = []
        for i in self.item:
            if not i == '@cosmos':
                cosmos_items.append(copy.deepcopy(self.item[i]))
        cosmos_acts = copy.deepcopy(self.act)
        self.concept['@cosmos'] = Concept(cosmos_items, cosmos_acts)
        for actor in self.concept.keys():
            self.concept[actor].concept_of = actor

    def transfer(self, item, actor, time):
        "Place an appropriate version of an Item in the Actor's Concept."
        concept = self.concept[actor]
        # If a Room, first add this Room as a child of @cosmos
        if item.room and str(item) not in self.concept[actor].item:
            new_cosmos = copy.deepcopy(concept.item['@cosmos'])
            new_cosmos.add_child('in', str(item))
            concept.update_item(new_cosmos, time)
        # Now, the basic transfer applicable to all Items
        if (str(item) not in concept.item or
            not concept.item[str(item)] == item):
            seen_item = copy.deepcopy(item)
            concept.update_item(seen_item, time)
            for (_, child) in item.children:
                if self.can_see(actor, child):
                    self.transfer(self.item[child], actor, time)
        # If a Room, add SharedThings & Doors to the Actor's Concept.
        if item.room:
            for shared_tag in self.item[str(item)].shared:
                self.transfer(self.item[shared_tag], actor, time)
            for door_tag in self.doors(str(item)):
                self.transfer(self.item[door_tag], actor, time)
        
    def transfer_out(self, item, actor, time):
        "Remove the Item from the Actor's Concept."
        concept = self.concept[actor]
        if str(item) in concept.item:
            missing_item = copy.deepcopy(concept.item[str(item)])
            missing_item.link = 'of'
            missing_item.parent = '@cosmos'
            concept.update_item(missing_item, time)

    def undo(self, action_id):
        'Revert the World back to the start time of the specified Action.'
        new_ids = []
        for i in self.act:
            new_ids.append((i, self.act[i].start))
        ids_times = sorted(new_ids, key=operator.itemgetter(1))
        target_time = self.act[action_id].start
        while len(ids_times) > 0 and ids_times[-1][1] >= target_time:
            (last_id, _) = ids_times.pop()
            last_action = self.act.pop(last_id)
            last_action.undo(self)
        self.back_up_clock(target_time)

