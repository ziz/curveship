'Text planning: Set tense and referring expressions, lexicalize.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import random
import re
import types

import reply_planner
from realizer import Section, Paragraph, Heading

def has_final(node):
    final = False
    if (hasattr(node, 'info') and hasattr(node.info, 'final') and 
        node.info.final):
        final = True
    elif hasattr(node, 'children'):
        for child in node.children:
            final = final or has_final(child)
    return final


def specify(reply_plan, concept, discourse):
    'Main microplanner invocation, returns blocks wrapped up as a section.'
    blocks = micro(reply_plan, concept, discourse, discourse.min,
                   discourse.max)
    if has_final(reply_plan):
        blocks += [Heading('The End')]
    return Section(blocks)


def determine_tense(event, ref, speech):
    "Returns a tense using Hans Reichenbach's system (1947)."
    if event < ref:
        tense_er = 'anterior'
    elif event == ref:
        tense_er = 'simple'
    else:
        tense_er = 'posterior'
    if ref < speech:
        tense_rs = 'past'
    elif ref == speech:
        tense_rs = 'present'
    else:
        tense_rs = 'future'
    return tense_er, tense_rs


def micro(reply_node, concept, discourse, ref, speech):
    'Does microplanning based on given reference and speech times or rules.'
    blocks = []
    if not isinstance(reply_node, reply_planner.Internal):
        if reply_node.category in ['action', 'room', 'ok']:
            if ref == discourse.right_before:
                ref = reply_node.event - 1
            if ref == discourse.follow:
                ref = reply_node.event
            if ref == discourse.right_after:
                ref = reply_node.event + 1
            if speech is discourse.follow:
                speech = reply_node.event
            e_r, r_s = determine_tense(reply_node.event, ref, speech)
        if reply_node.category == 'action':
            blocks = narrate_action(reply_node, concept, discourse, e_r, r_s)
        elif reply_node.category == 'room':
            blocks = name_room(reply_node, e_r, r_s, concept, discourse)
        elif reply_node.category == 'commentary':
            para = Paragraph(discourse.spin['template_filter'],
                             [reply_node.info])
            para.set(discourse.spin['narrator'], discourse.spin['narratee'],
                     'simple', 'present', discourse.spin['progressive'])
            blocks = [para]
        elif reply_node.category == 'ok':
            blocks = acknowledge(e_r, r_s, concept, discourse,
                                 discourse.spin['focalizer'])
    else:
        for child in reply_node.children:
            blocks += micro(child, concept, discourse, reply_node.ref,
                            reply_node.speech)
    return blocks


def acknowledge(tense_er, tense_rs, _, discourse, __):
    'Produces a rather empty utterance when there is nothing to represent.'
    template = 'nothing special [happen/1/v]'
    para = Paragraph(discourse.spin['template_filter'], [template])
    para.set(discourse.spin['narrator'], discourse.spin['narratee'],
             tense_er, tense_rs, discourse.spin['progressive'])
    return [para]


def name_room(node, tense_er, tense_rs, concept_now, discourse):
    'States the name of the room.'
    agent, time = node.info.agent, node.info.end
    concept = concept_now.copy_at(time)
    room = concept.room_of(agent)
    template = '[' + agent + '/s] [is/v] in ' + room.noun_phrase(discourse)
    para = Paragraph(discourse.spin['template_filter'], [template], time)
    para.set(discourse.spin['narrator'], discourse.spin['narratee'], tense_er,
              tense_rs, discourse.spin['progressive'])
    blocks = [para]
    return blocks


def select(string_or_list):
    'Return a string, either the one passed or a randome element from a list.'
    if type(string_or_list) == types.StringType:
        return string_or_list
    else:
        return random.choice(string_or_list)


def get_representation(action, discourse):
    'Returns the appropriate representation of an action.'
    verb = action.verb
    if verb in discourse.verb_representation:
        template = select(discourse.verb_representation[verb])
    else:
        template = None
        if hasattr(action, 'template'):
            template = select(action.template)
        for (rule, possible_template) in discourse.action_templates:
            if action.match_string(rule):
                template = select(possible_template)
                break
        if template is None:
            template = '[agent/s] [' + verb + '/v]'
            if hasattr(action, 'direct') or hasattr(action, 'target'):
                template = '[agent/s] [' + verb + '/v] [direct/o]'
            if hasattr(action, 'indirect') or hasattr(action, 'new_parent'):
                template = ('<<<ERROR:' + str(verb) +
                            ' has an indirect object but no template.>>>')
    return template


def failed(template, reasons, discourse):
    'Returns a template representing a failed action, explaining the failure.'
    if re.match('\[agent/s\]', template):
        verb_match = re.search('\[(\w+)/v\]', template)
        template = re.sub('\[(\w+)/v\]', verb_match.group(1), template)
        new_part = '[agent/s] [is/v] unable to'
        template = re.sub('\[agent/s\]', new_part, template)
    else:
        template = "impossible"
    first_reason = reasons[0]
    explanation = discourse.failure_to_english[first_reason[0]]
    if first_reason[0] == 'modify_to_different':
        (_, tag, feature, value) = first_reason
        explanation = ('[' + tag + '/s] [is/v] ' +
                       discourse.feature_to_english[feature](value) +
                       ' to begin with')
    if first_reason[0] == 'has_value':
        (_, tag, feature, value) = first_reason
        explanation = ('[' + tag + '/s] [is/not/v] ' +
                       discourse.feature_to_english[feature](value))
    if len(explanation) > 0:
        template += ' because ' + explanation
    return template


def refused(template, refusal):
    'Returns a template explaining a refused action.'
    if re.match('\[agent/s\]', template):
        verb_match = re.search('\[(\w+)/v\]', template)
        template = re.sub('\[(\w+)/v\]', verb_match.group(1), template)
        new_part = '[agent/s] [decide/v] not to'
        template += ' because ' + refusal
        template = re.sub('\[agent/s\]', new_part, template)
    else:
        template = "impossible"
    return template


def replace(node, label, attrs, template):
    'Return a template with label replaced if any attr is present.'
    for attr in attrs:
        if hasattr(node, attr):
            label = '\[' + label
            tag = '[' + getattr(node, attr)
            template = re.sub(label, tag, template)
    return template


def substitute_tags(template, info):
    """Returns a modified template with tags for agent and all objects.

    If certain passive constructions are used in the representations above,
    the direct (more rarely, even the indirect) objects can be subjects."""
    template = replace(info, 'agent', ['agent'], template)
    template = replace(info, 'direct', ['direct', 'target'], template)
    template = replace(info, 'indirect', ['indirect', 'new_parent'], template)
    return template


def narrate_action(node, concept_now, discourse, tense_er, tense_rs):
    'Return blocks that narrate the action in the node.'
    time = node.info.start
    sentence = get_representation(node.info, discourse)
    if len(node.info.failed) > 0:
        sentence = failed(sentence, node.info.failed, discourse)
    elif node.info.refusal is not None:
        sentence = refused(sentence, node.info.refusal)
    if '[old_link]' in sentence:
        old_link = discourse.link_to_english[node.info.old_link][0]
        sentence = re.sub('\[old_link\]', old_link, sentence)
    if '[old_parent' in sentence:
        sentence = re.sub('\[old_parent', '[' + node.info.old_parent, sentence)
    if '[direction]' in sentence:
        sentence = re.sub('\[direction\]', node.info.direction, sentence)
    if '[utterance]' in sentence:
        sentence = re.sub('\[utterance\]', node.info.utterance.lower(),
                          sentence)
    sentence = substitute_tags(sentence, node.info)
    strings = [sentence]
    if len(node.info.failed) == 0 and node.info.refusal is None:
        if hasattr(node.info, 'before'):
            strings = [node.info.before] + strings
        if hasattr(node.info, 'after'):
            strings += [node.info.after]
    para = Paragraph(discourse.spin['template_filter'], strings, time)
    para.set(discourse.spin['narrator'], discourse.spin['narratee'], tense_er,
             tense_rs, discourse.spin['progressive'])
    blocks = [para]
    time = node.info.end
    concept = concept_now.copy_at(time)
    if (node.info.sense and node.info.agent == discourse.spin['focalizer'] and
        len(node.info.failed) == 0 and node.info.refusal is None):
        if node.info.modality == 'sight':
            new_blocks = describe(node.info.direct, tense_er, tense_rs,
                node.speed, concept, discourse, node.info.agent,
                node.info.start)
            blocks += new_blocks
        elif node.info.modality in ['touch', 'hearing', 'smell', 'taste']:
            sense = getattr(concept.item[node.info.direct], node.info.modality)
            if not (sense == ['']):
                sense[0] = ('[*/s] [' +
                            discourse.sense_verb[node.info.modality] + '/v] ' +
                            sense[0])
                para = Paragraph(discourse.spin['template_filter'], sense, time)
                para.set(discourse.spin['narrator'],
                         discourse.spin['narratee'], tense_er, tense_rs,
                         discourse.spin['progressive'])
                blocks += [para]
    blocks = prepend_any_time_words(blocks, node, discourse.spin['time_words'])
    return blocks


def prepend_any_time_words(blocks, node, use_time_words):
    'Add the appropirate time phrase at the start of the first sentence.'
    if use_time_words and node.prior is not None:
        time_words = 'then,'
        if node.event == node.prior:
            time_words = 'meanwhile,'
        elif node.event < node.prior:
            time_words = random.choice(['before that,', 'previously,',
                                        'previous to that,', 'that was after',
                                        'earlier,', 'just beforehand,',
                                        'a moment before'])
        if (len(blocks) > 0 and hasattr(blocks[0], 'sentences') and
            len(blocks[0].sentences) > 0):
            blocks[0].sentences[0].prepend(time_words)
    return blocks

def slots(tag_list, role='o'):
    slot_list = []
    for tag in tag_list:
       slot_list.append('[' + tag + '/' + role + ']')
    return slot_list

def describe(tag, tense_er, tense_rs, speed, concept, discourse, sensor, time):
    'Return blocks of generated text describing the item.'

    # NOTE: This is quite a mess and could use to be broken up and streamlined.
    children = {'in':[], 'of':[], 'on':[], 'part_of':[], 'through':[]}
    child_sentences = []
    to_exclude = [sensor]
    item = concept.item[tag]
    if item == concept.compartment_of(sensor):
        to_exclude += concept.descendants(sensor)
    to_mention = [i for i in concept.descendants(tag, stop='opaque') 
                          if i not in to_exclude]
    for desc_tag in to_mention:
        desc_item = concept.item[desc_tag]
        if desc_item.mention:
            if desc_item.parent == str(item):
                children[desc_item.link].append(desc_tag)
            elif desc_item.parent == '@cosmos':
                children['in'].append(desc_tag)
            else:
                link = desc_item.link
                link_name = discourse.link_to_english[link][0]
                child_sentences.append('[' + desc_tag + '/s] [is/v]' + 
                                   link_name + ' [' + desc_item.parent + '/o]')
    description_block = []
    current_sentences = []
    for string in item.sight + ['']:
        if not string == '':
            current_sentences.append(re.sub('\[\*', '[' + sensor, string))
        elif len(current_sentences) > 0:
            description_block += [Paragraph(discourse.spin['template_filter'],
                                            current_sentences, time)]
            current_sentences = []
    for paragraph in description_block:
        paragraph.set(discourse.spin['narrator'], discourse.spin['narratee'],
                      tense_er, tense_rs, discourse.spin['progressive'])
    heading = None
    if (item.room and speed < 0.8 and concept.room_of(sensor) == item):
        if ('room_name_headings' not in discourse.spin or
            discourse.spin['room_name_headings']):
            room_name = item.noun_phrase(discourse, entire=False)
            heading = room_name[:1].upper() + room_name[1:]
    contents = None
    if (len(children['in']) + len(children['of']) +
        len(children['on'])) > 0:
        contents = '[' + sensor + '/s] [see/v] '
        parent = '[' + tag + '/s]'
        if item.room:
            contents += discourse.list_phrases(slots(children['in']))
        else:
            contents += 'that '
            if item.actor:
                contents += parent
                if len(children['of']) > 0:
                    contents += (' [possess/v] ' +
                                 discourse.list_phrases(slots(children['of'])))
                    if len(children['on']) > 0:
                        contents += ' and'
                if len(children['on']) > 0:
                    contents += (' [wear/ing/v] ' + 
                                 discourse.list_phrases(slots(children['on'],
                                                        role='s')))
            elif len(children['on']) > 0:
                contents += (discourse.list_phrases(slots(children['on'],
                                      role='s')) + ' [is/v] on ' + parent)
                if len(children['in']) > 0:
                    contents += (', which [contain/v] ' +
                                  discourse.list_phrases(slots(children['in'],
                                                         role='s')))
            elif len(children['in']) > 0:
                contents += (parent + ' [contain/v] ' +
                             discourse.list_phrases(slots(children['in'])))
        contents = [contents] + child_sentences
    listed = []
    in_directions = []
    if item.room:
        for direction in item.exits:
            if (concept.has('room', item.exits[direction]) and
                item.exits[direction] not in listed and
                discourse.spin['known_directions']):
                leads_to = concept.item[item.exits[direction]]
                in_directions += [leads_to.noun_phrase(discourse) +
                                  ' [is/1/v] toward the ' + direction]
                listed.append(item.exits[direction])
        far_strings = []
        for far_room in item.view:
            vdir = item.view[far_room][1]
            far_items = []
            if far_room in concept.item:
                for (_, child) in concept.item[far_room].children:
                    if child in concept.item:
                        far_items.append('[' + child + '/o]')
                if len(far_items) > 0:
                    far_line = (vdir + ', ' +
                                discourse.list_phrases(far_items))
                    far_strings.append(far_line)
        if len(far_strings) > 0:
            far_st = ('from [here], [' + sensor + '/s] [is/v] able to see: ' +
                     discourse.list_phrases(far_strings, delimiter=';'))
            in_directions += [far_st]
    blocks = []
    if heading is not None:
        blocks += [Heading(heading)]
    blocks += description_block
    if contents is not None:
        para = Paragraph(discourse.spin['template_filter'], contents, time)
        para.set(discourse.spin['narrator'], discourse.spin['narratee'],
                 tense_er, tense_rs, discourse.spin['progressive'])
        blocks += [para]
    if len(in_directions) > 0 and speed < 0.8:
        far_off = Paragraph(discourse.spin['template_filter'], in_directions,
                            time)
        far_off.set(discourse.spin['narrator'], discourse.spin['narratee'],
                    tense_er, tense_rs, discourse.spin['progressive'])
        blocks += [far_off]
    return blocks

