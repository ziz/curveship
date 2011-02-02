#!/usr/bin/env python
'An interactive fiction system offering control over the narrative discourse.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import sys
import os
import time
import optparse

import clarifier
import command_map
import discourse_model
import joker
import microplanner
import preparer
import presenter
import recognizer
import reply_planner
import world_model

class Multistream(object):
    'Encapsultes multiple output streams.'

    def __init__(self, streams, log=None):
        self.streams = streams
        self.log = log

    def close(self):
        """Close each of the streams.

        If one or more of the streams returns some exit status, the maximum
        value is returned by this method."""
        overall_status = None
        for stream in self.streams:
            status = stream.close()
            if status is not None:
                overall_status = max(overall_status, status)
        return overall_status

    def write(self, string):
        'Write string to each of the streams.'
        for stream in self.streams:
            stream.write(string)


def start_log(out_streams):
    'Open a log file named with the next available integer.'
    log_files = [os.path.splitext(l)[0] for l in os.listdir('logs/') if
                 os.path.splitext(l)[1] == '.log']
    if len(log_files) == 0:
        latest = 0
    else:
        latest = max([int(log_file) for log_file in log_files])
    log_file = 'logs/' + str(latest + 1) + '.log'
    try:
        log = file(log_file, 'w')
    except IOError, err:
        msg = ('Unable to open log file "' + log_file + '" for ' +
               'writing due to this error: ' + str(err))
        raise joker.StartupError(msg)
    # So that we output to the screen and the log file:
    out_streams.streams.append(log)
    # And indicate that this stream is the log file:
    out_streams.log = log
    presenter.present('\nLogged to: ' + log_file + '\nSession started ' +
                      time.strftime("%Y-%m-%d %H:%M:%S"), out_streams)
    return out_streams


def initialize(if_file, spin_files, out_streams):
    'Load all files and present the header and prologue.'
    for startup_string in joker.session_startup(__version__):
        presenter.center(startup_string, out_streams)
    fiction = joker.load_fiction(if_file, ['discourse', 'items'],
                                 discourse_model.FICTION_DEFAULTS)
    presenter.center('fiction: ' + if_file, out_streams)
    world = world_model.World(fiction)
    world.set_concepts(fiction.concepts)
    for i in dir(fiction):
        if i[:8] == 'COMMAND_':            
            setattr(command_map, i.partition('_')[2], getattr(fiction, i))
            delattr(fiction, i)
    for (key, value) in discourse_model.SPIN_DEFAULTS.items():
        if key not in fiction.discourse['spin']:
            fiction.discourse['spin'][key] = value
    while len(spin_files) > 0:
        next_file = spin_files.pop(0)
        new_spin = joker.load_spin(fiction.discourse['spin'], next_file)
        fiction.discourse['spin'].update(new_spin)
        presenter.center('spin: ' + next_file, out_streams)
    presenter.present('\n', out_streams)
    presenter.present('', out_streams)
    discourse = discourse_model.Discourse(fiction.discourse)
    reply = joker.show_frontmatter(discourse)
    if 'prologue' in discourse.metadata:
        reply += '\n\n' + joker.show_prologue(discourse.metadata)
    presenter.present(reply, out_streams)
    return (world, discourse)


def handle_input(user_input, world, discourse, in_stream, out_streams):
    """Deal with input obtained, sending it to the appropriate module.

    The commanded character's concept is used when trying to recognize
    commands."""
    c_concept = world.concept[discourse.spin['commanded']]
    user_input = recognizer.recognize(user_input, discourse, c_concept)
    if user_input.unrecognized:
        user_input = clarifier.clarify(user_input, c_concept, discourse,
                                       in_stream, out_streams)
    if user_input.command:
        user_input, id_list, world = simulator(user_input, world,
                                                  discourse.spin['commanded'])
        if hasattr(world.item['@cosmos'], 'update_spin'):
            discourse.spin = world.item['@cosmos'].update_spin(world, 
                                                               discourse)
        spin = discourse.spin
        if hasattr(world.item['@cosmos'], 'use_spin'):
            spin = world.item['@cosmos'].use_spin(world, discourse.spin)
        f_concept = world.concept[spin['focalizer']]
        tale, discourse = teller(id_list, f_concept, discourse)
        presenter.present(tale, out_streams)
    elif user_input.directive:
        texts, world, discourse = joker.joke(user_input.normal, world,
                                             discourse)
        for text in texts:
            if text is not None:
                presenter.present(text, out_streams)
    discourse.input_list.update(user_input)
    return (user_input, world, discourse)


def each_turn(world, discourse, in_stream, out_streams):
    'Obtain and processes input, if the session is interactive.'
    if discourse.spin['commanded'] is None:
        if hasattr(world.item['@cosmos'], 'interval'):
            world.item['@cosmos'].interval()
        _, id_list, world = simulator(None, world,
                                         discourse.spin['commanded'])
        focal_concept = world.concept[discourse.spin['focalizer']]
        reply_text, discourse = teller(id_list, focal_concept, discourse)
        presenter.present(reply_text, out_streams)
    else:
        if (hasattr(discourse, 'initial_inputs') and 
             len(discourse.initial_inputs) > 0):
            input_string = discourse.initial_inputs.pop(0)
            user_input = preparer.tokenize(input_string, discourse.separator)
            presenter.present('[> ' + input_string, out_streams, '', '')
        else:
            user_input = preparer.prepare(discourse.separator, 
                                          discourse.typo.prompt, in_stream, 
                                          out_streams)
        # After each input, present a newline all by itself.
        presenter.present('\n', out_streams, '', '')
        while len(user_input.tokens) > 0 and world.running:
            (user_input, world, discourse) = handle_input(user_input, world,
                                              discourse, in_stream,
                                              out_streams)
            presenter.present(discourse.input_list.show(1),
                              out_streams.log)
    return (world, discourse)


def simulator(user_input, world, commanded, actions_to_do=None):
    'Simulate the IF world using the Action from user input.'
    if actions_to_do is None:
        actions_to_do = []
    done_list = []
    start_time = world.ticks
    for tag in world.item:
        if (world.item[tag].actor and not tag == commanded and 
            world.item[tag].alive):
            # The commanded character does not act automatically. That is,
            # his, her, or its "act" method is not called.
            new_actions = world.item[tag].act(command_map, world.concept[tag])
            actions_to_do.extend(new_actions)
    if commanded is not None and user_input is not None:
        commanded = world.item[commanded]
        c_action = commanded.do_command(user_input.normal, command_map, world)
        if c_action is not None:
            c_action.cause = '"' + ' '.join(user_input.normal) + '"'
            actions_to_do.append(c_action)
            if user_input is not None:
                user_input.caused = c_action.id
    current_time = start_time
    while len(actions_to_do) > 0 and world.running:
        action = actions_to_do.pop(0)
        to_be_done = action.do(world)
        done_list.append(action.id)
        if action.final:
            world.running = False
        actions_to_do = to_be_done + actions_to_do
        if action.end > current_time:
            world.advance_clock(action.end - current_time)
            current_time = action.end
    return user_input, done_list, world


def teller(id_list, concept, discourse):
    'Narrate actions based on the concept. Update the discourse.'
    reply_plan = reply_planner.plan(id_list, concept, discourse)
    section = microplanner.specify(reply_plan, concept, discourse)
    output = section.realize(concept, discourse)
    return output, discourse


def parse_command_line(argv):
    'Improved option/argument parsing and help thanks to Andrew Plotkin.'
    parser = optparse.OptionParser(usage='[options] fiction.py [ spin.py ... ]')
    parser.add_option('--auto', dest='autofile',
                      help='read inputs from FILE', metavar='FILE')
    parser.add_option('--nodebug', action='store_false', dest='debug',
                      help='disable debugging directives',
                      default=True)
    opts, args = parser.parse_args(argv[1:])
    if not args:
        parser.print_usage()
        msg = ('At least one argument (the fiction file name) is ' +
               'needed; any other file names are processed in order ' +
               'as spin files.')
        raise joker.StartupError(msg)
    return opts, args


def main(argv, in_stream=sys.stdin, out_stream=sys.stdout):
    "Set up a session and run Curveship's main loop."
    return_code = 0
    try:
        out_streams = Multistream([out_stream])
        opts, args = parse_command_line(argv)
        out_streams = start_log(out_streams)
        world, discourse = initialize(args[0], args[1:], out_streams)
        discourse.debug = opts.debug
        if opts.autofile is not None:
            auto = open(opts.autofile, 'r+')
            discourse.initial_inputs = auto.readlines()
            auto.close()
        if len(world.act) > 0:
            _, id_list, world = simulator(None, world,
                                          discourse.spin['commanded'],
                                          world.act.values())
            focal_concept = world.concept[discourse.spin['focalizer']]
            reply_text, discourse = teller(id_list, focal_concept, discourse)
            presenter.present(reply_text, out_streams)
        while world.running:
            previous_time = time.time()
            world, discourse = each_turn(world, discourse, in_stream,
                                         out_streams)
            out_streams.log.write('#' + str(time.time() - previous_time))
    except joker.StartupError, err:
        presenter.present(err.msg, Multistream([sys.stderr]))
        return_code = 2
    except KeyboardInterrupt, err:
        presenter.present('\n', out_streams)
        return_code = 2
    except EOFError, err:
        presenter.present('\n', out_streams)
        return_code = 2
    finally:
        in_stream.close()
        out_streams.close()
    return return_code


if __name__ == '__main__':
    sys.exit(main(sys.argv))

