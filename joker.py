'Carry out directives such as save, restore, and quit.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import os
import pickle
import re

import discourse_model
import microplanner
import reply_planner

MESSAGE = {
    'are': '[] are the [].',

    'world_missing_item': 'The item [] does not exist in the interactive ' + 
        "fiction's world.",

    'world_usage': 'The "world" debugging directive provides information ' + 
        'about items as represented in the simulated world, as opposed to ' + 
        'any one actor\'s concept of it: \n\n"world actions" shows the ' + 
        'actions from the world .\n"world tree" shows items in the world as ' +
        'they are hierarchically arranged.\n"world tree [item]" shows a ' + 
        'subtree rooted at a specific item.\n"world dir [item]" shows the ' + 
        'directory of attributes of a specific item.',

    'concept_missing_item': 'The item [] is not included in []\'s concept of ' +
        'the world.',

    'concept_usage': 'The "concept" debugging directive provides information ' +
        'about items as represented in an actor\'s concept: \n\n"concept ' + 
        '[actor] actions" shows the actions known to the actor.\n"concept ' + 
        '[actor] tree" shows the item tree of the actor\'s concept.\n' + 
        '"concept [actor] tree [item]" shows a subtree rooted at a specific ' + 
        'item.\n"concept [actor] dir [item]" shows the directory of ' + 
        'attributes of a specific item as it represented in that actor\'s ' + 
        'concept.\n\nPossible actors are: [].',

    'inputs': 'The number of [] input so far is [] in this session, [] in ' + 
        'this traversal.',

    'invalid_actor': 'The tag "[]" does not specify a valid actor. Possible ' +
        'actors are: [].',

    'is': '[] is the [].',

    'light_level': "Light level in focalizer's room or compartment: [].",

    'not_an_actor': 'It is only possible to set the [] to be one of the ' + 
        'following: [].',

    'nothing_happened': 'Nothing has happened yet.',

    'order_usage': 'Order can be set to chronicle, retrograde, or achrony.',

    'spin_report': 'Current spin: \n\n[]',

    'spin_usage': 'Type "spin" or "narrating" by itself to see the current ' +
        'spin. Add other arguments to view or set specific values, e.g., ' + 
        '"narrating time after" to set the time of narrating to after events.',

    'quitting': 'This ends the session.',

    'recounting': 'Recounting the specified actions.',

    'restarted': 'The session has been restarted.',

    'restore_error': 'The session could not be restored due to an error ' +
         'locating, opening, or reading the save file.',

    'restore_usage': 'To restore the game, type "restore [filename]", where ' +
        '[filename] consists of only letters, underscores, and numbers.',

    'restored': 'The session has been restored.',

    'save_error': 'The session could not be save due to an error ' +
         'opening or writing the save file.',

    'save_usage': 'To save the game, type "save [filename]", where ' + 
        '[filename] consists of only letters, underscores, and numbers.',

    'saved': 'The session has been saved.',

    'set': 'The [] has been set to [].',

    'speed_usage': 'The default speed can only be set to a number between 0 ' +
        'and 1.',

    'ticks': '[] ticks have passed.',

    'time': 'The narration is done as if it were happening [] the events.',

    'time_already': 'That is the existing setting for the time of narration.',

    'time_usage': 'Time of narration can be set to "before," "during," or ' + 
        '"after" events.',

    'time_words_usage': 'Time words can be turned on or off.',

    'undo_impossible': 'It is not possible to undo [] when the total number ' +
        'of commands is [].',

    'undo_usage': 'The directive "undo" can be used alone or with a number ' + 
        'of commands, for instance, "undo 3," to cancel the effects of one ' +
        'or more previous commands. To type a command to undo something ' + 
        'within the fictional world, use a similar word, such as "unfasten."',

    'undone': 'The command "[]" has been undone.',

    'uses': 'New spin, [], has been loaded.',

    'uses_usage': 'Use "narrating uses [filename]" to load spin from a file; ' +
        '"filename.py" must exist in the "spin" directory.',

    'wrap': '[]'}


class StartupError(Exception):
    'Exception occuring during session startup or in loading a spin.'
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)


def load_file(file_name, required, defaults, module_type):
    """Loads either an interactive fiction or a spin file.

    Improved filename parsing thanks to Max Battcher."""
    dirname, _ = os.path.splitext(file_name)
    pieces = []
    while dirname:
        dirname, basename = os.path.split(dirname)
        if basename:
            pieces.append(basename)
        else:
            break
    pieces.reverse()
    module_name = '.'.join(pieces)
    try:
        mod = __import__(module_name, globals(), locals(), required, -1)
        for attr in required:
            if not hasattr(mod, attr):
                msg = ('This is not a complete fiction file: "' + attr +
                       '" is a required attribute, but the ' + module_type +
                       ' module ' + module_name + ' lacks it.')
                raise StartupError(msg)
        for (attr, default) in defaults.items():
            module = __import__(module_name, globals(), locals(), [attr])
            if not hasattr(module, attr):
                setattr(module, attr, default)
    except ImportError, err:
        msg = ('Unable to open '+ module_type + ' module "' + module_name +
               '" due to this error: ' + str(err))
        raise StartupError(msg)
    return module


def load_fiction(file_name, required, defaults):
    'Loads a fiction file.'
    fiction = load_file(file_name, required, defaults, 'interactive fiction')
    return fiction

def load_spin(existing_spin, spin_file):
    'Loads one spin file and returns an updated spin.'
    focalizer = existing_spin['focalizer']
    commanded = existing_spin['commanded']
    new_file = load_file(spin_file, [], discourse_model.SPIN_DEFAULTS, 'spin')
    if hasattr(new_file, 'spin'):
        existing_spin = update_spin(existing_spin, new_file.spin)
    return existing_spin

def update_spin(existing_spin, new_spin):
    for function in ['focalizer', 'commanded', 'narrator', 'narratee']:
        if function in new_spin and new_spin[function] == '@focalizer':
            new_spin[function] = focalizer
        if function in new_spin and new_spin[function] == '@commanded':
            new_spin[function] = commanded
    for level in ['token', 'sentence', 'paragraph']:
        if (level + '_filter' not in existing_spin or
            existing_spin[level + '_filter'] is None):
            existing_spin[level + '_filter'] = []
        if level + '_filter' in new_spin:
            new_filters = new_spin[level + '_filter']
            if new_filters is None:
                existing_spin[level + '_filter'] = []
            else:
                existing_spin[level + '_filter'] += new_filters
            del(new_spin[level + '_filter'])
# This is some of the machinery that would be used to update a concept if
# '@adventurer' or a similar key is in the spin file. Requires that "concept"
# is passed in as an argument.
##        for actor in concept:
#            if actor in new_spin:
#                for tag, feature, value in new_spin[actor]:
#                    setattr(concept[actor].item[tag], feature, value)
    existing_spin.update(new_spin)
    return existing_spin

def session_startup(version):
    'Return strings to be presented, centered, as a session begins.'
    startup_strings = [' __________', '/ Curveship', 'version ' + version]
    return startup_strings


def show_frontmatter(discourse):
    'Return a string with the title, headline, and credits.'
    frontmatter = ''
    if discourse.metadata['title'] is not None:
        frontmatter += discourse.metadata['title'].upper() + '\n'
    if 'headline' in discourse.metadata:
        frontmatter += discourse.metadata['headline'] + '\n'
    if 'people' in discourse.metadata:
        for (credit, person) in discourse.metadata['people']:
            frontmatter += discourse.typo.indentation + credit + ' '
            frontmatter += person + '\n'
    return frontmatter[:-1]


def show_prologue(data):
    'Return a string containing the prologue, if there is one.'
    if 'prologue' in data:
        return '\n\n'.join(data['prologue'])
    return ''


def report(kind, *params):
    'Prepare a report text using the MESSAGE dictionary.'
    parts = MESSAGE[kind].split('[]')
    string = parts.pop(0)
    params = list(params)
    while len(parts) > 0:
        string += str(params.pop(0))
        string += parts.pop(0)
    return '---\n' + string + '\n---'


def set_role(role, tokens, world, discourse):
    'Nams or change a narrative role, such as focalzier.'
    if len(tokens) == 2:
        report_text = report('is', discourse.spin[role], role)
    elif len(tokens) > 2 and tokens[2] == 'none':
        discourse.spin[role] = None
        report_text = report('set', role, None)
    elif len(tokens) > 2 and tokens[2] in world.concept:
        discourse.spin[role] = tokens[2]
        report_text = report('set', role, tokens[2])
    else:
        all_actors = ', '.join(world.concept)
        report_text = report('not_an_actor', role, all_actors)
    return (report_text, world, discourse)


def wc_info(tokens, world_or_concept, world, discourse):
    'Reports on the world or a concept: tree, item info, actions.'
    report_text = ''
    if tokens[1] == 'actions':
        ids = world_or_concept.act.keys()
        if len(ids) == 0:
            report_text = report('nothing_happened')
        else:
            ids.sort()
            if len(tokens) > 2:
                first = len(ids) - int(tokens[2])
                ids = ids[first:]
            for action in [world_or_concept.act[i] for i in ids]:
                report_text += action.show()
            report_text = report('wrap', report_text[1:-1])
    elif tokens[1] in ['attrs', 'dir']:
        item = world_or_concept.item[tokens[2]]
        for attr in dir(item):
            if not callable(getattr(item, attr)) and not attr[:2] == '__':
                report_text += attr + ': ' + str(getattr(item, attr))
                report_text += '\n'
        report_text = report('wrap', report_text[:-1])
    elif tokens[1] == 'tree':
        root = '@cosmos'
        if len(tokens) > 2:
            root = tokens[2]
        tree_string = world_or_concept.show_descendants(root)[:-1]
        report_text = report('wrap', tree_string)
    return (report_text, None, world, discourse)


# The following functions map directives to replies, reports, changes to the
# world, and changes to the discourse.


def comment(_, world, discourse):
    'A comment has been entered. Just continue.'
    return ('', None, world, discourse)


def concept_info(tokens, world, discourse):
    "Describes items or actions based on a particular actor's concept."
    report_text = ''
    try:
        tag = tokens.pop(1)
        if tag not in world.concept:
            all_actors = ', '.join(world.concept)
            report_text = report('invalid_actor', tag, all_actors)
        else:
            world_or_concept = world.concept[tag]
            if (tokens[1] in ['attrs', 'dir', 'tree'] and len(tokens) > 2 and
                tokens[2] not in world_or_concept.item):
                report_text = report('concept_missing_item', tokens[2], tag)
            else:
                (report_text, _, __, ___) = wc_info(tokens, world_or_concept,
                                                       world, discourse)
    except IndexError:
        pass
    if report_text == '':
        all_actors = ', '.join(world.concept)
        report_text = report('concept_usage', all_actors)
    return (report_text, None, world, discourse)


def count_commands(_, world, discourse):
    'Returns a report on the number of commands issued so far.'
    session, traversal = discourse.input_list.count_commands()
    report_text = report('inputs', 'commands', session, traversal)
    return (report_text, None, world, discourse)


def count_directives(_, world, discourse):
    'Return a report on the number of directives issues so far.'
    session, traversal = discourse.input_list.count_directives()
    report_text = report('inputs', 'directives', session, traversal)
    return (report_text, None, world, discourse)


def count_unrecognized(_, world, discourse):
    'Returns a report on the number of unrecognized inputs so far.'
    session, traversal = discourse.input_list.count_unrecognized()
    report_text = report('inputs', 'unrecognized strings', session, traversal)
    return (report_text, None, world, discourse)


def exits(_, world, discourse):
    "Lists the exits from the focalizer's current room."
    focalizer = discourse.spin['focalizer']
    exit_string = ""
    for (direction, room) in world.room_of(focalizer).exits.items():
        exit_string += direction + ' -> ' + room + '\n'
    report_text = report('are', exit_string,
                         "the exits from the focalizer's current room")
    return (report_text, None, world, discourse)


def inputs(tokens, world, discourse):
    'Returns a report listing all requested inputs.'
    if len(tokens) == 1:
        (how_many, _) = discourse.input_list.total()
    else:
        how_many = int(tokens[1])
    report_text = report('wrap', discourse.input_list.show(how_many))
    return (report_text, None, world, discourse)


def light(_, world, discourse):
    "Returns a report on the focalizer's compartment's light level."
    focalizer = discourse.spin['focalizer']
    report_text = report('light_level', world.light_level(focalizer))
    return (report_text, None, world, discourse)


def narrating_commanded(tokens, world, discourse):
    'Changes the commanded actor.'
    return set_role('commanded', tokens, world, discourse)


def narrating_dynamic(tokens, world, discourse):
    'Changes whether the spin is dynamic.'
    if len(tokens) == 2 or tokens[2] == 'on':
        discourse.spin['dynamic'] = True
    else:
        discourse.spin['dynamic'] = False
    setting = ('static', '(potentially) dynamic')[discourse.spin['progressive']]
    report_text = report('set', 'spin', setting)
    return (report_text, world, discourse)


def narrating_focalizer(tokens, world, discourse):
    'Changes the focalizing actor.'
    return set_role('focalizer', tokens, world, discourse)


def narrating_narratee(tokens, world, discourse):
    'Changes which actor (if any) is the narratee.'
    return set_role('narratee', tokens, world, discourse)


def narrating_narrator(tokens, world, discourse):
    'Changes which actor (if any) is the narrator.'
    return set_role('narrator', tokens, world, discourse)


def narrating_order(tokens, world, discourse):
    'Changes the order.'
    report_text = report('order_usage')
    if len(tokens) == 2:
        report_text = report('is', discourse.spin['order'].capitalize(),
                             'order (the method of ordering events)')
    if len(tokens) > 2:
        report_text = report('set', 'order', tokens[2])
        if tokens[2] in ['chronicle', 'retrograde', 'achrony', 'analepsis',
                         'syllepsis']:
            discourse.spin['order'] = tokens[2]
    return (report_text, world, discourse)


def narrating_perfect(tokens, world, discourse):
    'Changes whether narration is in the perfect by default.'
    if len(tokens) == 2 or tokens[2] == 'on':
        discourse.spin['perfect'] = True
    else:
        discourse.spin['perfect'] = False
    setting = 'default to ' + ('off', 'on')[discourse.spin['perfect']]
    report_text = report('set', 'perfect aspect', setting)
    return (report_text, world, discourse)


def narrating_player(tokens, world, discourse):
    'Changes the player character (both focalizer and commanded).'
    (report1, world, discourse) = set_role('commanded', tokens, world,
                                           discourse)
    (report2, world, discourse) = set_role('focalizer', tokens, world,
                                           discourse)
    return (report1 + report2, world, discourse)


def narrating_progressive(tokens, world, discourse):
    'Changes whether narration is in the progressive by default.'
    if len(tokens) == 2 or tokens[2] == 'on':
        discourse.spin['progressive'] = True
    else:
        discourse.spin['progressive'] = False
    setting = 'default to ' + ('off', 'on')[discourse.spin['progressive']]
    report_text = report('set', 'progressive aspect', setting)
    return (report_text, world, discourse)


def narrating_speed(tokens, world, discourse):
    'Changes the default speed of narration.'
    report_text = report('speed_usage')
    if len(tokens) == 2:
        report_text = report('is', discourse.spin['speed'], 'default speed')
    else:
        number = float(''.join(tokens[2:]))
        if number >= 0 and number <= 10:
            discourse.spin['speed'] = number
            report_text = report('set', 'default speed', number)
    return (report_text, world, discourse)


def narrating_time(tokens, world, discourse):
    "Changes the narrator's position in time relative to events."
    report_text = report('time_usage')
    new_value = None
    if len(tokens) == 2:
        report_text = report('time', discourse.spin['time'])
    elif len(tokens) > 2:
        if tokens[2] in ['before', 'previous', 'anterior', 'earlier']:
            new_value = 'before'
        elif tokens[2] in ['during', 'simultaneous']:
            new_value = 'during'
        elif tokens[2] in ['after', 'later', 'subsequent', 'posterior']:
            new_value = 'after'
        if new_value is not None:
            if new_value == discourse.spin['time']:
                report_text = report('time_already')
            else:
                discourse.spin['time'] = new_value
                report_text = report('set', 'time of narrating', new_value)
    return (report_text, world, discourse)


def narrating_timewords(tokens, world, discourse):
    'Turns time_words on or off.'
    if len(tokens) == 2 or tokens[2] == 'on':
        discourse.spin['time_words'] = True
    else:
        discourse.spin['time_words'] = False
    setting = ('off', 'on')[discourse.spin['time_words']]
    report_text = report('set', 'use of time words', setting)
    return (report_text, world, discourse)


def narrating_uses(tokens, world, discourse):
    'Loads a new spin (parameters for telling) from a file.'
    report_text = report('uses_usage')
    if len(tokens) > 2 and re.match('[a-zA-Z_0-9]+$', tokens[1]):
        spin_file = 'spin/' + tokens[2] + '.py'
        try:
            new_spin = load_spin(discourse.spin, spin_file)
            discourse.spin.update(new_spin)
            report_text = report('uses', tokens[2])
        except StartupError, err:
            report_text = str(err) + '. ' + report('uses_usage')
    return (report_text, world, discourse)


def narrating(tokens, world, discourse):
    'Returns a report describing the current spin.'
    report_text = report('spin_usage')
    if len(tokens) < 2:
        pairs = discourse.spin.items()
        pairs.sort()
        longest = max([len(i) for (i, _) in pairs])
        string = ''
        for (key, value) in pairs:
            string += (longest - len(key) + 1) * ' '
            string += key + '  ' + str(value) + '\n'
        report_text = report('spin_report', string[:-1])
    elif 'narrating_'+tokens[1] in globals():
        (report_text, _,
         __) = globals()['narrating_' + tokens[1]](tokens, world, discourse)
    return (report_text, None, world, discourse)


def prologue(_, world, discourse):
    'Returns a reply containing the prologue.'
    reply_text = report('wrap', show_prologue(discourse.metadata))
    return (reply_text, None, world, discourse)


def recount(tokens, world, discourse):
    'Returns a report and a reply with narration of previous events.'
    reply_text = None
    if len(world.concept[discourse.spin['focalizer']].act) == 0:
        report_text = report('nothing_happened')
    else:
        report_text = report('recounting')
        concept = world.concept[discourse.spin['focalizer']]
        ids = concept.act.keys()
        ids.sort()
        start = ids[0]
        end = ids[-1]
        if len(tokens) >= 2:
            start = int(tokens[1])
        if len(tokens) == 3:
            end = int(tokens[2])
        recount_ids = []
        current = start
        while current <= end:
            if current in concept.act:
                recount_ids.append(current)
            current = current + 1
        original_time = discourse.spin['time']
        discourse.spin['time'] = 'after'
        reply_plan = reply_planner.plan(recount_ids, concept, discourse)
        section = microplanner.specify(reply_plan, concept, discourse)
        reply_text = section.realize(concept, discourse)
        discourse.spin['time'] = original_time
    return (report_text, reply_text, world, discourse)


def restart(_, world, discourse):
    'Restarts the game and emit an appropriate report.'
    discourse.input_list.reset()
    world.reset()
    return (report('restarted'), None, world, discourse)


def restore(tokens, world, discourse):
    'Restores the game and emit an appropriate report.'
    if len(tokens) > 1 and re.match('[a-zA-Z_0-9]+$', tokens[1]):
        try:
            file_name = 'save/' + tokens[1] + '.ses'
            restore_file = file(file_name, 'r')
            (world, discourse) = pickle.load(restore_file)
            restore_file.close()
            report_text = report('restored')
        except IOError:
            report_text = report('restore_error')
    else:
        report_text = report('restore_usage')
    return (report_text, None, world, discourse)


def room_name(_, world, discourse):
    "Give the name of the focalizer's current room."
    focalizer = discourse.spin['focalizer']
    room = str(world.room_of(focalizer))
    report_text = report('is', room, "focalizer's current room")
    return (report_text, None, world, discourse)


def save(tokens, world, discourse):
    'Save the fiction/game/world and emit an appropriate report.'
    if len(tokens) > 1 and re.match('[a-z_0-9]+$', tokens[1]):
        try:
            file_name = 'save/' + tokens[1] + '.ses'
            save_file = file(file_name, 'w')
            pickle.dump((world, discourse), save_file)
            save_file.close()
            report_text = report('saved')
        except IOError:
            report_text = report('save_error')   
    else:
        report_text = report('save_usage')
    return (report_text, None, world, discourse)


def terminate(_, world, discourse):
    """Quits the game after emitting an appropriate report.

    Since 'quit' is a builtin function, this one is called 'terminate.'"""
    world.running = False
    return (report('quitting'), None, world, discourse)


def ticks(_, world, discourse):
    'Returns a report on how many ticks (time units) have passed.'
    return (report('ticks', world.ticks), None, world, discourse)


def title(_, world, discourse):
    'Returns a reply containing the frontmatter.'
    reply_text = report('wrap', show_frontmatter(discourse))
    return (reply_text, None, world, discourse)


def undo(tokens, world, discourse):
    'Undoes a turn and emits an appropriate report.'
    (_, commands) = discourse.input_list.count_commands()
    to_undo = 1
    try:
        if len(tokens) > 1:
            to_undo = int(tokens[1])
            if to_undo < 1:
                raise ValueError
        if to_undo > commands:
            if to_undo == 1:
                to_undo = 'a command'
            else:
                to_undo = str(to_undo) + ' commands'
            report_text = report('undo_impossible', to_undo, commands)
        else:
            report_text = ''
            undone = 0
            while undone < to_undo:
                command_to_undo = discourse.input_list.latest_command()
                report_text += report('undone', str(command_to_undo))
                discourse.input_list.undo()
                world.undo(command_to_undo.caused)
                undone += 1
    except ValueError:
        report_text = report('undo_usage')
    return (report_text, None, world, discourse)


def world_info(tokens, world, discourse):
    "Describes the world's items or actions."
    report_text = ''
    try:
        world_or_concept = world
        if (tokens[1] in ['attrs', 'dir', 'tree'] and len(tokens) > 2 and
            tokens[2] not in world.item):
            report_text = report('world_missing_item', tokens[2])
        else:
            (report_text, _, __, ___) = wc_info(tokens, world_or_concept,
                                                   world, discourse)
    except IndexError:
        pass
    if report_text == '':
        report_text = report('world_usage')
    return (report_text, None, world, discourse)


def joke(tokens, world, discourse):
    'Handles directives -- inputs that deal with the program state.'
    head = tokens[0].lower()
    if head in globals():
        (report_text, reply_text, world,
         discourse) = globals()[head](tokens, world, discourse)
    else:
        raise StandardError('The directive "' + head + '" is defined in the ' +
         'discourse, but the corresponding routine in the Joker is missing.')
    texts = (report_text, reply_text)
    return (texts, world, discourse)
