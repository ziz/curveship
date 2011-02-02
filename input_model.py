'Represent different user inputs (commmands, directives, unrecognized).'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

class RichInput(object):
    'Encapsulates a user input string and information derived from it.'

    def __init__(self, input_string, tokens):
        self.unrecognized = True
        self.command = False
        self.directive = False
        self._category = 'unrecognized'
        self.string = input_string
        self.tokens = tokens
        self.normal = []
        # "tokens" will be reduced to [] in building the normal form, "normal"
        self.possible = []
        self.caused = None

    def __str__(self):
        return self.string

    def get_category(self):
        'Getter for the input category (e.g., "command").'
        return self._category

    def set_category(self, value):
        'Setter for the input category (e.g., "command").'
        if value not in ['unrecognized', 'command', 'directive']:
            raise StandardError('"' + value + '" was given as an input ' +
                                'category but is not a valid category.')
        self._category = value
        self.unrecognized = (value == 'unrecognized')
        self.command = (value == 'command')
        self.directive = (value == 'directive')

    category = property(get_category, set_category)


class InputList(object):
    """Encapsulates all user inputs that have been typed, in order.

    Distinguishes between a session (everything since the program has started
    running) and a traversal (when the current game started, which might be
    because the player typed 'restart.')"""

    def __init__(self):
        self._all = []
        self._traversal_start = 0

    def _count(self, category):
        """Counts only those inputs in the specified category.

        The frist count covers the whole session (everything in the list). The
        second only considers the current traversal."""
        session = len([i for i in self._all if getattr(i, category)])
        traversal = len([i for i in self._all[self._traversal_start:]
                         if getattr(i, category)])
        return (session, traversal)

    def latest_command(self):
        'Returns the most recently entered command.'
        i = len(self._all) - 1
        while i >= 0:
            if self._all[i].command:
                return self._all[i]
            i -= 1

    def update(self, user_input):
        'Adds an input.'
        self._all.append(user_input)

    def reset(self):
        'Sets the list so that the next input will begin a new traversal.'
        self._traversal_start = len(self._all)

    def total(self):
        'Counts inputs in the whole session and in the current traversal.'
        session = len(self._all)
        traversal = session - self._traversal_start
        return (session, traversal)

    def show(self, number):
        'Produces a nicely-formatted list of up to number inputs.'
        full_list = ''
        index = max(len(self._all)-number, 0)
        begin = index
        for i in self._all[begin:]:
            index += 1
            full_list += str(index) + '. "' + str(i) + '" => ' + i.category
            if not i.unrecognized:
                full_list += ': ' + ' '.join(i.normal)
            full_list += '\n'
            if index == self._traversal_start:
                full_list += '\n---- Start of Current Traversal ----\n'
        return (full_list[:-1])

    def undo(self):
        """Changes a command to a directive. Used when the command is undone.

        Since the input no longer maps to an Action in this World, it makes
        to reclassify it as a directive."""
        for i in range(len(self._all)-1, -1, -1):
            if self._all[i].command:
                self._all[i].category = 'directive'
                self._all[i].normal = ['(HYPOTHETICALLY)'] + self._all[i].normal
                break

    def count_commands(self):
        'Counts commands in the session and current traversal.'
        return self._count('command')

    def count_directives(self):
        'Counts directives in the session and current traversal.'
        return self._count('directive')

    def count_unrecognized(self):
        'Counts unrecognized inputs in the session and current traversal.'
        return self._count('unrecognized')

