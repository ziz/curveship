'Understand prepared user input as commands or directives. The "parser."'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import copy
import re

def noun_phrase(item, discourse):
    'Returns a regular expression (string) corresponding to the Item.'
    (before, nouns, after) = item.referring
    if str(item) == discourse.spin['narratee']:
        nouns.update(discourse.me_nouns)
    if str(item) == discourse.spin['narrator']:
        nouns.update(discourse.you_nouns)
    phrase = ('((and|,|' + '|'.join(before) + '|' + '|'.join(nouns) + ') )*' +
              '(' + '|'.join(nouns) + ')' +
              '( (' + '|'.join(after) + '|' + '|'.join(nouns) + '))*')
    return discourse.determiner + phrase

def correspond(exp, string):
    'Returns True if and only if the expression matches the entire string.'
    if len(exp) > 0:
        if not exp[0] == '^':
            exp = '^' + exp
        if not exp[-1] == '$':
            exp = exp + '$'
    return re.match(exp, string)

def contained_substances(items, concept):
    contents = []
    for i in items:
        if ((hasattr(concept.item[i], 'vessel') or
             hasattr(concept.item[i], 'source')) and
            len(concept.item[i].children) > 0):
            (_, child) = concept.item[i].children[0]
            if child not in items:
                contents += [child]
    return contents

def nonterminal(nonterm, discourse, concept):
    'Returns all phrases that a token such as ACCESSIBLE matches.'
    phrases = []
    agent = discourse.spin['commanded']
    if nonterm == 'RELATION':
        link_names = discourse.english_to_link.items()
        link_names.sort()
        # Sorted here because 'onto' should be listed before 'on' and so on,
        # so the list of name to link mappings is reversed.
        link_names.reverse()
        for mapping in link_names:
            phrases.append(mapping)
    elif nonterm == 'ACCESSIBLE':
        for i in agent_access(agent, concept):
            phrases.append((noun_phrase(concept.item[i], discourse), i))
    elif nonterm == 'ACTOR':
        for i in agent_access(agent, concept):
            if concept.has('actor', i):
                phrases.append((noun_phrase(concept.item[i], discourse), i))
    elif nonterm == 'NOT-DESCENDANT':
        for i in not_descendant(agent, concept):
            phrases.append((noun_phrase(concept.item[i], discourse), i))
    elif nonterm == 'DESCENDANT':
        for i in concept.descendants(agent):
            phrases.append((noun_phrase(concept.item[i], discourse), i))
    elif nonterm == 'WORN':
        for i in worn(agent, concept):
            phrases.append((noun_phrase(concept.item[i], discourse), i))
    elif nonterm == 'DIRECTION':
        for (i, j) in discourse.compass.items():
            phrases.append((discourse.determiner + i, j))
    elif nonterm == 'NEARBY':
        if agent == '@cosmos':
            for i in concept.item:
                phrases.append((noun_phrase(concept.item[i], discourse), i))
            return phrases
        agent_room = concept.room_of(agent)
        if agent_room is None:
            return []
        elif concept.item[str(agent_room)].door:
            rooms_visible = concept.item[str(agent_room)].connects
        else:
            rooms_visible = agent_room.view.keys()
        for room in [str(agent_room)] + rooms_visible:
            for i in [room] + concept.descendants(room):
                phrases.append((noun_phrase(concept.item[i], discourse), i))
    return phrases

def agent_access(agent, concept):
    """Returns a list of everything the agent can access.

    Plus contained substances, actually, because even if they are in closed
    containers their names may be used metonymically."""
    items = concept.accessible(agent)
    items += contained_substances(items, concept)
    return items

def not_descendant(agent, concept):
    "Returns a list of accessible items not in the agent's descendants."
    not_of = []
    agent_children = []
    for (_, item) in concept.item[agent].children:
        agent_children += [item]
    for item in agent_access(agent, concept):
        if item not in agent_children:
            not_of += [item]
    return not_of

def worn(agent, concept):
    'Returns a list of things on (worn by) the agent.'
    items = []
    for (link, item) in concept.item[agent].children:
        if link == 'on':
            items.append(item)
    return items

def check_rule(rule_list, action_list, token_string, discourse, concept):
    """Returns all rules on the rule list that match the token string.

    For instance, the two tokens "take lamp" will match ['TAKE', '@lamp'],
    assuming there is an object @lamp called "lamp" in the area and nothing
    else is called "lamp." That will be returned from TAKE's rule list. When
    check_rule() is called with other rule lists, an empty list will be
    returned.

    In cases of ambiguity ("take a thing" when there are several around) a
    single call of check_rule() may return a list with several Items."""
    verb_part = rule_list[0]
    command_verb = action_list[0]
    result = []
    if len(rule_list) == 1:
        if correspond(verb_part, token_string):
            result = [[command_verb]]
    elif re.match(verb_part, token_string) is not None:
        token_string = re.sub('^' + verb_part + ' ', '', token_string)
        r_list = copy.copy(rule_list)
        a_list = copy.copy(action_list)
        args = check_args((r_list, 1), (a_list, 1), token_string,
                          discourse, concept)
        if len(args) == 1:
            if args[0].pop() == '-SUCCESS-':
                result = [[command_verb] + args[0]]
        elif len(args) > 1: # Ambiguous arguments; list every possibility
            result = []
            for i in args:
                i.pop() # Get rid of the "-SUCCESS-" token
                result.append([command_verb] + i)
    return result

def check_args(rule, action, token_string, discourse, concept):
    'Returns matches for tokens past the first one, the arguments.'
    (rule_list, rule_index) = rule
    (action_list, action_index) = action
    matched = []
    if len(token_string) == 0:
        # Nothing left to match. Two possibilities for success here.
        if len(rule_list) == rule_index:
            # The rule list has been exhausted too
            matched = [['-SUCCESS-']]
        elif len(rule_list) == rule_index + 1:
            # There is one last part remaining in the rule list...
            if (rule_list[rule_index][0] == '(' and
                rule_list[rule_index][-2:] == ')?'):
                # But this last part is optional.
                matched = [['-SUCCESS-']]
    # Continuing: There is something left in the token string.
    elif not len(rule_list) == rule_index:
        # As long as there is something left in the rule list, too, keep
        # checking...
        rule_piece = rule_list[rule_index]
        if not rule_piece[0].isupper():
            if not rule_piece[-1] == ' ':
                rule_piece += '(\\b|$)'
            if re.match(rule_piece, token_string) is not None:
                token_string = re.sub('^' + rule_piece, '', token_string)
                if token_string[:1] == ' ':
                    token_string = token_string[1:]
                matched = check_args((rule_list, rule_index+1),
                                     (action_list, action_index),
                                     token_string, discourse, concept)
        elif rule_piece == 'STRING':
            word = re.sub(' .*', '', token_string)
            token_string = re.sub('^'+word+' ?', '', token_string)
            additional = check_args((rule_list, rule_index+1),
                                    (action_list, action_index),
                                    token_string, discourse, concept)
            for i in additional:
                matched.append([word] + i)
        else:
            for (exp, arg) in nonterminal(rule_piece, discourse, concept):
                if len(exp) > 0 and not exp[-1] == ' ':
                    exp += '(\\b|$)'
                if re.match(exp, token_string) is not None:
                    new_token_string = re.sub('^' + exp, '', token_string)
                    if new_token_string[:1] == ' ':
                        new_token_string = new_token_string[1:]
                    additional = check_args((rule_list, rule_index+1),
                                            (action_list, action_index+1),
                                            new_token_string, discourse,
                                            concept)
                    for i in additional:
                        matched.append([arg] + i)
    return matched

def recognize(user_input, discourse, concept):
    """Main function for parsing user input.

    Deals with special cases (such as "west", which is mapped to a command
    with a verb), invokes check_rule for each command, and sets the
    appropriate information on user_input."""
    first = []
    while (len(user_input.tokens) > 0 and
           user_input.tokens[0] not in discourse.separator):
        first.append(user_input.tokens.pop(0))

    # Remove any extra separators
    while (len(user_input.tokens) > 0 and
           (user_input.tokens[0] in discourse.separator)):
        user_input.tokens.pop(0)

    if first[0] in discourse.compass:
        user_input.category = 'command'
        direction = discourse.compass[first[0]]
        user_input.normal = ['LEAVE', direction]

    rule_matches = []
    token_string = ' '.join(first)
    for (action_list, rule_list) in discourse.commands:
        for new_match in check_rule(rule_list, action_list, token_string,
                                    discourse, concept):
            if not new_match in rule_matches:
                rule_matches.append(new_match)

    if len(rule_matches) == 1:
        command = rule_matches[0]
        if (command[0] == 'TURN_ON' and
            'on' not in dir(concept.item[command[1]]) and
            'lit' in dir(concept.item[command[1]])):
            command[0] = 'ILLUMINATE'
        elif (command[0] == 'TURN_OFF' and
            'on' not in dir(concept.item[command[1]]) and
            'lit' in dir(concept.item[command[1]])):
            command[0] = 'EXTINGUISH'
        for token in command:
            if token in concept.item:
                if token not in discourse.givens:
                    discourse.givens.add(token)
        user_input.category = 'command'
        user_input.normal = command

    elif len(rule_matches) > 1:
        user_input.category = 'unrecognized'
        user_input.possible = rule_matches

    if first[0] in discourse.directive_verbs:
        head = discourse.directive_verbs[first[0]]
        directive = [head] + first[1:]
        user_input.category = 'directive'
        user_input.normal = directive

    if discourse.debug and first[0] in discourse.debugging_verbs:
        head = discourse.debugging_verbs[first[0]]
        if (head == 'narrating' and len(first) > 1 and
            first[1] in discourse.spin_arguments):
            argument = discourse.spin_arguments[first[1]]
            directive = [head] + [argument] + first[2:]
        else:
            directive = [head] + first[1:]
        user_input.category = 'directive'
        user_input.normal = directive

    return user_input
