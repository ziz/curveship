'Define categories of Action and their consequences in the World.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import copy
import re
import types
import discourse_model

def generator(num):
    'Provides unique, increasing integers.'
    while 1:
        yield num
        num += 1

ACTION_ID = generator(1)

class Action(object):
    'Abstract base class for things done by an agent in the world.'

    def __init__(self, verb, agent, category, **keywords):
        if self.__class__ == Action:
            raise StandardError('Attempt to instantiate abstract base ' +
                                'class action_model.Action')
        self.id = ACTION_ID.next()
        self.verb = verb
        self.agent = agent
        self.cause = self.agent
        self.salience = 0.5
        for i in ['salience', 'template', 'force']:
            if i in keywords:
                setattr(self, i, keywords[i])
        for i in ['behave', 'configure', 'modify', 'sense']:
            setattr(self, i, (category == i))
        self._category = category
        self.preconditions = []
        self.start = None
        self.final = False
        self.failed = []
        self.refusal = None
        self.enlightened = []

    def __str__(self):
        'Describes the action in a one-line string.'
        string = ':' + str(self.id) + ': '
        if self.refusal is not None:
            string += 'Refused '
        elif len(self.failed) > 0:
            string += 'Failed '
        string += self.verb.upper() + ' (' + self._category + ') '
        for i in ['agent', 'direct', 'indirect', 'direction', 'utterance',
                  'preposition', 'modality', 'force', 'manner', 'feature',
                  'old_value', 'new_value', 'old_link', 'old_parent',
                  'new_link', 'new_parent', 'target', 'cause', 'start']:
            if hasattr(self, i):
                string += i + '=' + str(getattr(self, i)) + ' '
        return string[:-1]

    @property
    def category(self):
        'Returns the category (behave, congifure, etc.) as a lowercase string.'
        return self._category

    @property
    def end(self):
        "Return the action's end time. All actions have duration 1 now."
        return self.start + 1

    def check_refusal(self, world):
        'If the agent refuses to do the action, update the reason.'
        if (not self.agent == '@cosmos' and 
            hasattr(world.item[self.agent], 'refuses')):
            agent = world.item[self.agent]
            for (wont_do, state, reason) in agent.refuses:
                if self.match_string(wont_do):
                    if type(state) == list:
                        if world.room_of(self.agent) in state: 
                            self.refusal = reason
                            break
                    elif state(world):
                        self.refusal = reason
                        break
            if self.refusal is None:
                if self.verb == 'leave':
                    room = world.room_of(self.agent)
                    if world.can_see(self.agent, str(room)):
                        if room.exit(self.direction) is None:
                            if self.direction not in room.exits:
                                self.refusal = ('[' + self.agent +
                                               '/s] [see/v] no way to do that')
                            else:
                                self.refusal = room.exits[self.direction]
                    else:
                        if self.direction in ['up', 'down']:
                            self.refusal = ('[' + self.agent +
                                            '/s] [find/not/v] any way to ' +
                                            'go [direction]')
            if self.refusal is not None:
                self.refusal = re.sub('\[\*', '[' + self.agent,
                                      self.refusal)

    def match_string(self, event_test):
        'Does the string indicate this action?'
        to_match = event_test.split()
        for i in to_match:
            if re.search(i, str(self)) is None:
                return False
        return True

    def undo(self, world):
        'Make the world as if this action had never happened.'
        self.change(world, False)

    def do(self, world):
        'Perform the action, updating the world.'
        to_be_done = []
        aware = set()
        self.start = world.ticks
        for actor in world.concept:
            # Did the actor see the agent or direct object (if any) beforehand?
            # If the actor performed the action, the actor is aware of it.
            if (actor == self.agent or world.can_see(actor, self.agent) or
                (hasattr(self, 'direct') and 
                 world.can_see(actor, self.direct))):
                aware.add(actor)
        self.check_refusal(world)
        if self.refusal is None:
            self.check_preconditions(world)
            can_respond = world.respondents(self)
            if len(self.failed) == 0:
                for tag in can_respond:
                    if world.item[tag].prevent(world, self):
                        self.failed.append(['prevented_by', tag])
            if len(self.failed) == 0:
                for tag in can_respond:
                    to_be_done += world.item[tag].react(world, self)
                self.change(world)
                if hasattr(self, 'entails'):
                    to_be_done += self.entails(world)
            else:
                for tag in can_respond:
                    to_be_done += world.item[tag].react_to_failed(world, self)
        for actor in world.concept:
            # Did the actor see the agent at the end of the action, for
            # instance, if the agent entered a room?
            if world.can_see(actor, self.agent):
                aware.add(actor)
        for actor in aware:
            world.concept[actor].act[self.id] = copy.deepcopy(self)
        world.act[self.id] = self
        return to_be_done

    def moved_somewhere_different(self, actor):
        'Tells whether this action caused the actor to move elsewhere.'
        return (self.configure and self.direct == actor and 
                not self.old_parent == self.new_parent)

    def change(self, world, making_change=True):
        'Alter the world. Only Modify and Configure actions do it.'
        pass

    def check_allowed(self, condition, world):
        'Does the "allowed" rule of the parent let the Item become a child?'
        head, tag, link, parent = condition                
        reason = None
        # First, the Item cannot be a room; rooms can only be 
        # children of @cosmos.
        if world.item[tag].room:
            reason = 'rooms_cannot_move'
        # Next, the Item can't be made the child of itself or
        # of any descendant of itself.
        elif tag in [parent] + world.ancestors(parent):
            reason = 'not_own_descendant' 
        # Next, if the Item is an amount of Substance (liquid, 
        # powder, etc.), there are different cases.
        elif world.item[tag].substance:
            substance = tag.partition('_')[0]
            # 'in' works if the amount is being placed in a 
            # vessel, or if a source is being replenished, or if
            # the amount is being moved to the substance item.
            if link == 'in':
                if not ((world.item[parent].substance and
                         parent == substance) or
                        (hasattr(world.item[parent], 'source') and
                         world.item[parent].source == substance) or
                        (hasattr(world.item[parent], 'vessel') and
                         len(world.item[parent].children) == 0)):
                    reason = 'substance_contained'
            # 'of' does not work; Substances cannot be held by
            # themselves, without vessels.
            elif link == 'of':
                reason = 'substance_contained'
            # There is no case for 'on' -- it falls through to success.
            # 'on' generally works -- an amount can be poured
            # onto anything. A Configure action will be entailed
            # immediately and the amount will be moved to the root
            # Substance Item.
        # Check the Item's own allowed rule:
        elif not world.item[parent].allowed(tag, link, world):
            reason = head + "_" + link
        # Finally, if there have been no other failures, continue
        # to test to see if the parent, with this new child,
        # is still allowed in the grandparent, and so on up the
        # tree. This is done for now rather expensively. A copy
        # of the world is made and, in it, the item is added as a
        # child of the new parent. Then, the testing proceeds.
        elif reason is None and not world.item[parent].parent == '@cosmos':
            met = True
            test = copy.deepcopy(world)
            test.item[parent].add_child(link, tag)
            met &= test.item[parent].allowed(tag, link, test)
            while met and not parent == '@cosmos':
                tag = parent
                parent = test.item[tag].parent
                link = test.item[tag].link
                met &= test.item[parent].allowed(tag, link, test)
            if not met:
                reason = head + '_' + link
        return reason

    def check_preconditions(self, world):
        'Determine if any of the preconditions fail, and why.'
        for condition in self.pre(world):
            failure = []
            head = condition[0]
            if head == 'allowed':
                reason = self.check_allowed(condition, world)
                if reason is not None:
                    failure.append([reason, agent, tag])
            elif head[:10] == 'can_access':
                _, agent, tag_list = condition
                met = False
                accessible_tags = world.accessible(agent)
                for tag in tag_list:
                    if tag in accessible_tags:
                        met = True
                if not met:
                    failure.append(condition)
            elif head == 'can_see':
                _, agent, tag = condition
                reason = world.prevents_sight(agent, tag)
                if reason is not None:
                    failure.append([reason, agent, tag])
            elif head == 'configure_to_different':
                _, child, link, parent = condition
                if (world.item[child].link == link and
                    world.item[child].parent == parent):
                    failure.append(condition)
            elif head == 'exit_exists':
                _, tag, direction = condition
                if direction not in world.room_of(tag).exits:
                    failure.append(condition)
            elif head == 'has_feature':
                _, tag, feature = condition
                if not hasattr(world.item[tag], feature):
                    failure.append(condition)
            elif head == 'has_value':
                _, tag, feature, value = condition
                if (hasattr(world.item[tag], feature) and
                    not getattr(world.item[tag], feature) == value):
                    failure.append(condition)
            elif head == 'modify_to_different':
                _, tag, feature, value = condition
                if (hasattr(world.item[tag], feature) and
                    getattr(world.item[tag], feature) == value):
                    failure.append(condition)
            elif head == 'never':
                failure.append([head + '_' + condition[1]])
            elif head == 'parent_is':
                _, child, link, parent = condition
                if (not world.item[child].link == link and
                    not world.item[child].parent == parent):
                    failure.append(condition)
            self.preconditions.append(((len(failure) == 0), condition))
            self.failed += failure

    def show(self):
        'Return verb, agent, cause, preconditions, type, any postcondition.'

        string = '\n'
        for (met, condition) in self.preconditions:
            if not type(condition) == str:
                condition = ' '.join(str(pre_part) for pre_part in condition)
            string += ['#####> ', '/ / /  '][met] + condition + '\n'
        string += str(self) + '\n'
        if hasattr(self, 'post'):
            success = (len(self.failed) == 0) and self.refusal is None
            string += [' ##### ', r'\ \ \  '][success]
            string += ' '.join(str(post_part) for post_part in self.post())
            string += '\n'
        return string

class Behave(Action):
    'An action that itself changes nothing, e.g., jumping up and down.'

    def __init__(self, verb, agent, **keywords):
        # Behave actions may have 'direct' 'indirect' 'direction' and/or 'utterance'
        for i in ['direct', 'indirect', 'target', 'direction', 'utterance']:
            if i in keywords:
                setattr(self, i, keywords[i])
                del keywords[i]
        self.force = 0.2
        Action.__init__(self, verb, agent, 'behave', **keywords)

    def pre(self, _):
        """Preconditions for Behave:

        The agent must be able to access all objects. If trying to consume
        food or drink, it must be consumable. If trying to leave, an exit
        must exist."""
        pre_list = []
        if hasattr(self, 'direct'):
            pre_list.append(('can_access_direct', self.agent, [self.direct]))
        if hasattr(self, 'indirect'):
            pre_list.append(('can_access_indirect', self.agent,
                             [self.indirect]))
        if hasattr(self, 'target'):
            pre_list.append(('can_see', self.agent, self.target))
        if self.verb in ['drink', 'eat']:
            pre_list.append(('has_feature', self.direct, 'consumable'))
        if self.verb == 'leave':
            pre_list.append(('exit_exists', self.agent, self.direction))
        return pre_list

    def entails(self, world):
        """Entailed Actions for Behave:

        Configure the actor to a new Room after leaving, remove food after 
        eating."""
        actions = []
        if len(self.failed) > 0:
            return actions
        # When an actor leaves in direction that is an exit, the Behave
        # action entails a new action: A Configure action that moves the actor 
        # to the new room or through the door.
        room = world.room_of(self.agent)
        if self.verb == 'leave' and room.exit(self.direction) is not None:
            goal = room.exits[self.direction]
            link = None
            if goal is not None and world.item[goal].door:
                link = 'through'
            else:
                link = 'in'
            new = Configure('enter', self.agent,
                            template='[agent/s] [arrive/v]',
                            direct=self.agent, new=(link, goal), salience=0.1)
            actions.append(new)
        if self.verb in ['drink', 'eat']:
            if hasattr(self, 'direct'):
                to_be_consumed = self.direct
            else:
                _, to_be_consumed = world.item[self.indirect].children[0]
            if world.item[to_be_consumed].substance:
                new_parent = ('in', to_be_consumed.partition('_')[0])
            else:
                new_parent = ('of', '@cosmos')
            actions.append(Configure('polish_off', '@cosmos', 
                                     direct=to_be_consumed,
                                     new=new_parent, salience=0))
        return actions

class Configure(Action):
    'An action that repositions an item in the item tree.'

    def __init__(self, verb, agent, **keywords):
        # Configure Actions must have 'direct' and 'new'.
        self.direct = keywords['direct']
        del keywords['direct']
        self.new_link = keywords['new'][0]
        self.new_parent = keywords['new'][1]
        del keywords['new']
        # 'old' is optional; if missing, any initial link and parent are fine.
        if 'old' in keywords:
            self.old_link = keywords['old'][0]
            self.old_parent = keywords['old'][1]
            del keywords['old']
        self.force = 0.2
        Action.__init__(self, verb, agent, 'configure', **keywords)

    def set_old_if_unset(self, world):
        'Set old_link and old_parent if they have been left off.'
        if not hasattr(self, 'old_link') and not hasattr(self, 'old_parent'):
            self.old_link = world.item[self.direct].link
            self.old_parent = world.item[self.direct].parent

    def change(self, world, making_change=True):
        'Put the item in the new (or old) arrangement in the tree.'
        self.set_old_if_unset(world)
        # If the Action failed, it itself had no consequence in the world.
        # In this case, there is nothing to do or reverse. However, it's
        # necessary to set the old_link and old_parent in the previous step
        # so that they will be there when the failed Action is later checked.
        if len(self.failed) > 0:
            return
        seen_by = {}
        if making_change:
            for actor in world.concept:
                seen_by[actor] = world.can_see(actor, self.direct)
                if (actor in [self.agent, self.direct] or
                    world.can_see(actor, self.direct)):
                    # Before the Action, the Actor can see the Item.
                    # Update the Item's departure from the "from" Item.
                    new_from = copy.deepcopy(world.item[self.old_parent])
                    new_from.remove_child(self.old_link, self.direct,
                                          making_change)
                    if not world.can_see(actor, self.old_parent):
                        new_from.blank()
                    world.transfer(new_from, actor, self.end)
        # Now make the event's changes in the world.
        world.item[self.old_parent].remove_child(self.old_link, self.direct,
                                                 making_change)
        world.item[self.new_parent].add_child(self.new_link, self.direct,
                                              making_change)
        item = world.item[self.direct]
        if making_change:
            item.parent = self.new_parent
            item.link = self.new_link
            for actor in world.concept:
                room_tag = str(world.room_of(actor))
                # If the item disappeared from sight, transfer it out...
                if seen_by[actor] and not world.can_see(actor, self.direct):
                    world.transfer_out(item, actor, self.end)  
                if (actor == self.agent or actor == self.direct or
                    world.can_see(actor, self.direct)):
                    # After the Action, the Actor can see the Item.
                    # Update the Item itself ...
                    world.transfer(item, actor, self.end)
                new_to = copy.deepcopy(world.item[self.new_parent])
                if (actor == self.new_parent or
                    world.can_see(actor, self.new_parent)):
                    # If the "to" Item is visible, update it fully.
                    world.transfer(new_to, actor, self.end)
                    # If the "to" Item is a Room, update other visible Rooms.
                    if new_to.room:
                        for view_tag in new_to.view:
                            if world.can_see(actor, view_tag):
                                world.transfer(world.item[view_tag], actor,
                                               self.end)
                else:
                    if (actor == self.direct and
                        not world.can_see(actor, room_tag)):
                    # Moved into a dark room; blank out the "to" item.
                        new_to.blank()
                        new_to.add_child(self.new_link, self.direct,
                                         making_change)
                        world.transfer(new_to, actor, self.end)
                if (room_tag in world.concept[actor].item and
                    world.concept[actor].item[room_tag].blanked and
                    world.can_see(actor, room_tag)):
                    world.transfer(world.item[room_tag], actor, self.end)
                    look_at = Sense('examine', actor, 
                                    modality='sight', direct=room_tag)
                    look_at.cause = ':' + str(self.id) + ':'
                    self.enlightened.append(look_at)
        else:
            item.parent = self.old_parent
            item.link = self.old_link

    def pre(self, world):
        """Preconditions for Configure:

        Only @cosmos may Configure Items that are part_of others, Doors, or 
        SharedThings. Configure requires a new link and parent. To be configured
        from "in" a container, the container (if it opens) must be open. To go
        "in" or "through" something, that Item must (if it opens) be open. Be
        able to access the Item and (in most cases) the new parent. The Item
        must be allowed in the new parent."""
        pre_list = []
        if not self.agent == '@cosmos':
            if world.item[self.direct].link == 'part_of':
                pre_list.append(('never', 'configure_parts'))
            if world.item[self.direct].door:
                pre_list.append(('never', 'configure_doors'))
            if hasattr(world.item[self.direct], 'sharedthing'):
                pre_list.append(('never', 'configure_sharedthings'))
        pre_list.append(('configure_to_different', self.direct, 
                         self.new_link, self.new_parent))
        if (hasattr(self, 'old_link') and self.old_link == 'in' and 
            hasattr(world.item[self.old_parent], 'open')):
            pre_list.append(('has_value', self.old_parent, 'open', True))
        if (self.new_link in ['in', 'through'] and
            hasattr(world.item[self.new_parent], 'open')):
            pre_list.append(('has_value', self.new_parent, 'open', True))
        if hasattr(self, 'old_link') and hasattr(self, 'old_parent'):
            pre_list.append(('parent_is', self.direct, self.old_link,
                            self.old_parent))
        pre_list.append(('can_access_direct', self.agent, [self.direct]))
        if (not self.new_parent == '@cosmos' and 
            not world.item[self.new_parent].room):
            pre_list.append(('can_access_indirect', self.agent,
                             [self.new_parent]))
        pre_list.append(('allowed', self.direct, self.new_link,
                         self.new_parent))
        return pre_list

    def post(self):
        'Postcondition: Item is in a new arrangement.'
        return ('parent_is', self.direct, self.new_link, self.new_parent)

    def entails(self, world):
        """Entailed Actions for Configure:

        Passing through Doors into new Rooms, looking at new Rooms,
        replenishing a source with a Substance and evaporating/dissipating a
        Substance. Also, looking at newly-lit Items."""
        actions = []
        if len (self.failed) > 0:
            return actions
        if self.new_link == 'through':
            if world.item[self.new_parent].door:
                rooms = world.item[self.new_parent].connects[:]
                rooms.remove(self.old_parent)
                goal = rooms[0] 
                actions.append(Configure('pass_through', self.agent,
                                 template=('[agent/s] [emerge/v] from [' + 
                                           self.new_parent + '/o]'),
                                 new=('in', goal), direct=self.direct))
            else:
                room = self.new_parent
                actions.append(Configure('fall', self.agent,
                                 template='[direct/s] [drop/v] to the ground',
                                 new=('in', room), direct=self.direct))
        elif (world.item[self.direct].actor and
             not self.old_parent == self.new_parent and
             not self.new_parent == '@cosmos'):
            room = self.new_parent
            look_at = Sense('examine', self.direct, 
                            modality='sight', direct=room)
            look_at.cause = ':' + str(self.id) + ':'
            actions.append(look_at)
        elif world.item[self.direct].substance:
            substance = self.direct.partition('_')[0]
            if (self.new_link == 'in' and 
                hasattr(world.item[self.old_parent], 'source') and 
                world.item[self.old_parent].source == substance):
                _, amount = world.item[substance].children[0]
                actions.append(Configure('replenish', '@cosmos',
                                         new=('in', self.old_parent),
                                         direct=amount, salience=0))
            elif (not hasattr(world.item[self.new_parent], 'vessel') and
                  not (hasattr(world.item[self.new_parent], 'source') and
                       world.item[self.new_parent].source == substance) and
                  not self.new_parent == substance):
                # The substance was poured onto something, and needs to vanish.
                actions.append(Configure('vanish', '@cosmos',
                                         new=('in', substance),
                                         template='the [' + self.direct + 
                                                  '/s] [is/v] gone [now]',
                                         direct=self.direct,))
        actions += self.enlightened
        return actions

class Modify(Action):
    "An action that changes some Item's state, the value of a feature."

    def __init__(self, verb, agent, **keywords):
        # Modify actions must have 'direct', 'feature', and 'new'
        self.direct = keywords['direct']
        del keywords['direct']
        self.feature = keywords['feature']
        del keywords['feature']
        self.new_value = keywords['new']
        del keywords['new']
        # 'old' is optional; if missing, any initial value is fine
        if 'old' in keywords:
            self.old_value = keywords['old']
            del keywords['old']
        # 'indirect' is optional, used only when an agent is using a tool
        if 'indirect' in keywords:
            self.indirect = keywords['indirect']
            del keywords['indirect']
        self.force = 0.2
        Action.__init__(self, verb, agent, 'modify', **keywords)

    def change(self, world, making_change=True):
        'Alter the state of the Item to the new (or old) one.'
        # If attributes are missing, indicating that any values work for this 
        # modify event, they are set with using the values in the world at 
        # this point. This allows the event to be undone later with the
        # correct old value put back into place.
        #
        item = world.item[self.direct]
        if not hasattr(self, 'old_value'):
            self.old_value = getattr(item, self.feature)
        # If the event failed, it itself had no consequence in the world.
        # Thus there is nothing to do or reverse.
        if len(self.failed) > 0:
            return
        # Make the change.
        value = (self.old_value, self.new_value)[making_change]
        setattr(item, self.feature, value)
        # Update the item in actors who can perceive this event. Also, check
        # to see if the actor's room became visible and needs an update.
        if making_change:
            for actor in world.concept:
                if (actor in [self.agent, self.direct] or 
                    world.can_see(actor, self.direct)):
                    world.transfer(item, actor, self.end)
                room_tag = str(world.room_of(actor))
                if (room_tag in world.concept[actor].item and
                    world.concept[actor].item[room_tag].blanked and
                    world.can_see(actor, room_tag)):
                    world.transfer(world.item[room_tag], actor, self.end)
                    look_at = Sense('examine', actor, 
                                    modality='sight', direct=room_tag)
                    look_at.cause = ':' + str(self.id) + ':'
                    self.enlightened.append(look_at)

    def pre(self, world):
        """Preconditions for Modify:

        The Item must have the feature being modified. Modify requires a 
        different value. The old value, if specified, must match. The item
        must be accessible by the agent. If opening an Item, it must (if
        lockable) be unlocked. If burning an Item, fire must be accessible.
        If unlocking an Item, the key must be accessible."""
        pre_list = [('has_feature', self.direct, self.feature)]
        pre_list.append(('modify_to_different', self.direct, self.feature,
                        self.new_value))
        if hasattr(self, 'old_value'):
            pre_list.append(('has_value', self.direct, self.feature,
                             self.old_value))
        pre_list.append(('can_access_direct', self.agent, [self.direct]))
        if self.feature == 'open' and self.new_value:
            if hasattr(world.item[self.direct], 'locked'):
                pre_list.append(('has_value', self.direct, 'locked', False))
        if self.feature == 'burnt':
            flames = [i for i in world.item if 
                      hasattr(world.item[i], 'flame') and world.item[i].flame]
            pre_list.append(('can_access_flames', self.agent, flames))
        if self.feature == 'locked':
            if hasattr(world.item[self.direct], 'key'):
                pre_list.append(('can_access_key', self.agent,
                                 [world.item[self.direct].key]))
            else:
                if not self.agent == '@cosmos':
                    pre_list.append(('never', 'permanently_locked'))
        return pre_list

    def post(self):
        "Postcondition: Item's feature has a new value."
        return ('has_value', self.direct, self.feature, str(self.new_value))

    def entails(self, _):
        'Entailed Actions for Modify: Just looking at newly-lit Items.'
        actions = self.enlightened
        return actions


class Sense(Action):
    'A perception that can update a concept.'

    def __init__(self, verb, agent, **keywords):
        # Sense Actions must have 'direct' and 'modality'.
        for i in ['direct', 'modality']:
            setattr(self, i, keywords[i])
            del keywords[i]
        self.force = 0.0
        Action.__init__(self, verb, agent, 'sense', **keywords)

    def pre(self, _):
        """Preconditions for Sense:

        The agent must be able to see the direct object if looking, access it
        if touching."""
        pre_list = []
        if self.modality == 'sight':
            pre_list.append(('can_see', self.agent, self.direct))
        if self.modality == 'touch':
            pre_list.append(('can_access_direct', self.agent, [self.direct]))
        return pre_list

