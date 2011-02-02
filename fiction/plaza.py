"""Plaza

Items (in particular, Things and Rooms) representing the setting of Lost One."""

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

from item_model import Room, Thing

items = [

    Room('@plaza_center',
        article='the',
        called='center of the plaza',
        referring='center broad plaza of | plaza americas center middle',
        sight="""

        [*'s] senses [hum/ing/2/v] as [*/s] [view/v] [@plaza_center/o]

        the morning [conclude/1/ed/v]

        it [is/1/v] midday [now]
        """,
        exits={
        'north':'@plaza_n',
        'northeast':'@plaza_ne',
        'east':'@plaza_e',
        'southeast':'@plaza_se',
        'south':'@plaza_s',
        'southwest':'@plaza_sw',
        'west':'@plaza_w',
        'northwest':'@plaza_nw'},
        view={
        '@plaza_n': (.5, 'to the north'),
        '@plaza_ne': (.5, 'to the northeast'),
        '@plaza_e': (.5, 'to the east'),
        '@plaza_se': (.5, 'to the southeast'),
        '@plaza_s': (.5, 'to the south'),
        '@plaza_sw': (.5, 'to the southwest'),
        '@plaza_w': (.5, 'to the west'),
        '@plaza_nw': (.5, 'to the northwest')}),

    Room('@plaza_n',
        article='the',
        called='northern area',
        referring='broad plaza of northern | plaza americas part expanse space',
        sight="""
        
        the space north of the plaza's center, which [is/1/v] particularly 
        barren of vegetation and ornament""",
        exits={
        'east':'@plaza_ne',
        'southeast':'@plaza_e',
        'south':'@plaza_center',
        'west':'@plaza_nw',
        'southwest':'@plaza_w',},
        view={
        '@plaza_ne': (.5, 'to the east'),
        '@plaza_e': (.5, 'to the southeast'),
        '@plaza_center': (.5, 'to the south'),
        '@plaza_nw': (.5, 'to the west'),
        '@plaza_w': (.5, 'to the southwest'),
        '@plaza_se': (.25, 'off toward the southeast'),
        '@plaza_s': (.25, 'across the plaza'),
        '@plaza_sw': (.25, 'off toward the southwest')}),

    Thing('@rock in @plaza_n',
        article='a',
        called=' rock',
        referring='fist-sized fist sized | rock stone',
        sight='a fist-sized rock',
        prominence=0.3),

    Thing('@statue part_of @plaza_n',
        article='a',
        called='statue',
        referring='marble | likeness Einstein',
        sight="""
        
        [*/s] [see/v] a marble likeness of Einstein
        
        there [is/1/v] almost no hint [here] of the playful, disheveled 
        scientist so often seen in the photographs that were popular in the 
        early twenty-first century""",
        qualities=['stone'],
        prominence=0.8),

        Room('@plaza_ne',
        article='the',
        called='northeastern area',
        referring=('broad of northeastern | plaza americas part side ' +
                   'expanse space'),
        sight="the space northeast of the plaza's center",
        exits={
       'south':'@plaza_e',
       'southwest':'@plaza_center',
       'west':'@plaza_n'},
        view={
       '@plaza_e': (.5, 'to the south'),
       '@plaza_center': (.5, 'to the southwest'),
       '@plaza_n': (.5, 'to the west'),
       '@plaza_nw': (.25, 'to the far west'),
       '@plaza_w': (.25, 'off toward the west'),
       '@plaza_sw': (.25, 'across the plaza'),
       '@plaza_s': (.25, 'off toward the south'),
       '@plaza_se': (.25, 'to the far south')}),

        Room('@plaza_e',
        article='the',
        called='eastern area',
        referring='broad of eastern | plaza americas part side expanse space',
        sight="the space east of the plaza's center",
        exits={
       'north':'@plaza_ne',
       'south':'@plaza_se',
       'southwest':'@plaza_s',
       'west':'@plaza_center',
       'northwest':'@plaza_n'},
        view={
       '@plaza_ne': (.5, 'to the north'),
       '@plaza_center': (.5, 'to the west'),
       '@plaza_se': (.5, 'to the south'),
       '@plaza_n': (.5, 'to the northwest'),
       '@plaza_s': (.5, 'to the southwest'),
       '@plaza_nw': (.25, 'off toward the northwest'),
       '@plaza_w': (.25, 'across the plaza'),
       '@plaza_sw': (.25, 'off toward the southwest')}),

        Thing('@shredded_shirt in @plaza_e',
        article='a',
        called='shredded shirt',
        referring=('shredded torn flesh-colored flesh colored useless of | ' +
                   'cloth shirt mess'),
        sight='a useless mess of flesh-colored cloth',
        qualities=['clothing', 'trash'],
        prominence=0.3),

        Thing('@newspaper_sheet in @plaza_e',
        article='a',
        called=' newspaper (sheet)',
        referring='news newspaper | sheet page paper newspaper',
        sight="""
        
        there [are/2/v] summary texts LEADER WORKING THROUGH NIGHT FOR COUNTRY,
        MONUMENT NEARS COMPLETION, and PURITY ACCOMPLISHED
        """,
        qualities=['trash'],
        prominence=0.3),

    Thing('@fountain part_of @plaza_e',
        article='a',
        called='fountain',
        referring='rectangular plain | fountain basin jet',
        sight='a single jet [fan/1/v] out, feeding a basin',
        prominence=0.8),

    Room('@plaza_se',
        article='the',
        called='southeastern area',
        referring=('broad plaza of southeastern | plaza americas part ' +
                   'expanse space'),
        sight="the space southeast of the plaza's center",
        exits={
       'north':'@plaza_e',
       'west':'@plaza_s',
       'northwest':'@plaza_center'},
        view={
        '@plaza_e': (.5, 'to the north'),
        '@plaza_s': (.5, 'to the west'),
        '@plaza_center': (.5, 'to the northwest'),
        '@plaza_sw': (.25, 'to the far west'),
        '@plaza_w': (.25, 'off to the west'),
        '@plaza_ne': (.25, 'to the far north'),
        '@plaza_n': (.25, 'off to the north'),
        '@plaza_nw': (.25, 'across the plaza')}),

    Thing('@scrap in @plaza_se',
        article='a',
        called='plastic scrap',
        referring='plastic black | scrap',
        sight='something that was perhaps once part of a black plastic bag',
        qualities=['trash'],
        prominence=0.3),

    Room('@plaza_s',
        article='the',
        called='southern area',
        referring=('broad plaza of southern | plaza americas part ' +
                   'expanse space'),
        sight="the space south of the plaza's center",
        exits={
        'north':'@plaza_center',
        'northeast':'@plaza_e',
        'northwest':'@plaza_w',
        'east':'@plaza_se',
        'west':'@plaza_sw'},
        view={
        '@plaza_se': (.5, 'to the east'),
        '@plaza_e': (.5, 'to the northeast'),
        '@plaza_center': (.5, 'to the north'),
        '@plaza_sw': (.5, 'to the west'),
        '@plaza_w': (.5, 'to the northwest'),
        '@plaza_ne': (.25, 'off toward the northeast'),
        '@plaza_n': (.25, 'across the plaza'),
        '@plaza_nw': (.25, 'off toward the northwest')}),

    Thing('@obelisk part_of @plaza_s',
        article='an',
        called='obelisk',
        referring='| obelisk',
        sight='the stone pointing the way it has for centuries',
        qualities=['stone'],
        prominence=1.0),

    Room('@plaza_sw',
        article='the',
        called='southwestern area',
        referring=('broad plaza of southwestern | plaza americas part ' +
                   'expanse space'),
        sight="the space southwest of the plaza's center",
        exits={
        'north':'@plaza_w',
        'northeast':'@plaza_center',
        'east':'@plaza_s'},
        view={
        '@plaza_w': (.5, 'to the north'),
        '@plaza_s': (.5, 'to the east'),
        '@plaza_center': (.5, 'to the northeast'),
        '@plaza_se': (.25, 'to the far east'),
        '@plaza_e': (.25, 'off to the east'),
        '@plaza_nw': (.25, 'to the far north'),
        '@plaza_n': (.25, 'off to the north'),
        '@plaza_ne': (.25, 'across the plaza')}),

    Thing('@candy_wrapper in @plaza_sw',
        article='a',
        called='candy wrapper',
        referring="candy commodity's | wrapper husk",
        sight="a commodity's husk",
        qualities=['trash'],
        prominence=0.3),

    Room('@plaza_w',
        article='the',
        called='western area',
        referring='broad plaza of western | plaza americas part expanse space',
        sight="the space west of the plaza's center",
        exits={
        'north':'@plaza_nw',
        'east':'@plaza_center',
        'south':'@plaza_sw',
        'northeast':'@plaza_n',
        'southeast':'@plaza_s'},
        view={
        '@plaza_nw': (.5, 'to the north'),
        '@plaza_center': (.5, 'to the east'),
        '@plaza_sw': (.5, 'to the south'),
        '@plaza_n': (.5, 'to the northeast'),
        '@plaza_s': (.5, 'to the southeast'),
        '@plaza_ne': (.25, 'off toward the northeast'),
        '@plaza_e': (.25, 'across the plaza'),
        '@plaza_se': (.25, 'off toward the southeast')}),

    Thing('@smashed_cup in @plaza_w',
        article='a',
        called='smashed cup',
        referring='smashed paper drinking | cup vessel',
        sight='what was once a paper drinking vessel',
        qualities=['trash'],
        prominence=0.3),

    Thing('@tree part_of @plaza_w',
        article='a',
        called='tree',
        referring='large immense sprawling |',
        sight='a tree sprawling by itself on the west side of the plaza',
        prominence=1.0),

    Room('@plaza_nw',
        article='the',
        called='northwestern area',
        referring=('broad plaza of northwestern | plaza americas part ' +
                   'expanse space'),
        sight="the space northwest of the plaza's center",
        exits={
        'east':'@plaza_n',
        'southeast':'@plaza_center',
        'south':'@plaza_w'},
        view={
        '@plaza_w': (.5, 'to the south'),
        '@plaza_n': (.5, 'to the east'),
        '@plaza_center': (.5, 'to the southeast'),
        '@plaza_ne': (.25, 'to the far east'),
        '@plaza_e': (.25, 'off to the east'),
        '@plaza_sw': (.25, 'to the far south'),
        '@plaza_s': (.25, 'off to the south'),
        '@plaza_se': (.25, 'across the plaza')})]

