'Deal with unrecognized inputs, including ambiguous ones.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import re

import preparer
import presenter

def english_command(tokens, concept, discourse):
    """Converts a command to English.

    E.g., ['LOOK_AT', '@lamp'] becomes 'look at the lamp'"""
    verb = tokens[0]
    line = ''
    i = 1
    for part in discourse.command_canonical[verb].split():
        if (part in ['ACCESSIBLE', 'ACTOR', 'DESCENDANT', 'NEARBY', 
                     'NOT-DESCENDANT', 'WORN']):
            line += concept.item[tokens[i]].noun_phrase(discourse)
            i += 1
        elif part in ['RELATION']:
            line += tokens[i].lower()
            i += 1
        elif part in ['STRING']:
            line += tokens[i]
        else:
            line += part
        line += ' '
    return line[:-1]


def clarify(user_input, concept, discourse, in_stream, out_streams):
    'States that input was not understood or attempts to disambiguate input.'

    if len(user_input.normal) == 0 and len(user_input.possible) == 0:
        clarification = ('(It\'s not clear what "' + str(user_input) +
        '" means. Try typing some other command to ' +
        concept.item[discourse.spin['commanded']].noun_phrase(discourse) + '.)')
    else:
        question = '(Is this a command to '
        commands = []
        options = []
        for possibility in user_input.possible:
            commands.append(english_command(possibility, concept, discourse))
            options.append('(' + str(len(commands)) + ') "' +
                           commands[-1] + '"')
        options.append('(' + str(len(commands) + 1) + ') none of these')
        question += discourse.list_phrases(options, conjunction='or') + '?)'
        question = re.sub('",', ',"', question)
        presenter.present(question, out_streams)
        choose_a_number = preparer.prepare(discourse.separator,
                          '(1-' + str(len(commands) + 1) + ')? ', in_stream)
        selected = None
        if len(choose_a_number.tokens) == 1:
            try:
                selected = int(choose_a_number.tokens[0])
            except ValueError:
                pass
        if selected is None or selected < 1 or selected > len(commands):
            clarification = ('\n(Since you did not select '+
                             discourse.list_phrases(range(1, len(commands) + 1),
                             conjunction='or') + ', the command "' + 
                             str(user_input) +
                             '" cannot be understood. Try something else.)')
        else:
            clarification = '\n(Very well ...)'
            user_input.category = 'command'
            user_input.normal = user_input.possible[selected-1]

    presenter.present(clarification, out_streams)
    return user_input

