# One-turn/initiative system...
# start turn, handle campaign sot level efcts, generate init q, resolve all sot efcts by timestamp, get action first q member, cont until q empty, handle campaign eot level efcts, resolve eot efcts by timestamp, clean transient vars, goto start turn

# finish warpfire to fit new sot/eot loc_effects loops

# willpower (new stat) determines dispel instead of 'level'

# effects in context menu: scrollable text box or clickable buttons w/ descrip

# add r-click pop-context, r-click is 'q'/'cancel' when cannot pop-context

# adding/removing psyshield/invis?, !!!!! effects need to handle their own instances of adding types. Removing/wiping all instances with a later spell, then adding another instance while effects are waiting to expire and will attempt to remove an instance will remove the later added instances

# remove all damage text now handled by apply_damage() (ents still handle their own 'miss' conditions/text)

# currently, local effects only have sot effects (loc_effects_dict), add: handle both sot and eot local effects

# update ali spells, app.spell_target_ents() app.action_target_ents()

# end turn 'q' cancel hotkey

# use other audio than pygame...
# python3.8.5 can use playsound.playsound('filename.wav|mpg', block = False) !!! needs second arg to run async, 
# playsound is just a wrapper around a few other funcs, just use them directly

# plague vis (does not get focus) when continuing to enemy off screen, prob fine

# to disable visuals (assuming spell/action visuals are the only thing that needs to be 'turned off') just check in creation of specific vis in spells/actions (check for flag 'no-visuals'...)

# scrollbox help menu
# text widget is editable text?!... use listbox or canvas?

# pain timing, cast on adjacent pb

# consider critical-hit/miss for dispel and to-hit 95-100% and 0-5%

# change fuse trap? undo_funcs should not cause dmg? also rage?

# all flying moves become 'large' (move above maptops)

# unbind all during mapmelds? labyrinth level 'map-fog'

# psi-push onto sparkle, was 'fixed' with 'psi-push-text', changed back...
# this is solved by tagging ALL text objects with both 'text' and a unique name ie tags = ('text', 'psionic_push')

# load all summon related images on levelstart

# restrict/lock screen size, do not allow screen resizings during logic execution

# ? cenobite, lesser demon, familiar (spell-produced summons/non-wolves) become ai-controlled?
# at least concept of 'woodland' type (morgan's spell-summons), ai-controlled friendly summons (like hunting_hawk)

# pathing manager, ai manager/dispatcher

# add lighting sound beleths
# beleths timing when moving map to focus on adjacent enemy

# deathmatch: set options num summons, sum level, spells

# change powerups like +1 all stats, +1 end, to specific lvl2's for each char, so each char can grow differently

# undead knight more interesting than just melee atk, lvl 3 boss

# log all text (descriptive, not just 'hit!')

# limit number of scarabs?

# finish version .9
# finish levels, add gorgon level
# final spells, cantrips
# debug ali spells
# add morgan lefay spells
# add 3rd level summons
# change found spells to char specific levelups

# throw visuals, (damage?)
# would need to transform the image of thrown ent (tkinter func),

# borders for text boxes between levels

# water and air mages enter same time

# eq loop timing, text object creation/destruction

# elemental attack visuals/timing
# eq too good? water mage doesnt hit often...
# check eq move focus / move off screen

# turn music on/off/up/down

# give shadow mist 'flight' or 'ethereal'

# pain spell, logically works fine, but timing of visual is affected by using it on ent with death_trigger(s)

# make wrapper for ALL partials so that they have same __name__ attr as their function argument

# white dragon melee attack and iceblast anims
# dragon level, at some point, lose the ability to click down on map, what coord is left click registering on bottom edge? probably hinges on moved_down/moved_right...

# minotaur shadow

# enemy to dispel stuff...

# test LOS, implement it with something (gorgon at least)

# mummify, make warrior lose leap

# pyinstaller...py2app, py2exe, must be built on target, linux?

# styling of sizes of stuff, buttons, fonts (mainly fonts, which will fill buttons to their size), make var on start that is screensize and set font as some fraction of that

# mesmerize too good against barbarian (sub-boss of level), newly acquired abilities should be useful on same level, just balance probably by raising psyche of barbarian

# is pain/entomb too good? base pain dmg on max_spirit of target

# fix sorc teleport barbarian, do not teleport if endloc is further from goal

# entomb handle 'all sqrs occupied' edge case, may not be possible to even reach this state with current levels...?

# minotaur regen? minotaur kill trigger? kill both undead knight trigger?

# add death of protag scenes

# 2 player mode needs some sort of terrain objective, reasons to engage or hold areas, when and where

# make walking/movement animations

# Instead of 'confirm_quit' labels, paste text across whole screen 

import tkinter as tk
# from tkinter import ttk
from os import walk
from PIL import ImageTk,Image
from random import choice, randrange
from functools import partial, reduce
from fractions import Fraction
# from pickle import dump, load
from copy import deepcopy
from math import ceil
# filehandler = open(filename, 'r') 
# object = pickle.load(filehandler)

def round_100(x):
    prefix = x // 100
    rm = int(str(x)[-2:])
    if rm >= 50:
        prefix += 1
    return prefix

# takes start and end coord ([x,y]), returns True if no interceding 'block' sqrs, else False
def los(start, end):
    blocked = [c for c in app.coords if app.grid[c[0]][c[1]] == 'block']
    x = start[0]*100+50-app.moved_right
    y = start[1]*100+50-app.moved_down
    endx = end[0]*100+50-app.moved_right
    endy = end[1]*100+50-app.moved_down
    if x == endx:
        xstep = 0
        ystep = 10
    elif y == endy:
        xstep = 10
        ystep = 0
    else:
        slope = Fraction(abs(x - endx), abs(y - endy))
        xstep = slope.numerator
        ystep = slope.denominator
        while xstep + ystep < 10:
            xstep *= 2
            ystep *= 2
    def los_loop(sx, sy, ex, ey, xstep, ystep):
        if abs(sx - ex) < 15 and abs(sy - ey) < 15:# close enough to goal sqr
            return True
        if sx > ex:
            sx -= xstep
        elif sx < ex:
            sx += xstep
        if sy > ey:
            sy -= ystep
        elif sy < ey:
            sy += ystep
        cx = round_100(sx)
        cy = round_100(sy)
        if [cx,cy] in blocked:
            return False
        else:
            return los_loop(sx, sy, ex, ey, xstep, ystep)
    return los_loop(x, y, endx, endy, xstep, ystep)

# convenience funcs
def dist(loc1, loc2):
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])

# start is coord like [2,3], goal is list of coords like [[2,4],[4,5]...], grid is list of lists where each list is a 'row'
# 'row' holds strings ('', 'EntityID', or 'block')
# returns path from start to goal (list of coords)
def bfs(start, goal, grid):
    path = []
    q = [[start]]
    visited = [start]
    while q:
        path = q[0]
        q = q[1:]
        last = path[-1]
        if last in goal:
            return path
        adj = [c for c in app.coords if dist(c, last) == 1 and grid[c[0]][c[1]] == '']
        for s in adj:
            if s not in visited:
                q.append(path + [s])
                visited.append(s)
    return None

def to_hit(a1, a2):
    base = 50
    dif = a1 - a2
    base += (dif*5)
    rand = randrange(1, 100)
    if rand < base:
        return True
    else:
        return False
        
# add random element?
def damage(a1, a2):
    base = 4
    dif = a1 - a2
    if base + dif < 1: return 1 
    else: return base + dif
    
# takes 2 ent objects, a negative int amount, a string type 'melee', 'ranged', 'poison', or 'magick', and a lockname string to set
# following effects MAY change amount applied (amount is always the only value returned, whether changed or not), OR do different non-damage things
def apply_damage(attacker, defender, amount, type, source, lockname):
    atk_loop(attacker.attack_effects[:] + app.loc_effects_dict[tuple(attacker.loc)].atk_effects, attacker, defender, amount, type, source, lockname)
    
def atk_loop(effects_list, attacker, defender, amount, type, source, lockname):
    if effects_list == []:
        defense_loop(defender.defense_effects[:] + app.loc_effects_dict[tuple(defender.loc)].def_effects[:], attacker, defender, amount, type, source, lockname)
    else:
        ef = effects_list[0]
        effects_list = effects_list[1:]
        amount, time = ef(attacker, defender, amount, type)
        root.after(time, lambda el = effects_list, at = attacker, de = defender, am = amount, ty = type, s = source, ln = lockname : atk_loop(el, at, de, am, ty, s, ln))
        
def defense_loop(effects_list, attacker, defender, amount, type, source, lockname):
    if effects_list == []:
        # delay to wait for lockvar to be created
        root.after(333, lambda at = attacker, de = defender, am = amount, ty = type, s = source, ln = lockname : finish_apply_damage(apply_damage, at, de, am, ty, s, ln))
    else:
        ef = effects_list[0]
        effects_list = effects_list[1:]
        amount, time = ef(attacker, defender, amount, type)
        root.after(time, lambda el = effects_list, at = attacker, de = defender, am = amount, ty = type, s = source, ln = lockname : defense_loop(el, at, de, am, ty, s, ln))

# func that is called with 'lock' must accept lockname which it changes after executing to signal completion
def lock(func, *args, **kwargs):
    name = 'dethlok'+str(app.death_count)
    app.death_count += 1
    app.dethloks[name] = tk.IntVar(0)
    func(*args, **kwargs, lockname = name)
    app.wait_variable(app.dethloks[name])

#
def finish_apply_damage(apply_damage, attacker, defender, amount, type, source, lockname = None):
    amount = abs(amount) # get amount as pos value to apply resist/wknss
    resist = defender.get_resist()
    if type in resist:
        amount = max(1,amount//2)
    weak = defender.get_weak()
    if type in weak:
        amount = int(amount*1.5)
    pre = defender.spirit
    defender.spirit -= amount
    if defender.spirit > defender.base_spirit:
        defender.spirit = defender.base_spirit
    post = defender.spirit
    d = pre - post
    app.canvas.create_text(defender.loc[0]*100+49-app.moved_right, defender.loc[1]*100+74-app.moved_down, text = source+' '+str(d)+' spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
    app.canvas.create_text(defender.loc[0]*100+50-app.moved_right, defender.loc[1]*100+75-app.moved_down, text = source+' '+str(d)+' spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
    if defender.spirit <= 0:
        app.canvas.create_text(defender.loc[0]*100+49-app.moved_right, defender.loc[1]*100+94-app.moved_down, text = defender.name.replace('_',' ') + ' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(defender.loc[0]*100+50-app.moved_right, defender.loc[1]*100+95-app.moved_down, text = defender.name.replace('_',' ') + ' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        name = 'Dethlok'+str(app.death_count)
        app.death_count += 1
        app.dethloks[name] = tk.IntVar(0)
        root.after(1888, lambda t = 'text' : app.canvas.delete(t))
        root.after(1999, lambda id = defender.number, name = name : app.kill(id, name))
        app.wait_variable(app.dethloks[name])
        app.dethloks[lockname].set(1)
    else:
        root.after(1888, lambda t = 'text' : app.canvas.delete(t))
        root.after(1999, lambda ln = lockname : app.dethloks[ln].set(1))
        
# takes 2 ent objects, positive int amount
def apply_heal(healer, target, amount):
    target.spirit += amount
    if target.spirit > target.base_spirit:
        target.spirit = target.base_spirit
        
# takes two lists of lists (lists of coords, [[x,y],[x2,y2],...])
# returns a list of their intrsct or []
def intersect(lx,ly):
    tx = [tuple(s) for s in lx]
    ty = [tuple(s) for s in ly]
    nl = list(set(tx) & set(ty))
    return [list(t) for t in nl]

# GLOBALS
curs_pos = [0, 0]
# is_object_selected = False
selected = []
selected_vis = []
map_pos = [0, 0]
grid_pos = [0,0]


# change to only import what is neededmm
# import pygame
from pygame import mixer
freq = 44100     # audio CD quality
bitsize = -16    # unsigned 16 bit
channels = 1     # 1 is mono, 2 is stereo
buffer = 1024    # number of samples (experiment to get right sound)
# use this just for intro screen, ideally make it loop smoothly (no lull in sound)
mixer.init(freq, bitsize, channels, buffer)
background_music = mixer.Channel(0) # argument must be int
sound_effects = mixer.Channel(1)
# background_music.music.set_volume(0.7) # optional volume 0 to 1.0
# background_music.music.load('Ove Melaa - Dead, Buried and Cold.ogg')
# background_music.music.play(-1, 0)

class Dummy():
    def __init__(self):
        pass

class Effect():
    def __init__(self, name = None, duration = None, level = None, undo_func = None, eot_func = None, sot_func = None):
        self.name = name
        # sot_func will change like eot_func once it is done changing to accept locknames
#         if sot_func == None:
#             def nothing():
#                 return None
#             self.sot_func = nothing
#         else:
        self.sot_func = sot_func
        self.eot_func = eot_func
        self.undo_func = undo_func
        self.duration = duration
        self.level = level
        app.effects_counter += 1
        
    def dispel(self, mod = 0):
        r = randrange(0, 101)
        if r > (self.level-mod)*10:
            self.undo_func()
            return True
        else:
        # maybe create the Fail text here...
            return False

# instances of these exist in the effects_dict of Loc instances (one Loc instance for each x,y coord on map)
# app.loc_effects_dict[(x,y)] = inst
class Local_Effect():
    def __init__(self, name = None, duration = None, level = None, undo_func = None, eot_func = None, sot_func = None, loc = None, avoid = None):
        self.name = name
        self.sot_func = sot_func
        self.eot_func = eot_func
        self.undo_func = undo_func
        self.duration = duration
        self.level = level
        self.loc = loc
        self.avoid = avoid
        app.effects_counter += 1
        
    def dispel(self, mod = 0):
        r = randrange(0, 101)
        if r > (self.level-mod)*10:
            self.undo()
            return True
        else:
            return False

class Vis():
    def __init__(self, name, loc):
        if name == 'Aura':
            self.name = name
            self.img = app.aura_anims[0]
            self.loc = loc
            self.anim_dict = {}
            self.anim_counter = 0
            for k,v in app.aura_anims.items():
                self.anim_dict[k] = v
        elif name == 'Mortar':
            self.name = name
            self.img = app.mortar_anims[0]
            self.loc = loc
            self.anim_dict = {}
            self.anim_counter = 0
            for k,v in app.mortar_anims.items():
                self.anim_dict[k] = v
        elif name == 'Pestilence':
            self.name = name
            self.img = app.pestilence_anims[0]
            self.loc = loc
            self.anim_dict = {}
            self.anim_counter = 0
            for k,v in app.pestilence_anims.items():
                self.anim_dict[k] = v
        elif name == 'Plague':
            self.name = name
            self.img = app.plague_anims[0]
            self.loc = loc
            self.anim_dict = {}
            self.anim_counter = 0
            for k,v in app.plague_anims.items():
                self.anim_dict[k] = v
        else:
            self.name = name
            self.img = ImageTk.PhotoImage(Image.open('animations/' + name + '/0.png'))
            self.loc = loc
            self.anim_dict = {}
            self.anim_counter = 0
            anims = [a for r,d,a in walk('animations/' + self.name + '/')][0]
            anims = [a for a in anims[:] if a[0] != '.']
            for i, anim in enumerate(anims):
                a = ImageTk.PhotoImage(Image.open('animations/' + name + '/' + anim))
                self.anim_dict[i] = a
            
    def rotate_image(self):
        total_imgs = len(self.anim_dict.keys())-1
        if self.anim_counter == total_imgs:
            self.anim_counter = 0
        else:
            self.anim_counter += 1
        self.img = self.anim_dict[self.anim_counter]


class Loc():
    def __init__(self, loc):
        self.loc = loc
        self.move_effects = []
        self.atk_effects = []
        self.def_effects = []
        # # these should be owned by the effect that created them, which are held in the effects dict
        # sot/eot loops should iterate over each Loc instance (one for each x,y coord on map), grab all of its effects, and call each effect's sot/eot func
        # edge case: order of operations for resolution of effects that may remove other effects that are poised to be resolved in this same turn phase, currently the sot/eot loop gets all effects from ONE Loc instance and queues them to be resolved (they are queued as funcs and will be called regardless of the removal of their controlling effect), HOWEVER any funcs within this queue that remove controlling/owning effects from OTHER Loc instances THAT HAVE YET TO BE CALLED/QUEUED will prevent their attached sot/eot funcs from being called, order of Loc instance resolution is up to the language (ordinals of x,y coords?), this should be resolved...
        # ABOVE  NOT TRUE
        # they are grabbed from all Loc instances at once...
#         self.eot_effects = []
#         self.sot_effects = []
        self.str_effects = []
        self.agl_effects = []
        self.end_effects = []
        self.dodge_effects = []
        self.psyche_effects = []
        self.effects_dict = {}

class Sqr():
    def __init__(self, img, loc):
        self.img = img
        self.loc = loc
        self.anim_dict = {}
        self.anim_counter = 0
        for k,v in app.sqr_anims.items():
            self.anim_dict[k] = v
            
    def rotate_image(self):
        total_imgs = len(self.anim_dict.keys())-1
        if self.anim_counter == total_imgs:
            self.anim_counter = 0
        else:
            self.anim_counter += 1
        self.img = self.anim_dict[self.anim_counter]

class Entity():
    def __init__(self, name, img, loc, owner, type = 'normal'):
        self.name = name
        self.img = img
        self.loc = loc
        self.owner = owner
        self.move_used = False
        self.immovable = False
        self.type = type # is this ever used over move_type?
#         self.targetable = True # not used
        if isinstance(self, Witch):
            self.tags = self.name
            self.number = self.name
        elif self.type == 'large':
            self.tags = ('large', self.number)
        elif isinstance(self, Summon):
            self.tags = self.number
        self.base_str = self.str
        self.base_agl = self.agl
        self.base_end = self.end
        self.base_dodge = self.dodge
        self.base_psyche = self.psyche
        self.base_spirit = self.spirit
        if isinstance(self, Witch):
            self.base_magick = self.magick
        self.str_effects = []
        self.agl_effects = []
        self.end_effects = []
        self.dodge_effects = []
        self.psyche_effects = []
        self.attack_effects = []
        self.defense_effects = []
        self.move_effects = []
        self.resist_effects = [] # obj.resist and obj.weak are in subclass instances
        self.weak_effects = [] # resist/weak resolved in apply_damage()
        self.types = [] 
        self.type_effects = []
        self.death_triggers = []
        self.effects_dict = {}
        self.anim_dict = {}
        self.init_normal_anims()
        self.anim_counter = randrange(0, len(self.anim_dict.keys()))
        self.action_effects = []
        
    def get_types(self):
        ts = self.types[:]
        for ef in self.type_effects:
            ts = ef(ts)
        return ts
        
    def get_resist(self):
        rs = self.resist[:]
        for ef in self.resist_effects:
            rs = ef(rs)
        return rs
        
    def get_weak(self):
        ws = self.weak[:]
        for ef in self.weak_effects:
            ws = ef(ws)
        return ws
        
        
    def get_actions(self):
        actions = dict(self.actions)
        for ef in self.action_effects:
            actions = ef(actions)
        return actions
            
            
    def rotate_image(self):
        total_imgs = len(self.anim_dict.keys())-1
        if self.anim_counter == total_imgs:
            self.anim_counter = 0
        else:
            self.anim_counter += 1
        self.img = self.anim_dict[self.anim_counter]
            
    def init_attack_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in walk('./attack_animations/' + self.name + '/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('attack_animations/' + self.name + '/' + anim))
            self.anim_dict[i] = a
            
    def init_cast_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in walk('./casting_animations/' + self.name + '/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('casting_animations/' + self.name + '/' + anim))
            self.anim_dict[i] = a
            
    def init_normal_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in walk('./animations/' + self.name + '/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/' + self.name + '/' + anim))
            self.anim_dict[i] = a
            
    def get_abl(self, abl):
        if abl == 'str':
            q = self.str_effects + app.loc_effects_dict[tuple(self.loc)].str_effects
            base = self.str
        elif abl == 'agl':
            q = self.agl_effects + app.loc_effects_dict[tuple(self.loc)].agl_effects
            base = self.agl
        elif abl == 'end':
            q = self.end_effects + app.loc_effects_dict[tuple(self.loc)].end_effects
            base = self.end
        elif abl == 'dodge':
            q = self.dodge_effects + app.loc_effects_dict[tuple(self.loc)].dodge_effects
            base = self.dodge
        elif abl == 'psyche':
            q = self.psyche_effects + app.loc_effects_dict[tuple(self.loc)].psyche_effects
            base = self.psyche
        elif abl == 'move_range':
            q = self.move_effects + app.loc_effects_dict[tuple(self.loc)].move_effects
            base = self.move_range
        for func in q:
            base = func(base)
        return base
        
    # add modifier
    def save_check(self, abl, mod = 0):
        if abl == 'str':
            a = self.get_abl('str')
        elif abl == 'agl':
            a = self.get_abl('agl')
        elif abl == 'end':
            a = self.get_abl('end')
        elif abl == 'dodge':
            a = self.get_abl('dodge')
        elif abl == 'psyche':
            a = self.get_abl('psyche')
        a += mod
        a *= 10
        rand = randrange(-1, 102)
        if a > rand:
            return True # pass
        else:
            return False # fail
            
    # used by ai controlled ents when their turn is done (for that individual ent)
    def ai_end_turn(self, ents_list):
        ents_list = ents_list[1:]
        if ents_list == []:
            app.end_turn()
        else:
            app.do_ai_loop(ents_list)
            
    # Move for user controlled Ents
    def move(self, event = None):
        if self.move_used == True:
            return
        app.depop_context(event = None)
#         root.unbind('<a>')
#         root.unbind('<q>')
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_move)
        sqrs = self.legal_moves()
        app.animate_squares(sqrs)
        b = tk.Button(app.context_menu, text = 'Confirm Move Square', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_move(e, sqr, sqrs))
        b.pack(side = 'top', pady = 3)
        app.context_buttons.append(b)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_move(e, sqr, sqrs))
        
    def do_move(self, event, sqr, sqrs):
        global selected
        if sqr not in sqrs:
            return
        app.unbind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        if isinstance(self, Shadow):
            if self.form == 'shadow_wolf':
                effect1 = mixer.Sound('Sound_Effects/footsteps.ogg')
                effect1.set_volume(.5)
                sound_effects.play(effect1, -1)
        elif isinstance(self, (Witch, Bard, Warrior, Plaguebearer)):
            effect1 = mixer.Sound('Sound_Effects/footsteps.ogg')
            effect1.set_volume(.5)
            sound_effects.play(effect1, -1)
        elif isinstance(self, Familiar_Imp):
            effect1 = mixer.Sound('Sound_Effects/familiar_imp_move.ogg')
            effect1.set_volume(.5)
            sound_effects.play(effect1, -1)
        elif isinstance(self, Familiar_Homonculus):
            effect1 = mixer.Sound('Sound_Effects/familiar_homonculus_move.ogg')
            effect1.set_volume(.5)
            sound_effects.play(effect1, -1)
        # start ANIM here
        if isinstance(self, Witch):
            id = self.name
        else:
            id = self.number
        start_sqr = self.loc[:]
        end_sqr = sqr
        selected = [id]
        # get path and move_loop over each sqr until path consumed
        path = bfs(start_sqr, [end_sqr], app.grid) # end_sqr must be in list
        begin = path[0]
        end = path[1]
        x = begin[0]*100+50-app.moved_right
        y = begin[1]*100+50-app.moved_down
        endx = end[0]*100+50-app.moved_right
        endy = end[1]*100+50-app.moved_down
        def move_loop(id, x, y, endx, endy, start_sqr, end_sqr, path):
            if x % 20 == 0 or y % 20 == 0:
                self.rotate_image()
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if x > endx:
                x -= 10
                app.canvas.move(id, -10, 0)
            if x < endx: 
                x += 10
                app.canvas.move(id, 10, 0)
            if y > endy: 
                y -= 10
                app.canvas.move(id, 0, -10)
            if y < endy: 
                y += 10
                app.canvas.move(id, 0, 10)
            try: app.canvas.tag_lower((self.tags), 'large')
            except: pass
            app.canvas.tag_lower((app.ent_dict[id].tags), 'maptop')
            app.canvas.tag_raise('cursor')
            if x == end_sqr[0]*100+50-app.moved_right and y == end_sqr[1]*100+50-app.moved_down: # END WHOLE MOVE
                self.finish_move(id, end_sqr, start_sqr)
            elif x == endx and y == endy: # END PORTION OF PATH
                path = path[1:]
                begin = path[0]
                end = path[1]
                x = begin[0]*100+50-app.moved_right
                y = begin[1]*100+50-app.moved_down
                endx = end[0]*100+50-app.moved_right
                endy = end[1]*100+50-app.moved_down
                move_loop(id, x, y, endx, endy, start_sqr, end_sqr, path)
            else: # CONTINUE LOOP
                root.after(66, lambda id = id, x = x, y = y, ex = endx, ey = endy, s = start_sqr, s2 = end_sqr, p = path : move_loop(id, x, y, ex, ey, s, s2, p))
        move_loop(id, x, y, endx, endy, start_sqr, end_sqr, path)
        
    def flying_move(self, event = None):
        if self.move_used == True:
            return
        app.depop_context(event = None)
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_move)
        sqrs = self.legal_moves()
        app.animate_squares(sqrs)
        b = tk.Button(app.context_menu, text = 'Confirm Move Square', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_flying_move(e, sqr, sqrs))
        b.pack(side = 'top', pady = 3)
        app.context_buttons.append(b)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_flying_move(e, sqr, sqrs))
        
    def do_flying_move(self, event = None, sqr = None, sqrs = None):
        global selected
        if sqr not in sqrs:
            return
        app.unbind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        selected = [self.number]
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        endx = sqr[0]*100+50-app.moved_right
        endy = sqr[1]*100+50-app.moved_down
        start_sqr = self.loc[:]
        end_sqr = sqr[:]
        total_distance = abs(x - endx) + abs(y - endy)
        # tic doesnt matter for circular image loop, would need to make flying_anims and switch to
        tic = 30 #total_distance/9 # Magic Number debug, number of images for vis
        if x == endx:
            xstep = 0
            ystep = 10
        elif y == endy:
            xstep = 10
            ystep = 0
        else:
            slope = Fraction(abs(x - endx), abs(y - endy))
            # needs to be moving at least 10 pixels, xstep + ystep >= 10
            xstep = slope.numerator
            ystep = slope.denominator
            while xstep + ystep < 10:
                xstep *= 2
                ystep *= 2
        def flying_arc(x, y, endx, endy, start_sqr, end_sqr, acm, tic, xstep, ystep):
            if acm >= tic:
                acm = 0
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if x > endx:
                acm += xstep
                x -= xstep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            elif x < endx:
                acm += xstep
                x += xstep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if y > endy:
                acm += ystep
                y -= ystep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            elif y < endy:
                acm += ystep
                y += ystep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if abs(x - endx) < 13 and abs(y - endy) < 13:
                self.finish_move(self.number, end_sqr, start_sqr)
            else: # CONTINUE LOOP
                root.after(66, lambda x = x, y = y, e = endx, e2 = endy, s = start_sqr, s2 = end_sqr, acm = acm, tic = tic, xs = xstep, ys = ystep : flying_arc(x, y, e, e2, s, s2, acm, tic, xs, ys))
        flying_arc(x, y, endx, endy, start_sqr, end_sqr, tic+1, tic, xstep, ystep)
        
        
    # used by trickster, shadow, ...
    def teleport_move(self, event = None):
        if self.move_used == True:
            return
        app.depop_context(event = None)
#         root.unbind('<a>')
#         root.unbind('<q>')
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_move)
        sqrs = self.legal_moves()
        app.animate_squares(sqrs)
        if isinstance(self, Shadow):
            text = 'Confirm Mist Move'
        else:
            text = 'Confirm Teleport Square'
        b = tk.Button(app.context_menu, text = text, wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = sqrs : self.do_teleport(e, s))
        b.pack(side = 'top', pady = 3)
        app.context_buttons.append(b)
        root.bind('<a>', lambda e, s = sqrs : self.do_teleport(e, s))
        
    def do_teleport(self, event, sqrs):
#         global selected
        endloc = grid_pos[:]
        if endloc not in sqrs:
            return
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        self.move_used = True
        oldloc = self.loc[:]
        if isinstance(self, Shadow):
            effect1 = mixer.Sound('Sound_Effects/shadow_move.ogg')
            effect1.set_volume(.3)
            sound_effects.play(effect1, 0)
            app.vis_dict['Shadow_Move'] = Vis(name = 'Shadow_Move', loc = oldloc[:])
            vis = app.vis_dict['Shadow_Move']
        else:
            effect1 = mixer.Sound('Sound_Effects/teleport_move.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = oldloc[:])
            vis = app.vis_dict['Teleport']
        app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(1999, lambda endloc = endloc : self.finish_teleport(endloc))
        
    def finish_teleport(self, endloc):
        app.grid[self.loc[0]][self.loc[1]] = ''
        app.canvas.delete(self.number)
        self.loc = endloc[:]
        app.grid[endloc[0]][endloc[1]] = self.number
        app.canvas.delete('Teleport')
        if isinstance(self, Shadow):
            del app.vis_dict['Shadow_Move']
            app.vis_dict['Shadow_Move'] = Vis(name = 'Shadow_Move', loc = endloc[:])
            vis = app.vis_dict['Shadow_Move']
        else:
            effect1 = mixer.Sound('Sound_Effects/teleport_move.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            del app.vis_dict['Teleport']
            app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = endloc[:])
            vis = app.vis_dict['Teleport']
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(1999, lambda endloc = endloc : self.cleanup_teleport(endloc))
        
    def cleanup_teleport(self, endloc):
        app.cleanup_squares()
        try: 
            del app.vis_dict['Teleport']
            app.canvas.delete('Teleport')
        except: pass
        try: 
            del app.vis_dict['Shadow_Move']
            app.canvas.delete('Shadow_Move')
        except: pass
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = self.img, tags = self.tags)
        try: app.canvas.tag_lower(self.tags, 'large')
        except: pass
        app.canvas.tag_lower(self.tags, 'maptop')
        app.depop_context(event = None)
        app.unbind_all()
        app.rebind_all()
            
            
    def finish_move(self, id, end, start):
        sound_effects.stop()
        global selected
        selected = []
        oldloc = start
        newloc = end
        self.loc = newloc[:]
        app.grid[oldloc[0]][oldloc[1]] = ''
        app.grid[newloc[0]][newloc[1]] = self.number
        self.move_used = True
        self.cleanup_move()
        
    def cleanup_move(self, event = None):
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        if app.active_player == 'p1' or app.num_players == 2:
            app.rebind_all()
    

class Summon(Entity):
    def __init__(self, name, img, loc, owner, number, type = 'normal'):
        self.number = number
        super().__init__(name, img, loc, owner, type = type)
        
    # only called by computer controlled Entities, takes the list of all entities to act that is consumed by each entity as it uses its turn, and the location being moved to
    # debug add other move sounds...
    def ai_move(self, ents_list, endloc):
        global selected
        if isinstance(self, Skeleton):
            effect1 = mixer.Sound('Sound_Effects/undead_move.ogg')
            effect1.set_volume(2)
            sound_effects.play(effect1, -1)
        elif isinstance(self, Undead_Knight):
            effect1 = mixer.Sound('Sound_Effects/undead_knight_move.ogg')
            effect1.set_volume(.5)
            sound_effects.play(effect1, -1)
        else:
            effect1 = mixer.Sound('Sound_Effects/footsteps.ogg')
            effect1.set_volume(.5)
            sound_effects.play(effect1, -1)
        self.move_used = True
        selected = [self.number]
        id = self.number
        start_sqr = self.loc[:]
        path = bfs(start_sqr, [endloc], app.grid[:]) # end_sqr must be put in list
        begin = path[0]
        end = path[1]
        x = begin[0]*100+50-app.moved_right
        y = begin[1]*100+50-app.moved_down
        endx = end[0]*100+50-app.moved_right
        endy = end[1]*100+50-app.moved_down
        def move_loop(id, x, y, endx, endy, start_sqr, endloc, path):
            if x % 20 == 0 or y % 20 == 0:
                self.rotate_image()
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if x > endx:
                x -= 10
                app.canvas.move(id, -10, 0)
            elif x < endx: 
                x += 10
                app.canvas.move(id, 10, 0)
            if y > endy: 
                y -= 10
                app.canvas.move(id, 0, -10)
            elif y < endy: 
                y += 10
                app.canvas.move(id, 0, 10)
            try: app.canvas.tag_lower((self.tags), 'large')
            except: pass
            app.canvas.tag_lower((self.tags), 'maptop')
            app.canvas.tag_raise('cursor')
            if x == endloc[0]*100+50-app.moved_right and y == endloc[1]*100+50-app.moved_down: # END WHOLE MOVE
                self.ai_finish_move(endloc, start_sqr, ents_list)
            elif x == endx and y == endy: # END PORTION OF PATH
                path = path[1:]
                begin = path[0]
                end = path[1]
                x = begin[0]*100+50-app.moved_right
                y = begin[1]*100+50-app.moved_down
                endx = end[0]*100+50-app.moved_right
                endy = end[1]*100+50-app.moved_down
                move_loop(id, x, y, endx, endy, start_sqr, endloc, path)
            else: # CONTINUE LOOP
                root.after(66, lambda id = id, x = x, y = y, ex = endx, ey = endy, s = start_sqr, s2 = endloc, p = path : move_loop(id, x, y, ex, ey, s, s2, p))
        move_loop(id, x, y, endx, endy, start_sqr, endloc, path)
        
    def ai_finish_move(self, end_sqr, start_sqr, ents_list):
        global selected
        sound_effects.stop()
        selected = []
        self.loc = end_sqr[:]
        app.grid[start_sqr[0]][start_sqr[1]] = ''
        app.grid[end_sqr[0]][end_sqr[1]] = self.number
        if isinstance(self, Kensai):
            atk_sqrs = self.legal_attacks()
            atk_sqrs = [e for e in atk_sqrs if app.grid[e[0]][e[1]] not in self.attacked_ids]
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(1333, lambda el = ents_list, t = id : self.do_attack(el, t)) # EXIT THROUGH ATTACK
            else:
                self.ai_end_turn(ents_list)
        else:
            root.after(1666, lambda el = ents_list : self.ai_finish_turn(ents_list))
        
        
class Tomb(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {}
        self.attack_used = False
        self.str = 1
        self.agl = 1
        self.end = 5
        self.dodge = 1
        self.psyche = 5
        self.spirit = 20
        self.move_range = 0
        self.move_type = 'immobile'
        super().__init__(name, img, loc, owner, number)
        
# lvl 2 gains spellcasting/alchemy/psyche
# add actions: Tracer bolt, doubling cube, flash grenade
class Trickster(Summon):
    def __init__(self, name, img, loc, owner, number, level):
        if level == 1:
            self.actions = {'Move':self.move, 'Pyrotechnics':self.pyrotechnics, 'Simulacrum':self.simulacrum,'Gate':self.gate, 'Mortar':self.mortar}
            self.attack_used = False
            self.str = 2
            self.agl = 4
            self.end = 2
            self.dodge = 5
            self.psyche = 5
            self.spirit = 13
            self.move_range = 4
            self.level = level
        elif level == 2:
            self.actions = {'Move':self.move, 'Pyrotechnics':self.pyrotechnics, 'Simulacrum':self.simulacrum,'Gate':self.gate, 'Mortar':self.mortar, 'Tracer Grenade':self.tracer_grenade, 'Doubling Cube':self.doubling_cube}
            self.attack_used = False
            self.str = 2
            self.agl = 5
            self.end = 2
            self.dodge = 6
            self.psyche = 7
            self.spirit = 16
            self.move_range = 4
            self.level = level
        self.move_type = 'teleport'
        self.weak = ['crushing', 'slashing']
        self.resist = ['piercing', 'explosive', 'fire']
        super().__init__(name, img, loc, owner, number)


    def doubling_cube(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_doubling_cube)
        sqrs = [c for c in app.coords if dist(self.loc, c) <= 3]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_doubling_cube(event = e, sqr = sqr, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Confirm Doubling Cube Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_doubling_cube(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_doubling_cube(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.action_target_ents().keys():
            return
#         if not isinstance(app.ent_dict[id], (Trickster, Warrior, Plaguebearer, Shadow)):
#              return
        self.attack_used = True
#         self.init_attack_anims()
#         effect1 = mixer.Sound('Sound_Effects/aura.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        ents = [k for k,v in app.all_ents().items() if dist(v.loc, sqr) <= 2 and v.owner == self.owner]
        app.get_focus(choice(ents))
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Doubling Cube', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Doubling Cube', justify = 'center', fill = 'ivory', font = ('Andale Mono', 16), tags = 'text')
        app.vis_dict['Doubling_Cube'] = Vis(name = 'Doubling_Cube', loc = self.loc[:])
        app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Doubling_Cube'].img, tags = 'Doubling_Cube')
        def cleanup_doubling_cube_vis():
            del app.vis_dict['Doubling_Cube']
            app.canvas.delete('Doubling_Cube')
        root.after(999, cleanup_doubling_cube_vis)
        for id in ents:
            if 'Doubling_Cube' not in app.ent_dict[id].effects_dict.keys():
                def cube_effect(atkr, dfndr, amt ,type):
                    if amt < 0 and (type == 'melee' or type == 'ranged'):
                        if atkr.save_check('psyche', mod = -1) == False:
                            app.canvas.create_text(dfndr.loc[0]*100+49-app.moved_right, dfndr.loc[1]*100+94-app.moved_down, text = 'Double absorbs spirit...', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
                            app.canvas.create_text(dfndr.loc[0]*100+50-app.moved_right, dfndr.loc[1]*100+95-app.moved_down, text = 'Double absorbs spirit...', font = ('Andale Mono', 14), fill = 'lightcyan', tags = 'text')
                            root.after(1888, lambda t = 'text' : app.canvas.delete(t))
                            return (amt//2, 1666)
                        else:
                            app.canvas.create_text(atkr.loc[0]*100+49-app.moved_right, atkr.loc[1]*100+94-app.moved_down, text = 'Psyche Save...', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
                            app.canvas.create_text(atkr.loc[0]*100+50-app.moved_right, atkr.loc[1]*100+95-app.moved_down, text = 'Psyche Save...', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
                            root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                            return (amt, 1666)
                    else:
                        return (amt, 0)
                p = partial(cube_effect)
                app.ent_dict[id].defense_effects.append(p)
                # make undo and effect
                def undo(id, p):
                    app.ent_dict[id].defense_effects.remove(p)
                u = partial(undo, id, p)
                app.ent_dict[id].effects_dict['Doubling_Cube'] = Effect(name = 'Doubling_Cube', undo_func = u, duration = 6, level = 5)
                un = 'Cube'+str(app.effects_counter)
                app.effects_counter+=1
                start_loc = app.ent_dict[id].loc[:]
                tag = id
                app.vis_dict[un] = Vis(name = 'Double', loc = start_loc[:])
                app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = ('Double','left'+tag))
                app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = ('Double','right'+tag))
                app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = ('Double','right'+tag))
                app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = ('Double','left'+tag))
    #             app.canvas.create_text(start_loc[0]*100+49-app.moved_right, start_loc[1]*100+94-app.moved_down, text = 'Doubled...', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
    #             app.canvas.create_text(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+95-app.moved_down, text = 'Doubled...', font = ('Andale Mono', 14), fill = 'lightcyan', tags = 'text')
                x = start_loc[0]*100+50-app.moved_right
                y = start_loc[1]*100+50-app.moved_down
                end_left = start_loc[0]*100-app.moved_right # minus 50 from center
                end_right = start_loc[0]*100+100-app.moved_right # plus 50 from center
                selected_vis = [un]
                def simulacrum_loop_left(vis, x, y, end_left, tar):
                    if x % 5 == 0: # this just gets new image (flickers simulacrum opacity)
                        app.vis_dict[vis].rotate_image()
                        app.canvas.delete('left'+tar) # this deletes both vis left and right
                        app.canvas.create_image(x, y, image = app.ent_dict[tar].img, tags = ('Double','left'+tar))
                        app.canvas.create_image(x, y, image = app.vis_dict[vis].img, tags = ('Double','left'+tar))
                    app.canvas.tag_raise(vis)
                    if x > end_left:
                        x -= 10
                        app.canvas.move('left'+tar,-10,0)
                    if x == end_left:
                        pass
                    else:
                        root.after(100, lambda vis = un, x = x, y = y, end_left = end_left, tar = tar : simulacrum_loop_left(vis, x, y, end_left, tar))
                def simulacrum_loop_right(vis, x, y, end_right, tar, un):
                    if x % 5 == 0: # this just gets new image (flickers simulacrum opacity)
                        app.vis_dict[vis].rotate_image()
                        app.canvas.delete('right'+tar) # this deletes both vis left and right
                        app.canvas.create_image(x, y, image = app.ent_dict[tar].img, tags = ('Double','right'+tar))
                        app.canvas.create_image(x, y, image = app.vis_dict[vis].img, tags = ('Double','right'+tar))
                    app.canvas.tag_raise(vis)
                    if x < end_right:
                        x += 10
                        app.canvas.move('right'+tar,10,0)
                    if x == end_right:
                        root.after(666, lambda un = un :self.cleanup_cube(un))
                    else:
                        root.after(100, lambda vis = un, x = x, y = y, end_right = end_right, tar = tar, un = un : simulacrum_loop_right(vis, x, y, end_right, tar, un))
                simulacrum_loop_left(un, x, y, end_left, id)
                simulacrum_loop_right(un, x, y, end_right, id, un)
        root.after(1666, self.finish_doubling_cube)
        
    def cleanup_cube(self, un):
        del app.vis_dict[un]
        app.canvas.delete(un)
        
        
    def finish_doubling_cube(self, event = None):
#         self.init_normal_anims()
        try:
            app.canvas.delete('Double')
        except:
            pass
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)


    def tracer_grenade(self, event = None):
        if self.attack_used == True:
            return
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_mortar)
        sqrs = [s for s in app.coords if 6 < dist(self.loc, s) <= 8]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_tracer_grenade(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Location for Grenade', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_tracer_grenade(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_tracer_grenade(self, event, sqr, sqrs):
        global selected_vis
        if sqr not in sqrs:
            return
        effect1 = mixer.Sound('Sound_Effects/mortar.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.vis_dict['Tracer_Grenade'] = Vis(name = 'Tracer_Grenade', loc = self.loc)
        app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Tracer_Grenade'].img, tags = 'Tracer_Grenade')
        selected_vis = ['Tracer_Grenade']
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        endx = sqr[0]*100+50-app.moved_right
        endy = sqr[1]*100+50-app.moved_down
        start_sqr = self.loc[:]
        end_sqr = sqr[:]
        total_distance = abs(x - endx) + abs(y - endy)
        tic = total_distance/9 # Magic Number debug, number of images for vis
        if x == endx:
            xstep = 0
            ystep = 10
        elif y == endy:
            xstep = 10
            ystep = 0
        else:
            slope = Fraction(abs(x - endx), abs(y - endy))
            # needs to be moving at least 10 pixels, xstep + ystep >= 10
            xstep = slope.numerator
            ystep = slope.denominator
            while xstep + ystep < 10:
                xstep *= 2
                ystep *= 2
        # need to call rotate_image every tic
        def mortar_arc(x, y, endx, endy, start_sqr, end_sqr, acm, tic, xstep, ystep):
            if acm >= tic:
                acm = 0
                app.vis_dict['Tracer_Grenade'].rotate_image()
                app.canvas.delete('Tracer_Grenade')
                app.canvas.create_image(x, y, image = app.vis_dict['Tracer_Grenade'].img, tags = 'Tracer_Grenade')
            if x > endx:
                acm += xstep
                x -= xstep
                app.canvas.delete('Tracer_Grenade')
                app.canvas.create_image(x, y, image = app.vis_dict['Tracer_Grenade'].img, tags = 'Tracer_Grenade')
                app.canvas.tag_raise('Tracer_Grenade')
            elif x < endx:
                acm += xstep
                x += xstep
                app.canvas.delete('Tracer_Grenade')
                app.canvas.create_image(x, y, image = app.vis_dict['Tracer_Grenade'].img, tags = 'Tracer_Grenade')
                app.canvas.tag_raise('Tracer_Grenade')
            if y > endy:
                acm += ystep
                y -= ystep
                app.canvas.delete('Tracer_Grenade')
                app.canvas.create_image(x, y, image = app.vis_dict['Tracer_Grenade'].img, tags = 'Tracer_Grenade')
                app.canvas.tag_raise('Tracer_Grenade')
            elif y < endy:
                acm += ystep
                y += ystep
                app.canvas.delete('Tracer_Grenade')
                app.canvas.create_image(x, y, image = app.vis_dict['Tracer_Grenade'].img, tags = 'Tracer_Grenade')
                app.canvas.tag_raise('Tracer_Grenade')
            if abs(x - endx) < 13 and abs(y - endy) < 13:
                self.continue_tracer_grenade(end_sqr)
            else: # CONTINUE LOOP
                root.after(66, lambda x = x, y = y, e = endx, e2 = endy, s = start_sqr, s2 = end_sqr, acm = acm, tic = tic, xs = xstep, ys = ystep : mortar_arc(x, y, e, e2, s, s2, acm, tic, xs, ys))
        mortar_arc(x, y, endx, endy, start_sqr, end_sqr, tic+1, tic, xstep, ystep)
        
        
    def continue_tracer_grenade(self, sqr):
        global selected_vis
        app.canvas.delete('text')
        del app.vis_dict['Tracer_Grenade']
        app.canvas.delete('Tracer_Grenade')
        selected_vis = []
#         effect1 = mixer.Sound('Sound_Effects/tracer_explosion.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.vis_dict['Tracer_Exploded'] = Vis(name = 'Tracer_Exploded', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Tracer_Exploded'].img, tags = 'Tracer_Exploded')
        def cleanup_explode():
            del app.vis_dict['Tracer_Exploded']
            app.canvas.delete('Tracer_Exploded')
        root.after(999, cleanup_explode)
        ents = [k for k,v in app.all_ents().items() if dist(v.loc, sqr) <= 2]
        # mortar loop
        def mortar_loop(ents):
            if ents == []:
                self.cleanup_mortar()
            else:
                id = ents[0]
                ents = ents[1:]
                n = 'Traced' + str(app.effects_counter)
                app.effects_counter += 1
                loc = app.ent_dict[id].loc[:]
#                 root.after(13,lambda loc = loc : app.focus_square(loc))
                app.focus_square(loc)
#                 app.focus_square(loc)
                app.vis_dict[n] = Vis(name = 'Traced', loc = loc)
                def cleanup_vis(name):
                    app.canvas.delete('text')
                    del app.vis_dict[name]
                    app.canvas.delete(name)
                app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = n)
                if 'Tracer_Grenade' not in app.ent_dict[id].effects_dict.keys():
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Traced...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Traced...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    def tracer_effect(stat):
                        stat -= 2
                        if stat < 1:
                            return 1
                        else:
                            return stat
                    p = partial(tracer_effect)
                    app.ent_dict[id].dodge_effects.append(p)
                    def undo(id, p):
                        app.ent_dict[id].dodge_effects.remove(p)
                    u = partial(undo, id, p)
                    app.ent_dict[id].effects_dict['Tracer_Grenade'] = Effect(name = 'Tracer_Grenade', undo_func = u, duration = 6, level = 5)
                    root.after(1666, lambda n = n : cleanup_vis(n))
                    root.after(1777, lambda ents = ents : mortar_loop(ents))
                else:
                    cleanup_vis(n)
                    mortar_loop(ents)
        mortar_loop(ents)
        
    def cleanup_tracer_grenade(self, event = None):
        app.depop_context(event = None)
        app.cleanup_squares()
        app.canvas.delete('text')
#         app.unbind_all()
        app.rebind_all()



    def mortar(self, event = None):
        if self.attack_used == True:
            return
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_mortar)
        sqrs = [s for s in app.coords if 6 < dist(self.loc, s) <= 8]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_mortar(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Location for Mortar', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_mortar(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_mortar(self, event, sqr, sqrs):
        global selected_vis
        if sqr not in sqrs:
            return
        effect1 = mixer.Sound('Sound_Effects/mortar.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.vis_dict['Mortar'] = Vis(name = 'Mortar', loc = self.loc)
        app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Mortar'].img, tags = 'Mortar')
        selected_vis = ['Mortar']
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        endx = sqr[0]*100+50-app.moved_right
        endy = sqr[1]*100+50-app.moved_down
        start_sqr = self.loc[:]
        end_sqr = sqr[:]
        total_distance = abs(x - endx) + abs(y - endy)
        tic = total_distance/9 # Magic Number debug, number of images for vis
        if x == endx:
            xstep = 0
            ystep = 10
        elif y == endy:
            xstep = 10
            ystep = 0
        else:
            slope = Fraction(abs(x - endx), abs(y - endy))
            # needs to be moving at least 10 pixels, xstep + ystep >= 10
            xstep = slope.numerator
            ystep = slope.denominator
            while xstep + ystep < 10:
                xstep *= 2
                ystep *= 2
        # need to call rotate_image every tic
        def mortar_arc(x, y, endx, endy, start_sqr, end_sqr, acm, tic, xstep, ystep):
            if acm >= tic:
                acm = 0
                app.vis_dict['Mortar'].rotate_image()
                app.canvas.delete('Mortar')
                app.canvas.create_image(x, y, image = app.vis_dict['Mortar'].img, tags = 'Mortar')
            if x > endx:
                acm += xstep
                x -= xstep
                app.canvas.delete('Mortar')
                app.canvas.create_image(x, y, image = app.vis_dict['Mortar'].img, tags = 'Mortar')
                app.canvas.tag_raise('Mortar')
            elif x < endx:
                acm += xstep
                x += xstep
                app.canvas.delete('Mortar')
                app.canvas.create_image(x, y, image = app.vis_dict['Mortar'].img, tags = 'Mortar')
                app.canvas.tag_raise('Mortar')
            if y > endy:
                acm += ystep
                y -= ystep
                app.canvas.delete('Mortar')
                app.canvas.create_image(x, y, image = app.vis_dict['Mortar'].img, tags = 'Mortar')
                app.canvas.tag_raise('Mortar')
            elif y < endy:
                acm += ystep
                y += ystep
                app.canvas.delete('Mortar')
                app.canvas.create_image(x, y, image = app.vis_dict['Mortar'].img, tags = 'Mortar')
                app.canvas.tag_raise('Mortar')
            if abs(x - endx) < 13 and abs(y - endy) < 13:
                self.continue_mortar(end_sqr)
            else: # CONTINUE LOOP
                root.after(66, lambda x = x, y = y, e = endx, e2 = endy, s = start_sqr, s2 = end_sqr, acm = acm, tic = tic, xs = xstep, ys = ystep : mortar_arc(x, y, e, e2, s, s2, acm, tic, xs, ys))
        mortar_arc(x, y, endx, endy, start_sqr, end_sqr, tic+1, tic, xstep, ystep)
        
        
    def continue_mortar(self, sqr):
        global selected_vis
        app.canvas.delete('text')
        del app.vis_dict['Mortar']
        app.canvas.delete('Mortar')
        selected_vis = []
        effect1 = mixer.Sound('Sound_Effects/fuse_explosion.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.vis_dict['Mortar_Exploded'] = Vis(name = 'Mortar_Exploded', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Mortar_Exploded'].img, tags = 'Mortar_Exploded')
        def cleanup_explode():
            del app.vis_dict['Mortar_Exploded']
            app.canvas.delete('Mortar_Exploded')
        root.after(999, cleanup_explode)
        ents = [k for k,v in app.all_ents().items() if dist(v.loc, sqr) <= 2]
        # mortar loop
        def mortar_loop(ents):
            if ents == []:
                self.cleanup_mortar()
            else:
                id = ents[0]
                ents = ents[1:]
                n = 'Pain_Explode' + str(app.effects_counter)
                app.effects_counter += 1
                loc = app.ent_dict[id].loc[:]
#                 root.after(13,lambda loc = loc : app.focus_square(loc))
                app.focus_square(loc)
#                 app.focus_square(loc)
                app.vis_dict[n] = Vis(name = 'Pain_Explode', loc = loc)
                def cleanup_vis(name):
                    app.canvas.delete('text')
                    del app.vis_dict[name]
                    app.canvas.delete(name)
                app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = n)
                if app.ent_dict[id].save_check('dodge', mod = -2) == False: # Fail Save
                    d = choice([1,2,3])
#                     pre = app.ent_dict[id].spirit
                    root.after(1666, lambda name = n : cleanup_vis(name))
                    lock(apply_damage, self, app.ent_dict[id], -d, 'explosive', 'Mortar')
#                     post = app.ent_dict[id].spirit
#                     d = pre - post
#                     app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
#                     app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
# #                     name = 'dethlok'+str(app.death_count)
# #                     app.death_count += 1
# #                     app.dethloks[name] = tk.IntVar(0)
# #                     root.wait_variable(app.dethloks[name])
#                     if app.ent_dict[id].spirit <= 0:
#                         app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
#                         app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
#                         name = 'dethlok'+str(app.death_count)
#                         app.death_count += 1
#                         app.dethloks[name] = tk.IntVar(0)
#                         root.after(2666, lambda n = n : cleanup_vis(n))
#                         root.after(2777, lambda id = id, name = name : app.kill(id, name))
#                         root.wait_variable(app.dethloks[name])
                    mortar_loop(ents)
#                     else:
#                         root.after(1666, lambda n = n : cleanup_vis(n))
#                         root.after(1777, lambda ents = ents : mortar_loop(ents))
                else: # Save
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Dodge Save!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Dodge Save!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    root.after(1666, lambda n = n : cleanup_vis(n))
                    root.after(1777, lambda ents = ents : mortar_loop(ents))
        mortar_loop(ents)
        
    def cleanup_mortar(self, event = None):
        app.depop_context(event = None)
        app.cleanup_squares()
        app.canvas.delete('text')
#         app.unbind_all()
        app.rebind_all()
        
    def pyrotechnics(self, event = None):
        if self.attack_used == True:
            return
        app.unbind_nonarrows()
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_pyrotechnics)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 3]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_pyrotechnics(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Pyrotechnics', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_pyrotechnics(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_pyrotechnics(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.action_target_ents().keys():
            return
        app.unbind_all()
        effect1 = mixer.Sound('Sound_Effects/pyrotechnics.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.vis_dict['Pyrotechnics'] = Vis(name = 'Pyrotechnics', loc = sqr[:])
        vis = app.vis_dict['Pyrotechnics']
#         pre = app.ent_dict[id].spirit
        lock(apply_damage, self, app.ent_dict[id], -2, 'explosive', 'Pyrotechnics')
        root.after(1999, lambda e = None, id = id : self.cleanup_pyrotechnics(event = e, id = id))
#         post = app.ent_dict[id].spirit
#         d = pre - post
#         app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Pyrotechnics')
#         app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = str(d)+' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
#         app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = str(d)+' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
#         if app.ent_dict[id].spirit <= 0:
#             app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
#             app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
        
    def cleanup_pyrotechnics(self, event = None, id = None):
        try: 
            del app.vis_dict['Pyrotechnics']
            app.canvas.delete('Pyrotechnics')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        app.canvas.delete('text')
        if id:
            if app.ent_dict[id].spirit <= 0:
                lock(app.kill, id)
#                 name = 'Dethlok'+str(app.death_count)
#                 app.death_count += 1
#                 app.dethloks[name] = tk.IntVar(0)
#                 root.after(666, lambda id = id, name = name : app.kill(id, name))
#                 app.wait_variable(app.dethloks[name])
#         app.unbind_all()
        app.rebind_all()
        
        
    def simulacrum(self, event = None):
        if self.attack_used == True:
            return
        app.depop_context(event = None)
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_simulacrum)
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_simulacrum(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Simulacrum', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_simulacrum(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_simulacrum(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        # target must be Summon, Witch, (future type...)
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        if not isinstance(app.ent_dict[id], (Witch, Summon)):
             return
        # PREVENT STACKING OF SIMULACRUM
        if 'Simulacrum' in app.ent_dict[id].effects_dict.keys():
            return
        app.unbind_all()
        effect1 = mixer.Sound('Sound_Effects/simulacrum.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        # DO SIMULACRUM EFFECTS
        def simulacrum_effect(stat):
            stat += 3
            return stat
        f = simulacrum_effect
        app.ent_dict[id].agl_effects.append(f)
        app.ent_dict[id].dodge_effects.append(f)
        def un(i):
            app.ent_dict[i].agl_effects.remove(simulacrum_effect)
            app.ent_dict[i].dodge_effects.remove(simulacrum_effect)
            return None
        p = partial(un, id)
        n = 'Simulacrum' + str(app.effects_counter)
        app.ent_dict[id].effects_dict['Simulacrum'] = Effect(name = 'Simulacrum', undo_func = p, duration = 3, level = 4)
        # DO SIMULACRUM VISUALS
        start_loc = app.ent_dict[id].loc[:]
        app.vis_dict['Simulacrum'] = Vis(name = 'Simulacrum', loc = start_loc[:])
        app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = 'left')
        app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = 'right')
        app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.vis_dict['Simulacrum'].img, tags = ('Simulacrum','right'))
        app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.vis_dict['Simulacrum'].img, tags = ('Simulacrum','left'))
        app.canvas.create_text(start_loc[0]*100+49-app.moved_right, start_loc[1]*100+94-app.moved_down, text = 'Simulacrum', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+95-app.moved_down, text = 'Simulacrum', font = ('Andale Mono', 14), fill = 'lightcyan', tags = 'text')
        x = start_loc[0]*100+50-app.moved_right
        y = start_loc[1]*100+50-app.moved_down
        end_left = start_loc[0]*100-app.moved_right # minus 50 from center
        end_right = start_loc[0]*100+100-app.moved_right # plus 50 from center
        selected_vis = ['Simulacrum']
        def simulacrum_loop_left(vis, x, y, end_left, tar):
            if x % 5 == 0: # this just gets new image (flickers simulacrum opacity)
                app.vis_dict[vis].rotate_image()
                app.canvas.delete('left') # this deletes both vis left and right
                app.canvas.create_image(x, y, image = app.ent_dict[tar].img, tags = 'left')
                app.canvas.create_image(x, y, image = app.vis_dict[vis].img, tags = ('Simulacrum','left'))
            app.canvas.tag_raise(vis)
            if x > end_left:
                x -= 10
                app.canvas.move('left',-10,0)
            if x == end_left:
                pass
            else:
                root.after(100, lambda vis = 'Simulacrum', x = x, y = y, end_left = end_left, tar = tar : simulacrum_loop_left(vis, x, y, end_left, tar))
        def simulacrum_loop_right(vis, x, y, end_right, tar):
            if x % 5 == 0: # this just gets new image (flickers simulacrum opacity)
                app.vis_dict[vis].rotate_image()
                app.canvas.delete('right') # this deletes both vis left and right
                app.canvas.create_image(x, y, image = app.ent_dict[tar].img, tags = 'right')
                app.canvas.create_image(x, y, image = app.vis_dict[vis].img, tags = ('Simulacrum','right'))
            app.canvas.tag_raise(vis)
            if x < end_right:
                x += 10
                app.canvas.move('right',10,0)
            if x == end_right:
                root.after(666, self.cleanup_simulacrum)
            else:
                root.after(100, lambda vis = 'Simulacrum', x = x, y = y, end_right = end_right, tar = tar : simulacrum_loop_right(vis, x, y, end_right, tar))
        simulacrum_loop_left('Simulacrum', x, y, end_left, id)
        simulacrum_loop_right('Simulacrum', x, y, end_right, id)
        
        
    def cleanup_simulacrum(self, event = None):
#         app.unbind_all()
        app.rebind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        app.canvas.delete('left')
        app.canvas.delete('right')
        try: 
            del app.vis_dict['Simulacrum']
            app.canvas.delete('Simulacrum')
        except: pass
        app.canvas.delete('text')
        
        
    def gate(self, event = None):
        if self.attack_used == True:# or self.magick < 3:
            return
#         root.unbind('<q>')
#         root.unbind('<a>')
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_gate)
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 2:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.choose_target(e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.choose_target(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
        
    def choose_target(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        if app.ent_dict[id].immovable == True:
            return
        app.depop_context(event = None)
        app.unbind_all()
        app.rebind_arrows()
        root.bind('<q>', self.cleanup_gate)
        distance = 5
        app.cleanup_squares()
        sqrs = self.doorway_squares(distance)
        if sqrs == []:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+59-app.moved_down, text = 'No Available Area', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+60-app.moved_down, text = 'No Available Area', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
            root.after(999, self.cleanup_gate)
        else:
            app.animate_squares(sqrs)
            root.bind('<a>', lambda e, id = id, sqr = grid_pos, sqrs = sqrs : self.do_gate(e, id = id, sqr = sqr, sqrs = sqrs))
            b = tk.Button(app.context_menu, text = 'Choose Location', font = ('chalkduster', 24), fg = 'tan3', wraplength = 190, highlightbackground = 'tan3', command = lambda e = None, id = id, sqr = grid_pos, sqrs = sqrs : self.do_gate(e, id, sqr, sqrs))
            b.pack(side = 'top')
            app.context_buttons.append(b)
    
    def do_gate(self, event = None, id = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        self.attack_used = True
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        effect1 = mixer.Sound('Sound_Effects/gate.ogg')
        effect1.set_volume(.4)
        sound_effects.play(effect1, 0)
        oldloc = app.ent_dict[id].loc[:]
        newloc = sqr[:]
        app.vis_dict['Gate'] = Vis(name = 'Gate', loc = oldloc[:])
        vis = app.vis_dict['Gate']
        app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Gateway')
        root.after(1666, lambda newloc = newloc, id = id : self.finish_gate(newloc, id))
        
    def finish_gate(self, newloc, id):
        app.grid[app.ent_dict[id].loc[0]][app.ent_dict[id].loc[1]] = ''
        app.canvas.delete(id)
        app.ent_dict[id].loc = newloc[:]
        app.grid[newloc[0]][newloc[1]] = id
        try: 
            del app.vis_dict['Gate']
            app.canvas.delete('Gate')
        except: pass
        app.vis_dict['Gate'] = Vis(name = 'Gate', loc = newloc[:])
        vis = app.vis_dict['Gate']
        root.after(1666, lambda id = id, newloc = newloc : self.place_entity(id, newloc))
        
    def place_entity(self, id, newloc):
        del app.vis_dict['Gate']
        app.canvas.delete('Gate')
        app.canvas.create_image(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = app.ent_dict[id].tags)
        try: app.canvas.tag_lower((app.ent_dict[id].tags), 'large')
        except: pass
        app.canvas.tag_lower((app.ent_dict[id].tags), 'maptop')
        root.after(666, self.cleanup_gate)
    
    def doorway_squares(self, distance):
        sqr_list = []
        for c in app.coords:
            if dist(c, self.loc) <= distance: 
                if app.grid[c[0]][c[1]] == '':
                    sqr_list.append(c)
        return sqr_list
    
    def cleanup_gate(self, event = None):
        try:
            del app.vis_dict['Gate']
            app.canvas.delete('Gate')
        except: pass
        app.canvas.delete('text')
        app.depop_context(event = None)
        app.cleanup_squares()
        app.rebind_all()
    
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        

# lvl 2 wolf gains more phys stats and melee/range atks, lvl 2 shadow gains more disruptive/buff spells
# wolf: darkblast, teeth, stalk
# mist: warpfire, possession, chaos warp
class Shadow(Summon):
    def __init__(self, name, img, loc, owner, number, level):
        if level == 1:
            self.actions = {'Move':self.move, 'Shadow Strike':self.shadow_strike, 'Dark Shroud':self.dark_shroud, 'Phase Shift':self.phase_shift}
            self.attack_used = False
            self.str = 3
            self.agl = 6
            self.end = 4
            self.dodge = 6
            self.psyche = 4
            self.spirit = 15
            self.move_range = 4
            self.level = level
        elif level == 2:
            self.actions = {'Move':self.move, 'Shadow Strike':self.shadow_strike, 'Dark Shroud':self.dark_shroud, 'Darkblast':self.darkblast, 'Stalk':self.stalk, 'Phase Shift':self.phase_shift}
            self.attack_used = False
            self.str = 6
            self.agl = 7
            self.end = 4
            self.dodge = 6
            self.psyche = 4
            self.spirit = 26
            self.move_range = 5
            self.level = level
        self.move_type = 'normal'
        self.weak = ['slashing', 'elec']
        self.resist = ['piercing', 'cold']
        self.form = 'shadow_wolf'
        super().__init__(name, img, loc, owner, number)
        
    def init_normal_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        if self.form == 'shadow_wolf':
            anims = [a for r,d,a in walk('./animations/Shadow_Wolf/')][0]
            anims = [a for a in anims[:] if a[-3:] == 'png']
            for i, anim in enumerate(anims):
                a = ImageTk.PhotoImage(Image.open('animations/Shadow_Wolf/' + anim))
                self.anim_dict[i] = a
        elif self.form == 'shadow_mist':
            anims = [a for r,d,a in walk('./animations/Shadow_Mist/')][0]
            anims = [a for a in anims[:] if a[-3:] == 'png']
            for i, anim in enumerate(anims):
                a = ImageTk.PhotoImage(Image.open('animations/Shadow_Mist/' + anim))
                self.anim_dict[i] = a
        
    def phase_shift(self, event = None):
        if self.attack_used == True:
            return
        app.unbind_nonarrows()
        root.bind('<q>', self.cancel_phase_shift)
        sqrs = [self.loc[:]]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e : self.do_phase_shift(e))
        app.depop_context(event = None)
        b = tk.Button(app.context_menu, text = 'Confirm Phase Shift', font = ('chalkduster', 24), fg='tan3', wraplength = 190, highlightbackground = 'tan3', command = lambda e = None : self.do_phase_shift(event = e))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_phase_shift(self, event = None):
        effect1 = mixer.Sound('Sound_Effects/phase_shift.ogg')
        effect1.set_volume(0.5)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        self.attack_used = True
        app.vis_dict['Phase_Shift'] = Vis(name = 'Phase_Shift', loc = self.loc[:])
        vis = app.vis_dict['Phase_Shift']
        app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = vis.img, tags = 'Phase_Shift')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+84, text = 'Phase Shift', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+85, text = 'Phase Shift', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
        # shift from one phase to the other...
        if self.form == 'shadow_wolf':
            if self.level == 1:
                self.form = 'shadow_mist'
                self.str = 2
                self.agl = 3
                self.end = 3
                self.dodge = 6
                self.psyche = 6
                self.move_range = 5
                self.base_str = self.str
                self.base_agl = self.agl
                self.base_end = self.end
                self.base_dodge = self.dodge
                self.base_psyche = self.psyche
                self.base_spirit = 15
                self.move_type = 'teleport'
                self.weak = ['explosive', 'fire', 'cold', 'elec']
                self.resist = ['magick', 'poison', 'slashing', 'piercing', 'crushing']
                self.actions = {'Mist Move':self.teleport_move, 'Drain Life':self.drain_life, 'Muddle':self.muddle, 'Phase Shift':self.phase_shift}
                def legal_moves(obj):
                    move_list = []
                    for c in app.coords:
                        if app.grid[c[0]][c[1]] == '':
                            if dist(obj.loc, c) <= self.get_abl('move_range'):
                                move_list.append(c)
                    return move_list
                p = partial(legal_moves, self)
                self.legal_moves = p
            elif self.level == 2:
                self.form = 'shadow_mist'
                self.str = 2
                self.agl = 3
                self.end = 3
                self.dodge = 6
                self.psyche = 6
                self.base_str = self.str
                self.base_agl = self.agl
                self.base_end = self.end
                self.base_dodge = self.dodge
                self.base_psyche = self.psyche
                self.base_spirit = 26
                self.move_range = 6
                self.move_type = 'teleport'
                self.weak = ['explosive', 'fire', 'cold', 'elec']
                self.resist = ['magick', 'poison', 'slashing', 'piercing', 'crushing']
                self.actions = {'Mist Move':self.teleport_move, 'Drain Life':self.drain_life, 'Muddle':self.muddle, 'Phase Shift':self.phase_shift, 'Warpfire':self.warpfire, 'Tendrils of Chaos':self.tendrils_of_chaos}
                def legal_moves(obj):
                    move_list = []
                    for c in app.coords:
                        if app.grid[c[0]][c[1]] == '':
                            if dist(obj.loc, c) <= self.get_abl('move_range'):
                                move_list.append(c)
                    return move_list
                p = partial(legal_moves, self)
                self.legal_moves = p
        elif self.form == 'shadow_mist':
            if self.level == 1:
                self.form = 'shadow_wolf'
                self.str = 3
                self.agl = 6
                self.end = 4
                self.dodge = 6
                self.psyche = 4
                self.base_str = self.str
                self.base_agl = self.agl
                self.base_end = self.end
                self.base_dodge = self.dodge
                self.base_psyche = self.psyche
                self.base_spirit = 15
                self.move_range = 4
                self.move_type = 'normal'
                self.weak = ['slashing', 'elec']
                self.resist = ['piercing', 'cold']
                self.actions = {'Move':self.move, 'Shadow Strike':self.shadow_strike, 'Dark Shroud':self.dark_shroud, 'Phase Shift':self.phase_shift}
                def legal_moves(obj):
                    loc = obj.loc[:]
                    mvlist = []
                    sqr_cost_map = {}
                    def findall(loc, start, distance):
                        if start > distance:
                            return
                        adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
                        for s in adj:
                            if tuple(s) in sqr_cost_map:
                                if sqr_cost_map[tuple(s)] < start:
                                    continue
                            sqr_cost_map[tuple(s)] = start
                            if s not in mvlist:
                                mvlist.append(s)
                            findall(s, start+1, distance)
                    findall(loc, 1, self.get_abl('move_range'))
                    return mvlist
                p = partial(legal_moves, self)
                self.legal_moves = p
            elif self.level == 2:
                self.form = 'shadow_wolf'
                self.str = 6
                self.agl = 7
                self.end = 4
                self.dodge = 6
                self.psyche = 4
                self.spirit = 26
                self.base_str = self.str
                self.base_agl = self.agl
                self.base_end = self.end
                self.base_dodge = self.dodge
                self.base_psyche = self.psyche
                self.base_spirit = 26
                self.move_range = 5
                self.move_type = 'normal'
                self.weak = ['slashing', 'elec']
                self.resist = ['piercing', 'cold']
                self.actions = {'Move':self.move, 'Shadow Strike':self.shadow_strike, 'Dark Shroud':self.dark_shroud, 'Phase Shift':self.phase_shift, 'Darkblast':self.darkblast, 'Stalk':self.stalk}
                def legal_moves(obj):
                    loc = obj.loc[:]
                    mvlist = []
                    sqr_cost_map = {}
                    def findall(loc, start, distance):
                        if start > distance:
                            return
                        adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
                        for s in adj:
                            if tuple(s) in sqr_cost_map:
                                if sqr_cost_map[tuple(s)] < start:
                                    continue
                            sqr_cost_map[tuple(s)] = start
                            if s not in mvlist:
                                mvlist.append(s)
                            findall(s, start+1, distance)
                    findall(loc, 1, self.get_abl('move_range'))
                    return mvlist
                p = partial(legal_moves, self)
                self.legal_moves = p
        self.init_normal_anims()
        root.after(2333, self.cancel_phase_shift)
        
    def cancel_phase_shift(self, event = None):
        try:
            app.canvas.delete('text')
            del app.vis_dict['Phase_Shift']
            app.canvas.delete('Phase_Shift')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        app.rebind_all()
        
        
    def tendrils_of_chaos(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_tendrils_of_chaos)
        sqrs = [c for c in app.coords if 2 <= dist(self.loc,c) <= 6]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_tendrils_of_chaos(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Choose Target Tendrils of Chaos', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos[:], sqrs = sqrs : self.do_baleful_stare(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_tendrils_of_chaos(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        if app.grid[sqr[0]][sqr[1]] == '' or app.grid[sqr[0]][sqr[1]] == 'block':
            return
        id = app.grid[sqr[0]][sqr[1]]
#         self.init_attack_anims()
#         effect1 = mixer.Sound('Sound_Effects/tendrils_of_chaos.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        self.attack_used = True
        visloc = app.ent_dict[id].loc[:]
        app.vis_dict['Tendrils_of_Chaos'] = Vis(name = 'Tendrils_of_Chaos', loc = visloc)
        app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Tendrils_of_Chaos'].img, tags = 'Tendrils_of_Chaos')
        my_psyche = self.get_abl('psyche')
        target_agl = app.ent_dict[id].get_abl('agl')
        if to_hit(my_psyche, target_agl) == True and 'Tendrils_Move' not in [ef.name for k,ef in app.ent_dict[id].effects_dict.items()]:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+74-app.moved_down, text = 'Move Reduced...', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Move Reduced...', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            def tendrils_move(move_range):
                if move_range < 2:
                    return move_range
                else:
                    return move_range-1
            app.ent_dict[id].move_effects.append(tendrils_move)
            def un(i):
                app.ent_dict[i].move_effects.remove(tendrils_move)
                return None
            p = partial(un, id)
            n = 'Tendrils_Move' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Tendrils_Move', undo_func = p, duration = 5, level = 6)
        # -1 rand non-str stat, cumulative
        target_str = app.ent_dict[id].get_abl('str')
        if to_hit(my_psyche, target_str) == True:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+94-app.moved_down, text = '-1 random stat...', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+95-app.moved_down, text = '-1 random stat...', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            def tendrils_effect(stat):
                stat -= 1
                if stat < 1:
                    return 1
                else:
                    return stat
            f = tendrils_effect
            any = choice(range(1,5))
            if any == 1:
                app.ent_dict[id].str_effects.append(f)
                ef_type = 'psyche'
            elif any == 2:
                app.ent_dict[id].end_effects.append(f)
                ef_type = 'end'
            elif any == 3:
                app.ent_dict[id].agl_effects.append(f)
                ef_type = 'agl'
            elif any == 4:
                app.ent_dict[id].dodge_effects.append(f)
                ef_type = 'dodge'
            def un(i, ef_type):
                if ef_type == 'str':
                    app.ent_dict[i].str_effects.remove(tendrils_effect)
                elif ef_type == 'end':
                    app.ent_dict[i].end_effects.remove(tendrils_effect)
                elif ef_type == 'agl':
                    app.ent_dict[i].agl_effects.remove(tendrils_effect)
                elif ef_type == 'dodge':
                    app.ent_dict[i].dodge_effects.remove(tendrils_effect)
                elif ef_type == 'psyche':
                    app.ent_dict[i].psyche_effects.remove(tendrils_effect)
                return None
            p_undo = partial(un, id, ef_type)
            n = 'Tendrils_Drain' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Tendrils_Drain', undo_func = p_undo, duration = 5, level = 6)
        root.after(2666, lambda e = None : self.finish_tendrils_of_chaos(event = e))
        
    def finish_tendrils_of_chaos(self, event = None):
#         self.init_normal_anims()
        app.rebind_all()
        app.canvas.delete('text')
        try: 
            del app.vis_dict['Tendrils_of_Chaos']
            app.canvas.delete('Tendrils_of_Chaos')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        
    def warpfire(self, event = None):
#         loc_effects = [v.name for k,v in app.loc_effects_dict.items()]
#         if 'Warpfire' in loc_effects:
#             return
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.cleanup_warpfire)
        sqrs = []
        for c in app.coords:
            if 2 < dist(self.loc, c) <= 7:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_warpfire(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Choose Warpfire Location', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_warpfire(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_warpfire(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        if 'Warpfire'+self.number in [k for k,v in app.loc_effects_dict[tuple(sqr)].effects_dict.items()]:
            return
        if 'Warpfire' in [v.name for c in app.coords for k,v in app.loc_effects_dict[tuple(c)].effects_dict.items()]:
            return
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
#         effect1 = mixer.Sound('Sound_Effects/warpfire.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Warpfire', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Warpfire', font = ('Andale Mono', 14), fill = 'deeppink', tags = 'text')
        un = 'Warpfire' + str(app.effects_counter)
        app.effects_counter += 1
        app.vis_dict[un] = Vis(name = 'Warpfire', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = un)
        def warpfire_effect(s, lockname):
            # first dmg ent at this loc if exists
            ent = [k for k,v in app.ent_dict.items() if v.loc == s]
            if ent != []:
                tar = ent[0]
                app.get_focus(tar)
                lock(apply_damage, self, app.ent_dict[tar], -2, 'fire', 'Warpfire')
                root.after(666, lambda ln = lockname : app.dethloks[ln].set(1))
            else:
                root.after(666, lambda ln = lockname : app.dethloks[ln].set(1))
        sot = partial(warpfire_effect, sqr[:])
        app.loc_effects_dict[tuple(sqr)].sot_effects.append(sot)
        def warp_move(s, lockname):
            app.focus_square(s)
            ents = [k for k,v in app.ent_dict.items() if dist(v.loc,s) <= 3]
            es = [c for c in app.coords if dist(c,s) <= 3 and app.grid[c[0]][c[1]] == '']
            for id in ents:
                if es == []:
                    break
                loc = app.ent_dict[id].loc[:]
                endloc = choice(es)
                es.remove(endloc)
                un = 'Warpfire'+str(app.effects_counter)
                app.effects_counter += 1
                def cleanup_warpfire(n):
                    del app.vis_dict[n]
                    app.canvas.delete(n)
                app.vis_dict[un] = Vis(name = 'Portal', loc = loc[:])
                vis = app.vis_dict[un]
                app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = vis.img, tags = un)
                root.after(1888, lambda n = un : cleanup_warpfire(n))
                app.grid[loc[0]][loc[1]] = ''
                app.canvas.delete(id)
                app.ent_dict[id].loc = endloc[:]
                app.grid[endloc[0]][endloc[1]] = id
                un2 = 'Portal'+str(app.effects_counter)
                app.effects_counter += 1
                app.vis_dict[un2] = Vis(name = 'Portal', loc = endloc[:])
                vis2 = app.vis_dict[un2]
                app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = vis2.img, tags = un2)
                root.after(1888, lambda n = un2 : cleanup_warpfire(n))
                app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = app.ent_dict[id].tags)
                try: app.canvas.tag_lower((app.ent_dict[id].tags), 'large')
                except: pass
                app.canvas.tag_lower((app.ent_dict[id].tags), 'maptop')
            root.after(666, lambda ln = lockname : app.dethloks[ln].set(1))
        sot2 = partial(warp_move, sqr[:])
        app.loc_effects_dict[tuple(sqr)].sot_effects.append(sot2)
        def undo(s, un, p, p2):
            app.loc_effects_dict[tuple(s)].sot_effects.remove(p)
            app.loc_effects_dict[tuple(s)].sot_effects.remove(p2)
            del app.vis_dict[un]
            app.canvas.delete(un)
        u = partial(undo, sqr[:], un, sot, sot2)
        app.loc_effects_dict[tuple(sqr)].effects_dict[un] = Local_Effect(name = 'Warpfire', undo_func = u, sot_func = , duration = 5, level = 7, loc = sqr[:], avoid = 6)
        root.after(1666, self.cleanup_warpfire)
        
    def cleanup_warpfire(self, event = None):
        app.unbind_all()
        app.rebind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        try: app.canvas.delete('text')
        except: pass
        
        
        
        
    def stalk(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_stalk)
        sqrs = [c for c in app.coords if 3 <= dist(self.loc, c) <= 9]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_stalk(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Stalk Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_stalk(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_stalk(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if app.ent_dict[id].owner == self.owner:
            return
        if 'Stalk' in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
            return
#         effect1 = mixer.Sound('Sound_Effects/stalk.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Stalk', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Stalk', justify = 'center', fill = 'gray88', font = ('Andale Mono', 16), tags = 'text')
#         app.vis_dict['Stalk'] = Vis(name = 'Stalk', loc = sqr[:])
#         vis = app.vis_dict['Stalk']
#         app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Stalk')
        # Dodge save, if fail gets def_ef that incr ranged dmg
        if app.ent_dict[id].save_check('dodge', mod = -3) == False: # Fail Save
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Stalked...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Stalked...', justify = 'center', fill = 'gray88', font = ('Andale Mono', 13), tags = 'text')
#             app.vis_dict['Stalk'] = Vis(name = 'Stalk', loc = sqr)
#             app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Stalk'].img, tags = 'Stalk')
            def stalk_effect(atkr, dfndr, amt, type):
                if type == 'ranged' and amt < 0:
                    app.canvas.create_text(dfndr.loc[0]*100-app.moved_right+49, dfndr.loc[1]*100-app.moved_down+49, text = '+2 Stalk', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(dfndr.loc[0]*100-app.moved_right+50, dfndr.loc[1]*100-app.moved_down+50, text = '+2 Stalk', justify = 'center', fill = 'gray88', font = ('Andale Mono', 13), tags = 'text')
                    root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                    return (amt-2, 1666)
                else:
                    return (amt, 0)
            app.ent_dict[id].defense_effects.append(stalk_effect)
            def un(id):
                app.ent_dict[id].defense_effects.remove(stalk_effect)
                return None
            u = partial(un, id)
            n = 'Stalk' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Stalk', undo_func = u, duration = 11, level = 7)
            root.after(2666, self.finish_stalk)
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Dodge Save', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Dodge Save', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, self.finish_stalk)
        
    def finish_stalk(self, event = None):
        try: 
            del app.vis_dict['Stalk']
            app.canvas.delete('Stalk')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        
        
    def darkblast(self, event = None):
        if self.attack_used == True:
            return
        app.unbind_nonarrows()
        root.bind('<q>', self.finish_darkblast)
        sqrs = [c for c in app.coords if 1 <= dist(self.loc, c) <= 5]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_darkblast(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Darkblast Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_darkblast(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_darkblast(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
#         effect1 = mixer.Sound('Sound_Effects/darkblast.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
#         app.vis_dict['Darkblast'] = Vis(name = 'Darkblast', loc = sqr[:])
#         vis = app.vis_dict['Darkblast']
#         app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Darkblast')
        if app.ent_dict[id].owner != self.owner:
            my_agl = self.get_abl('agl')
            tar_dodge = app.ent_dict[id].get_abl('dodge')
            if to_hit(my_agl, tar_dodge) == True:
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                d = d//2
                if d == 0: d = 1
                d += 1
#                 pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Darkblast')
                if id not in app.all_ents().keys():
                    root.after(666, lambda e = None, id = id : self.finish_darkblast(event = e, id = id))
#                 post = app.ent_dict[id].spirit
#                 d = pre - post
#                 app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
#                 app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text') 
#                 if app.ent_dict[id].spirit <= 0:
#                     app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
#                     app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                else:# ent still alive, attempt dispel target effect (must create interface to target) then finish_darkblast
                    app.depop_context(event = None)
                    app.cntxt_info_bg = ImageTk.PhotoImage(Image.open('page.png'))
                    bg = tk.Canvas(app.context_menu, width = 190, height = 363, bg = 'burlywood4', bd=0, relief='raised', highlightthickness=0)
                    bg.pack(side = 'top')
                    bg.create_image(0,0, image = app.cntxt_info_bg, anchor = 'nw')
                    bg.create_text(15, 15, text= 'Choose Effect...', width = 190, anchor = 'nw', font = ('chalkduster', 16), fill = 'indianred')
                    app.context_buttons.append(bg)
                    efs = [(k, v.name) for k,v in app.ent_dict[id].effects_dict.items()]
                    if efs == []:
                        root.after(1666, lambda e = None, id = id : self.finish_darkblast(event = e, id = id))
                    else:
                        for key,name in efs:
    #                         i += 1
    #                         root.bind(str(i), call)
    #                         p = partial(call, None)
                            b = tk.Button(app.context_menu, text = name.replace('_',' '), wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda id = id, ef_name = name, key = key : self.darkblast_dispel(id, ef_name, key))
                            b.pack(side = 'top')
                            app.context_buttons.append(b)
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = None, id = id : self.finish_darkblast(event = e, id = id))
        else:# FRIENDLY ENT, heal 3 then attempt target dispel
            if isinstance(app.ent_dict[id], (Warrior, Trickster, Bard, Plaguebearer)):# heal if summon, else just dispel friendly
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Heal 3 spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Heal 3 spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                apply_heal(self, app.ent_dict[id], 3)
            app.depop_context(event = None)
            app.cntxt_info_bg = ImageTk.PhotoImage(Image.open('page.png'))
            bg = tk.Canvas(app.context_menu, width = 190, height = 363, bg = 'burlywood4', bd=0, relief='raised', highlightthickness=0)
            bg.pack(side = 'top')
            bg.create_image(0,0, image = app.cntxt_info_bg, anchor = 'nw')
            bg.create_text(15, 15, text= 'Choose Effect...', width = 190, anchor = 'nw', font = ('chalkduster', 16), fill = 'indianred')
            app.context_buttons.append(bg)
            efs = [(k, v.name) for k,v in app.ent_dict[id].effects_dict.items()]
            if efs == []:
                root.after(2666, lambda e = None, id = id : self.finish_darkblast(event = e, id = id))
            else:
                for key,name in efs:
    #                         i += 1
    #                         root.bind(str(i), call)
    #                         p = partial(call, None)
                    b = tk.Button(app.context_menu, text = name.replace('_',' '), wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda id = id, ef_name = name, key = key : self.darkblast_dispel(id, ef_name, key))
                    b.pack(side = 'top')
                    app.context_buttons.append(b)
            
    def darkblast_dispel(self, id, ef_name, key):
        app.depop_context(event = None)
        app.canvas.delete('text')
        if app.ent_dict[id].effects_dict[key].dispel(2) == True:
            del app.ent_dict[id].effects_dict[key]
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Dispel '+ef_name.replace('_',' '), justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Dispel '+ef_name.replace('_',' '), justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(1999, lambda id = id : self.finish_darkblast(id = id))
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Dispel failed...'+ef_name.replace('_',' '), justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Dispel failed...'+ef_name.replace('_',' '), justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(1999, lambda id = id : self.finish_darkblast(id = id))
            
            
    def finish_darkblast(self, event = None, id = None):
        try: 
            del app.vis_dict['Darkblast']
            app.canvas.delete('Darkblast')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        if id:
            if app.ent_dict[id].spirit <= 0:
                lock(app.kill, id)
        app.rebind_all()
        
    # all friendly non-shadow wolf summons (war, bar, plagb, trkstr) within range3 of target heal 2, get non-stacking +1 dodge
    def dark_shroud(self, event = None):
        if self.attack_used == True:
            return
        app.unbind_nonarrows()
        root.bind('<q>', self.finish_dark_shroud)
        sqrs = [c for c in app.coords if 1 <= dist(self.loc, c) <= 3]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_dark_shroud(event = e, sqr = sqr, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Choose Target Dark Shroud', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_dark_shroud(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_dark_shroud(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if app.ent_dict[id].owner != self.owner:
            return
        if not isinstance(app.ent_dict[id], (Warrior, Bard, Trickster, Plaguebearer)):
            return
        self.attack_used = True
        effect1 = mixer.Sound('Sound_Effects/dark_shroud.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        app.vis_dict['Dark_Shroud'] = Vis(name = 'Dark_Shroud', loc = self.loc[:])
        app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Dark_Shroud'].img, tags = 'Dark_Shroud')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+84, text = 'Dark Shroud', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+85, text = 'Dark Shroud', justify = 'center', fill = 'thistle1', font = ('Andale Mono', 13), tags = 'text')
        ents = [app.grid[s[0]][s[1]] for s in app.coords if dist(s, sqr) <= 3 and app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
        ents = [e for e in ents if app.ent_dict[e].owner == self.owner]
        ents = [e for e in ents if isinstance(app.ent_dict[e], (Warrior, Bard, Trickster, Plaguebearer))]
        for id in ents:
            s = app.ent_dict[id].loc[:]
            uniq = 'Dark_Shroud'+str(app.effects_counter)
            app.effects_counter += 1
            app.vis_dict[uniq] = Vis(name = 'Dark_Shroud', loc = s)
            app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[uniq].img, tags = 'Dark_Shroud')
            app.canvas.create_text(s[0]*100-app.moved_right+49, s[1]*100-app.moved_down+84, text = '+2 spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(s[0]*100-app.moved_right+50, s[1]*100-app.moved_down+85, text = '+2 spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            # text, heal
            apply_heal(self, app.ent_dict[id], 2)
            # dodge bonus effect if eff does not exist
            ks = [k for k,v in app.ent_dict[id].effects_dict.items() if v.name == 'Dark_Shroud']
            if ks == []:
                app.canvas.create_text(s[0]*100-app.moved_right+49, s[1]*100-app.moved_down+94, text = '+1 dodge', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(s[0]*100-app.moved_right+50, s[1]*100-app.moved_down+95, text = '+1 dodge', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                def dark_shroud_effect(stat):
                    return stat+1
                f = dark_shroud_effect
                app.ent_dict[id].dodge_effects.append(f)
                def un(i, func):
                    app.ent_dict[i].dodge_effects.remove(func)
                    return None
                p = partial(un, id, f)
                n = 'Dark_Shroud' + str(app.effects_counter)
                app.ent_dict[id].effects_dict[n] = Effect(name = 'Dark_Shroud', undo_func = p, duration = 3, level = 3)
        root.after(3333, self.finish_dark_shroud)
            
            
    def finish_dark_shroud(self, event = None):
        try:
            ks = list(app.vis_dict.keys())
            for k in ks:
                if k.startswith('Dark_Shroud') == True:
                    del app.vis_dict[k]
            app.canvas.delete('Dark_Shroud')
        except: pass
        app.cleanup_squares()
#         app.unbind_all()
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)
    
    # psy v psy, psy v psy//2 + 1, range5, heal amnt
    def drain_life(self, event = None):
        if self.attack_used == True:
            return
        app.unbind_nonarrows()
        root.bind('<q>', self.finish_drain_life)
        sqrs = [c for c in app.coords if 2 <= dist(self.loc, c) <= 5]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_drain_life(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Drain Life Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_drain_life(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_drain_life(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
#         effect1 = mixer.Sound('Sound_Effects/drain_life.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.vis_dict['Drain_Life'] = Vis(name = 'Drain_Life', loc = sqr[:])
        vis = app.vis_dict['Drain_Life']
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Drain_Life')
        my_psyche = self.get_abl('psyche')
        tar_psyche = app.ent_dict[id].get_abl('psyche')
        if to_hit(my_psyche, tar_psyche) == True:
            d = damage(my_psyche, tar_psyche)
            d = d//2
            if d == 0: d = 1
            d += 1
            pre = app.ent_dict[id].spirit
            lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Drain Life')
            if id not in app.all_ents().keys():
                d = pre
            else:
                post = app.ent_dict[id].spirit
                d = pre - post
            max_heal = d
            if max_heal < 0:
                max_heal = 0
#             app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
#             app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text') 
            apply_heal(self, self, max_heal)
            app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+74, text = 'Heal ' + str(max_heal) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+75, text = 'Heal ' + str(max_heal) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(1666, lambda e = None, id = id : self.finish_drain_life(event = e, id = id))
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, lambda e = None, id = id : self.finish_drain_life(event = e, id = id))
        
    def finish_drain_life(self, event = None, id = None):
        try: 
            del app.vis_dict['Drain_Life']
            app.canvas.delete('Drain_Life')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        if id:
            if app.ent_dict[id].spirit <= 0:
                lock(app.kill, id)
#                 name = 'Dethlok'+str(app.death_count)
#                 app.death_count += 1
#                 app.dethloks[name] = tk.IntVar(0)
#                 root.after(666, lambda id = id, name = name : app.kill(id, name))
#                 app.wait_variable(app.dethloks[name])
#         app.unbind_all()
        app.rebind_all()
        
    def muddle(self, event = None):
        if self.attack_used == True:
            return
#         root.unbind('<q>')
#         root.unbind('<a>')
        app.unbind_nonarrows()
        root.bind('<q>', self.finish_muddle)
        sqrs = []
        for coord in app.coords:
            if 1 <= dist(coord, self.loc) <= 4:
                sqrs.append(coord)
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_muddle(e, sqr, sqrs))
        app.depop_context(event = None)
        b = tk.Button(app.context_menu, text = 'Confirm Muddle', font = ('chalkduster', 24), fg='tan3', wraplength = 190, highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs: self.do_muddle(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_muddle(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if 'Muddle' in [ef.name for k,ef in app.ent_dict[id].effects_dict.items()]:
            return
        self.attack_used = True
        effect1 = mixer.Sound('Sound_Effects/muddle.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        app.vis_dict['Muddle'] = Vis(name = 'Muddle', loc = sqr[:])
        vis = app.vis_dict['Muddle']
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Muddle')
        if app.ent_dict[id].save_check('psyche', mod = 1) == False: # SAVE FAILS
            app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+74, text = 'Confused...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+75, text = 'Confused...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            # add effect
            def muddle_effect():
                pass
            f = muddle_effect
            def un():
                return None
            p = un
            # EOT FUNC
            def attack_self(id, lockname = None):
                app.get_focus(id)
                my_agl = app.ent_dict[id].get_abl('agl')
                if to_hit(my_agl, my_agl) == True:
                    my_str = app.ent_dict[id].get_abl('str')
                    my_end = app.ent_dict[id].get_abl('end')
                    d = damage(my_str, my_end)
                    lock(apply_damage, app.ent_dict[id], app.ent_dict[id], -d, 'melee', 'Muddle')
                else:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+74-app.moved_down, text = 'Muddle miss...', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Muddle miss...', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                root.after(1666, lambda ln = lockname : app.dethloks[ln].set(1))
            eot = partial(attack_self, id)
            n = 'Muddle' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Muddle', undo_func = p, duration = 3, level = 5, eot_func = eot)
            root.after(3333, lambda e = None : self.finish_muddle(event = e))
        else:
            app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+79, text = 'Muddle Psyche Save', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+80, text = 'Muddle Psyche Save', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(3333, lambda e = None : self.finish_muddle(event = e))
    
    def finish_muddle(self, event = None):
        app.canvas.delete('text')
        try:
            del app.vis_dict['Muddle']
            app.canvas.delete('Muddle')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        app.rebind_all()
        
    # agl v dodge, str v end, range 4
    def shadow_strike(self, event = None):
        if self.attack_used == True:
            return
#         root.unbind('<q>')
#         root.unbind('<a>')
        app.unbind_nonarrows()
        root.bind('<q>', self.finish_shadow_strike)
        sqrs = []
        for coord in app.coords:
            if 1 < dist(coord, self.loc) <= 7:
                sqrs.append(coord)
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_shadow_strike(e, sqr, sqrs))
        app.depop_context(event = None)
        b = tk.Button(app.context_menu, text = 'Confirm Attack', font = ('chalkduster', 24), fg='tan3', wraplength = 190, highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs: self.do_shadow_strike(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_shadow_strike(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        effect1 = mixer.Sound('Sound_Effects/shadow_strike.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        my_agl = self.get_abl('agl')
        target_dodge = app.ent_dict[id].get_abl('dodge')
        app.vis_dict['Shadow_Strike'] = Vis(name = 'Shadow_Strike', loc = sqr[:])
        vis = app.vis_dict['Shadow_Strike']
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Shadow_Strike')
        if to_hit(my_agl, target_dodge) == True:
            # VISUAL TO HIT
            my_str = self.get_abl('str')
            target_end = app.ent_dict[id].get_abl('end')
            d = damage(my_str, target_end)
#             pre = app.ent_dict[id].spirit
            root.after(2333, lambda e = None, id = id : self.finish_shadow_strike(event = e, id = id))
            lock(apply_damage, self, app.ent_dict[id], -d, 'piercing', 'Shadow Strike')
        else:
            app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+49, text = 'Missed!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+50, text = 'Missed!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2333, lambda e = None, id = id : self.finish_shadow_strike(event = e, id = id))
        self.attack_used = True
    
    def finish_shadow_strike(self, event = None, id = None):
        app.canvas.delete('text')
        try:
            del app.vis_dict['Shadow_Strike']
            app.canvas.delete('Shadow_Strike')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        if id:
            if app.ent_dict[id].spirit <= 0:
                lock(app.kill, id)
#                 name = 'Dethlok'+str(app.death_count)
#                 app.death_count += 1
#                 app.dethloks[name] = tk.IntVar(0)
#                 root.after(666, lambda id = id, name = name : app.kill(id, name))
#                 app.wait_variable(app.dethloks[name])
#         app.unbind_all()
        app.rebind_all()
    
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist


# lvl 2 gains resistances and magick (mummy/embalmed one)
# scarab, scarab swarm, spore cloud, dessicate, sleep
class Plaguebearer(Summon):
    def __init__(self, name, img, loc, owner, number, level):
        if level == 1:
            self.actions = {'Move':self.move, 'Pox':self.pox, 'Paralyze':self.paralyze, 'Scarab Gestation':self.scarab_gestation}
            self.attack_used = False
            self.str = 2
            self.agl = 2
            self.end = 6
            self.dodge = 2
            self.psyche = 5
            self.spirit = 15
            self.move_range = 2
            self.level = level
        elif level == 2:
            self.actions = {'Move':self.move, 'Pox':self.pox, 'Paralyze':self.paralyze, 'Scarab Gestation':self.scarab_gestation, 'Spore Cloud':self.spore_cloud, 'Scarab Swarm':self.scarab_swarm}
            self.attack_used = False
            self.str = 2
            self.agl = 2
            self.end = 7
            self.dodge = 2
            self.psyche = 7
            self.spirit = 26
            self.move_range = 3
            self.level = level
        self.move_type = 'normal'
        self.resist = ['piercing', 'poison']
        self.weak = ['fire', 'crushing']
        super().__init__(name, img, loc, owner, number)
        # not a method, below function appended to death_triggers
        def contagion_trigger():
            effect1 = mixer.Sound('Sound_Effects/contagion.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            app.focus_square(self.loc)
            sqrs = [c for c in app.coords if dist(self.loc, c) == 1]
            ents = [app.grid[s[0]][s[1]] for s in sqrs if app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
            for e in ents:
                ef_names = [v.name for k,v in app.ent_dict[e].effects_dict.items() if v.name == 'Contagion']
                if 'Contagion' in ef_names:
                    continue
                else:
                    n = 'Contagion' + str(app.effects_counter)
                    def contagion_effect(stat):
                        stat -= 3
                        if stat < 1:
                            return 1
                        else:
                            return stat
                    f = contagion_effect
                    app.ent_dict[e].str_effects.append(f)
                    app.ent_dict[e].end_effects.append(f)
                    app.ent_dict[e].agl_effects.append(f)
                    app.ent_dict[e].dodge_effects.append(f)
                    def un(id, func):
                        app.ent_dict[id].str_effects.remove(func)
                        app.ent_dict[id].end_effects.remove(func)
                        app.ent_dict[id].agl_effects.remove(func)
                        app.ent_dict[id].dodge_effects.remove(func)
                        return None
                    p = partial(un, e, f)
                    app.ent_dict[e].effects_dict[n] = Effect(name = 'Contagion', undo_func = p, duration = 3, level = 7)
                    n2 = 'Contagion' + str(app.effects_counter) # not an effect, just need unique int
                    app.effects_counter += 1 # that is why this is incr manually here, no Effect init
                    app.vis_dict[n2] = Vis(name = 'Contagion', loc = app.ent_dict[e].loc[:])
                    rand_start_anim = randrange(1,7)
                    for i in range(rand_start_anim):
                        app.vis_dict[n2].rotate_image()
                    app.canvas.create_text(app.ent_dict[e].loc[0]*100-app.moved_right+49, app.ent_dict[e].loc[1]*100-app.moved_down+89, text = 'CONTAGION', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = ('contagion_text'))
                    app.canvas.create_text(app.ent_dict[e].loc[0]*100-app.moved_right+50, app.ent_dict[e].loc[1]*100-app.moved_down+90, text = 'CONTAGION', justify = 'center', fill = 'green2', font = ('Andale Mono', 16), tags = ('contagion_text'))# CALLED DURING A SET_ATTR, SO NEED A DIFFERENT TEXT TAG TO AVOID CLEANUP OF UNRELATED TEXT OBJECTS ON CANVAS
                    app.canvas.create_image(app.ent_dict[e].loc[0]*100+50-app.moved_right, app.ent_dict[e].loc[1]*100+50-app.moved_down, image = app.vis_dict[n2].img, tags = n2)
            def cleanup_contagion():
                try:
                    keys = [k for k,v in app.vis_dict.items() if v.name == 'Contagion']
                    for k in keys:
                        del app.vis_dict[k]
                    app.canvas.delete('Contagion')
                except: pass
                app.canvas.delete('contagion_text')
            root.after(2333, cleanup_contagion)
        self.death_triggers.append(contagion_trigger)
    # END CLASS INIT
    
    
    # must choose a scarab, remove (do not kill) and replace with scarab swarm
    def scarab_swarm(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_scarab_swarm)
        scarabs = [k for k,v in app.ent_dict.items() if v.name == 'Scarab' and v.owner == self.owner and dist(v.loc, self.loc) <= 4]
        sqrs = []
        for id in scarabs:
            sqrs.append(app.ent_dict[id].loc[:])
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_scarab_swarm(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Scarab To Transform', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_scarab_swarm(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_scarab_swarm(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
#         self.init_cast_anims()
#         effect1 = mixer.Sound('Sound_Effects/scarab_swarm.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.canvas.delete(id)
        app.grid[app.ent_dict[id].loc[0]][app.ent_dict[id].loc[1]] = ''
        del app.ent_dict[id]
        app.vis_dict['Summon'] = Vis(name = 'Summon', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Summon'].img, tags = 'Summon')
        root.after(1666, lambda s = sqr : self.finish_scarab_swarm(s))
        root.after(2666, self.cleanup_scarab_swarm)
        
    def finish_scarab_swarm(self, sqr):
        img = ImageTk.PhotoImage(Image.open('summon_imgs/Scarab_Swarm.png'))
        if self.owner == 'p1':
            number = 'a'+str(app.ent_dict[app.p1_witch].summon_ids)
            app.ent_dict[app.p1_witch].summon_ids += 1
        else:
            number = 'b'+str(app.ent_dict[app.p2_witch].summon_ids)
            app.ent_dict[app.p2_witch].summon_ids += 1
        app.ent_dict[number] =  Scarab_Swarm(name = 'Scarab_Swarm', img = img, loc = sqr[:], owner = self.owner, number = number)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.ent_dict[number].img, tags = app.ent_dict[number].tags)
        app.grid[sqr[0]][sqr[1]] = number
        
    def cleanup_scarab_swarm(self, event = None):
        try:
            del app.vis_dict['Summon']
            app.canvas.delete('Summon')
        except:
            pass
        app.unbind_all()
        app.rebind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        try: app.canvas.delete('text')
        except: pass
        
        
    
    def spore_cloud(self, event = None):
#         loc_effects = [v.name for k,v in app.loc_effects_dict.items()]
#         if 'Spore_Cloud' in loc_effects:
#             return
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.cleanup_spore_cloud)
        sqrs = []
        for c in app.coords:
            if dist(self.loc, c) <= 2:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_spore_cloud(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Choose Spore Cloud Location', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_spore_cloud(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_spore_cloud(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        if 'Spore_Cloud' in [v.name for k,v in app.loc_effects_dict[tuple(sqr)].effects_dict.items()]:
            return
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
#         effect1 = mixer.Sound('Sound_Effects/spore_cloud.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Spore Cloud', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Spore Cloud', font = ('Andale Mono', 14), fill = 'olivedrab2', tags = 'text')
        un = 'Spore_Cloud' + str(app.effects_counter)
        app.effects_counter += 1
        app.vis_dict[un] = Vis(name = 'Spore_Cloud', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = un)
        def spore_effect(stat):
            return stat+2
        p = partial(spore_effect)
        app.loc_effects_dict[tuple(sqr)].dodge_effects.append(p)
        def spore_def(attacker, defender, amount, type):
            if amount < 0 and (type == 'melee' or type == 'ranged'):
                app.canvas.create_text(defender.loc[0]*100+49-app.moved_right, defender.loc[1]*100+54-app.moved_down, text = '-2 (min1) spirit spore cloud', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                app.canvas.create_text(defender.loc[0]*100+50-app.moved_right, defender.loc[1]*100+55-app.moved_down, text = '-2 (min1) spirit spore cloud', justify ='center', font = ('Andale Mono', 13), fill = 'olivedrab2', tags = 'text')
                root.after(1888, lambda t = 'text' : app.canvas.delete(t))
                amount += 2
                if amount > -1:
                    return -1
                else:
                    return amount
            else:
                return amount
        app.loc_effects_dict[tuple(sqr)].def_effects.append(spore_def)
        def undo(s, un, p_ef):
            app.loc_effects_dict[tuple(s)].dodge_effects.remove(p_ef)
            app.loc_effects_dict[tuple(s)].def_effects.remove(spore_def)
            del app.vis_dict[un]
            app.canvas.delete(un)
        u = partial(undo, sqr[:], un, p)
        app.loc_effects_dict[tuple(sqr)].effects_dict[un] = Local_Effect(name = 'Spore_Cloud', undo = u, duration = 6, level = 8, loc = sqr[:], avoid = -7)
        root.after(1666, self.cleanup_spore_cloud)
        
    def cleanup_spore_cloud(self, event = None):
        app.unbind_all()
        app.rebind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        try: app.canvas.delete('text')
        except: pass
    
    def scarab_gestation(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_scarab_gestation)
        sqrs = [c for c in app.coords if dist(self.loc, c) == 1]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_scarab_gestation(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Scarab Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_scarab_gestation(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_scarab_gestation(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if app.ent_dict[id].owner == self.owner:
            return
        if 'Scarab_Gestation' in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
            return
#         effect1 = mixer.Sound('Sound_Effects/scarab_gestation.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Scarab Gestation', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Scarab Gestation', justify = 'center', fill = 'thistle2', font = ('Andale Mono', 16), tags = 'text')
        app.vis_dict['Scarab_Gestation'] = Vis(name = 'Scarab_Gestation', loc = sqr[:])
        vis = app.vis_dict['Scarab_Gestation']
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Scarab_Gestation')
        if app.ent_dict[id].save_check('str', mod = -2) == False: # Fail Save
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Scarab...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Scarab...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            def scarab_effect(id):
                # this ent is killed, create scarab in its loc
                # make generation in nearest empty sqr
                s = app.ent_dict[id].loc[:]
                sqr = reduce(lambda a,b : a if dist(a,s) < dist(b,s) else b, [c for c in app.coords if app.grid[c[0]][c[1]] == ''])
                img = ImageTk.PhotoImage(Image.open('summon_imgs/Scarab.png'))
                if self.owner == 'p1':
                    number = 'a'+str(app.ent_dict[app.p1_witch].summon_ids)
                    app.ent_dict[app.p1_witch].summon_ids += 1
                else:
                    number = 'b'+str(app.ent_dict[app.p2_witch].summon_ids)
                    app.ent_dict[app.p2_witch].summon_ids += 1
                app.ent_dict[number] =  Scarab(name = 'Scarab', img = img, loc = sqr[:], owner = self.owner, number = number)
                app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.ent_dict[number].img, tags = app.ent_dict[number].tags)
                app.grid[sqr[0]][sqr[1]] = number
                
            p = partial(scarab_effect, id)
            app.ent_dict[id].death_triggers.append(p)
            def un(i, p):
                app.ent_dict[i].death_triggers.remove(p)
                return None
            u = partial(un, id, p)
            n = 'Scarab_Gestation' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Scarab_Gestation', undo_func = u, duration = 9, level = 7)
            root.after(2666, self.finish_scarab_gestation)
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Strength Save', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Strength Save', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, self.finish_scarab_gestation)
        
    def finish_scarab_gestation(self, event = None):
        try: 
            del app.vis_dict['Scarab_Gestation']
            app.canvas.delete('Scarab_Gestation')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        
    def paralyze(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_paralyze)
        sqrs = [c for c in app.coords if dist(self.loc, c) == 1]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_paralyze(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Paralyze Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_paralyze(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_paralyze(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if app.ent_dict[id].owner == self.owner:
            return
        if 'Paralyze' in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
            return
#         effect1 = mixer.Sound('Sound_Effects/paralyze.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Paralyze', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Paralyze', justify = 'center', fill = 'thistle2', font = ('Andale Mono', 16), tags = 'text')
        app.vis_dict['Paralyze'] = Vis(name = 'Paralyze', loc = sqr[:])
        vis = app.vis_dict['Paralyze']
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Paralyze')
        # End save, if fail and user-ent: effect stores then overwrites abils, if ai-ent: wrap/overwrite do_ai()
        if app.ent_dict[id].save_check('end', mod = 1) == False: # Fail Save
        ######## OLD PARALYZE ########
#             app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Stun 1 turn...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
#             app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Stun 1 turn...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
#             
#             app.vis_dict['Paralyze'] = Vis(name = 'Paralyze', loc = sqr)
#             app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Paralyze'].img, tags = 'Paralyze')
#             if app.num_players == 2:
#                 old_actions = dict(app.ent_dict[id].actions)
#                 app.ent_dict[id].actions = {}
#             else:
#                 def paralyze_ai(ents_list, id):
#                     app.ent_dict[id].ai_end_turn(ents_list)
#                 f = partial(paralyze_ai, id = id)
#                 app.ent_dict[id].do_ai = f
#             def un(i, old_actions = None):
#                 if app.num_players == 2:
#                     app.ent_dict[i].actions = old_actions
#                 else:
#                     p2 = partial(app.ent_dict[i].__class__.do_ai, app.ent_dict[i]) # PUT BACK CLASS actions
#                     app.ent_dict[i].do_ai = p2
#                 return None
#             if app.num_players == 2:
#                 p = partial(un, id, old_actions = old_actions)
#             else:
#                 p = partial(un, id)
#           ########### END OLD PARALYZE ##########
            # move range set 1, atk efct reduce melee ranged
            def paralyze_move(move_range):
                if move_range > 1:
                    return 1
                else:
                    return move_range
            app.ent_dict[id].move_effects.append(paralyze_move)
            def paralyze_atk(atkr, dfndr, amt, type):
                if type == 'melee' or type == 'ranged':
                    app.canvas.create_text(atkr.loc[0]*100-app.moved_right+49, atkr.loc[1]*100-app.moved_down+74, text = 'Paralyzed, dmg halved...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(atkr.loc[0]*100-app.moved_right+50, atkr.loc[1]*100-app.moved_down+75, text = 'Paralyzed, dmg halved...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                    return (amt//2, 1666)
                else:
                    return (amt, 0)
            app.ent_dict[id].attack_effects.append(paralyze_atk)
            def undo(id):
                app.ent_dict[id].move_effects.remove(paralyze_move)
                app.ent_dict[id].attack_effects.remove(paralyze_atk)
                return None
            u = partial(undo, id)
            n = 'Paralyze' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Paralyze', undo_func = u, duration = 2, level = 6)
            root.after(2666, self.finish_paralyze)
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Endurance Save', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Endurance Save', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, self.finish_paralyze)

        
    def finish_paralyze(self, event = None):
        try: 
            del app.vis_dict['Paralyze']
            app.canvas.delete('Paralyze')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        
    # give all adj units pox Effect if they have no pox effects, causes 2 spirit damage EOT
    def pox(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_pox)
        sqrs = [c for c in app.coords if dist(self.loc, c) == 1]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = sqrs : self.do_pox(event = e, sqrs = s)) 
        b = tk.Button(app.context_menu, text = 'Confirm Pox', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = sqrs : self.do_pox(event = e, sqrs = s))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_pox(self, event = None, sqrs = None):
        effect1 = mixer.Sound('Sound_Effects/pox.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        self.attack_used = True
#         self.init_attack_anims()
        app.cleanup_squares()
        app.depop_context(event = None)
        app.unbind_all()
        ents = []
        for s in sqrs:
            n2 = 'Pox' + str(app.effects_counter) # not an effect, just need unique int
            app.effects_counter += 1 # that is why this is incr manually here, no Effect init
            app.vis_dict[n2] = Vis(name = 'Pox', loc = s)
            rand_start_anim = randrange(1,7)
            for i in range(rand_start_anim):
                app.vis_dict[n2].rotate_image()
            ent = app.grid[s[0]][s[1]]
            if ent != '' and ent != 'block' and isinstance(app.ent_dict[ent], Plaguebearer) == False:
                #GIVE POX EFFECT if doesn't exist
                ef_names = [v.name for k,v in app.ent_dict[ent].effects_dict.items()]
                if 'Pox' not in ef_names:
                    n = 'Pox'+str(app.effects_counter)
                    def take_2(tar, lockname = None):
                        app.get_focus(tar)
                        lock(apply_damage, self, app.ent_dict[tar], -2, 'poison', 'Pox')
                        root.after(1666, lambda ln = lockname : app.dethloks[ln].set(1))
                    # EOT
                    eot = partial(take_2, ent)
                    # UNDO
                    def un():
                        return None
                    u = un
                    # POX VIS
                    app.ent_dict[ent].effects_dict[n] = Effect(name = 'Pox', eot_func = eot , undo_func = u, duration = 4, level = 6)
                    app.canvas.create_text(app.ent_dict[ent].loc[0]*100-app.moved_right+49, app.ent_dict[ent].loc[1]*100-app.moved_down+89, text = 'Pox', justify = 'center', fill = 'black', font = ('Andale Mono', 14), tags = 'text')
                    app.canvas.create_text(app.ent_dict[ent].loc[0]*100-app.moved_right+50, app.ent_dict[ent].loc[1]*100-app.moved_down+90, text = 'Pox', justify = 'center', fill = 'darkolivegreen3', font = ('Andale Mono', 14), tags = 'text')
        root.after(2999, self.finish_pox)
        
    def finish_pox(self, event = None):
#         self.init_normal_anims()
        try:
            keys = [k for k in app.vis_dict.keys() if k.startswith('Pox')]
            for k in keys:
                del app.vis_dict[k]
            app.canvas.delete('Pox')
        except: pass
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)
        app.cleanup_squares()
    
    
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist


class Scarab_Swarm(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'Bite':self.bite, 'Move':self.flying_move}
        self.attack_used = False
        self.str = 4
        self.agl = 6
        self.end = 5
        self.dodge = 6
        self.psyche = 4
        self.spirit = 19
        self.move_range = 6
        self.level = 1
        self.move_type = 'flying'
        self.weak = []
        self.resist = ['magick', 'fire', 'poison', 'piercing', 'slashing', 'elec']
        super().__init__(name, img, loc, owner, number)
        
    def bite(self, event = None):
        if self.attack_used == True:
            return
        app.unbind_nonarrows()
        root.bind('<q>', self.finish_bite)
        sqrs = [c for c in app.coords if dist(self.loc, c) == 1]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_bite(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Bite Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_bite(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_bite(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.action_target_ents().keys():
            return
#         effect1 = mixer.Sound('Sound_Effects/bite.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
#         app.vis_dict['Bite'] = Vis(name = 'Bite', loc = sqr[:])
#         vis = app.vis_dict['Bite']
#         app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Bite')
        my_agl = self.get_abl('agl')
        tar_agl = app.ent_dict[id].get_abl('agl')
        if to_hit(my_agl, tar_agl) == True:
            my_str = self.get_abl('str')
            tar_end = app.ent_dict[id].get_abl('end')
            d = damage(my_str, tar_end)
#             pre = app.ent_dict[id].spirit
            lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Bite')
            root.after(2666, lambda e = None, id = id : self.finish_bite(event = e, id = id))
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+79, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+80, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, lambda e = None, id = id : self.finish_bite(event = e, id = id))
        
    def finish_bite(self, event = None, id = None):
#         try: 
#             del app.vis_dict['Bite']
#             app.canvas.delete('Bite')
#         except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        if id:
            if app.ent_dict[id].spirit <= 0:
                lock(app.kill, id)
        app.unbind_all()
        app.rebind_all()
    
    
    def legal_moves(self):
        loc = self.loc
        mvlist = []
        for c in app.coords:
            if dist(c, loc) <= self.get_abl('move_range') and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist


class Scarab(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'Bite':self.bite, 'Move':self.move}
        self.attack_used = False
        self.str = 2
        self.agl = 3
        self.end = 3
        self.dodge = 3
        self.psyche = 2
        self.spirit = 9
        self.move_range = 5
        self.level = 1
        self.move_type = 'normal'
        self.weak = ['crushing']
        self.resist = ['magick', 'fire', 'poison', 'piercing', 'slashing', 'elec']
        super().__init__(name, img, loc, owner, number)
        
    def bite(self, event = None):
        if self.attack_used == True:
            return
        app.unbind_nonarrows()
        root.bind('<q>', self.finish_bite)
        sqrs = [c for c in app.coords if dist(self.loc, c) == 1]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_bite(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Bite Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_bite(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_bite(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.action_target_ents().keys():
            return
#         effect1 = mixer.Sound('Sound_Effects/bite.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
#         app.vis_dict['Bite'] = Vis(name = 'Bite', loc = sqr[:])
#         vis = app.vis_dict['Bite']
#         app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Bite')
        my_agl = self.get_abl('agl')
        tar_agl = app.ent_dict[id].get_abl('agl')
        if to_hit(my_agl, tar_agl) == True:
            my_str = self.get_abl('str')
            tar_end = app.ent_dict[id].get_abl('end')
            d = damage(my_str, tar_end)
#             pre = app.ent_dict[id].spirit
            lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Bite')
            root.after(2666, lambda e = None, id = id : self.finish_bite(event = e, id = id))
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+79, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+80, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, lambda e = None, id = id : self.finish_bite(event = e, id = id))
        
    def finish_bite(self, event = None, id = None):
#         try: 
#             del app.vis_dict['Bite']
#             app.canvas.delete('Bite')
#         except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        if id:
            if app.ent_dict[id].spirit <= 0:
                lock(app.kill, id)
        app.unbind_all()
        app.rebind_all()
    
    
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist

# lvl 2 gains more range atk abils, minor magick
# add actions: Aura, Tranquility, Grasp of Vines
class Bard(Summon):
    def __init__(self, name, img, loc, owner, number, level):
        if level == 1:
            self.actions = {'Move':self.move, 'Unholy Chant':self.unholy_chant, 'Discord' : self.discord, 'Moonlight' : self.moonlight, 'Esuna':self.esuna}
            self.attack_used = False
            self.str = 2
            self.agl = 3
            self.end = 3
            self.dodge = 5
            self.psyche = 5
            self.spirit = 15
            self.move_range = 5
            self.level = level
        elif level == 2:
            self.actions = {'Move':self.move, 'Unholy Chant':self.unholy_chant, 'Discord' : self.discord, 'Moonlight' : self.moonlight, 'Esuna':self.esuna, 'Aura':self.aura, 'Tranquility':self.tranquility}
            self.attack_used = False
            self.str = 3
            self.agl = 7
            self.end = 5
            self.dodge = 5
            self.psyche = 5
            self.spirit = 21
            self.move_range = 6
            self.level = level
#             name = 'Ranger' #this works, just need appr anim files
        self.move_type = 'normal'
        self.weak = ['cold', 'crushing']
        self.resist = ['magick', 'explosive', 'poison']
        super().__init__(name, img, loc, owner, number)
        
        
    def aura(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_aura)
        sqrs = [c for c in app.coords if 1 <= dist(self.loc, c) <= 3]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_aura(event = e, sqr = sqr, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Confirm Aura', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_aura(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_aura(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        if not isinstance(app.ent_dict[id], (Trickster, Warrior, Plaguebearer, Shadow)):
             return
        self.attack_used = True
#         self.init_attack_anims()
#         effect1 = mixer.Sound('Sound_Effects/aura.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        ents = [k for k,v in app.ent_dict.items() if dist(v.loc, sqr) <= 2 and isinstance(v, (Trickster, Warrior, Plaguebearer, Shadow)) and v.owner == self.owner]
        app.get_focus(choice(ents))
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Aura', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Aura', justify = 'center', fill = 'ivory', font = ('Andale Mono', 16), tags = 'text')
        for id in ents:
            loc = app.ent_dict[id].loc[:]
            apply_heal(self, app.ent_dict[id], 3)
            un = 'Aura' + str(app.effects_counter)
            app.effects_counter += 1
            app.vis_dict[un] = Vis(name = 'Aura', loc = loc[:])
            vis = app.vis_dict[un]
            app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = vis.img, tags = un)
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = '+3 spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = '+3 spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            def cleanup_aura(un):
                del app.vis_dict[un]
                app.canvas.delete(un)
            root.after(2666, lambda un = un : cleanup_aura(un))
        root.after(2777, self.finish_aura)
        
    def finish_aura(self, event = None):
#         self.init_normal_anims()
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)

    def tranquility(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_tranquility)
        sqrs = [c for c in app.coords if dist(self.loc, c) <= 6]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_tranquility(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Tranquility Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_tranquility(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_tranquility(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
#         effect1 = mixer.Sound('Sound_Effects/tranquility.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Tranquility', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Tranquility', justify = 'center', fill = 'ivory', font = ('Andale Mono', 16), tags = 'text')
        app.vis_dict['Tranquility'] = Vis(name = 'Tranquility', loc = sqr[:])
        vis = app.vis_dict['Tranquility']
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Tranquility')
        app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+74, text = 'Dispel Attempt\n Local Effects', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
        app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+75, text = 'Dispel Attempt\n Local Effects', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
        to_remove = []
        for k,v in app.loc_effects_dict[tuple(sqr)].effects_dict.items():
            if v.dispel(2) == True:
                to_remove.append(k)
        for k in to_remove:
            del app.loc_effects_dict[tuple(sqr)].effects_dict[k]
        root.after(2666, self.finish_tranquility)
        
    def finish_tranquility(self, event = None):
        try: 
            del app.vis_dict['Tranquility']
            app.canvas.delete('Tranquility')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        
    def esuna(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_esuna)
        sqrs = [c for c in app.coords if 1 <= dist(self.loc, c) <= 3]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_esuna(event = e, sqr = sqr, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Confirm Esuna Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_esuna(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_esuna(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        effect1 = mixer.Sound('Sound_Effects/esuna.ogg')
        effect1.set_volume(.5)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Esuna', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Esuna', justify = 'center', fill = 'ivory', font = ('Andale Mono', 16), tags = 'text')
        app.vis_dict['Esuna'] = Vis(name = 'Esuna', loc = sqr[:])
        vis = app.vis_dict['Esuna']
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Esuna')
        app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Dispel Attempt\nAll Effects', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
        app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Dispel Attempt\nAll Effects', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
        to_remove = []
        for k,v in app.ent_dict[id].effects_dict.items():
            if v.dispel(0) == True:
                to_remove.append(k)
        for k in to_remove:
            del app.ent_dict[id].effects_dict[k]
        root.after(2666, self.finish_esuna)
        
    def finish_esuna(self, event = None):
        try: 
            del app.vis_dict['Esuna']
            app.canvas.delete('Esuna')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        
    def moonlight(self, event = None):
        if self.attack_used == True:
            return
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_moonlight)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 3]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_moonlight(event = e, s = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Moonlight', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_moonlight(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_moonlight(self, event, s, sqrs):
        global selected_vis
        id = app.grid[s[0]][s[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        if s not in sqrs:
            return
        if not isinstance(app.ent_dict[id], (Trickster, Warrior, Plaguebearer, Shadow)):
             return
        effect1 = mixer.Sound('Sound_Effects/moonlight.ogg')
        effect1.set_volume(.2)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
#         self.init_cast_anims()
#         app.ent_dict[id].set_attr('spirit', 4)
        apply_heal(self, app.ent_dict[id], 4)
        self.attack_used = True
        app.vis_dict['Moonlight'] = Vis(name = 'Moonlight', loc = s)
        app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+70-app.moved_down, image = app.vis_dict['Moonlight'].img, tags = 'Moonlight')
        app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+74-app.moved_down, text = 'Moonlight', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
        app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+75-app.moved_down, text = 'Moonlight', font = ('Andale Mono', 16), fill = 'azure', tags = 'text')
        app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+89-app.moved_down, text = '+4 Spirit', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+90-app.moved_down, text = '+4 Spirit', font = ('Andale Mono', 13), fill = 'azure', tags = 'text')
        selected_vis = ['Moonlight']
        def moonlight_loop(starty, endy, x):
            if starty > endy:
                app.vis_dict['Moonlight'].rotate_image()
                app.canvas.delete('Moonlight')
                app.canvas.create_image(x, starty, image = app.vis_dict['Moonlight'].img, tags = 'Moonlight')
                starty -= 10
                app.canvas.move('Moonlight', 0, -10)
                app.canvas.tag_raise('Moonlight')
            if starty == endy:
                root.after(333, self.cleanup_moonlight)
            else:
                root.after(166, lambda sy = starty, ey = endy, x = x : moonlight_loop(sy, ey, x))
        locy = s[1]*100+70-app.moved_down
        locx = s[0]*100+50-app.moved_right
        moonlight_loop(locy, locy-120, locx)
        
    def cleanup_moonlight(self, event = None):
        global selected, selected_vis
#         self.init_normal_anims()
        app.unbind_all()
        app.rebind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        try: 
            del app.vis_dict['Moonlight']
            app.canvas.delete('Moonlight')
        except: pass
        try: app.canvas.delete('text')
        except: pass
        selected = []
        selected_vis = []
        
    # +1 to all stats for 1 turn, non-stackable
    def unholy_chant(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_unholy_chant)
        sqrs = [c for c in app.coords if dist(self.loc, c) <= 2]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = sqrs : self.do_unholy_chant(event = e, sqrs = s)) 
        b = tk.Button(app.context_menu, text = 'Confirm Unholy Chant', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs : self.do_unholy_chant(event = e, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
        
    def do_unholy_chant(self, event = None, sqrs = None):
        self.attack_used = True
#         self.init_attack_anims()
        effect1 = mixer.Sound('Sound_Effects/unholy_chant.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        ents = []
        for s in sqrs:
            ent = app.grid[s[0]][s[1]]
            if ent != '' and ent != 'block':
                if app.ent_dict[ent].owner == app.active_player:
                    ef_names = [v.name for k,v in app.ent_dict[ent].effects_dict.items()]
                    if 'Unholy_Chant' not in ef_names:
                        n2 = 'Unholy_Chant' + str(app.effects_counter) # not an effect, just need unique int
                        app.effects_counter += 1 # that is why this is incr manually here, no Effect init
                        app.vis_dict[n2] = Vis(name = 'Unholy_Chant', loc = s)
                        app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[n2].img, tags = 'Unholy_Chant')
                        app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+69-app.moved_down, text = 'Unholy Chant', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
                        app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+70-app.moved_down, text = 'Unholy Chant', justify = 'center', font = ('Andale Mono', 14), fill = 'ivory3', tags = 'text')
                        app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+89-app.moved_down, text = '+1 All Stats', font = ('Andale Mono', 12), fill = 'black', tags = 'text')
                        app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+90-app.moved_down, text = '+1 All Stats', font = ('Andale Mono', 12), fill = 'white', tags = 'text')
                        def unholy_chant_effect(stat):
                            stat += 1
                            return stat
                        f = unholy_chant_effect
                        app.ent_dict[ent].str_effects.append(f)
                        app.ent_dict[ent].end_effects.append(f)
                        app.ent_dict[ent].agl_effects.append(f)
                        app.ent_dict[ent].dodge_effects.append(f)
                        app.ent_dict[ent].psyche_effects.append(f)
                        
                        def un(i, func):
                            app.ent_dict[i].str_effects.remove(func)
                            app.ent_dict[i].end_effects.remove(func)
                            app.ent_dict[i].agl_effects.remove(func)
                            app.ent_dict[i].dodge_effects.remove(func)
                            app.ent_dict[i].psyche_effects.remove(func)
                            return None
                        p = partial(un, ent, f)
                        n = 'Unholy_Chant' + str(app.effects_counter)
                        app.ent_dict[ent].effects_dict[n] = Effect(name = 'Unholy_Chant', undo_func = p, duration = 1, level = 4)
        root.after(3666, self.finish_unholy_chant)
        
    def finish_unholy_chant(self, event = None):
#         self.init_normal_anims()
        try:
            keys = [k for k in app.vis_dict.keys() if k[:12] == 'Unholy_Chant']
            for k in keys:
                del app.vis_dict[k]
            app.canvas.delete('Unholy_Chant')
        except: pass
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)
    
    # minor attack, psyche based
    def discord(self, event = None):
        if self.attack_used == True:
            return
#         root.unbind('<a>')
#         root.unbind('<q>')
        app.unbind_nonarrows()
        root.bind('<q>', self.finish_discord)
        sqrs = [c for c in app.coords if 1 <= dist(self.loc, c) <= 5]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_discord(event = e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Discord Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_discord(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_discord(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        effect1 = mixer.Sound('Sound_Effects/discord.ogg')
        effect1.set_volume(.5)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.vis_dict['Discord'] = Vis(name = 'Discord', loc = sqr[:])
        vis = app.vis_dict['Discord']
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Discord')
        my_psyche = self.get_abl('psyche')
        tar_psyche = app.ent_dict[id].get_abl('psyche')
        if to_hit(my_psyche, tar_psyche) == True:
            d = damage(my_psyche, tar_psyche)
            d = d//2
            if d == 0: d = 1
            d += 1
#             pre = app.ent_dict[id].spirit
            lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Discord')
            root.after(2666, lambda e = None, id = id : self.finish_discord(event = e, id = id))
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+79, text = 'Discord Missed!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+80, text = 'Discord Missed!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, lambda e = None, id = id : self.finish_discord(event = e, id = id))
        
    def finish_discord(self, event = None, id = None):
        try: 
            del app.vis_dict['Discord']
            app.canvas.delete('Discord')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        if id:
            if app.ent_dict[id].spirit <= 0:
                lock(app.kill, id)
#                 name = 'Dethlok'+str(app.death_count)
#                 app.death_count += 1
#                 app.dethloks[name] = tk.IntVar(0)
#                 root.after(666, lambda id = id, name = name : app.kill(id, name))
#                 app.wait_variable(app.dethloks[name])
        app.unbind_all()
        app.rebind_all()
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
        
class White_Dragon_Top(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = True):
#         self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 9
        self.agl = 8
        self.end = 9
        self.dodge = 7
        self.psyche = 9
        self.spirit = 157
        self.waiting = waiting
        super().__init__(name, img, loc, owner, number, type = 'large')
    # 'tall' ent, bigger than 100 pixels height, needs to be split into 2 images so the 'top' image is 'large' (raised above 'maptop', bottom part of ent is hidden behind 'maptop'
class White_Dragon(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_iceblast}
        self.attack_used = False
        self.str = 9
        self.agl = 8
        self.end = 9
        self.dodge = 7
        self.psyche = 9
        self.spirit = 157
        self.move_range = 7
        self.waiting = waiting
        self.summoned_kobolds = False
        self.retreated_once = False
        self.move_type = 'flying'
        self.resist = ['cold', 'poison']
        self.weak = ['fire']
        anims = [a for r,d,a in walk('./animations/White_Dragon_Ascend/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        self.ascend_anims = []
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/White_Dragon_Ascend/' + anim))
            self.ascend_anims.append(a)
        anims = [a for r,d,a in walk('./animations/White_Dragon_Flight/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        self.flight_anims = []
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/White_Dragon_Flight/' + anim))
            self.flight_anims.append(a)
        anims = [a for r,d,a in walk('./animations/White_Dragon_Descend/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        self.descend_anims = []
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/White_Dragon_Descend/' + anim))
            self.descend_anims.append(a)
        super().__init__(name, img, loc, owner, number, type = 'large_bottom')
        self.immovable = True
        # create top half
        img = ImageTk.PhotoImage(Image.open('animations/White_Dragon_Top/0.png'))
        app.ent_dict[self.number+'top'] = White_Dragon_Top(name = 'White_Dragon_Top', img = img, loc = [self.loc[0],self.loc[1]], owner = 'p2', number = self.number+'top')
        
    def large_undo(self):
        app.canvas.delete(self.number+'top')
        del app.ent_dict[self.number+'top']
        
    def init_ascend_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        for i, anim in enumerate(self.ascend_anims):
            self.anim_dict[i] = anim
        self.img = self.anim_dict[0]
            
    def init_flight_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        for i, anim in enumerate(self.flight_anims):
            self.anim_dict[i] = anim
        self.img = self.anim_dict[0]
            
    def init_descend_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        for i, anim in enumerate(self.descend_anims):
            self.anim_dict[i] = anim
        self.img = self.anim_dict[0]
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    #  White_Dragon AI
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        elif self.spirit < 150 and self.summoned_kobolds == False:
            empty_locs = [c for c in app.coords if app.grid[c[0]][c[1]] == '' and dist(c, self.loc) >= 12]
            endloc = choice(empty_locs)
            orc_sqrs = [[15,1],[16,1],[17,1],[18,1],[15,2],[16,2],[17,2],[18,2],[15,3],[16,3],[17,3],[18,3],[15,4],[16,4],[17,4],[18,4]]
            for s in orc_sqrs[:]:
                if app.grid[s[0]][s[1]] != '':
                    orc_sqrs.remove(s)
            if endloc in orc_sqrs[:]:
                orc_sqrs.remove(endloc)
            loc1 = choice(orc_sqrs)
            orc_sqrs.remove(loc1)
            loc2 = choice(orc_sqrs)
            orc_sqrs.remove(loc2)
            loc3 = choice(orc_sqrs)
            orc_sqrs.remove(loc3)
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Kobold_Shaman.png'))
            img2 = ImageTk.PhotoImage(Image.open('summon_imgs/Orc_Axeman.png'))
            app.ent_dict['b2'] = Orc_Axeman(name = 'Orc_Axeman', img = img2, loc = loc1[:], owner = 'p2', number = 'b2')
            app.ent_dict['b3'] = Kobold_Shaman(name = 'Kobold_Shaman', img = img, loc = loc2[:], owner = 'p2', number = 'b3')
            app.ent_dict['b4'] = Kobold_Shaman(name = 'Kobold_Shaman', img = img, loc = loc3[:], owner = 'p2', number = 'b4')
            app.grid[loc1[0]][loc1[1]] = 'b2'
            app.grid[loc2[0]][loc2[1]] = 'b3'
            app.grid[loc3[0]][loc3[1]] = 'b4'
            self.summoned_kobolds = True
            self.white_dragon_move(ents_list, endloc)
        # if spirit low, fly to random spot can occupy, set waiting, summon orcs
        elif self.spirit < 88 and self.retreated_once == False:
            empty_locs = [c for c in app.coords if app.grid[c[0]][c[1]] == '' and dist(c, self.loc) >= 12]
            endloc = choice(empty_locs)
            # create orcs
            orc_sqrs = [[15,1],[16,1],[17,1],[18,1],[15,2],[16,2],[17,2],[18,2],[15,3],[16,3],[17,3],[18,3],[15,4],[16,4],[17,4],[18,4]]
            for s in orc_sqrs[:]:
                if app.grid[s[0]][s[1]] != '':
                    orc_sqrs.remove(s)
            if endloc in orc_sqrs[:]:
                orc_sqrs.remove(endloc)
            loc1 = choice(orc_sqrs)
            orc_sqrs.remove(loc1)
            loc2 = choice(orc_sqrs)
            orc_sqrs.remove(loc2)
            loc3 = choice(orc_sqrs)
            orc_sqrs.remove(loc3)
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Orc_Axeman.png'))
            img2 = ImageTk.PhotoImage(Image.open('summon_imgs/Kobold_Shaman.png'))
            app.ent_dict['b5'] = Orc_Axeman(name = 'Orc_Axeman', img = img, loc = loc1[:], owner = 'p2', number = 'b5')
            app.ent_dict['b6'] = Orc_Axeman(name = 'Kobold_Shaman', img = img, loc = loc2[:], owner = 'p2', number = 'b6')
            app.ent_dict['b7'] = Orc_Axeman(name = 'Kobold_Shaman', img = img, loc = loc3[:], owner = 'p2', number = 'b7')
            app.grid[loc1[0]][loc1[1]] = 'b5'
            app.grid[loc2[0]][loc2[1]] = 'b6'
            app.grid[loc3[0]][loc3[1]] = 'b7'
            self.retreated_once = True
            self.white_dragon_move(ents_list, endloc)
        else:
            self.continue_ai(ents_list)
            
    # first make melee atk against adj if any
    # then attempt to move adj to nearest ent
    # if s.atk_used == False, make melee atk against adj if any
    # then attempt iceblast against ent in range4-6 if any
    def continue_ai(self, ents_list):
#         atk_sqrs = self.legal_attacks()
        melee_atks = [k for k,v in app.action_target_ents().items() if dist(self.loc, v.loc) == 1 and v.owner != self.owner]
        if melee_atks != []:
            id = choice(melee_atks)
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_melee_attack(el, id)) # ATTACK
        else: # CANNOT ATTACK FROM START LOC, GET TARGET AND MOVE TOWARDS
            enemy_locs = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
            goals = [c for c in app.coords for el in enemy_locs if dist(c, el) == 1 and app.grid[c[0]][c[1]] == '']
            egrid = [[''] * (app.map_height//100) for i in range(app.map_width//100)]
            path = bfs(self.loc[:], goals, egrid[:])
            self.move_along_path(path, ents_list)
                
    def do_melee_attack(self, ents_list, id):
#         self.start_melee_anims()
        effect1 = mixer.Sound('Sound_Effects/dragon_melee.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        my_agl = self.get_abl('agl')
        target_agl = app.ent_dict[id].get_abl('agl')
        if to_hit(my_agl, target_agl) == True:#hit
            my_str = self.get_abl('str')
            target_end = app.ent_dict[id].get_abl('end')
            d = damage(my_str, target_end)
#             pre = app.ent_dict[id].spirit
            lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Claw Rake')
            self.attack_used = True
#             root.after(2555, lambda t = 'text' : app.canvas.delete(t))
            root.after(1666, lambda el = ents_list : self.finish_melee_move(el))
        else:#missed
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'aquamarine', font = ('Andale Mono', 13), tags = 'text')
            self.attack_used = True
            root.after(2555, lambda t = 'text' : app.canvas.delete(t))
            root.after(2666, lambda el = ents_list : self.finish_melee_move(el))
        
    def finish_melee_move(self, ents_list):
        if self.move_used == True and self.attack_used == True: # go to iceblast
            ents = [k for k,v in app.spell_target_ents().items() if 3 <= dist(v.loc, self.loc) <= 5 and v.owner != self.owner]
            if ents == []:
                self.ai_end_turn(ents_list)
            else:
                id = ents[0]
                self.do_iceblast(ents_list, id)
        elif self.attack_used == True: # go to iceblast
            ents = [k for k,v in app.spell_target_ents().items() if 3 <= dist(v.loc, self.loc) <= 5 and v.owner != self.owner]
            if ents == []:
                self.ai_end_turn(ents_list)
            else:
                id = ents[0]
                self.do_iceblast(ents_list, id)
        elif self.move_used: # go to melee
            atk_sqrs = self.legal_attacks()
            melee_atks = [k for k,v in app.action_target_ents().items() if dist(self.loc, v.loc) == 1 and v.owner != self.owner]
            if melee_atks != []:
                id = choice(melee_atks)
                root.after(666, lambda id = id : app.get_focus(id))
                root.after(1333, lambda el = ents_list, id = id : self.do_melee_attack(el, id))
            else: # go to iceblast
                ents = [k for k,v in app.spell_target_ents().items() if 3 <= dist(v.loc, self.loc) <= 5 and v.owner != self.owner]
                if ents == []:
                    self.ai_end_turn(ents_list)
                else:
                    id = ents[0]
                    self.do_iceblast(ents_list, id)
        else: # go to move
            enemy_locs = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
            goals = [c for c in app.coords for el in enemy_locs if dist(c, el) == 1 and app.grid[c[0]][c[1]] == '']
            egrid = [[''] * (app.map_height//100) for i in range(app.map_width//100)]
            path = bfs(self.loc[:], goals, egrid[:])
            self.move_along_path(path, ents_list)
                
    # takes a list of coords, passes an estimate of the 'best' destination coord to self.ai_move
    def move_along_path(self, path, ents_list):
        moves = self.legal_moves()
        if moves == []:
            ents = [k for k,v in app.spell_target_ents().items() if 3 <= dist(v.loc, self.loc) <= 5 and v.owner != self.owner]
            if ents == []:
                self.ai_end_turn(ents_list)
            else:
                id = ents[0]
                do_iceblast(ents_list, id)
        else:
            intrsct = intersect(moves, path)
            if intrsct == []:
                self.ai_end_turn(ents_list)
            else:
                move = list(reduce(lambda a,b : a if dist(self.loc, a) > dist(self.loc, b) else b, intrsct))
                root.after(666, lambda sqr = move : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = move : self.white_dragon_move(el, sqr))
            
    def white_dragon_move(self, ents_list, endloc):
        global selected
        selected = [self.number, self.number+'top']
        app.canvas.delete(self.number)
        app.canvas.delete(self.number+'top')
        self.init_ascend_anims()
        app.canvas.create_image(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+40, image = self.img, tags = self.tags)
        self.type = 'large'
        self.tags = (self.number, 'large')
        effect1 = mixer.Sound('Sound_Effects/dragon_flight.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, -1)
        def ascend_loop(timer):
            if timer == 0:
                self.dragon_flight(ents_list, endloc)
            else:
                self.rotate_image()
                app.canvas.delete(self.number)
                app.canvas.create_image(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+30, image = self.img, tags = self.tags)
                timer -= 1
                root.after(333, lambda t = timer : ascend_loop(t))
        root.after(333, lambda t = 2 : ascend_loop(t))
            
    def dragon_flight(self, ents_list, endloc):
        global selected
        id = self.number
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        endx = endloc[0]*100+50-app.moved_right
        endy = endloc[1]*100+50-app.moved_down
        start_sqr = self.loc[:]
        end_sqr = endloc[:]
        self.init_flight_anims()
        def move_loop(id, x, y, endx, endy, start_sqr, end_sqr, tics):
            if tics == 0:
                tics = 5
                self.rotate_image()
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if x > endx:
                x -= 10
                app.canvas.move(id, -10, 0)
            elif x < endx: 
                x += 10
                app.canvas.move(id, 10, 0)
            if y > endy: 
                y -= 10
                app.canvas.move(id, 0, -10)
            elif y < endy: 
                y += 10
                app.canvas.move(id, 0, 10)
            tics -= 1
            app.canvas.tag_raise('cursor')
            if x == endx and y == endy:
                self.finish_move(id, end_sqr, start_sqr, ents_list)
            else:
                root.after(66, lambda id = id, x = x, y = y, e = endx, e2 = endy, s = start_sqr, s2 = end_sqr, t = tics : move_loop(id, x, y, e, e2, s, s2, t))
        move_loop(id, x, y, endx, endy, start_sqr, end_sqr, 4)
            
    def finish_move(self, id, end_sqr, start_sqr, ents_list):
        self.loc = end_sqr[:]
        app.focus_square(end_sqr)
        app.ent_dict[id+'top'].loc = [end_sqr[0],end_sqr[1]]
        app.grid[start_sqr[0]][start_sqr[1]] = ''
        app.grid[end_sqr[0]][end_sqr[1]] = self.number
        self.move_used = True
        self.init_descend_anims()
        app.canvas.delete(self.number)
        app.canvas.create_image(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+40, image = self.img, tags = self.tags)
        def descend_loop(timer):
            if timer == 0:
                sound_effects.stop()
                self.finish_descend(ents_list)
            else:
                self.rotate_image()
                app.canvas.delete(self.number)
                app.canvas.create_image(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+50, image = self.img, tags = self.tags)
                timer -= 1
                root.after(333, lambda t = timer : descend_loop(t))
        root.after(333, lambda t = 2 : descend_loop(t))
        
    def finish_descend(self, ents_list):
        global selected
        self.init_normal_anims()
        app.canvas.delete(self.number)
        self.type = 'large_bottom'
        self.tags = self.number
        selected = []
        self.finish_melee_move(ents_list)
    
    def do_iceblast(self, ents_list, id):
        app.get_focus(id)
        effect1 = mixer.Sound('Sound_Effects/iceblast.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        ents = [k for k,v in app.all_ents().items() if dist(v.loc, app.ent_dict[id].loc) <= 1]
        if 'b1' in ents:
            ents.remove('b1')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Iceblast', justify ='center', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Iceblast', justify ='center', font = ('Andale Mono', 16), fill = 'aquamarine', tags = 'text')
        def iceblast_loop(ents):
            if ents == []:
                self.ai_end_turn(ents_list)
            else:
                id = ents[0]
                ents = ents[1:]
                n = 'Iceblast' + str(app.effects_counter) # not an effect, just need unique int
                app.effects_counter += 1 # that is why this is incr manually here, no Effect init
                loc = app.ent_dict[id].loc[:]
                app.focus_square(loc)
                app.vis_dict[n] = Vis(name = 'Iceblast', loc = loc)
                def cleanup_vis(name):
                    app.canvas.delete('text')
                    del app.vis_dict[name]
                    app.canvas.delete(name)
                app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = n)
    #         app.ent_dict[self.number+'top'].init_attack_anims()
                my_psyche = self.get_abl('psyche')
                tar_dodge = app.ent_dict[id].get_abl('dodge')
                if to_hit(my_psyche, tar_dodge) == True:#hit
                    tar_psyche = app.ent_dict[id].get_abl('psyche')
                    tar_end = app.ent_dict[id].get_abl('end')
                    tar_psy_end = (tar_psyche+tar_end)//2
                    d = damage(my_psyche, tar_psy_end)
#                     pre = app.ent_dict[id].spirit
                    root.after(1999, lambda n = n : cleanup_vis(n))
                    lock(apply_damage, self, app.ent_dict[id], -d, 'cold', 'Iceblast')
                    iceblast_loop(ents)
                else:#missed
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'aquamarine', font = ('Andale Mono', 13), tags = 'text')
                    root.after(2555, lambda n = n : cleanup_vis(n))
                    root.after(2666, lambda ents = ents : iceblast_loop(ents))
        root.after(1555, lambda t = 'text' : app.canvas.delete(t))
        root.after(1666, lambda ents = ents : iceblast_loop(ents))
        
    # white dragon gets adj and ranged, pared later
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1 or 4 <= dist(c, self.loc) <= 6:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.all_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        for c in app.coords:
            if app.grid[c[0]][c[1]] == '' and 1 <= dist(loc, c) <= self.get_abl('move_range'):
                mvlist.append(c)
        return mvlist
        
        
class Tortured_Soul(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 7
        self.agl = 6
        self.end = 7
        self.dodge = 4
        self.psyche = 2
        self.spirit = 25
        self.move_range = 6
        self.waiting = waiting
        self.resist = ['piercing', 'slashing', 'crushing']
        self.weak = ['poison']
        self.move_type = 'normal'
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.spell_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if 3 <= dist(el,g) <= 4 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if 3 <= dist(el,g) <= 4 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if 3 <= dist(el,g) <= 4 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
            self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/tortured_soul_agony.ogg')
            sound_effects.play(effect1, 0)
            visloc = app.ent_dict[id].loc[:]
            app.vis_dict['Tortured_Soul_Agony'] = Vis(name = 'Tortured_Soul_Agony', loc = visloc)
            app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Tortured_Soul_Agony'].img, tags = 'Tortured_Soul_Agony')
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Agony', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Agony', font = ('Andale Mono', 16), fill = 'orangered4', tags = 'text')
            my_agl = self.get_abl('agl')
            target_dodge = app.ent_dict[id].get_abl('dodge')
            if to_hit(my_agl, target_dodge) == True:# HIT
                my_str = self.get_abl('str')
                tar_psy = app.ent_dict[id].get_abl('psyche')
                d = damage(my_str, tar_psy)
                lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Agony')
                root.after(2666, lambda e = ents_list : self.cleanup_attack(e))
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list : self.cleanup_attack(e))
        
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
        
        
    def cleanup_attack(self, ents_list):
        self.init_normal_anims()
        try: 
            app.canvas.delete('text')
            del app.vis_dict['Tortured_Soul_Agony']
            app.canvas.delete('Tortured_Soul_Agony')
        except: pass
        if self.move_used == False:
            self.get_path(ents_list)
        else:
            self.ai_end_turn(ents_list)
            
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 4:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.spell_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
        
class Skeleton_Archer(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 3
        self.agl = 5
        self.end = 2
        self.dodge = 3
        self.psyche = 2
        self.spirit = 13
        self.move_range = 3
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['slashing', 'piercing', 'poison']
        self.weak = ['crushing', 'magick', 'fire']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
#             self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/undead_archer_attack.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Black Arrow', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Black Arrow', font = ('Andale Mono', 16), fill = 'gray88', tags = 'text')
            root.after(2111, lambda id = id : app.get_focus(id))
            root.after(2111, lambda t = 'text' : app.canvas.delete('text'))
            root.after(2333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
        
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if 4 <= dist(el,g) <= 16 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if 4 <= dist(el,g) <= 16 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if 4 <= dist(el,g) <= 16 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    # returned to from ai_move() (after moving, usually but not necessarily without attacking)
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
#                 self.init_attack_anims()
                effect1 = mixer.Sound('Sound_Effects/undead_archer_attack.ogg')
                effect1.set_volume(1)
                sound_effects.play(effect1, 0)
                app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Black Arrow', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
                app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Black Arrow', font = ('Andale Mono', 16), fill = 'gray88', tags = 'text')
                root.after(2111, lambda id = id : app.get_focus(id))
                root.after(2111, lambda t = 'text' : app.canvas.delete('text'))
                root.after(2333, lambda el = ents_list, t = id : self.do_attack(el, t)) # EXIT THROUGH ATTACK
            else:
                self.ai_end_turn(ents_list)
        elif self.move_used == False:
            self.get_path(ents_list)
        else:
            self.ai_end_turn(ents_list)

            
    def do_attack(self, ents_list, id):
        self.init_normal_anims()
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
            visloc = app.ent_dict[id].loc[:]
            app.vis_dict['Black_Arrow'] = Vis(name = 'Black_Arrow', loc = visloc)
            app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Black_Arrow'].img, tags = 'Black_Arrow')
            my_agl = self.get_abl('agl')
            target_dodge = app.ent_dict[id].get_abl('dodge')
            if to_hit(my_agl, target_dodge) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                lock(apply_damage, self, app.ent_dict[id], -d, 'piercing', 'Black Arrow')
                root.after(666, lambda e = ents_list : self.cleanup_attack(e))
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list : self.cleanup_attack(e))
        
        
    def cleanup_attack(self, ents_list):
#         self.init_normal_anims()
        try: 
            app.canvas.delete('text')
            del app.vis_dict['Black_Arrow']
            app.canvas.delete('Black_Arrow')
        except: pass
        self.ai_end_turn(ents_list)
            
#     def finish_attack(self, ents_list):
#         self.init_normal_anims()
#         try: app.canvas.delete('text')
#         except: pass
#         self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if 4 <= dist(c, self.loc) <= 16:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
class Ghost(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 7
        self.agl = 9
        self.end = 8
        self.dodge = 9
        self.psyche = 11
        self.spirit = 75
        self.move_range = 4
        self.times_retreated = 0
        self.waiting = waiting
        self.move_type = 'ethereal'
        self.resist = ['slashing', 'piercing', 'crushing', 'poison']
        self.weak = ['fire', 'elec', 'cold']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    #  GHOST AI
    # change to: cast fear, slow, or willowisp w/i range, then Wail(equake no dmg), then move randomly w/i 4
    # only act if ent w/i range of spells
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        elif app.map_number == 21 and self.times_retreated == 0 and self.spirit < 45:
            for func in app.map_triggers[:]:
                if func.__name__ == 'ghost_death':
                    app.map_triggers.remove(func)
            self.times_retreated += 1
            # erase from map / ent_dict, place map_trigger to watch 1,2 2,2 3,2
            to_remove = []
            for k,v in app.ent_dict['b2'].effects_dict.items():
                v.undo_func()
                to_remove.append(k)
            for k in to_remove:
                del app.ent_dict['b2'].effects_dict[k]
            loc = app.ent_dict['b2'].loc[:]
            app.vis_dict['Ghost_Disappear'] = Vis(name = 'Ghost_Disappear', loc = loc[:])
            app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict['Ghost_Disappear'].img, tags = 'Ghost_Disappear')
            def cleanup_ghost_disappear():
                del app.vis_dict['Ghost_Disappear']
                app.canvas.delete('Ghost_Disappear')
            root.after(1333, cleanup_ghost_disappear)
            app.grid[loc[0]][loc[1]] = ''
            app.ent_dict['b2'].loc = [0,0]
            app.canvas.delete('b2')
            ghost = app.ent_dict['b2']
            del app.ent_dict['b2']
            def ghost_area2(ghost):
                if app.grid[1][2] == '' or app.grid[2][2] == '' or app.grid[3][2] == '':
                    # place ghost
                    locs = [c for c in [[1,2],[2,2],[3,2]] if app.grid[c[0]][c[1]] == '']
                    loc = choice(locs)
                    app.ent_dict['b2'] = ghost
                    app.ent_dict['b2'].loc = loc[:]
                    app.grid[loc[0]][loc[1]] = 'b2'
                    app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.ent_dict['b2'].img, tags = 'b2')
                    # create ghost death/victory trigger
                    def ghost_death2():
                        if 'b2' not in app.ent_dict.keys():
                            return 'victory'
                    app.map_triggers.append(ghost_death2)
                    app.map_triggers.remove(ghosty)
            ghosty = partial(ghost_area2, ghost)
            app.map_triggers.append(ghosty)
            self.ai_end_turn(ents_list)
        else: # ATTEMPT ATTACK FROM STARTLOC
            action_ents = [k for k,v in app.action_target_ents().items() if v.owner != self.owner and dist(v.loc, self.loc) <= 6]
            spell_ents = [k for k,v in app.spell_target_ents().items() if v.owner != self.owner and dist(v.loc, self.loc) <= 6]
            slow_ents = [k for k,v in app.spell_target_ents().items() if v.owner != self.owner and dist(v.loc, self.loc) <= 6 and 'Slow' not in [j.name for i,j in v.effects_dict.items()]]
            rando = []
            if action_ents != []:
                rando.append('action')
            if spell_ents != []:
                rando.append('spell')
            if spell_ents != []:
                rando.append('slow')
            if rando != []:
                r = choice(rando)
                if r == 'action':
                    id = choice(action_ents)
                    kind = 'fear'
                elif r == 'spell':
                    id = choice(spell_ents)
                    kind = 'willowisp'
                elif r == 'slow':
                    id = choice(slow_ents)
                    kind = 'slow'
                root.after(666, lambda id = id : app.get_focus(id))
                root.after(1333, lambda el = ents_list, id = id, kind = kind : self.do_attack(el, id, kind))
            else:
                self.ai_end_turn(ents_list)
                    
    # change to cast one of 3 rand spells
    def do_attack(self, ents_list, id, kind):
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            app.get_focus(id)
            if kind == 'fear':
                self.fear(id, ents_list)
            elif kind == 'willowisp':
                self.willowisp(id, ents_list)
            elif kind == 'slow':
                self.slow(id, ents_list)
    
    # tar gets psy reduction, mov reduce by 1, and psy v psy atk with psy v psy dmg
    def fear(self, id, ents_list):
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Fear', justify = 'center', fill = 'black', font = ('Andale Mono', 15), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Fear', justify = 'center', fill = 'bisque2', font = ('Andale Mono', 15), tags = 'text')
        root.after(2555, lambda t = 'text' : app.canvas.delete(t))
        obj = app.ent_dict[id]
        ents = [k for k,v in app.ent_dict.items() if dist(v.loc, obj.loc) <= 1 and v.owner == obj.owner]
        def fear_loop(ents):
            if ents == []:
                self.cleanup_attack(ents_list)
            else:
                id = ents[0]
                ents = ents[1:]
                app.get_focus(id)
                # do dmg
                my_psy = self.get_abl('psyche')
                tar_psy = app.ent_dict[id].get_abl('psyche')
                loc = app.ent_dict[id].loc[:]
                if to_hit(my_psy, tar_psy) == True:
                    d = damage(my_psy, tar_psy)
                    pre = app.ent_dict[id].spirit
                    lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Fear')
                    if 'Fear' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
                        def fear_move(move_range):
                            move_range -= 1
                            if move_range < 0:
                                return 0
                            else:
                                return move_range
                        app.ent_dict[id].move_effects.append(fear_move)
                        def fear_effect(stat):
                            stat -= 1
                            return max(1, stat)
                        app.ent_dict[id].psyche_effects.append(fear_effect)
                        def undo(tar, fe):
                            app.ent_dict[tar].move_effects.remove(fear_move)
                            app.ent_dict[tar].psyche_effects.remove(fe)
                        u = partial(undo, id, fear_effect)
                        n = 'Fear'+str(app.effects_counter)
                        app.effects_counter += 1
                        app.ent_dict[id].effects_dict[n] = Effect(name = 'Fear', undo_func = u, duration = 7, level = 8)
                        app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+54, text = 'Fear...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                        app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+55, text = 'Fear...', justify = 'center', fill = 'bisque2', font = ('Andale Mono', 13), tags = 'text')
                        root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                        root.after(1666, lambda ents = ents : fear_loop(ents))
                    else:
                        root.after(666, lambda ents = ents : fear_loop(ents))
                else:
                    app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'bisque2', font = ('Andale Mono', 13), tags = 'text')
                    root.after(2555, lambda t = 'text' : app.canvas.delete(t))
                    root.after(2666, lambda ents = ents : fear_loop(ents))
        fear_loop(ents)
    
    # tar gets move reduce by 3 and atk efct dmg halved rounded down min1
    def slow(self, id, ents_list):
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Slow', justify = 'center', fill = 'black', font = ('Andale Mono', 15), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Slow', justify = 'center', fill = 'bisque2', font = ('Andale Mono', 15), tags = 'text')
        root.after(2555, lambda t = 'text' : app.canvas.delete(t))
        obj = app.ent_dict[id]
        ents = [k for k,v in app.ent_dict.items() if dist(v.loc, obj.loc) <= 1 and v.owner == obj.owner]
        def slow_loop(ents):
            if ents == []:
                self.cleanup_attack(ents_list)
            else:
                id = ents[0]
                ents = ents[1:]
                if 'Slow' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
                    app.get_focus(id)
                    loc = app.ent_dict[id].loc[:]
                    def slow_move(move_range):
                        move_range -= 2
                        if move_range < 0:
                            return 0
                        else:
                            return move_range
                    app.ent_dict[id].move_effects.append(slow_move)
                    def slow_atk(atkr, dfndr, dmg, type):
                        loc = atkr.loc[:]
                        if type == 'melee' or type == 'ranged':
                            app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+74, text = 'Attack Slowed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                            app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+75, text = 'Attack Slowed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                            root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                            if dmg < 0:
                                return (min(-1, dmg//2), 1666)
                            else:
                                return (dmg, 0)
                        else:
                            return (dmg, 0)
                    app.ent_dict[id].attack_effects.append(slow_atk)
                    def undo(tar, sa):
                        app.ent_dict[tar].move_effects.remove(slow_move)
                        app.ent_dict[tar].attack_effects.remove(sa)
                    u = partial(undo, id, slow_atk)
                    n = 'Slow'+str(app.effects_counter)
                    app.effects_counter += 1
                    app.ent_dict[id].effects_dict[n] = Effect(name = 'Slow', undo_func = u, duration = 4, level = 6)
                    
                    # create vis and text
                    app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+74, text = 'Slowed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+75, text = 'Slowed...', justify = 'center', fill = 'bisque2', font = ('Andale Mono', 13), tags = 'text')
                    root.after(2555, lambda t = 'text' : app.canvas.delete(t))
                    root.after(2666, lambda ents = ents : slow_loop(ents))
                else:
                    slow_loop(ents)
        slow_loop(ents)

    # psy v end dmg, end save at -2 or get burn effect, move target to rand sqr w/i rang 4 (use normal move pathing)
    def willowisp(self, id, ents_list):
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = "Will o'Wisp", justify = 'center', fill = 'black', font = ('Andale Mono', 15), tags = 'wisp_text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = "Will o'Wisp", justify = 'center', fill = 'bisque2', font = ('Andale Mono', 15), tags = 'wisp_text')
        root.after(2555, lambda t = 'wisp_text' : app.canvas.delete(t))
        my_psy = self.get_abl('psyche')
        tar_end = app.ent_dict[id].get_abl('end')
        d = damage(my_psy, tar_end)+2
        pre = app.ent_dict[id].spirit
        lock(apply_damage, self, app.ent_dict[id], -d, 'fire', "Will o' Wisp")
        if 'Burn' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
            loc = app.ent_dict[id].loc[:]
            app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+54, text = 'Burned...', justify = 'center', fill = 'black', font = ('Andale Mono', 14), tags = 'text')
            app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+55, text = 'Burned...', justify = 'center', fill = 'orangered2', font = ('Andale Mono', 14), tags = 'text')
            root.after(2555, lambda t = 'text' : app.canvas.delete(t))
            def burn_effect(attacker, defender, amount, type):
                if amount < 0 and (type == 'melee' or type == 'ranged'):
                    app.canvas.create_text(defender.loc[0]*100+49-app.moved_right, defender.loc[1]*100+54-app.moved_down, text = '+2 spirit burn', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(defender.loc[0]*100+50-app.moved_right, defender.loc[1]*100+55-app.moved_down, text = '+2 spirit burn', justify ='center', font = ('Andale Mono', 13), fill = 'orangered2', tags = 'text')
                    root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                    amount -= 2
                    return (amount, 1666)
                else:
                    return (amount, 0)
            app.ent_dict[id].defense_effects.append(burn_effect)
            def undo(tar):
                app.ent_dict[tar].defense_effects.remove(burn_effect)
            u = partial(undo, id)
            n = 'Burn'+str(app.effects_counter)
            app.effects_counter += 1
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Burn', undo_func = u, duration = 9, level = 6)
            # insert rndmly move tar
            sqrs = [s for s in app.coords if dist(s, loc) <= 4 and app.grid[s[0]][s[1]] == '' and bfs(loc, [s], app.grid) and len(bfs(loc, [s], app.grid)) <= 5]
            if sqrs == []:
                root.after(666, lambda el = ents_list : self.cleanup_attack(el))
            else:
                sqr = choice(sqrs)
                app.focus_square(sqr)
                app.ent_dict[id].do_move(event = None, sqr = sqr, sqrs = [sqr])
                root.after(4666, lambda el = ents_list : self.cleanup_attack(el))
        else:
            root.after(666, lambda el = ents_list : self.cleanup_attack(el))
        
    def cleanup_attack(self, ents_list):
#         self.init_normal_anims()
        try: 
            app.canvas.delete('text')
#             del app.vis_dict['']
#             app.canvas.delete('')
        except: pass
        # insert Wail (equak no dmg), then 'wander'
        self.wail(ents_list)
        
    # change to ensure path is no greater than 2 or 3, only move to increase distance from ghost
    def wail(self, ents_list):
        sqrs = [c for c in app.coords if dist(c,self.loc) <= 6]
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+84-app.moved_down, text = 'Wail', font = ('Andale Mono', 17), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+85-app.moved_down, text = 'Wail', font = ('Andale Mono', 17), fill = 'bisque2', tags = 'text')
        root.after(2555, lambda t = 'text' : app.canvas.delete(t))
#         app.vis_dict['Wail'] = Vis(name = 'Wail', loc = self.loc[:])
#         app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Wail'].img, tags = 'Wail')
        ents = [k for k,v in app.ent_dict.items() if v.owner != self.owner and v.loc in sqrs ]
        def wail_loop(ents):
            if ents == []:
                self.wander(ents_list)
            else:
                id = ents[0]
                ents = ents[1:]
                loc = app.ent_dict[id].loc
                app.get_focus(id)
                sqrs = [s for s in app.coords if dist(s, loc) <= 2 and app.grid[s[0]][s[1]] == '' and dist(s,self.loc) >= dist(loc,self.loc) and bfs(loc, [s], app.grid) and len(bfs(loc, [s], app.grid)) <= 3]
                if sqrs == []:
                    root.after(666, lambda ents = ents : wail_loop(ents))
                else:
                    sqr = choice(sqrs)
                    app.focus_square(sqr)
                    app.ent_dict[id].do_move(event = None, sqr = sqr, sqrs = [sqr])
                    root.after(3666, lambda ents = ents : wail_loop(ents))
        root.after(2666, lambda ents = ents : wail_loop(ents))
        
    def wander(self, ents_list):
        sqrs = [s for s in app.coords if dist(self.loc, s) <= self.get_abl('move_range') and app.grid[s[0]][s[1]] == '']
        if sqrs == []:
            self.ai_end_turn(ents_list)
        else:
            sqr = choice(sqrs)
            self.do_flying_move(event = None, sqr = sqr, sqrs = [sqr])
            root.after(3666, lambda el = ents_list : self.ai_end_turn(el))

        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 6:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner:
                        sqrs.append(c)
        return sqrs
        
class Revenant(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 4
        self.agl = 5
        self.end = 5
        self.dodge = 5
        self.psyche = 7
        self.spirit = 16
        self.move_range = 5
        self.waiting = waiting
        self.move_type = 'ethereal'
        self.resist = ['slashing', 'piercing', 'crushing', 'poison']
        self.weak = ['fire', 'elec', 'cold', 'acid']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    #  REVENANT AI
    def do_ai(self, ents_list):
        if self.waiting == True: 
            self.pass_priority(ents_list)
        else: # ATTEMPT ATTACK FROM STARTLOC
            self.continue_ai(ents_list)
            
    # has flight/ethereal move through obstacles
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.spell_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if 1 <= dist(el,g) <= 2 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if 1 <= dist(el,g) <= 2 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if 1 <= dist(el,g) <= 2 and app.grid[g[0]][g[1]] == '']
        if gs1 == []:
            if gs2 == []:
                if gs3 == []:
                    self.ai_end_turn(ents_list)
                else:
                    g = reduce(lambda a,b : a if dist(a,self.loc) < dist(b,self.loc) else b, gs3)
            else:
                g = reduce(lambda a,b : a if dist(a,self.loc) < dist(b,self.loc) else b, gs2)
        else:
            g = reduce(lambda a,b : a if dist(a,self.loc) < dist(b,self.loc) else b, gs1)
        ms = self.legal_moves()
        moves = [m for m in ms if m in cs]
        if moves == []:
            if ms == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,g) < dist(b,g) else b, ms)
                root.after(333, lambda id = self.number : app.get_focus(id))
                root.after(999, lambda el = ents_list, sqr = m : self.revenant_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,g) < dist(b,g) else b, moves)
            root.after(333, lambda id = self.number : app.get_focus(id))
            root.after(999, lambda el = ents_list, sqr = m : self.revenant_move(el, sqr))
            
    def revenant_move(self, ents_list, sqr):
        global selected
        selected = [self.number]
        app.focus_square(sqr)
        effect1 = mixer.Sound('Sound_Effects/revenant_move.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        endx = sqr[0]*100+50-app.moved_right
        endy = sqr[1]*100+50-app.moved_down
        start_sqr = self.loc[:]
        end_sqr = sqr[:]
        total_distance = abs(x - endx) + abs(y - endy)
        # tic doesnt matter for circular image loop, would need to make flying_anims and switch to
        tic = 60 #total_distance/9 # Magic Number debug, number of images for vis
        if x == endx:
            xstep = 0
            ystep = 10
        elif y == endy:
            xstep = 10
            ystep = 0
        else:
            slope = Fraction(abs(x - endx), abs(y - endy))
            # needs to be moving at least 10 pixels, xstep + ystep >= 10
            xstep = slope.numerator
            ystep = slope.denominator
            while xstep + ystep < 10:
                xstep *= 2
                ystep *= 2
        def flying_arc(x, y, endx, endy, start_sqr, end_sqr, acm, tic, xstep, ystep):
            if acm >= tic:
                acm = 0
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if x > endx:
                acm += xstep
                x -= xstep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            elif x < endx:
                acm += xstep
                x += xstep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if y > endy:
                acm += ystep
                y -= ystep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            elif y < endy:
                acm += ystep
                y += ystep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if abs(x - endx) < 13 and abs(y - endy) < 13:
                self.finish_move(self.number, end_sqr, start_sqr, ents_list)
            else: # CONTINUE LOOP
                root.after(66, lambda x = x, y = y, e = endx, e2 = endy, s = start_sqr, s2 = end_sqr, acm = acm, tic = tic, xs = xstep, ys = ystep : flying_arc(x, y, e, e2, s, s2, acm, tic, xs, ys))
        flying_arc(x, y, endx, endy, start_sqr, end_sqr, tic+1, tic, xstep, ystep)
            
            
    def finish_move(self, id, end_sqr, start_sqr, ents_list):
        global selected
        selected = []
        self.loc = end_sqr[:]
        app.grid[start_sqr[0]][start_sqr[1]] = ''
        app.grid[end_sqr[0]][end_sqr[1]] = self.number
        # MAKE ATTACK ON ANY ENEMY ENT WITHIN RANGE
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []:
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda t = id : app.get_focus(t))
            root.after(1333, lambda el = ents_list, t = id : self.do_attack(el, t)) # EXIT THROUGH ATTACK
        else:
        # CANNOT ATTACK, EXIT FUNC
            root.after(1333, lambda el = ents_list : self.ai_end_turn(el))
    
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            app.get_focus(id)
    #         self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/revenant_terror.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            visloc = app.ent_dict[id].loc[:]
            app.vis_dict['Revenant_Terror'] = Vis(name = 'Revenant_Terror', loc = visloc)
            app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Revenant_Terror'].img, tags = 'Revenant_Terror')
            app.canvas.create_text(visloc[0]*100+49-app.moved_right, visloc[1]*100+104-app.moved_down, text = 'Terror', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(visloc[0]*100+50-app.moved_right, visloc[1]*100+105-app.moved_down, text = 'Terror', font = ('Andale Mono', 16), fill = 'gray77', tags = 'text')
            my_psyche = self.get_abl('psyche')
            target_psyche = app.ent_dict[id].get_abl('psyche')
            if to_hit(my_psyche, target_psyche) == True:
                d = damage(my_psyche, target_psyche)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Terror')
                root.after(666, lambda  el = ents_list, id = id : self.cleanup_attack(el, id))
            else:
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(1666, lambda  el = ents_list, id = id : self.cleanup_attack(el, id))
            
    def cleanup_attack(self, ents_list, id):
        self.init_normal_anims()
        try: 
            app.canvas.delete('text')
            del app.vis_dict['Revenant_Terror']
            app.canvas.delete('Revenant_Terror')
        except: pass
        if app.ent_dict[id].spirit <= 0:
            name = 'dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(666, lambda id = id, name = name : app.kill(id, name))
            root.wait_variable(app.dethloks[name])
            self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 2:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.spell_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        for c in app.coords:
            if dist(loc, c) <= self.get_abl('move_range') and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist
        
# make cut attack against numerous ents, cannot have stats altered
class Kensai(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 4
        self.agl = 8
        self.end = 5
        self.dodge = 9
        self.psyche = 8
        self.spirit = 59
        self.move_range = 4
        self.times_attacked = 0
        self.attacked_ids = []
        self.waiting = waiting
        self.move_type = 'normal'
        self.weak = ['cold', 'slashing']
        self.resist = ['piercing', 'crushing']
        super().__init__(name, img, loc, owner, number)
        
    def get_attr(self, attr):
        if attr == 'str':
            return self.base_str
        elif attr == 'end':
            return self.base_end
        elif attr == 'agl':
            return self.base_agl
        elif attr == 'dodge':
            return self.base_dodge
        elif attr == 'psyche':
            return self.base_psyche
        elif attr == 'move_range':
            q = self.move_effects + app.loc_effects_dict[tuple(self.loc)].move_effects
            base = self.move_range
            for func in q:
                base = func(base)
            return base
            
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    #  KENSAI AI
    def do_ai(self, ents_list):
        if self.waiting == True: # WAITING, PASSIVE, PASS PRIORITY
            self.pass_priority(ents_list)
        else: # NO TARGET PRIORITY, ATTEMPT ATTACK FROM STARTLOC
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            app.get_focus(id)
            self.init_attack_anims()
    #         effect1 = mixer.Sound('Sound_Effects/kensai_cut.ogg')
    #         effect1.set_volume(1)
    #         sound_effects.play(effect1, 0)
            visloc = app.ent_dict[id].loc[:]
            app.vis_dict['Kensai_Cut'] = Vis(name = 'Kensai_Cut', loc = visloc)
            app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Kensai_Cut'].img, tags = 'Kensai_Cut')
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:
                my_str = self.get_abl('str')
                target_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, target_end)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'melee', 'Cut')
                root.after(666, lambda e = ents_list, i = id : self.cleanup_attack(e, id)) # EXIT THROUGH CLEANUP_ATTACK()
            else:
                # MISSED, SHOW VIS, EXIT THROUGH CLEANUP_ATTACK()
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(1666, lambda e = ents_list, i = id : self.cleanup_attack(e, id))
        
    def cleanup_attack(self, ents_list, id):
        self.init_normal_anims()
        try: 
            del app.vis_dict['Kensai_Cut']
            app.canvas.delete('Kensai_Cut')
        except: pass
        try: app.canvas.delete('text')
        except: pass
        if app.ent_dict[id].spirit <= 0:
            name = 'dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(666, lambda id = id, name = name : app.kill(id, name))
            root.wait_variable(app.dethloks[name])
            self.continue_cleanup(ents_list, id)
        else:
            self.continue_cleanup(ents_list, id)
                
    def continue_cleanup(self, ents_list, id):
        self.attacked_ids.append(id)
        if self.times_attacked < 4:
            pot_targets = [k for k,v in app.action_target_ents().items() if dist(v.loc, self.loc) <= 3 and v.owner != self.owner and k not in self.attacked_ids]
            if pot_targets != []:
                id = choice(pot_targets)
                self.times_attacked += 1
                self.do_ai(ents_list)
            else:
                self.end_attack(ents_list)
        else:
            self.end_attack(ents_list)
                
    def end_attack(self, ents_list):
#         self.times_attacked = 0
#         self.attacked_ids = []
        ents_list = ents_list[1:]
        if ents_list == []:
            app.end_turn()
        else:
            root.after(666, lambda e = ents_list : app.do_ai_loop(e))
        
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist

class Kobold_Cleric(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 3
        self.agl = 4
        self.end = 5
        self.dodge = 4
        self.psyche = 5
        self.spirit = 11
        self.move_range = 4
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['poison', 'fire', 'cold', 'elec']
        self.weak = ['magick', 'crushing']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    # hex is stat effects to enemies, chant buff friendly, then do melee
    def continue_ai(self, ents_list):
        # first check for hex or warcry cast
        hex_tars = [k for k,v in app.spell_target_ents().items() if dist(v.loc, self.loc) <= 4 and v.owner != self.owner and 'Hex' not in [j.name for i,j in v.effects_dict.items()]]
        warcry_tars = [k for k, v in app.spell_target_ents().items() if 1 <= dist(v.loc, self.loc) <= 4 and v.owner == self.owner and 'Warcry' not in [j.name for i,j in v.effects_dict.items()]]
        if len(hex_tars) >= 1:
            app.get_focus(self.number)
            app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Hex', justify = 'center', fill = 'black', font = ('Andale Mono', 15), tags = 'text')
            app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Hex', justify = 'center', fill = 'gray88', font = ('Andale Mono', 15), tags = 'text')
            tar = choice(hex_tars)
            ents = [k for k,v in app.all_ents().items() if dist(v.loc, app.ent_dict[tar].loc) < 1 and v.owner != self.owner and 'Hex' not in [j.name for i,j in v.effects_dict.items()]]
            def hex_loop(ents):
                if ents == []:
                    self.finish_ai(ents_list)
                else:
                    id = ents[0]
                    ents = ents[1:]
                    app.get_focus(id)
                    visloc = app.ent_dict[id].loc[:]
                    def cleanup_hex(name):
                        app.canvas.delete(name)
                        del app.vis_dict[name]
                        app.canvas.delete('text')
                    name = 'Hex' + str(app.effects_counter)
                    app.effects_counter += 1
                    app.vis_dict[name] = Vis(name = 'Hex', loc = visloc)
                    app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict[name].img, tags = name)
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hex, -1 stats', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hex, -1 stats', justify = 'center', fill = 'gray88', font = ('Andale Mono', 13), tags = 'text')
                    
                    def hex_effect(stat):
                        stat -= 1
                        if stat < 1:
                            return 1
                        else:
                            return stat
                    f = hex_effect
                    app.ent_dict[id].str_effects.append(f)
                    app.ent_dict[id].end_effects.append(f)
                    app.ent_dict[id].agl_effects.append(f)
                    app.ent_dict[id].dodge_effects.append(f)
                    app.ent_dict[id].psyche_effects.append(f)
                    def un(i):
                        app.ent_dict[i].str_effects.remove(hex_effect)
                        app.ent_dict[i].end_effects.remove(hex_effect)
                        app.ent_dict[i].agl_effects.remove(hex_effect)
                        app.ent_dict[i].dodge_effects.remove(hex_effect)
                        app.ent_dict[i].psyche_effects.remove(hex_effect)
                        return None
                    p = partial(un, id)
                    n = 'Hex' + str(app.effects_counter)
                    app.ent_dict[id].effects_dict[n] = Effect(name = 'Hex', undo_func = p, duration = 4, level = 3)
                    root.after(2111, lambda name = name : cleanup_hex(name))
                    root.after(2333, lambda ents = ents : hex_loop(ents))
            root.after(999, lambda t = 'text' : app.canvas.delete(t))
            root.after(1111, lambda ents = ents : hex_loop(ents))
        elif len(warcry_tars) >= 1:
            app.get_focus(self.number)
            app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Warcry', justify = 'center', fill = 'black', font = ('Andale Mono', 15), tags = 'text')
            app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Warcry', justify = 'center', fill = 'gray88', font = ('Andale Mono', 15), tags = 'text')
            tar = choice(warcry_tars)
            ents = [k for k,v in app.all_ents().items() if dist(v.loc, app.ent_dict[tar].loc) < 1 and v != self and v.owner == self.owner and 'Warcry' not in [j.name for i,j in v.effects_dict.items()]]
            def warcry_loop(ents):
                if ents == []:
                    self.finish_ai(ents_list)
                else:
                    id = ents[0]
                    ents = ents[1:]
                    app.get_focus(id)
                    visloc = app.ent_dict[id].loc[:]
                    def cleanup_warcry(name):
                        app.canvas.delete(name)
                        del app.vis_dict[name]
                        app.canvas.delete('text')
                    name = 'Warcry' + str(app.effects_counter)
                    app.effects_counter += 1
                    app.vis_dict[name] = Vis(name = 'Warcry', loc = visloc)
                    app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict[name].img, tags = name)
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Warcry, +1 stats', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Warcry, +1 stats', justify = 'center', fill = 'salmon1', font = ('Andale Mono', 13), tags = 'text')
                    
                    def warcry_effect(stat):
                        stat += 1
                        if stat < 1:
                            return 1
                        else:
                            return stat
                    f = warcry_effect
                    app.ent_dict[id].str_effects.append(f)
                    app.ent_dict[id].end_effects.append(f)
                    app.ent_dict[id].agl_effects.append(f)
                    app.ent_dict[id].dodge_effects.append(f)
                    app.ent_dict[id].psyche_effects.append(f)
                    def un(i):
                        app.ent_dict[i].str_effects.remove(warcry_effect)
                        app.ent_dict[i].end_effects.remove(warcry_effect)
                        app.ent_dict[i].agl_effects.remove(warcry_effect)
                        app.ent_dict[i].dodge_effects.remove(warcry_effect)
                        app.ent_dict[i].psyche_effects.remove(warcry_effect)
                        return None
                    p = partial(un, id)
                    n = 'Warcry' + str(app.effects_counter)
                    app.ent_dict[id].effects_dict[n] = Effect(name = 'Warcry', undo_func = p, duration = 4, level = 3)
                    root.after(2111, lambda name = name : cleanup_warcry(name))
                    root.after(2333, lambda ents = ents : warcry_loop(ents))
            root.after(999, lambda t = 'text' : app.canvas.delete(t))
            root.after(1111, lambda ents = ents : warcry_loop(ents))
        else:
            self.finish_ai(ents_list)
            
    def finish_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.ai_end_turn(ents_list)
        else:
            app.get_focus(id)
#             self.init_attack_anims()
#             effect1 = mixer.Sound('Sound_Effects/fire_elemental_attack.ogg')
#             sound_effects.play(effect1, 0)
            my_agl = self.get_abl('agl')
            tar_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, tar_agl ) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Scratch')
                root.after(666, lambda e = ents_list : self.ai_end_turn(e))
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                root.after(1666, lambda e = ents_list : self.ai_end_turn(e))
            
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
            
            
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist


class Kobold_Shaman(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 2
        self.agl = 5
        self.end = 3
        self.dodge = 5
        self.psyche = 4
        self.spirit = 13
        self.move_range = 4
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['poison', 'fire', 'cold', 'elec']
        self.weak = ['magick', 'crushing']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.spell_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if 3 <= dist(el,g) <= 4 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if 3 <= dist(el,g) <= 4 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if 3 <= dist(el,g) <= 4 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        global selected_vis
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            self.attack_used = True
            app.get_focus(id)
    #         self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/fire_elemental_attack.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            loc = app.ent_dict[id].loc[:]
            app.vis_dict['Fire_Elem_Ball'] = Vis(name = 'Fire_Elem_Ball', loc = self.loc[:])
            app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
            selected_vis = ['Fire_Elem_Ball']
            def fireball_loop(startx, endx, starty, endy, xstep, ystep):
                if starty > endy:
                    starty -= ystep
                    app.canvas.delete('Fire_Elem_Ball')
                    app.canvas.create_image(startx, starty, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
                    app.canvas.tag_raise('Fire_Elem_Ball')
                elif starty < endy:
                    starty += ystep
                    app.canvas.delete('Fire_Elem_Ball')
                    app.canvas.create_image(startx, starty, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
                    app.canvas.tag_raise('Fire_Elem_Ball')
                if startx > endx:
                    startx -= xstep
                    app.canvas.delete('Fire_Elem_Ball')
                    app.canvas.create_image(startx, starty, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
                    app.canvas.tag_raise('Fire_Elem_Ball')
                elif startx < endx:
                    startx += xstep
                    app.canvas.delete('Fire_Elem_Ball')
                    app.canvas.create_image(startx, starty, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
                    app.canvas.tag_raise('Fire_Elem_Ball')
                    # debug here, if within certain range...
                app.vis_dict['Fire_Elem_Ball'].rotate_image()
                if abs(starty - endy) < 13 and abs(startx - endx) < 13:
                    root.after(333, lambda el = ents_list, id = id : self.continue_attack(el, id))
                else:
                    root.after(40, lambda sx = startx, ex = endx, sy = starty, ey = endy, xs = xstep, ys = ystep  : fireball_loop(sx, ex, sy, ey, xs, ys))
            startx = self.loc[0]*100+50-app.moved_right
            starty = self.loc[1]*100+50-app.moved_down
            endx = loc[0]*100+50-app.moved_right
            endy = loc[1]*100+50-app.moved_down
            if startx == endx:
                xstep = 0
                ystep = 10
            elif starty == endy:
                xstep = 10
                ystep = 0
            else:
                slope = Fraction(abs(startx - endx), abs(starty - endy))
                # needs to be moving at least 10 pixels, xstep + ystep >= 10
                xstep = slope.numerator
                ystep = slope.denominator
                while xstep + ystep < 10:
                    xstep *= 2
                    ystep *= 2
            fireball_loop(startx, endx, starty, endy, xstep, ystep)
            
    def continue_attack(self, ents_list, id):
        loc = app.ent_dict[id].loc[:]
        my_psyche = self.get_abl('psyche')
        target_dodge = app.ent_dict[id].get_abl('dodge')
        def cleanup_fireball():
            global selected_vis
            selected_vis = []
            self.init_normal_anims()
            try: 
#                 app.canvas.delete('text')
                del app.vis_dict['Fire_Elem_Ball']
                app.canvas.delete('Fire_Elem_Ball')
            except: pass
        if to_hit(my_psyche, target_dodge) == True:
            target_end = app.ent_dict[id].get_abl('end')
            d = damage(my_psyche, target_end)
            root.after(666, cleanup_fireball)
            lock(apply_damage, self, app.ent_dict[id], -d, 'fire', 'Fireball')
            root.after(666, lambda e = ents_list : self.finish_attack(e))
        else:# MISS
            app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(666, cleanup_fireball)
            root.after(999, lambda t = 'text' : app.canvas.delete(t))
            root.after(999, lambda e = ents_list : self.finish_attack(e))
            
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
            
                    
    def finish_attack(self, ents_list):
        if self.move_used == False:
            self.get_path(ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 4:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.spell_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        

class Ghoul(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 5
        self.agl = 4
        self.end = 5
        self.dodge = 2
        self.psyche = 3
        self.spirit = 13
        self.move_range = 3
        self.waiting = waiting
        self.move_type = 'normal'
        self.weak = ['magick', 'crushing', 'fire']
        self.resist = ['slashing', 'piercing', 'poison']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
            self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/undead_attack.ogg')
            sound_effects.play(effect1, 0)
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                d = d//2
                if d == 0:
                    d = 1
                lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Venomous Bite')
                if id in app.all_ents().keys() and 'Ghoul_Venom' not in app.ent_dict[id].effects_dict.keys():# HIT, NO KILL add ghoul_venom if not exists
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = 'Ghoul Venom...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = 'Ghoul Venom...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    def ghoul_effect(stat):
                        stat -= 1
                        if stat < 1:
                            return 1
                        else:
                            return stat
                    app.ent_dict[id].str_effects.append(ghoul_effect)
                    app.ent_dict[id].end_effects.append(ghoul_effect)
                    def un(i):
                        app.ent_dict[i].str_effects.remove(ghoul_effect)
                        app.ent_dict[i].end_effects.remove(ghoul_effect)
                        return None
                    p = partial(un, id)
                    # EOT FUNC
                    def take_2(tar, lockname = None):
                        app.get_focus(tar)
                        lock(apply_damage, self, app.ent_dict[tar], -2, 'poison', 'Ghoul Venom')
                        root.after(1333, lambda ln = lockname : app.dethloks[ln].set(1))
                    eot = partial(take_2, id)
                    app.ent_dict[id].effects_dict['Ghoul_Venom'] = Effect(name = 'Ghoul_Venom', eot_func = eot, undo_func = p, duration = 9, level = 4)
                    root.after(2666, lambda e = ents_list : self.finish_attack(e))
                else:
                    root.after(2666, lambda e = ents_list : self.finish_attack(e))
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list : self.finish_attack(e))
        
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)

        
    def cleanup_attack(self):
        self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
            
    def finish_attack(self, ents_list):
        self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
        self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist

        
class Skeleton(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 5
        self.agl = 3
        self.end = 4
        self.dodge = 2
        self.psyche = 2
        self.spirit = 9
        self.move_range = 3
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['slashing', 'piercing', 'poison']
        self.weak = ['crushing', 'magick', 'fire']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
            self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/undead_attack.ogg')
            sound_effects.play(effect1, 0)
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                root.after(1666, self.init_normal_anims)
                lock(apply_damage, self, app.ent_dict[id], -d, 'crushing', 'Bone Strike')
                self.finish_attack(ents_list)
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list : self.finish_attack(e))
        
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
        
#     def cleanup_attack(self):
#         self.init_normal_anims()
#         try: app.canvas.delete('text')
#         except: pass
            
    def finish_attack(self, ents_list):
        self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
        self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
class Undead_Knight(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 10
        self.agl = 8
        self.end = 6
        self.dodge = 8
        self.psyche = 6
        self.spirit = 86
        self.move_range = 4
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['slashing', 'piercing', 'magick', 'poison']
        self.weak = ['fire', 'crushing']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
            effect1 = mixer.Sound('Sound_Effects/undead_knight_attack.ogg')
            sound_effects.play(effect1, 0)
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Sword Strike')
                root.after(666, lambda e = ents_list : self.finish_attack(e))
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(1666, lambda e = ents_list : self.finish_attack(e))
        
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)

        
    def cleanup_attack(self):
        try: app.canvas.delete('text')
        except: pass
            
    def finish_attack(self, ents_list):
        try: app.canvas.delete('text')
        except: pass
        self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
class Troll(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 9
        self.agl = 6
        self.end = 8
        self.dodge = 5
        self.psyche = 2
        self.spirit = 35
        self.move_range = 8
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['slashing', 'piercing']
        self.weak = ['fire', 'acid']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        # TROLL REGEN
        if self.spirit < 35:
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+74-app.moved_down, text='Regen 2 Spirit', font= ('Andale Mono', 13), fill = 'black', tags = 'regen_text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+75-app.moved_down, text='Regen 2 Spirit', font= ('Andale Mono', 13), fill = 'white', tags = 'regen_text')
            root.after(999, lambda t = 'regen_text' : app.canvas.delete(t))
            self.spirit += 2
            if self.spirit > 35:
                self.spirit = 35
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
            effect1 = mixer.Sound('Sound_Effects/troll_attack.ogg')
            sound_effects.play(effect1, 0)
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'crushing', 'Pummel')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:# HIT, KILL
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    name = 'dethlok'+str(app.death_count)
                    app.death_count += 1
                    app.dethloks[name] = tk.IntVar(0)
                    root.after(2666, self.cleanup_attack)
                    root.after(2666, lambda id = id, name = name : app.kill(id, name))
                    root.wait_variable(app.dethloks[name])
                    self.finish_attack(ents_list)
                else:# HIT, NO KILL
                    root.after(2666, lambda e = ents_list : self.finish_attack(e))
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list : self.finish_attack(e))
        
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)

        
    def cleanup_attack(self):
        try: app.canvas.delete('text')
        except: pass
            
    def finish_attack(self, ents_list):
        try: app.canvas.delete('text')
        except: pass
        self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    
#     def legal_moves(self):
#         path = []
#         q = [[c] for c in app.coords if dist(self.loc, c) == 1 and app.grid[c[0]][c[1]] == '']
#         visited = [q[:]]
#         mvlist = []
#         while q:
#             path = q[0]
#             q = q[1:]
#             if len(path) > 8 or path in visited:
#                 continue
#             else:
#                 visited.append(path)
#                 last = path[-1]
#                 if last not in mvlist:
#                     mvlist.append(last)
#     #             if last in goal:
#     #                 return path
#                 adj = [c for c in app.coords if dist(c, last) == 1 and app.grid[c[0]][c[1]] == '']
#                 for s in adj:
#                     q.append(path + [s])
# #                     visited.append(s)
#         return mvlist
        
        
    # every square has a 'cost', which is the number of moves required to reach
    # if you reach a square with equal or lower cost than your own associated with it, return
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
        
class Warlock(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 5
        self.agl = 8
        self.end = 7
        self.dodge = 7
        self.psyche = 11
        self.spirit = 89
        self.move_range = 5
        self.waiting = waiting
        self.move_type = 'teleport'
        self.resist = ['magick', 'fire', 'elec', 'cold', 'poison']
        self.weak = ['slashing', 'piercing', 'crushing']
        super().__init__(name, img, loc, owner, number)
        
    def get_attr(self, attr):
        if attr == 'str':
            q = self.str_effects + app.loc_effects_dict[tuple(self.loc)].str_effects
            base = self.str
        elif attr == 'agl':
            q = self.agl_effects + app.loc_effects_dict[tuple(self.loc)].agl_effects
            base = self.agl
        elif attr == 'end':
            q = self.end_effects + app.loc_effects_dict[tuple(self.loc)].end_effects
            base = self.end
        elif attr == 'dodge':
            q = self.dodge_effects + app.loc_effects_dict[tuple(self.loc)].dodge_effects
            base = self.dodge
        elif attr == 'psyche':
            q = self.psyche_effects + app.loc_effects_dict[tuple(self.loc)].psyche_effects
            base = self.psyche
        elif attr == 'move_range':# WARLOCK MOVE RANGE NOT AFFECTED BY MOVE EFFECTS
            q = []
            base = self.move_range
        for func in q:
            base = func(base)
        return base
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    # make casting anims
    # immune to move_effects
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            # Summon Skeleton
            root.after(1333, lambda el = ents_list : self.warlock_summon(el))
            
    def warlock_summon(self, ents_list):
        effect1 = mixer.Sound('Sound_Effects/warlock_summon.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.effects_counter += 3 # skip existing ent ids
        uniq_num = app.effects_counter
        app.effects_counter += 1
        # get random empty location
        coords = [c for c in app.coords if dist(c, self.loc) <= 6 and app.grid[c[0]][c[1]] == '']
        if coords != []:
            undead_loc = choice(coords)
            app.focus_square(undead_loc)
            app.vis_dict['Summon_Skeleton'] = Vis(name = 'Summon_Skeleton', loc = undead_loc[:])
            app.canvas.create_image(undead_loc[0]*100+50-app.moved_right, undead_loc[1]*100+50-app.moved_down, image = app.vis_dict['Summon_Skeleton'].img, tags = 'Summon_Skeleton')
            def cleanup_vis(name):
                del app.vis_dict[name]
                app.canvas.delete(name)
            root.after(2333, lambda name = 'Summon_Skeleton' : cleanup_vis(name))
            app.canvas.create_text(undead_loc[0]*100+49-app.moved_right, undead_loc[1]*100+89-app.moved_down, text = 'Summon Skeleton', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
            app.canvas.create_text(undead_loc[0]*100+50-app.moved_right, undead_loc[1]*100+90-app.moved_down, text = 'Summon Skeleton', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Skeleton.png'))
            app.ent_dict['b'+str(uniq_num)] = Skeleton(name = 'Skeleton', img = img, loc = undead_loc[:], owner = 'p2', number = 'b'+str(uniq_num))
            app.grid[undead_loc[0]][undead_loc[1]] = 'b'+str(uniq_num)
            app.canvas.create_image(undead_loc[0]*100+50-app.moved_right, undead_loc[1]*100+50-app.moved_down, image = img, tags = 'b'+str(uniq_num))
            root.after(2333, lambda t = 'text' : app.canvas.delete(t))
        root.after(2333, lambda ents_list = ents_list : self.continue_ai(ents_list))
        # End Summon Skeleton, ATTEMPT ATTACK
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        atk_sqrs = [x for x in atk_sqrs if app.ent_dict[app.grid[x[0]][x[1]]].owner == 'p1']
        if atk_sqrs != []:
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # CANNOT ATTACK FROM START LOC, GET TARGET AND MOVE TOWARDS
            # among legal sqrs, move to sqr within dist of attack or that minimizes dist
            leg_sqrs = self.legal_moves()
            if leg_sqrs != []:
                enemy_ent_locs = [v.loc for k,v in app.ent_dict.items() if v.owner != self.owner]
                # first try to move to sqr at edge of attack range
                goals = [c for c in app.coords for e in enemy_ent_locs if dist(c, e) <= 3 and app.grid[c[0]][c[1]] == '']
                target_sqrs = []
                for sqr in leg_sqrs:
                    if sqr in goals:
                        target_sqrs.append(sqr)
                if target_sqrs != []: # move to sqr within target_sqrs that is furthest from enemy_ent_loc
                    furthest_sqrs = [s for s in target_sqrs for x in enemy_ent_locs if dist(s, x) == max([dist(j, y) for j in target_sqrs for y in enemy_ent_locs])]
                    loc = choice(furthest_sqrs)
                    root.after(666, lambda sqr = loc : app.focus_square(sqr))
                    root.after(1333, lambda el = ents_list, endloc = loc : self.warlock_move(el, loc))
                else: # move to sqr within leg_sqrs that minimizes dist
                    closest_sqrs = [s for s in leg_sqrs for x in enemy_ent_locs if dist(s, x) == min([dist(j, y) for j in leg_sqrs for y in enemy_ent_locs])]
                    loc = choice(closest_sqrs)
                    root.after(666, lambda sqr = loc : app.focus_square(sqr))
                    root.after(1333, lambda el = ents_list, endloc = loc : self.warlock_move(el, loc))
            else: # continue ai_loop
                self.ai_end_turn(ents_list)
            
    # change to 'teleport move'
    def warlock_move(self, ents_list, endloc):
        global selected
        self.move_used = True
        oldloc = self.loc[:]
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = oldloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.finish_move(ents_list, endloc))
        
    def finish_move(self, ents_list, endloc):
        app.grid[self.loc[0]][self.loc[1]] = ''
        app.canvas.delete(self.number)
        self.loc = endloc[:]
        app.grid[endloc[0]][endloc[1]] = self.number
        try: 
            del app.vis_dict['Teleport']
            app.canvas.delete('Teleport')
        except: pass
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = endloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.cleanup_teleport(ents_list, endloc))
        
    def cleanup_teleport(self, ents_list, endloc):
        del app.vis_dict['Teleport']
        app.canvas.delete('Teleport')
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = self.img, tags = self.tags)
        try: app.canvas.tag_lower(self.tags, 'large')
        except: pass
        app.canvas.tag_lower(self.tags, 'maptop')
        root.after(666, lambda ents_list = ents_list : self.finish_turn(ents_list))
        
        
    def finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(1333, lambda el = ents_list, t = id : self.do_attack(el, t)) # EXIT THROUGH ATTACK
            else: # END TURN
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
    
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            app.get_focus(id)
            self.attack_used = True
    #         self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/warlock_duress.ogg')
            effect1.set_volume(.7)
            sound_effects.play(effect1, 0)
            # make range atk vis
            visloc = app.ent_dict[id].loc[:]
            app.vis_dict['Duress'] = Vis(name = 'Duress', loc = visloc)
            app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Duress'].img, tags = 'Duress')
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+89-app.moved_down, text = 'Duress', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+90-app.moved_down, text = 'Duress', font = ('Andale Mono', 16), fill = 'lightgray', tags = 'text')
            my_psyche = self.get_abl('psyche')
            target_psyche = app.ent_dict[id].get_abl('psyche')
            if to_hit(my_psyche, target_psyche) == True:
                d = damage(my_psyche, target_psyche)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Duress')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+89, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+90, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            else:
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(3666, lambda  el = ents_list, id = id : self.cleanup_attack(el, id))
        
    def cleanup_attack(self, ents_list, id):
        self.init_normal_anims()
        try: 
            del app.vis_dict['Duress']
            app.canvas.delete('Duress')
        except: pass
        try: app.canvas.delete('text')
        except: pass
        if app.ent_dict[id].spirit <= 0:
            name = 'dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(666, lambda id = id, name = name : app.kill(id, name))
            root.wait_variable(app.dethloks[name])
            self.finish_cleanup(ents_list, id)
        else:
            self.finish_cleanup(ents_list, id)
        
    # DEBUG no longer using id here...
    def finish_cleanup(self, ents_list, id):
        # if havent moved, attempt random move
        if self.move_used == False:
            # move to random square at least 9 away
            empty_sqrs = [s for s in app.coords if app.grid[s[0]][s[1]] == '' and dist(self.loc, s) > 9]
            if empty_sqrs != []:
                s =  choice(empty_sqrs)
                effect1 = mixer.Sound('Sound_Effects/warlock_teleport_away.ogg')
                effect1.set_volume(1)
                sound_effects.play(effect1, 0)
                self.warlock_move(ents_list, s)
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 3:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner:
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        for c in app.coords:
            if dist(loc, c) <= self.get_abl('move_range') and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist
        
class Air_Mage(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 4
        self.agl = 10
        self.end = 6
        self.dodge = 10
        self.psyche = 8
        self.spirit = 59
        self.move_range = 9
        self.waiting = waiting
        self.move_type = 'teleport'
        self.resist = ['piercing', 'crushing', 'cold', 'fire']
        self.weak = ['elec', 'acid']
        self.summons_used = False
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
    
    # make casting anims
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            if self.summons_used == False:
                self.summons_used = True
                maxid = max([int(v.number[1:]) for k,v in app.ent_dict.items() if v.owner == self.owner])
                if app.effects_counter <= maxid:
                    app.effects_counter = maxid+1
                num1 = app.effects_counter
                app.effects_counter += 1
                num2 = app.effects_counter
                app.effects_counter += 1
                num3 = app.effects_counter
                app.effects_counter += 1
                nums = [num1, num2, num3]
                # get 3 empty locations
                coords = [c for c in app.coords if dist(c, self.loc) <= 7]
                empty = [c for c in coords if app.grid[c[0]][c[1]] == '']
                if len(empty) >= 3:
                    f_loc1 = choice(empty)
                    empty.remove(f_loc1)
                    f_loc2 = choice(empty)
                    empty.remove(f_loc2)
                    f_loc3 = choice(empty)
                    empty.remove(f_loc3)
                    f_locs = [f_loc1[:], f_loc2[:], f_loc3[:]]
                    def summon_loop(loc, num):
                        app.focus_square(loc)
                        app.vis_dict['Summon_Skeleton'] = Vis(name = 'Summon_Skeleton', loc = loc[:])
                        app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict['Summon_Skeleton'].img, tags = 'Summon_Skeleton')
                        def cleanup_vis(name):
                            del app.vis_dict[name]
                            app.canvas.delete(name)
                        root.after(2333, lambda name = 'Summon_Skeleton' : cleanup_vis(name))
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+89-app.moved_down, text = 'Summon Air Elemental', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+90-app.moved_down, text = 'Summon Air Elemental', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                        img = ImageTk.PhotoImage(Image.open('summon_imgs/Air_Elemental.png'))
                        app.ent_dict['b'+str(num)] = Air_Elemental(name = 'Air_Elemental', img = img, loc = loc[:], owner = 'p2', number = 'b'+str(num))
                        app.grid[loc[0]][loc[1]] = 'b'+str(num)
                        app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = img, tags = 'b'+str(num))
                        root.after(2333, lambda t = 'text' : app.canvas.delete(t))
                        if f_locs == []:
                            app.get_focus(self.number)
                            root.after(2333, lambda ents_list = ents_list : self.continue_ai(ents_list))
                        else:
                            loc = f_locs.pop()
                            num = nums.pop()
                            root.after(2333, lambda l = loc, n = num : summon_loop(l, n))
                    loc = f_locs.pop()
                    num = nums.pop()
                    summon_loop(loc, num)
                else:
                    app.get_focus(self.number)
                    root.after(1333, lambda el = ents_list : self.continue_ai(el))
            else:
                root.after(1333, lambda el = ents_list : self.continue_ai(el))
                
    # teleport to limit of range, ranged atk or spell?
    def continue_ai(self, ents_list):
        # get empty sqrs exactly 3 or 4 from any enemy
        ent_locs = [v.loc[:] for k,v in app.all_ents().items() if v.owner == 'p1']
        locs = [s for s in app.coords for c in ent_locs if 3 <= dist(s, c) <= 4  and app.grid[s[0]][s[1]] == '']
        if locs != []:
            loc = choice(locs)
            app.focus_square(loc)
            root.after(1333, lambda el = ents_list, loc = loc : self.air_mage_move(el, loc))
        else:
            root.after(1333, lambda el = ents_list : self.do_attack(el)) # ATTACK
            
    def air_mage_move(self, ents_list, endloc):
#         global selected
        self.move_used = True
        oldloc = self.loc[:]
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = oldloc[:])
        vis = app.vis_dict['Teleport']
#         app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.finish_move(ents_list, endloc))
        
    def finish_move(self, ents_list, endloc):
        app.grid[self.loc[0]][self.loc[1]] = ''
        app.canvas.delete(self.number)
        self.loc = endloc[:]
        app.grid[endloc[0]][endloc[1]] = self.number
        try: 
            del app.vis_dict['Teleport']
            app.canvas.delete('Teleport')
        except: pass
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = endloc[:])
        vis = app.vis_dict['Teleport']
#         app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.cleanup_teleport(ents_list, endloc))
        
    def cleanup_teleport(self, ents_list, endloc):
        del app.vis_dict['Teleport']
        app.canvas.delete('Teleport')
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = self.img, tags = self.tags)
        try: app.canvas.tag_lower(self.tags, 'large')
        except: pass
        app.canvas.tag_lower(self.tags, 'maptop')
        root.after(666, lambda ents_list = ents_list : self.finish_turn(ents_list))
        
        
    def finish_turn(self, ents_list):
        if self.attack_used == False:
            root.after(1333, lambda el = ents_list : self.do_attack(el)) # EXIT THROUGH ATTACK
        else:# CANNOT ATTACK, EXIT FUNC
            self.ai_end_turn(ents_list)
    
    def do_attack(self, ents_list):
        if self.attack_used == True:
            root.after(666, lambda e = ents_list : app.do_ai_loop(e))
        else:
            self.attack_used = True
    #         self.init_attack_anims()
            rand = randrange(1,100)
            if rand < 20:
                self.do_sandstorm(ents_list)
            elif 20 <= rand < 85:
                self.do_cyclone(ents_list)
            else:
                elems = [v for k,v in app.all_ents().items() if v.name == 'Air_Elemental']
                if elems == []:
                    self.do_sandstorm(ents_list)
                else:
                    self.do_breath_of_life(ents_list)
                
    # aoe remove effects then give effect that damages and debuffs
    def do_sandstorm(self, ents_list):
        effect1 = mixer.Sound('Sound_Effects/teleport_move.ogg')
        effect1.set_volume(.8)
        sound_effects.play(effect1, 0)
        ents = [k for k,v in app.action_target_ents().items() if dist(v.loc,self.loc) <= 4 and v.owner != self.owner]
        if ents == []:
            root.after(666, lambda e = ents_list : app.do_ai_loop(e))
        else:
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+84-app.moved_down, text = 'Sandstorm', font = ('Andale Mono', 15), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+85-app.moved_down, text = 'Sandstorm', font = ('Andale Mono', 15), fill = 'gray', tags = 'text')
            id = choice(ents)
            loc = app.ent_dict[id].loc[:]
            ents = [k for k,v in app.all_ents().items() if dist(v.loc,loc) <= 2 and v.name != 'Air_Elemental' and v != self]
            for id in ents:
                loc = app.ent_dict[id].loc[:]
                app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+84-app.moved_down, text = 'Effects\nRemoved', justify = 'center', font = ('Andale Mono', 12), fill = 'black', tags = 'text')
                app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+85-app.moved_down, text = 'Effects\nRemoved', justify = 'center', font = ('Andale Mono', 12), fill = 'white', tags = 'text')
                n = 'Sandstorm' + str(app.effects_counter)
                app.effects_counter += 1
                app.vis_dict[n] = Vis(name = 'Sandstorm', loc = loc[:])
                app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = 'Sandstorm')
                to_remove = []
                for k,v in app.ent_dict[id].effects_dict.items():
                    v.undo()
                    to_remove.append(k)
                for k in to_remove:
                    del app.ent_dict[id].effects_dict[k]
                def sandstorm_effect(stat):
                    if stat <= 1:
                        return stat
                    else:
                        stat -= 1
                        return stat
                p2 = partial(sandstorm_effect)
                app.ent_dict[id].str_effects.append(p2)
                app.ent_dict[id].end_effects.append(p2)
                app.ent_dict[id].agl_effects.append(p2)
                app.ent_dict[id].dodge_effects.append(p2)
                app.ent_dict[id].psyche_effects.append(p2)
                def un(i, func):
                    app.ent_dict[i].str_effects.remove(func)
                    app.ent_dict[i].end_effects.remove(func)
                    app.ent_dict[i].agl_effects.remove(func)
                    app.ent_dict[i].dodge_effects.remove(func)
                    app.ent_dict[i].psyche_effects.remove(func)
                    return None
                p = partial(un, id, p2)
                # EOT FUNC
                def take_2(tar, lockname = None):
                    app.get_focus(tar)
                    lock(apply_damage, self, app.ent_dict[tar], -2, 'magick', 'Sandstorm')
                    root.after(1333, lambda ln = lockname : app.dethloks[ln].set(1))
                eot = partial(take_2, id)
                n = 'Sandstorm' + str(app.effects_counter)
                app.ent_dict[id].effects_dict[n] = Effect(name = 'Sandstorm', eot_func = eot, undo_func = p, duration = 3, level = 5)
            root.after(3666, lambda el = ents_list : self.cleanup_attack(el))
                    
                    
    # dmg and teleport one target
    def do_cyclone(self, ents_list):
#         effect1 = mixer.Sound('Sound_Effects/cyclone.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        ents = [k for k,v in app.spell_target_ents().items() if dist(v.loc,self.loc) <= 4 and v.owner != self.owner]
        if ents == []:
            root.after(666, lambda el = ents_list : self.cleanup_attack(el))
        else:
            id = choice(ents)
            loc = app.ent_dict[id].loc[:]
            app.focus_square(loc)
            app.vis_dict['Cyclone'] = Vis(name = 'Cyclone', loc = loc[:])
            app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict['Cyclone'].img, tags = 'Cyclone')
            my_psyche = self.get_abl('psyche')
            tar_str = app.ent_dict[id].get_abl('str')
            if to_hit(my_psyche, tar_str) == True:
                d = damage(my_psyche, tar_str)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Cyclone')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = 'Hit! '+str(d)+' spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = 'Hit! '+str(d)+' spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+94-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+95-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                    root.after(3333, lambda el = ents_list, id = id : self.cleanup_attack(el, id))
                else:# Teleport to random loc
                    sqrs = [c for c in app.coords if app.grid[c[0]][c[1]] == '']
                    loc = choice(sqrs)
                    root.after(3333, lambda el = ents_list, id = id, loc = loc : self.cyclone_teleport(el, id, loc))
            else:
                app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = 'Miss!', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = 'Miss!', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                root.after(3333, lambda el = ents_list : self.cleanup_attack(el))
    
    def cyclone_teleport(self, el, id, loc):
        global selected
        selected.append(id)
        del app.vis_dict['Cyclone']
        app.canvas.delete('Cyclone')
        app.canvas.delete('text')
        app.vis_dict['Cyclone'] = Vis(name = 'Cyclone', loc = loc[:])
        app.focus_square(loc)
        app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict['Cyclone'].img, tags = 'Cyclone')
        app.grid[app.ent_dict[id].loc[0]][app.ent_dict[id].loc[1]] = ''
        app.canvas.delete(id)
        root.after(1666, lambda el = el, id = id, loc = loc : self.finish_cyclone(el, id, loc))
        
    def finish_cyclone(self, el, id, loc):
        global selected
        app.ent_dict[id].loc = loc[:]
        app.grid[loc[0]][loc[1]] = id
        del app.vis_dict['Cyclone']
        app.canvas.delete('Cyclone')
        app.canvas.create_image(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = app.ent_dict[id].tags)
        selected.remove(id)
        try: app.canvas.tag_lower((app.ent_dict[id].tags), 'large')
        except: pass
        app.canvas.tag_lower((app.ent_dict[id].tags), 'maptop')
        root.after(666, lambda el = el, id = id : self.cleanup_attack(el, id))
        
    # only called when summons exist, heal whatever summons remain for some amount, give them stat boost effect
    def do_breath_of_life(self, ents_list):
        effect1 = mixer.Sound('Sound_Effects/moonlight.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Breath of Life', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Breath of Life', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
#         app.vis_dict['Breath_of_Life'] = Vis(name = 'Breath_of_Life', loc = self.loc[:])
#         app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Breath_of_Life'].img, tags = 'Breath_of_Life')
        ents = [k for k,v in app.all_ents().items() if v.name == 'Air_Elemental']
        def breath_loop(ents):
            if ents == []:
                self.cleanup_attack(ents_list)
            else:
                id = ents[0]
                ents = ents[1:]
                loc = app.ent_dict[id].loc[:]
                app.focus_square(loc)
                n = 'Breath_of_Life'+str(app.effects_counter)
                app.effects_counter += 1
                app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = '+10 spirit, effects removed', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = '+10 spirit, effects removed', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                app.vis_dict[n] = Vis(name = 'Breath_of_Life', loc = loc[:])
                app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = 'Breath_of_Life')
#                 app.ent_dict[id].set_attr('spirit', 10)
                apply_heal(self, app.ent_dict[id], 10)
                to_remove = []
                for k,v in app.ent_dict[id].effects_dict.items():
                    v.undo()
                    to_remove.append(k)
                for k in to_remove:
                    del app.ent_dict[id].effects_dict[k]
                root.after(2666, lambda n = n : self.clean_breath_vis(n))
                root.after(2999, lambda e = ents : breath_loop(e))
        root.after(1888, lambda t = 'text' : app.canvas.delete(t))
        root.after(1999, lambda e = ents : breath_loop(e))
                
    def clean_breath_vis(self, name):
        app.canvas.delete('text')
        del app.vis_dict[name]
        app.canvas.delete('Breath_of_Life')
                
    def cleanup_attack(self, ents_list = None, id = None):
#         self.init_normal_anims()
        names = [k for k,v in app.vis_dict.items() if v.name == 'Sandstorm' or v.name == 'Cyclone' or v.name == 'Breath_of_Life']
        for n in names:
            del app.vis_dict[n]
            app.canvas.delete(n)
        try: app.canvas.delete('text')
        except: pass
        if id:
            if app.ent_dict[id].spirit <= 0:
                name = 'dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(666, lambda id = id, name = name : app.kill(id, name))
                root.wait_variable(app.dethloks[name])
                self.ai_end_turn(ents_list)
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
                    
#     def legal_attacks(self):
#         sqrs = []
#         for coord in app.coords:
#             if dist(coord, self.loc) <= 3:
#                 if app.grid[coord[0]][coord[1]] != '' and app.grid[coord[0]][coord[1]] != 'block':
#                     sqrs.append(coord)
#         return sqrs
        
    # not used for movement, kept for purposes of monkey-patching
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        for c in app.coords:
            if dist(loc, c) <= self.get_abl('move_range') and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist


class Air_Elemental(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 4
        self.agl = 7
        self.end = 3
        self.dodge = 7
        self.psyche = 3
        self.spirit = 19
        self.move_range = 4
        self.waiting = waiting
        self.move_type = 'flying'
        self.resist = ['poison', 'piercing', 'fire']
        self.weak = ['cold']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if 3 <= dist(el,g) <= 4 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if 3 <= dist(el,g) <= 4 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if 3 <= dist(el,g) <= 4 and app.grid[g[0]][g[1]] == '']
        if gs1 == []:
            if gs2 == []:
                if gs3 == []:
                    self.ai_end_turn(ents_list)
                else:
                    g = reduce(lambda a,b : a if sum([dist(a,el) for el in els]) > sum([dist(b,el) for el in els]) else b, gs3)
            else:
                g = reduce(lambda a,b : a if sum([dist(a,el) for el in els]) > sum([dist(b,el) for el in els]) else b, gs2)
        else:
            g = reduce(lambda a,b : a if sum([dist(a,el) for el in els]) > sum([dist(b,el) for el in els]) else b, gs1)
        ms = self.legal_moves()
        moves = [m for m in ms if m in cs]
        if moves == []:
            if ms == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,g) < dist(b,g) else b, ms)
                root.after(333, lambda id = self.number : app.get_focus(id))
                root.after(999, lambda el = ents_list, sqr = m : self.air_elemental_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,g) < dist(b,g) else b, moves)
            root.after(333, lambda id = self.number : app.get_focus(id))
            root.after(999, lambda el = ents_list, sqr = m : self.air_elemental_move(el, sqr))
            
    def air_elemental_move(self, ents_list, sqr):
        global selected
        self.move_used = True
        selected.append(self.number)
        app.focus_square(sqr)
#         effect1 = mixer.Sound('Sound_Effects/revenant_move.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        endx = sqr[0]*100+50-app.moved_right
        endy = sqr[1]*100+50-app.moved_down
        start_sqr = self.loc[:]
        end_sqr = sqr[:]
        total_distance = abs(x - endx) + abs(y - endy)
        # tic doesnt matter for circular image loop, would need to make flying_anims and switch to
        tic = 60 #total_distance/9 # Magic Number debug, number of images for vis
        if x == endx:
            xstep = 0
            ystep = 10
        elif y == endy:
            xstep = 10
            ystep = 0
        else:
            slope = Fraction(abs(x - endx), abs(y - endy))
            # needs to be moving at least 10 pixels, xstep + ystep >= 10
            xstep = slope.numerator
            ystep = slope.denominator
            while xstep + ystep < 10:
                xstep *= 2
                ystep *= 2
        def flying_arc(x, y, endx, endy, start_sqr, end_sqr, acm, tic, xstep, ystep):
            if acm >= tic:
                acm = 0
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if x > endx:
                acm += xstep
                x -= xstep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            elif x < endx:
                acm += xstep
                x += xstep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if y > endy:
                acm += ystep
                y -= ystep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            elif y < endy:
                acm += ystep
                y += ystep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if abs(x - endx) < 13 and abs(y - endy) < 13:
                self.finish_move(self.number, end_sqr, start_sqr, ents_list)
            else: # CONTINUE LOOP
                root.after(66, lambda x = x, y = y, e = endx, e2 = endy, s = start_sqr, s2 = end_sqr, acm = acm, tic = tic, xs = xstep, ys = ystep : flying_arc(x, y, e, e2, s, s2, acm, tic, xs, ys))
        flying_arc(x, y, endx, endy, start_sqr, end_sqr, tic+1, tic, xstep, ystep)
            
            
    def finish_move(self, id, end_sqr, start_sqr, ents_list):
        global selected
        selected.remove(self.number)
        self.loc = end_sqr[:]
        app.grid[start_sqr[0]][start_sqr[1]] = ''
        app.grid[end_sqr[0]][end_sqr[1]] = self.number
        # MAKE ATTACK ON ANY ENEMY ENT WITHIN RANGE
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []:
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda t = id : app.get_focus(t))
            root.after(1333, lambda el = ents_list, t = id : self.do_attack(el, t)) # EXIT THROUGH ATTACK
        else:
        # CANNOT ATTACK, EXIT FUNC
            root.after(1333, lambda el = ents_list : self.ai_end_turn(el))
    
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            app.get_focus(id)
            self.attack_used = True
    #         self.init_attack_anims()
#             effect1 = mixer.Sound('Sound_Effects/revenant_terror.ogg')
#             effect1.set_volume(1)
#             sound_effects.play(effect1, 0)
#             visloc = app.ent_dict[id].loc[:]
#             app.vis_dict['Revenant_Terror'] = Vis(name = 'Revenant_Terror', loc = visloc)
#             app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Revenant_Terror'].img, tags = 'Revenant_Terror')
#             app.canvas.create_text(visloc[0]*100+49-app.moved_right, visloc[1]*100+104-app.moved_down, text = 'Terror', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
#             app.canvas.create_text(visloc[0]*100+50-app.moved_right, visloc[1]*100+105-app.moved_down, text = 'Terror', font = ('Andale Mono', 16), fill = 'gray77', tags = 'text')
            my_agl = self.get_abl('agl')
            target_dodge = app.ent_dict[id].get_abl('dodge')
            if to_hit(my_agl, target_dodge) == True:
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'acid', 'Toxic Vapor')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            else:
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(3666, lambda  el = ents_list, id = id : self.cleanup_attack(el, id))
            
    def cleanup_attack(self, ents_list, id):
#         self.init_normal_anims()
        try: 
            app.canvas.delete('text')
#             del app.vis_dict['Revenant_Terror']
#             app.canvas.delete('Revenant_Terror')
        except: pass
        if app.ent_dict[id].spirit <= 0:
            name = 'dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(666, lambda id = id, name = name : app.kill(id, name))
            root.wait_variable(app.dethloks[name])
            # DEBUG update pathing...
        if self.move_used == False:
            els = [v.loc for k,v in app.ent_dict.items() if v.owner != self.owner]
            cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
            ms = self.legal_moves()
            moves = [m for m in ms if m in cs]
            if moves == []:
                moves = ms
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if sum([dist(a,el) for el in els]) > sum([dist(b,el) for el in els]) else b, moves)
                self.air_elemental_move(ents_list, m)
        else:
            self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 4:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        for c in app.coords:
            if dist(loc, c) <= self.get_abl('move_range') and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist
        
        
class Water_Mage(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 6
        self.agl = 9
        self.end = 7
        self.dodge = 4
        self.psyche = 8
        self.spirit = 79
        self.move_range = 9
        self.waiting = waiting
        self.move_type = 'teleport'
        self.resist = ['crushing', 'fire']
        self.weak = ['elec', 'cold']
        self.summons_used = False
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        ents_list = ents_list[1:]
        if ents_list == []:
            app.end_turn()
        else:
            app.do_ai_loop(ents_list)
    
    # make casting anims
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            # summon wave of elems (echelon)
            maxid = max([int(v.number[1:]) for k,v in app.ent_dict.items() if v.owner == self.owner])
            if app.effects_counter <= maxid:
                app.effects_counter = maxid+1
            num1 = app.effects_counter
            app.effects_counter += 1
            num2 = app.effects_counter
            app.effects_counter += 1
            num3 = app.effects_counter
            app.effects_counter += 1
            nums = [num1, num2, num3]
            # get 3 empty locations
            coords = [c for c in app.coords if dist(c, self.loc) <= 7]
            empty = [c for c in coords if app.grid[c[0]][c[1]] == '']
            if len(empty) >= 3:
                f_loc1 = choice(empty)
                empty.remove(f_loc1)
                f_loc2 = choice(empty)
                empty.remove(f_loc2)
                f_loc3 = choice(empty)
                empty.remove(f_loc3)
                f_locs = [f_loc1[:], f_loc2[:], f_loc3[:]]
                def summon_loop(loc, num):
                    app.focus_square(loc)
                    app.vis_dict['Summon_Skeleton'] = Vis(name = 'Summon_Skeleton', loc = loc[:])
                    app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict['Summon_Skeleton'].img, tags = 'Summon_Skeleton')
                    def cleanup_vis(name):
                        del app.vis_dict[name]
                        app.canvas.delete(name)
                    root.after(2333, lambda name = 'Summon_Skeleton' : cleanup_vis(name))
                    app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+89-app.moved_down, text = 'Summon Water Elemental', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+90-app.moved_down, text = 'Summon Water Elemental', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                    img = ImageTk.PhotoImage(Image.open('summon_imgs/Water_Elemental.png'))
                    app.ent_dict['b'+str(num)] = Water_Elemental(name = 'Water_Elemental', img = img, loc = loc[:], owner = 'p2', number = 'b'+str(num))
                    app.grid[loc[0]][loc[1]] = 'b'+str(num)
                    app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = img, tags = 'b'+str(num))
                    root.after(2333, lambda t = 'text' : app.canvas.delete(t))
                    if f_locs == []:
                        app.get_focus(self.number)
                        root.after(2333, lambda ents_list = ents_list : self.continue_ai(ents_list))
                    else:
                        loc = f_locs.pop()
                        num = nums.pop()
                        root.after(2333, lambda l = loc, n = num : summon_loop(l, n))
                loc = f_locs.pop()
                num = nums.pop()
                summon_loop(loc, num)
            else:
                app.get_focus(self.number)
                root.after(1333, lambda el = ents_list : self.continue_ai(el))
            
    # teleport to limit of range, ranged atk or spell?
    def continue_ai(self, ents_list):
        # get empty sqrs exactly 3 or 4 from any enemy
        ent_locs = [v.loc[:] for k,v in app.all_ents().items() if v.owner == 'p1']
        locs = [s for s in app.coords for c in ent_locs if 3 <= dist(s, c) <= 4  and app.grid[s[0]][s[1]] == '']
        if locs != []:
            loc = choice(locs)
            app.focus_square(loc)
            root.after(1333, lambda el = ents_list, loc = loc : self.water_mage_move(el, loc))
        else:
            root.after(1333, lambda el = ents_list : self.do_attack(el)) # ATTACK
            
            
    def water_mage_move(self, ents_list, endloc):
        global selected
        self.move_used = True
        oldloc = self.loc[:]
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = oldloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.finish_move(ents_list, endloc))
        
    def finish_move(self, ents_list, endloc):
        app.grid[self.loc[0]][self.loc[1]] = ''
        app.canvas.delete(self.number)
        self.loc = endloc[:]
        app.grid[endloc[0]][endloc[1]] = self.number
        try: 
            del app.vis_dict['Teleport']
            app.canvas.delete('Teleport')
        except: pass
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = endloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.cleanup_teleport(ents_list, endloc))
        
    def cleanup_teleport(self, ents_list, endloc):
        del app.vis_dict['Teleport']
        app.canvas.delete('Teleport')
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = self.img, tags = self.tags)
        try: app.canvas.tag_lower(self.tags, 'large')
        except: pass
        app.canvas.tag_lower(self.tags, 'maptop')
        root.after(666, lambda ents_list = ents_list : self.finish_turn(ents_list))
        
        
    def finish_turn(self, ents_list):
        if self.attack_used == False:
            root.after(1333, lambda el = ents_list : self.do_attack(el)) # EXIT THROUGH ATTACK
        else:# CANNOT ATTACK, EXIT FUNC
            self.ai_end_turn(ents_list)
    
    # ranged water attack or stat affecting spell?
    def do_attack(self, ents_list):
        if self.attack_used == True:
            root.after(666, lambda e = ents_list : self.ai_end_turn(e))
        else:
            self.attack_used = True
    #         self.init_attack_anims()
            # randomly choose between attacks
            rand = randrange(1,100)
            if rand < 35:
                # do area damage and movement reduction spell
                self.do_deluge(ents_list)
            else:
                # do stat affecting spell
                self.do_fog(ents_list)
                
    # area attack all within range2 of target within range4, psy v dodge, psy v psy
    # NEED to add: inhibit movement, after changing overwrite of legal_moves() to moves_effects list
    def do_deluge(self, ents_list):
#         effect1 = mixer.Sound('Sound_Effects/deluge.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        ents = [k for k,v in app.spell_target_ents().items() if dist(v.loc, self.loc) <= 4 and v.owner != self.owner]
        if ents == []:
            root.after(666, lambda e = ents_list : self.ai_end_turn(e))
        else:
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+84-app.moved_down, text = 'Deluge', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+85-app.moved_down, text = 'Deluge', font = ('Andale Mono', 16), fill = 'cyan', tags = 'text')
#             app.vis_dict['Deluge'] = Vis(name = 'Deluge', loc = self.loc[:])
#             app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Deluge'].img, tags = 'Deluge')
            id = choice(ents)
            loc = app.ent_dict[id].loc[:]
            ents = [k for k,v in app.all_ents().items() if dist(loc, v.loc) <= 2 and v.owner != self.owner]
            def deluge_loop(ents):
                if ents == []:
                    self.cleanup_attack(ents_list)
                else:
                    id = ents[0]
                    ents = ents[1:]
                    loc = app.ent_dict[id].loc[:]
                    app.focus_square(loc)
                    n = 'Deluge' + str(app.effects_counter)
                    app.effects_counter += 1
                    app.vis_dict[n] = Vis(name = 'Deluge', loc = loc[:])
                    app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = 'Deluge')
                    my_psyche = self.get_abl('psyche')
                    tar_dodge = app.ent_dict[id].get_abl('dodge')
                    if to_hit(my_psyche, tar_dodge) == True:
                        tar_psyche = app.ent_dict[id].get_abl('psyche')
                        d = damage(my_psyche, tar_psyche)
                        pre = app.ent_dict[id].spirit
                        lock(apply_damage, self, app.ent_dict[id], -d, 'cold', 'Deluge')
                        post = app.ent_dict[id].spirit
                        d = pre - post
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = str(d)+' spirit', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = str(d)+' spirit', font = ('Andale Mono', 13), fill = 'cyan', tags = 'text')
                        if app.ent_dict[id].spirit <= 0:
                            app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+94-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                            app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+95-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', font = ('Andale Mono', 13), fill = 'cyan', tags = 'text')
                            name = 'dethlok'+str(app.death_count)
                            app.death_count += 1
                            app.dethloks[name] = tk.IntVar(0)
                            root.after(666, lambda id = id, name = name : app.kill(id, name))
                            root.wait_variable(app.dethloks[name])
                        else:# still alive, add movement reduction if not already
                            if 'Deluge' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
                                def deluge_move(move_range):
                                    move_range -= 2
                                    if move_range < 0:
                                        return 0
                                    else:
                                        return move_range
                                app.ent_dict[id].move_effects.append(deluge_move)
                                def undo(i):
                                    app.ent_dict[i].move_effects.remove(deluge_move)
                                u = partial(undo, id)
                                n = 'Deluge' + str(app.effects_counter)
                                app.ent_dict[id].effects_dict[n] = Effect(name = 'Deluge', undo_func = u, duration = 6, level = 8)
                    else:
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+84-app.moved_down, text = 'Miss', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+85-app.moved_down, text = 'Miss', font = ('Andale Mono', 13), fill = 'cyan', tags = 'text')
                    root.after(1888, lambda t = 'text' : app.canvas.delete(t))
                    root.after(1999, lambda e = ents : deluge_loop(e))
            root.after(1888, lambda t = 'text' : app.canvas.delete(t))
            root.after(1999, lambda e = ents : deluge_loop(ents))
            
            
    # all within an area get -3 str -3 psyche
    def do_fog(self, ents_list):
#         effect1 = mixer.Sound('Sound_Effects/fog.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        ents = [k for k,v in app.action_target_ents().items() if dist(v.loc, self.loc) <= 4 and v.owner != self.owner]
        if ents == []:
            root.after(666, lambda e = ents_list : self.ai_end_turn(e))
        else:
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+84-app.moved_down, text = 'Fog', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+85-app.moved_down, text = 'Fog', font = ('Andale Mono', 16), fill = 'cyan', tags = 'text')
#             app.vis_dict['Fog'] = Vis(name = 'Fog', loc = self.loc[:])
#             app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Fog'].img, tags = 'Fog')
            id = choice(ents)
            loc = app.ent_dict[id].loc[:]
            ents = [k for k,v in app.all_ents().items() if dist(loc, v.loc) <= 2 and v.owner != self.owner]
            def fog_loop(ents):
                if ents == []:
                    self.cleanup_attack(ents_list)
                else:
                    id = ents[0]
                    ents = ents[1:]
                    loc = app.ent_dict[id].loc[:]
                    app.focus_square(loc)
                    n = 'Fog' + str(app.effects_counter)
                    app.effects_counter += 1
                    app.vis_dict[n] = Vis(name = 'Fog', loc = loc[:])
                    app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = 'Fog')
                    my_psyche = self.get_abl('psyche')
                    tar_psyche = app.ent_dict[id].get_abl('psyche')
                    if to_hit(my_psyche, tar_psyche) == True and 'Fog' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = 'Fog...', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = 'Fog...', font = ('Andale Mono', 13), fill = 'cyan', tags = 'text')
                        def fog_effect(stat):
                            stat -= 3
                            if stat < 1:
                                return 1
                            else:
                                return stat
                        app.ent_dict[id].str_effects.append(fog_effect)
                        app.ent_dict[id].psyche_effects.append(fog_effect)
                        def undo(i):
                            app.ent_dict[i].str_effects.remove(fog_effect)
                            app.ent_dict[i].psyche_effects.remove(fog_effect)
                        u = partial(undo, id)
                        n = 'Fog' + str(app.effects_counter)
                        app.ent_dict[id].effects_dict[n] = Effect(name = 'Fog', undo_func = u, duration = 5, level = 8)
                    else:
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+84-app.moved_down, text = 'Miss', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+85-app.moved_down, text = 'Miss', font = ('Andale Mono', 13), fill = 'cyan', tags = 'text')
                    root.after(1888, lambda t = 'text' : app.canvas.delete(t))
                    root.after(1999, lambda e = ents : fog_loop(e))
            root.after(1888, lambda t = 'text' : app.canvas.delete(t))
            root.after(1999, lambda e = ents : fog_loop(ents))
                
    def cleanup_attack(self, ents_list):
#         self.init_normal_anims()
        names = [k for k,v in app.vis_dict.items() if v.name == 'Deluge' or v.name == 'Fog']
        for n in names:
            del app.vis_dict[n]
        try:
            app.canvas.delete('Deluge')
        except: pass
        try:
            app.canvas.delete('Fog')
        except: pass
        try: app.canvas.delete('text')
        except: pass
        self.ai_end_turn(ents_list)
                
                
    # not used for movement, kept for purposes of monkey-patching
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        for c in app.coords:
            if dist(loc, c) <= 5 and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist


# change to move in straight line, make ranged atk, die when running into obstacle (block, maybe ent)
class Water_Elemental(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 4
        self.agl = 4
        self.end = 3
        self.dodge = 4
        self.psyche = 4
        self.spirit = 11
        self.move_range = 3
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['cold', 'fire', 'piercing']
        self.weak = ['elec', 'magick']
        self.direction = choice(['up','down','left','right'])
        self.dissipating = False
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    # change to atk, then try move maybe die
    def do_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != [] and self.attack_used == False:
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda t = id : app.get_focus(t))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id))
        else:# just move maybe die
            moves = self.legal_moves()
            if len(moves) < 3:
                self.dissipating = True
                if moves == []:
                    self.dissipate(ents_list)
                else:
                    move = reduce(lambda a,b : a if dist(self.loc,a) > dist(self.loc,b) else b, moves)
                    root.after(666, lambda sqr = move : app.focus_square(sqr))
                    root.after(1333, lambda el = ents_list, sqr = move : self.ai_move(el, sqr))
            else:# just move
                sqr = reduce(lambda a,b : a if dist(self.loc,a) > dist(self.loc,b) else b, moves)
                root.after(666, lambda sqr = sqr : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = sqr : self.ai_move(el, sqr))
                
            
    def ai_finish_turn(self, ents_list):
        if self.dissipating == True:
            self.dissipate(ents_list)
        else:
            self.ai_end_turn(ents_list)
    
    def dissipate(self, ents_list):
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+74, text = 'Water Elemental dissipates\n   into a puddle...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+75, text = 'Water Elemental dissipates\n   into a puddle...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
        name = 'dethlok'+str(app.death_count)
        app.death_count += 1
        app.dethloks[name] = tk.IntVar(0)
        root.after(2222, lambda t = 'text' : app.canvas.delete(t))
        root.after(2333, lambda id = self.number, name = name : app.kill(id, name))
        root.wait_variable(app.dethloks[name])
        self.ai_end_turn(ents_list)
            
            
    def do_attack(self, ents_list, id):
        app.get_focus(id)
        self.attack_used = True
#             self.init_attack_anims()
#             effect1 = mixer.Sound('Sound_Effects/water_elemental_attack.ogg')
#             sound_effects.play(effect1, 0)
        my_agl = self.get_abl('agl')
        target_dodge = app.ent_dict[id].get_abl('dodge')
        if to_hit(my_agl, target_dodge) == True:# HIT
            my_str = self.get_abl('str')
            tar_end = app.ent_dict[id].get_abl('end')
            d = damage(my_str, tar_end)
            pre = app.ent_dict[id].spirit
            lock(apply_damage, self, app.ent_dict[id], -d, 'cold', 'Wave Crash')
            post = app.ent_dict[id].spirit
            d = pre - post
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            if app.ent_dict[id].spirit <= 0:# HIT, KILL
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                name = 'dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(2666, self.cleanup_attack)
                root.after(2666, lambda id = id, name = name : app.kill(id, name))
                root.wait_variable(app.dethloks[name])
                self.finish_attack(ents_list)
            else:# HIT, NO KILL
                root.after(2666, lambda e = ents_list : self.finish_attack(e))
        else:# MISS
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, lambda e = ents_list : self.finish_attack(e))
        
    def cleanup_attack(self):
        self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
            
    def finish_attack(self, ents_list):
#         self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
        if self.move_used == True:
            self.ai_end_turn(ents_list)
        else:
            self.do_ai(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 4:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    # get only squares in self.direction, if length is less than 3: is obstructed so kill
    def legal_moves(self):
        s = self.loc[:]
        mvlist = []
        if self.direction == 'up':
            for i in range(1,4):
                if [s[0],s[1]-i] in app.coords and app.grid[s[0]][s[1]-i] == '':
                    mvlist.append([s[0],s[1]-i])
                else:
                    break
        elif self.direction == 'down':
            for i in range(1,4):
                if [s[0],s[1]+i] in app.coords and app.grid[s[0]][s[1]+i] == '':
                    mvlist.append([s[0],s[1]+i])
                else:
                    break
        elif self.direction == 'left':
            for i in range(1,4):
                if [s[0]-i,s[1]] in app.coords and app.grid[s[0]-i][s[1]] == '':
                    mvlist.append([s[0]-i,s[1]])
                else:
                    break
        elif self.direction == 'right':
            for i in range(1,4):
                if [s[0]+i,s[1]] in app.coords and app.grid[s[0]+i][s[1]] == '':
                    mvlist.append([s[0]+i,s[1]])
                else:
                    break
        return list(filter(lambda x : dist(x, self.loc) <= self.get_abl('move_range'), mvlist))
        
class Earth_Mage(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 3
        self.agl = 3
        self.end = 4
        self.dodge = 2
        self.psyche = 5
        self.spirit = 79
        self.move_range = 9
        self.waiting = waiting
        self.move_type = 'teleport'
        self.resist = ['slashing', 'poison', 'elec']
        self.weak = ['crushing', 'fire']
        self.summons_used = False
        super().__init__(name, img, loc, owner, number)
        # add effects that alter abls based on alive elementals
        def elementals(stat):
            alive = [k for k,v in app.ent_dict.items() if v.name == 'Earth_Elemental']
            bonus = len(alive)
            stat += bonus
            return stat
        self.str_effects.append(elementals)
        self.agl_effects.append(elementals)
        self.end_effects.append(elementals)
        self.dodge_effects.append(elementals)
        self.psyche_effects.append(elementals)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
    
    # make casting anims
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            # summon elementals once
            if self.summons_used == False:
                self.summons_used = True
                maxid = max([int(v.number[1:]) for k,v in app.ent_dict.items() if v.owner == self.owner])
                if app.effects_counter <= maxid:
                    app.effects_counter = maxid+1
                num1 = app.effects_counter
                app.effects_counter += 1
                num2 = app.effects_counter
                app.effects_counter += 1
                num3 = app.effects_counter
                app.effects_counter += 1
                nums = [num1, num2, num3]
                # get random empty locations
                coords = [c for c in app.coords if dist(c, self.loc) <= 7]
                empty = [c for c in coords if app.grid[c[0]][c[1]] == '']
                if len(empty) >= 3:
                    f_loc1 = choice(empty)
                    empty.remove(f_loc1)
                    f_loc2 = choice(empty)
                    empty.remove(f_loc2)
                    f_loc3 = choice(empty)
                    empty.remove(f_loc3)
                    f_locs = [f_loc1[:], f_loc2[:], f_loc3[:]]
                    def summon_loop(loc, num):
                        app.focus_square(loc)
                        app.vis_dict['Summon_Skeleton'] = Vis(name = 'Summon_Skeleton', loc = loc[:])
                        app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict['Summon_Skeleton'].img, tags = 'Summon_Skeleton')
                        def cleanup_vis(name):
                            del app.vis_dict[name]
                            app.canvas.delete(name)
                        root.after(2333, lambda name = 'Summon_Skeleton' : cleanup_vis(name))
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+89-app.moved_down, text = 'Summon Earth Elemental', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+90-app.moved_down, text = 'Summon Earth Elemental', justify = 'center', font = ('Andale Mono', 14), fill = 'orange4', tags = 'text')
                        img = ImageTk.PhotoImage(Image.open('summon_imgs/Earth_Elemental.png'))
                        app.ent_dict['b'+str(num)] = Earth_Elemental(name = 'Earth_Elemental', img = img, loc = loc[:], owner = 'p2', number = 'b'+str(num))
                        app.grid[loc[0]][loc[1]] = 'b'+str(num)
                        app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = img, tags = 'b'+str(num))
                        root.after(2333, lambda t = 'text' : app.canvas.delete(t))
                        if f_locs == []:
                            app.get_focus(self.number)
                            root.after(2333, lambda ents_list = ents_list : self.continue_ai(ents_list))
                        else:
                            loc = f_locs.pop()
                            num = nums.pop()
                            root.after(2333, lambda l = loc, n = num : summon_loop(l, n))
                    loc = f_locs.pop()
                    num = nums.pop()
                    summon_loop(loc, num)
                else:
                    app.get_focus(self.number)
                    root.after(1333, lambda el = ents_list : self.continue_ai(el))
            else:
                app.get_focus(self.number)
                root.after(1333, lambda el = ents_list : self.continue_ai(el))
            
            
    # teleport near enemy ents, cast earthquake
    def continue_ai(self, ents_list):
        # get empty sqrs within 6 of any enemy
        ent_locs = [v.loc[:] for k,v in app.all_ents().items() if v.owner == 'p1']
        locs = [s for s in app.coords for c in ent_locs if dist(s, c) <= 6 and app.grid[s[0]][s[1]] == '']
        if locs != []:
            loc = choice(locs)
            app.focus_square(loc)
            root.after(1333, lambda el = ents_list, loc = loc : self.earth_mage_move(el, loc))
        else:
            root.after(1333, lambda el = ents_list : self.do_attack(el)) # ATTACK
            
            
    def earth_mage_move(self, ents_list, endloc):
        global selected
        self.move_used = True
        oldloc = self.loc[:]
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = oldloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.finish_move(ents_list, endloc))
        
    def finish_move(self, ents_list, endloc):
        app.grid[self.loc[0]][self.loc[1]] = ''
        app.canvas.delete(self.number)
        self.loc = endloc[:]
        app.grid[endloc[0]][endloc[1]] = self.number
        try: 
            del app.vis_dict['Teleport']
            app.canvas.delete('Teleport')
        except: pass
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = endloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.cleanup_teleport(ents_list, endloc))
        
    def cleanup_teleport(self, ents_list, endloc):
        del app.vis_dict['Teleport']
        app.canvas.delete('Teleport')
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = self.img, tags = self.tags)
        try: app.canvas.tag_lower(self.tags, 'large')
        except: pass
        app.canvas.tag_lower(self.tags, 'maptop')
        root.after(666, lambda ents_list = ents_list : self.finish_turn(ents_list))
        
        
    def finish_turn(self, ents_list):
        if self.attack_used == False:
            root.after(1333, lambda el = ents_list : self.do_attack(el)) # EXIT THROUGH ATTACK
        else:# CANNOT ATTACK, EXIT FUNC
            ents_list = ents_list[1:]
            if ents_list == []:
                app.end_turn()
            else:
                root.after(666, lambda e = ents_list : app.do_ai_loop(e))
    
    # earthquake, dmg near ents (non-flying) and move them 'back'
    def do_attack(self, ents_list):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            self.attack_used = True
    #         self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/earthquake.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            sqrs = []
            for c in app.coords:
                if dist(c, self.loc) <= 3:
                    sqrs.append(c)
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+84-app.moved_down, text = 'Earthquake', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+85-app.moved_down, text = 'Earthquake', font = ('Andale Mono', 16), fill = 'orange4', tags = 'text')
            app.vis_dict['Earthquake'] = Vis(name = 'Earthquake', loc = self.loc[:])
            app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Earthquake'].img, tags = 'Earthquake')
            # get all ents in vicinity
            ents = [k for k,v in app.all_ents().items() if v.owner != self.owner and v.loc in sqrs and v.move_type != 'flying' and v.move_type != 'ethereal']
            if ents != []:
                t1,t2,t3 = [],[],[]
                for e in ents:
                    if dist(app.ent_dict[e].loc, self.loc) == 3:
                        t1.append(e)
                    elif dist(app.ent_dict[e].loc, self.loc) == 2:
                        t2.append(e)
                    elif dist(app.ent_dict[e].loc, self.loc) == 1:
                        t3.append(e)
                ents = t1[:] + t2[:] + t3[:]
                def earthquake_loop(ents_list, ids):
                    global selected
                    if ids == []:
                        self.cleanup_attack(ents_list)
                    else:
                        id = ids[0]
                        ids = ids[1:]
                        app.get_focus(id)
                        loc = app.ent_dict[id].loc[:]
                        my_psyche = self.get_abl('psyche')
                        target_agl = app.ent_dict[id].get_abl('agl')
                        d = damage(my_psyche, target_agl)
                        pre = app.ent_dict[id].spirit
                        lock(apply_damage, self, app.ent_dict[id], -d, 'crushing', 'Earthquake')
                        post = app.ent_dict[id].spirit
                        d = pre - post
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = str(d)+' spirit', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = str(d)+' spirit', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                        if app.ent_dict[id].spirit <= 0:
                            app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 12), tags = 'text')
                            app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 12), tags = 'text')
                            name = 'dethlok'+str(app.death_count)
                            app.death_count += 1
                            app.dethloks[name] = tk.IntVar(0)
                            root.after(666, lambda id = id, name = name : app.kill(id, name))
                            root.wait_variable(app.dethloks[name])
                            earthquake_loop(ents_list, ids)
                        else: # ENT NOT KILLED, INSERT PSI PUSH
                            start_loc = app.ent_dict[id].loc[:]
                            # LEFT
                            if start_loc[0] < self.loc[0] and abs(start_loc[1] - self.loc[1]) <= 1:
                                if [start_loc[0]-1,start_loc[1]] in app.coords and app.grid[start_loc[0]-1][start_loc[1]] == '':
                                    if [start_loc[0]-2,start_loc[1]] in app.coords and app.grid[start_loc[0]-2][start_loc[1]] == '':
                                        dest = [start_loc[0]-2,start_loc[1]]
                                    else:
                                        dest = [start_loc[0]-1,start_loc[1]]
                                else:
                                    dest = start_loc[:]
                            # RIGHT
                            elif start_loc[0] > self.loc[0] and abs(start_loc[1] - self.loc[1]) <= 1:
                                if [start_loc[0]+1,start_loc[1]] in app.coords and app.grid[start_loc[0]+1][start_loc[1]] == '':
                                    if [start_loc[0]+2,start_loc[1]] in app.coords and app.grid[start_loc[0]+2][start_loc[1]] == '':
                                        dest = [start_loc[0]+2,start_loc[1]]
                                    else:
                                        dest = [start_loc[0]+1,start_loc[1]]
                                else:
                                    dest = start_loc[:]
                            # UP
                            elif abs(start_loc[0] - self.loc[0]) <= 1 and start_loc[1] < self.loc[1]:
                                if [start_loc[0],start_loc[1]-1] in app.coords and app.grid[start_loc[0]][start_loc[1]-1] == '':
                                    if [start_loc[0],start_loc[1]-2] in app.coords and app.grid[start_loc[0]][start_loc[1]-2] == '':
                                        dest = [start_loc[0],start_loc[1]-2]
                                    else:
                                        dest = [start_loc[0],start_loc[1]-1]
                                else:
                                    dest = start_loc[:]
                            # DOWN
                            elif abs(start_loc[0] - self.loc[0]) <= 1 and start_loc[1] > self.loc[1]:
                                if [start_loc[0],start_loc[1]+1] in app.coords and app.grid[start_loc[0]][start_loc[1]+1] == '':
                                    if [start_loc[0],start_loc[1]+2] in app.coords and app.grid[start_loc[0]][start_loc[1]+2] == '':
                                        dest = [start_loc[0],start_loc[1]+2]
                                    else:
                                        dest = [start_loc[0],start_loc[1]+1]
                                else:
                                    dest = start_loc[:]
                            # end destination logic
                            x = start_loc[0]*100+50-app.moved_right
                            y = start_loc[1]*100+50-app.moved_down
                            endx = dest[0]*100+50-app.moved_right
                            endy = dest[1]*100+50-app.moved_down
                            if start_loc != dest: # do move then go to next eq loop, else go to next eq loop
                                selected = [id]
                                def finish_psionic_push(tar, end_loc, start_loc):
                                    global selected
                                    selected = []
                                    app.ent_dict[tar].loc = end_loc[:]
                                    app.grid[start_loc[0]][start_loc[1]] = ''
                                    app.grid[end_loc[0]][end_loc[1]] = tar
                                    root.after(3666, lambda el = ents_list, ids = ids : earthquake_loop(el, ids))
                                def psi_move_loop(ent, x, y, endx, endy, sqr, start_sqr):
                                    if x % 25 == 0 and y % 25 == 0:
                                        app.ent_dict[ent].rotate_image()
                                        app.canvas.delete(ent)
                                        app.canvas.create_image(x, y, image = app.ent_dict[ent].img, tags = app.ent_dict[ent].tags)
                                    if x > endx:
                                        x -= 10
                                        app.canvas.move(ent, -10, 0)
                                    elif x < endx: 
                                        x += 10
                                        app.canvas.move(ent, 10, 0)
                                    if y > endy: 
                                        y -= 10
                                        app.canvas.move(ent, 0, -10)
                                    elif y < endy: 
                                        y += 10
                                        app.canvas.move(ent, 0, 10)
                                    try: app.canvas.tag_lower(app.ent_dict[ent].tags, 'large')
                                    except: pass
                                    app.canvas.tag_lower(app.ent_dict[ent].tags, 'maptop')
                                    if x == endx and y == endy:
                                        root.after(666, lambda e = ent, s = sqr, ss = start_sqr : finish_psionic_push(e, s, ss))
                                    else:
                                        root.after(50, lambda id = id, x = x, y = y, endx = endx, endy = endy, s = sqr, s2 = start_sqr : psi_move_loop(id, x, y, endx, endy, s, s2))
                                psi_move_loop(id, x, y, endx, endy, dest, start_loc)
                            else:
                                root.after(3666, lambda el = ents_list, ids = ids : earthquake_loop(el, ids))
                    # first call of eq loop, called if affected ents exist
                root.after(1999, lambda el = ents_list, ids = ents : earthquake_loop(el, ids))
            else: # no affected ents, exit
                root.after(3333, lambda el = ents_list : self.cleanup_attack(el))
            
            
    def cleanup_attack(self, ents_list):
#         self.init_normal_anims()
        names = [k for k,v in app.vis_dict.items() if v.name == 'Earthquake']
        for n in names:
            del app.vis_dict[n]
        try:
            del app.vis_dict['Earthquake']
            app.canvas.delete('Earthquake')
        except: pass
        try: app.canvas.delete('text')
        except: pass
        ents_list = ents_list[1:]
        if ents_list == []:
            app.end_turn()
        else:
            root.after(666, lambda el = ents_list : app.do_ai_loop(el))
        
        
#     def legal_attacks(self):
#         sqrs = []
#         for coord in app.coords:
#             if dist(coord, self.loc) <= 3:
#                 if app.grid[coord[0]][coord[1]] != '' and app.grid[coord[0]][coord[1]] != 'block':
#                     sqrs.append(coord)
#         return sqrs
        
    # not used for movement, kept for purposes of monkey-patching
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        for c in app.coords:
            if dist(loc, c) <= 5 and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist
        
        
class Earth_Elemental(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 6
        self.agl = 4
        self.end = 7
        self.dodge = 3
        self.psyche = 3
        self.spirit = 19
        self.move_range = 4
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['slashing', 'piercing', 'elec']
        self.weak = ['crushing', 'fire', 'cold', 'magick']
        super().__init__(name, img, loc, owner, number)
        
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
#             self.init_attack_anims()
#             effect1 = mixer.Sound('Sound_Effects/.ogg')
#             sound_effects.play(effect1, 0)
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'crushing', 'Rock Punch')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:# HIT, KILL
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    name = 'dethlok'+str(app.death_count)
                    app.death_count += 1
                    app.dethloks[name] = tk.IntVar(0)
                    root.after(2666, self.cleanup_attack)
                    root.after(2666, lambda id = id, name = name : app.kill(id, name))
                    root.wait_variable(app.dethloks[name])
                    self.finish_attack(ents_list)
                else:# HIT, NO KILL
                    root.after(2666, lambda e = ents_list : self.finish_attack(e))
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list : self.finish_attack(e))
        
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)

        
    def cleanup_attack(self):
#         self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
            
    def finish_attack(self, ents_list):
#         self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
        self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
# casts firewall after teleporting randomly within a dist, resummons fire elementals if they all die
# immune to move_effects, does not use legal_moves
class Fire_Mage(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 5
        self.agl = 6
        self.end = 6
        self.dodge = 5
        self.psyche = 9
        self.spirit = 79
        self.move_range = 9
        self.waiting = waiting
        self.move_type = 'teleport'
        self.weak = ['cold', 'acid', 'poison']
        self.resist = ['fire', 'slashing', 'crushing']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
    
    # make casting anims
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else: # summon elementals
            root.after(1333, lambda el = ents_list : self.elemental_summon(el))
            
    def elemental_summon(self, ents_list):
        effect1 = mixer.Sound('Sound_Effects/warlock_summon.ogg')
        effect1.set_volume(.5)
        sound_effects.play(effect1, 0)
        f_elems = [v.name for k,v in app.ent_dict.items() if v.name == 'Fire_Elemental']
        if f_elems == []:
            maxid = max([int(v.number[1:]) for k,v in app.ent_dict.items() if v.owner == self.owner])
            if app.effects_counter <= maxid:
                app.effects_counter = maxid+1
            num1 = app.effects_counter
            app.effects_counter += 1
            num2 = app.effects_counter
            app.effects_counter += 1
            num3 = app.effects_counter
            app.effects_counter += 1
            nums = [num1, num2, num3]
            # get random empty location
            coords = [c for c in app.coords if dist(c, self.loc) <= 7]
            empty = [c for c in coords if app.grid[c[0]][c[1]] == '']
            if len(empty) >= 3:
                f_loc1 = choice(empty)
                empty.remove(f_loc1)
                f_loc2 = choice(empty)
                empty.remove(f_loc2)
                f_loc3 = choice(empty)
                empty.remove(f_loc3)
                f_locs = [f_loc1[:], f_loc2[:], f_loc3[:]]
                def summon_loop(loc, num):
                    app.focus_square(loc)
                    app.vis_dict['Summon_Skeleton'] = Vis(name = 'Summon_Skeleton', loc = loc[:])
                    app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict['Summon_Skeleton'].img, tags = 'Summon_Skeleton')
                    def cleanup_vis(name):
                        del app.vis_dict[name]
                        app.canvas.delete(name)
                    root.after(2333, lambda name = 'Summon_Skeleton' : cleanup_vis(name))
                    app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+89-app.moved_down, text = 'Summon Fire Elemental', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
                    app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+90-app.moved_down, text = 'Summon Fire Elemental', justify = 'center', font = ('Andale Mono', 14), fill = 'orangered2', tags = 'text')
                    img = ImageTk.PhotoImage(Image.open('summon_imgs/Fire_Elemental.png'))
                    app.ent_dict['b'+str(num)] = Fire_Elemental(name = 'Fire_Elemental', img = img, loc = loc[:], owner = 'p2', number = 'b'+str(num))
                    app.grid[loc[0]][loc[1]] = 'b'+str(num)
                    app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = img, tags = 'b'+str(num))
                    root.after(2333, lambda t = 'text' : app.canvas.delete(t))
                    if f_locs == []:
                        app.get_focus(self.number)
                        root.after(2333, lambda ents_list = ents_list : self.continue_ai(ents_list))
                    else:
                        loc = f_locs.pop()
                        num = nums.pop()
                        root.after(2333, lambda l = loc, n = num : summon_loop(l, n))
                loc = f_locs.pop()
                num = nums.pop()
                summon_loop(loc, num)
            else:
                app.get_focus(self.number)
                root.after(2333, lambda ents_list = ents_list : self.continue_ai(ents_list))
        else:
            app.get_focus(self.number)
            root.after(2333, lambda ents_list = ents_list : self.continue_ai(ents_list))
        # End Summon Elemental, ATTEMPT ATTACK
            
    # teleport to random sqr within 6 of an enemy ent, do firewall
    def continue_ai(self, ents_list):
        # get empty sqrs within 6 of any enemy
        ent_locs = [v.loc[:] for k,v in app.all_ents().items() if v.owner == 'p1']
        locs = [s for s in app.coords for c in ent_locs if dist(s, c) <= 6 and app.grid[s[0]][s[1]] == '']
        if locs != []:
            loc = choice(locs)
            app.focus_square(loc)
            root.after(1333, lambda el = ents_list, loc = loc : self.fire_mage_move(el, loc))
        else:
            root.after(1333, lambda el = ents_list : self.do_attack(el)) # ATTACK
            
            
    def fire_mage_move(self, ents_list, endloc):
        global selected
        self.move_used = True
        oldloc = self.loc[:]
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = oldloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.finish_move(ents_list, endloc))
        
    def finish_move(self, ents_list, endloc):
        app.grid[self.loc[0]][self.loc[1]] = ''
        app.canvas.delete(self.number)
        self.loc = endloc[:]
        app.grid[endloc[0]][endloc[1]] = self.number
        try: 
            del app.vis_dict['Teleport']
            app.canvas.delete('Teleport')
        except: pass
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = endloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.cleanup_teleport(ents_list, endloc))
        
    def cleanup_teleport(self, ents_list, endloc):
        del app.vis_dict['Teleport']
        app.canvas.delete('Teleport')
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = self.img, tags = self.tags)
        try: app.canvas.tag_lower(self.tags, 'large')
        except: pass
        app.canvas.tag_lower(self.tags, 'maptop')
        root.after(666, lambda ents_list = ents_list : self.finish_turn(ents_list))
        
    def finish_turn(self, ents_list):
        if self.attack_used == False:
            root.after(1333, lambda el = ents_list : self.do_attack(el)) # EXIT THROUGH ATTACK
        else:# CANNOT ATTACK, EXIT FUNC
            self.ai_end_turn(ents_list)
    
    def do_attack(self, ents_list):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            self.attack_used = True
    #         self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/firewall.ogg')
            effect1.set_volume(.7)
            sound_effects.play(effect1, 0)
            sqrs = []
            for c in app.coords:
                if c[0] == self.loc[0] and abs(c[1] - self.loc[1]) <= 6:
                    sqrs.append(c)
                elif abs(c[0] - self.loc[0]) <= 5 and c[1] == self.loc[1]:
                    sqrs.append(c)
            sqrs.remove(self.loc)
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+84-app.moved_down, text = 'Firewall', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+85-app.moved_down, text = 'Firewall', font = ('Andale Mono', 16), fill = 'orangered2', tags = 'text')
            for s in sqrs:
                u_name = 'Firewall' + str(app.effects_counter)
                app.effects_counter += 1
                app.vis_dict[u_name] = Vis(name = 'Firewall', loc = s[:])
                app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[u_name].img, tags = 'Firewall')
            # get all ents in paths
            ents = [k for k,v in app.all_ents().items() if v.name != 'Fire_Elemental' and v.loc in sqrs]
            if ents != []:
                # check for dmg and create text object
                def firewall_loop(ents):
                    if ents == []:
                        self.cleanup_attack(ents_list)
                    else:
                        app.canvas.delete('text')
                        id = ents[0]
                        ents = ents[1:]
                        app.get_focus(id)
                        my_psyche = self.get_abl('psyche')
                        target_end = app.ent_dict[id].get_abl('end')
                        d = damage(my_psyche, target_end)
                        pre = app.ent_dict[id].spirit
                        lock(apply_damage, self, app.ent_dict[id], -d, 'fire', 'Firewall')
                        post = app.ent_dict[id].spirit
                        d = pre - post
                        loc = app.ent_dict[id].loc[:]
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = str(d)+' spirit', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = str(d)+' spirit', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                        if app.ent_dict[id].spirit <= 0:
                            app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 12), tags = 'text')
                            app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 12), tags = 'text')
                            name = 'dethlok'+str(app.death_count)
                            app.death_count += 1
                            app.dethloks[name] = tk.IntVar(0)
                            root.after(2222, lambda t = 'text' : app.canvas.delete('text'))
                            root.after(2333, lambda id = id, name = name : app.kill(id, name))
                            root.wait_variable(app.dethloks[name])
                            firewall_loop(ents)
                        else:
                            root.after(3666, lambda ents = ents : firewall_loop(ents))
                root.after(1666, lambda e = ents : firewall_loop(e))
            else: # cleanup vis / cont ai_loop
                root.after(2999, lambda el = ents_list : self.cleanup_attack(el))
            
    def cleanup_attack(self, ents_list):
#         self.init_normal_anims()
        names = [k for k,v in app.vis_dict.items() if v.name == 'Firewall']
        for n in names:
            del app.vis_dict[n]
        try:
            app.canvas.delete('Firewall')
        except: pass
        try: app.canvas.delete('text')
        except: pass
        ents_list = ents_list[1:]
        if ents_list == []:
            app.end_turn()
        else:
            root.after(666, lambda e = ents_list : app.do_ai_loop(e))
    # this unit has no need of legal_attacks(), left here in case of overwrite
    def legal_attacks(self):
        pass
    # this unit has no need of legal_moves(), left here in case of overwrite
    def legal_moves(self):
        pass
        
        
class Sorceress(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 5
        self.agl = 6
        self.end = 6
        self.dodge = 6
        self.psyche = 7
        self.spirit = 59
        self.move_range = 6
        self.waiting = waiting
        self.move_type = 'teleport'
        self.weak = ['slashing', 'piercing', 'crushing', 'cold']
        self.resist = ['magick', 'fire']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    # attempt to teleport barbarian, do not teleport away instead teleport towards barbarian
    #  SORCERESS AI
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.teleport_barbarian(ents_list)
    # b2 is barbarian
    def teleport_barbarian(self, ents_list):
        # if b2 within 10 sqrs teleport it to the nearest enemy ent
        sqrs = [s for s in app.coords if dist(s, self.loc) <= 10]
        ents = [k for k,v in app.all_ents().items() if v.loc in sqrs]
        if 'b2' in ents:
            # find nearest enemy ent
            enemy_ent_locs = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
            loc = reduce(lambda a,b : a if dist(self.loc,a) < dist(self.loc,b) else b, enemy_ent_locs)
            # find the closest empty sqr that is within teleport range, debug maybe impossible edge case will not exist
            empty_sqrs = [s for s in app.coords if app.grid[s[0]][s[1]] == '' and dist(s, self.loc) < 5]
            closest_sqr = reduce(lambda a,b : a if dist(self.loc,a) < dist(self.loc,b) else b, empty_sqrs)
            # teleport b2 to closest_sqr
            oldloc = app.ent_dict['b2'].loc[:]
            app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = oldloc)
            vis = app.vis_dict['Teleport']
            app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
            root.after(2333, lambda ents_list = ents_list, oldloc = oldloc, newloc = closest_sqr : self.cleanup_bar_teleport(ents_list, oldloc, newloc))
        else:
            self.continue_ai(ents_list)
        
    def cleanup_bar_teleport(self, ents_list, oldloc, newloc):
        del app.vis_dict['Teleport']
        app.canvas.delete('Teleport')
        app.grid[oldloc[0]][oldloc[1]] = ''
        app.grid[newloc[0]][newloc[1]] = 'b2'
        app.ent_dict['b2'].loc = newloc[:]
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = newloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(newloc[0]*100+50-app.moved_right, newloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        app.canvas.create_image(newloc[0]*100+50-app.moved_right, newloc[1]*100+50-app.moved_down, image = app.ent_dict['b2'].img, tags = app.ent_dict['b2'].tags)
        root.after(2333, lambda ents_list = ents_list : self.continue_ai(ents_list))
        
            
    def continue_ai(self, ents_list):
        try:
            del app.vis_dict['Teleport']
            app.canvas.delete('Teleport')
        except: pass
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []:
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # CANNOT ATTACK FROM START LOC, GET TARGET AND MOVE TOWARDS
            # among legal sqrs, move to sqr within dist of attack or that minimizes dist
            leg_sqrs = self.legal_moves()
            if leg_sqrs != []:
                enemy_ent_locs = [v.loc for k,v in app.spell_target_ents().items() if v.owner != self.owner]
                # first try to move to sqr at edge of attack range
                goals = [c for c in app.coords for e in enemy_ent_locs if dist(c, e) <= 3 and app.grid[c[0]][c[1]] == '']
                target_sqrs = []
                for sqr in leg_sqrs:
                    if sqr in goals:
                        target_sqrs.append(sqr)
                if target_sqrs != []: # move to sqr within target_sqrs that is furthest from enemy_ent_loc
                    furthest_sqrs = [s for s in target_sqrs for x in enemy_ent_locs if dist(s, x) == max([dist(j, y) for j in target_sqrs for y in enemy_ent_locs])]
                    loc = choice(furthest_sqrs)
                    root.after(666, lambda sqr = loc : app.focus_square(sqr))
                    root.after(1333, lambda el = ents_list, endloc = loc : self.sorceress_move(el, loc))
                else: # move to sqr within leg_sqrs that minimizes dist
                    closest_sqrs = [s for s in leg_sqrs for x in enemy_ent_locs if dist(s, x) == min([dist(j, y) for j in leg_sqrs for y in enemy_ent_locs])]
                    loc = choice(closest_sqrs)
                    root.after(666, lambda sqr = loc : app.focus_square(sqr))
                    root.after(1333, lambda el = ents_list, endloc = loc : self.sorceress_move(el, loc))
            else: # continue ai_loop
                self.ai_end_turn(ents_list)
            
    # change to 'teleport move'
    def sorceress_move(self, ents_list, endloc):
        global selected
        self.move_used = True
        oldloc = self.loc[:]
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = oldloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.finish_move(ents_list, endloc))
        
    def finish_move(self, ents_list, endloc):
        app.grid[self.loc[0]][self.loc[1]] = ''
        app.canvas.delete(self.number)
        self.loc = endloc[:]
        app.grid[endloc[0]][endloc[1]] = self.number
        try: 
            del app.vis_dict['Teleport']
            app.canvas.delete('Teleport')
        except: pass
        app.vis_dict['Teleport'] = Vis(name = 'Teleport', loc = endloc[:])
        vis = app.vis_dict['Teleport']
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Teleport')
        root.after(2999, lambda ents_list = ents_list, endloc = endloc : self.cleanup_teleport(ents_list, endloc))
        
    def cleanup_teleport(self, ents_list, endloc):
        del app.vis_dict['Teleport']
        app.canvas.delete('Teleport')
        app.canvas.create_image(endloc[0]*100+50-app.moved_right, endloc[1]*100+50-app.moved_down, image = self.img, tags = self.tags)
        try: app.canvas.tag_lower(self.tags, 'large')
        except: pass
        app.canvas.tag_lower(self.tags, 'maptop')
        root.after(666, lambda ents_list = ents_list : self.finish_turn(ents_list))
        
        
    def finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs == []:
                self.ai_end_turn(ents_list)
            else:
                ids = [k for k,v in app.spell_target_ents().items() if v.loc in atk_sqrs]
                id = choice(ids)
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(1333, lambda el = ents_list, t = id : self.do_attack(el, t)) # EXIT THROUGH ATTACK
        else:
            self.ai_end_turn(ents_list)
    
    # change to fireblast
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            app.get_focus(id)
            self.attack_used = True
    #         self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/immolate.ogg')
            effect1.set_volume(.7)
            sound_effects.play(effect1, 0)
            visloc = app.ent_dict[id].loc[:]
            app.vis_dict['Fireblast'] = Vis(name = 'Fireblast', loc = visloc)
            app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Fireblast'].img, tags = 'Fireblast')
            app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+89-app.moved_down, text = 'Fireblast', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
            app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+90-app.moved_down, text = 'Fireblast', font = ('Andale Mono', 16), fill = 'brickred', tags = 'text')
            my_psyche = self.get_abl('psyche')
            target_psyche = app.ent_dict[id].get_abl('psyche')
            if to_hit(my_psyche, target_psyche) == True:
                d = damage(my_psyche, target_psyche)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'fire', 'Fireblast')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            else:
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(3666, lambda  el = ents_list, id = id : self.cleanup_attack(el, id))
        
    def cleanup_attack(self, ents_list, id):
        self.init_normal_anims()
        try: 
            app.canvas.delete('text')
            del app.vis_dict['Fireblast']
            app.canvas.delete('Fireblast')
        except: pass
        if app.ent_dict[id].spirit <= 0:
            name = 'dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(666, lambda id = id, name = name : app.kill(id, name))
            root.wait_variable(app.dethloks[name])
            self.finish_attack(ents_list)
        else:
            self.finish_attack(ents_list)
                    
    def finish_attack(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 3:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.spell_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        for c in app.coords:
            if dist(loc, c) <= 5 and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist
        
        
class Orc_Axeman(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 6
        self.agl = 6
        self.end = 6
        self.dodge = 7
        self.psyche = 3
        self.spirit = 29
        self.move_range = 4
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['fire', 'cold', 'elec']
        self.weak = ['poison']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
#             self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/orc_axeman_attack.ogg')
            sound_effects.play(effect1, 0)
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Axe Swipe')
                self.ai_end_turn(ents_list)
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(1666, lambda e = ents_list : self.finish_attack(e))
        
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
        
    def cleanup_attack(self):
#         self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
            
    def finish_attack(self, ents_list):
#         self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
        self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
        
class Fire_Elemental(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 4
        self.agl = 4
        self.end = 3
        self.dodge = 4
        self.psyche = 2
        self.spirit = 19
        self.move_range = 4
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['fire', 'slashing', 'piercing', 'crushing']
        self.weak = ['explosive', 'cold']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if 3 <= dist(el,g) <= 4 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if 3 <= dist(el,g) <= 4 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if 3 <= dist(el,g) <= 4 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        global selected_vis
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            self.attack_used = True
            app.get_focus(id)
    #         self.init_attack_anims()
            effect1 = mixer.Sound('Sound_Effects/fire_elemental_attack.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            loc = app.ent_dict[id].loc[:]
            app.vis_dict['Fire_Elem_Ball'] = Vis(name = 'Fire_Elem_Ball', loc = self.loc[:])
            app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
            selected_vis = ['Fire_Elem_Ball']
            def fireball_loop(startx, endx, starty, endy, xstep, ystep):
                if starty > endy:
                    starty -= ystep
                    app.canvas.delete('Fire_Elem_Ball')
                    app.canvas.create_image(startx, starty, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
                    app.canvas.tag_raise('Fire_Elem_Ball')
                elif starty < endy:
                    starty += ystep
                    app.canvas.delete('Fire_Elem_Ball')
                    app.canvas.create_image(startx, starty, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
                    app.canvas.tag_raise('Fire_Elem_Ball')
                if startx > endx:
                    startx -= xstep
                    app.canvas.delete('Fire_Elem_Ball')
                    app.canvas.create_image(startx, starty, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
                    app.canvas.tag_raise('Fire_Elem_Ball')
                elif startx < endx:
                    startx += xstep
                    app.canvas.delete('Fire_Elem_Ball')
                    app.canvas.create_image(startx, starty, image = app.vis_dict['Fire_Elem_Ball'].img, tags = 'Fire_Elem_Ball')
                    app.canvas.tag_raise('Fire_Elem_Ball')
                    # debug here, if within certain range...
                app.vis_dict['Fire_Elem_Ball'].rotate_image()
                if abs(starty - endy) < 13 and abs(startx - endx) < 13:
                    root.after(333, lambda el = ents_list, id = id : self.continue_attack(el, id))
                else:
                    root.after(40, lambda sx = startx, ex = endx, sy = starty, ey = endy, xs = xstep, ys = ystep  : fireball_loop(sx, ex, sy, ey, xs, ys))
            startx = self.loc[0]*100+50-app.moved_right
            starty = self.loc[1]*100+50-app.moved_down
            endx = loc[0]*100+50-app.moved_right
            endy = loc[1]*100+50-app.moved_down
            if startx == endx:
                xstep = 0
                ystep = 10
            elif starty == endy:
                xstep = 10
                ystep = 0
            else:
                slope = Fraction(abs(startx - endx), abs(starty - endy))
                # needs to be moving at least 10 pixels, xstep + ystep >= 10
                xstep = slope.numerator
                ystep = slope.denominator
                while xstep + ystep < 10:
                    xstep *= 2
                    ystep *= 2
            fireball_loop(startx, endx, starty, endy, xstep, ystep)
            
    def continue_attack(self, ents_list, id):
        loc = app.ent_dict[id].loc[:]
        my_str = self.get_abl('str')
        target_dodge = app.ent_dict[id].get_abl('dodge')
        if to_hit(my_str, target_dodge) == True:
            target_end = app.ent_dict[id].get_abl('end')
            d = damage(my_str, target_end)
            pre = app.ent_dict[id].spirit
            lock(apply_damage, self, app.ent_dict[id], -d, 'fire', 'Fireball')
            post = app.ent_dict[id].spirit
            d = pre - post
            app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            if app.ent_dict[id].spirit <= 0:
                app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, lambda e = ents_list, id = id : self.cleanup_attack(e, id))
        else:# MISS
            app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(2666, lambda e = ents_list, id = id : self.cleanup_attack(e, id))
            
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def cleanup_attack(self, ents_list, id):
        global selected_vis
        selected_vis = []
        self.init_normal_anims()
        try: 
            app.canvas.delete('text')
            del app.vis_dict['Fire_Elem_Ball']
            app.canvas.delete('Fire_Elem_Ball')
        except: pass
        if app.ent_dict[id].spirit <= 0:
            name = 'dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(666, lambda id = id, name = name : app.kill(id, name))
            root.wait_variable(app.dethloks[name])
            self.finish_attack(ents_list)
        else:
            self.finish_attack(ents_list)
                    
    def finish_attack(self, ents_list):
        if self.move_used == False:
            self.get_path(ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) <= 4:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
        
class Barbarian(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 10
        self.agl = 8
        self.end = 8
        self.dodge = 5
        self.psyche = 3
        self.spirit = 79
        self.move_range = 3
        self.waiting = waiting
        self.move_type = 'normal'
        self.weak = ['magick']
        self.resist = ['slashing', 'piercing', 'crushing', 'fire', 'elec', 'cold', 'poison']
        super().__init__(name, img, loc, owner, number)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            self.continue_ai(ents_list)
            
    def continue_ai(self, ents_list):
        atk_sqrs = self.legal_attacks()
        if atk_sqrs != []: # CAN ATTACK BEFORE MOVING
            any = atk_sqrs[0]
            id = app.grid[any[0]][any[1]]
            root.after(666, lambda id = id : app.get_focus(id))
            root.after(1333, lambda el = ents_list, id = id : self.do_attack(el, id)) # ATTACK
        else: # FIND PATH
            self.get_path(ents_list)
            
    def get_path(self, ents_list):
        els = [v.loc for k,v in app.action_target_ents().items() if v.owner != self.owner]
        cs = [c for c in app.coords if sum([ef.avoid for k,ef in app.loc_effects_dict[tuple(c)].effects_dict.items()])*10 < randrange(30,60)]
        fls = [v.loc for k,v in app.all_ents().items() if v.owner == self.owner]
        egrid = deepcopy(app.grid)
        for s in fls:
            egrid[s[0]][s[1]] = ''
        gs1 = [g for g in cs for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        gs2 = [g for g in cs for el in els if dist(el,g) == 1 and egrid[g[0]][g[1]] == '']
        gs3 = [g for g in app.coords for el in els if dist(el,g) == 1 and app.grid[g[0]][g[1]] == '']
        if bfs(self.loc[:], gs1, app.grid[:]):
            path = bfs(self.loc[:], gs1, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs2, egrid[:]):
            path = bfs(self.loc[:], gs2, egrid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, app.grid[:]):
            path = bfs(self.loc[:], gs3, app.grid[:])
            self.get_move(path, cs, ents_list)
        elif bfs(self.loc[:], gs3, egrid[:]):
            path = bfs(self.loc[:], gs3, egrid[:])
            self.get_move(path, cs, ents_list)
        else:
            self.ai_end_turn(ents_list)
            
    def get_move(self, path, cs, ents_list):
        # get m of ms in path in cs else m of ms in path else end
        ms = self.legal_moves()
        moves = [m for m in ms if m in path and m in cs]
        if moves == []:
            moves = [m for m in ms if m in path]
            if moves == []:
                self.ai_end_turn(ents_list)
            else:
                m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
                root.after(666, lambda sqr = m : app.focus_square(sqr))
                root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
        else:
            m = reduce(lambda a,b : a if dist(a,self.loc) > dist(b,self.loc) else b, moves)
            root.after(666, lambda sqr = m : app.focus_square(sqr))
            root.after(1333, lambda el = ents_list, sqr = m : self.ai_move(el, sqr))
            
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list)
        else:
            app.get_focus(id)
            self.init_attack_anims()
#             effect1 = mixer.Sound('Sound_Effects/undead_attack.ogg')
            sound_effects.play(effect1, 0)
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:# HIT
                my_str = self.get_abl('str')
                tar_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, tar_end)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Fury Strikes')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:# HIT, KILL
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    name = 'dethlok'+str(app.death_count)
                    app.death_count += 1
                    app.dethloks[name] = tk.IntVar(0)
                    root.after(2666, self.cleanup_attack)
                    root.after(2666, lambda id = id, name = name : app.kill(id, name))
                    root.wait_variable(app.dethloks[name])
                    self.finish_attack(ents_list)
                else:# HIT, NO KILL
                    root.after(2666, lambda e = ents_list : self.finish_attack(e))
            else:# MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list : self.finish_attack(e))
        
    def ai_finish_turn(self, ents_list):
        if self.attack_used == False:
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(999, lambda el = ents_list, t = id : self.do_attack(el, t))
            else:
                self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
        
    def cleanup_attack(self):
        self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
            
    def finish_attack(self, ents_list):
        self.init_normal_anims()
        try: app.canvas.delete('text')
        except: pass
        self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner and id in app.action_target_ents().keys():
                        sqrs.append(c)
        return sqrs
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
    # if no ent within immediate move/attack range, only move toward witch
class Minotaur_Top(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = True):
#         self.actions = {'attack':self.do_attack}
        self.attack_used = False
        self.str = 11
        self.agl = 11
        self.end = 11
        self.dodge = 5
        self.psyche = 9
        self.spirit = 163
        self.waiting = waiting
        super().__init__(name, img, loc, owner, number, type = 'large')
        self.move_type = 'normal'
        self.immovable = True
        
    def init_stomp_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in walk('./animations/Minotaur_Stomp_Top/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Minotaur_Stomp_Top/' + anim))
            self.anim_dict[i] = a
            
    def init_move_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in walk('./animations/Minotaur_Move_Top/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Minotaur_Move_Top/' + anim))
            self.anim_dict[i] = a
            
    # 'tall' ent, bigger than 100 pixels height, needs to be split into 2 images so the 'top' image is 'large' (raised above 'maptop', bottom part of ent is hidden behind 'maptop'
class Minotaur(Summon):
    def __init__(self, name, img, loc, owner, number, waiting = False):
        self.actions = {'attack':self.charge_attack}
        self.attack_used = False
        self.str = 11
        self.agl = 11
        self.end = 11
        self.dodge = 5
        self.psyche = 9
        self.spirit = 163
        self.move_range = 5
        self.waiting = waiting
        self.move_type = 'normal'
        self.resist = ['piercing', 'crushing', 'poison', 'cold', 'acid', 'fire']
        self.weak = ['slashing']
        super().__init__(name, img, loc, owner, number, type = 'large_bottom')
        self.immovable = True
        # create top half
        img = ImageTk.PhotoImage(Image.open('animations/Minotaur_Top/0.png'))
        app.ent_dict[self.number+'top'] = Minotaur_Top(name = 'Minotaur_Top', img = img, loc = [self.loc[0],self.loc[1]], owner = 'p2', number = self.number+'top')
        
    def large_undo(self):
        app.canvas.delete(self.number+'top')
        del app.ent_dict[self.number+'top']
        
    def init_stomp_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in walk('./animations/Minotaur_Stomp_Bot/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Minotaur_Stomp_Bot/' + anim))
            self.anim_dict[i] = a
            
    def init_move_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in walk('./animations/Minotaur_Move_Bot/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Minotaur_Move_Bot/' + anim))
            self.anim_dict[i] = a
        
    # takes 2 locs that share 1 axis, returns True if all sqrs between are empty ('')
    def clear_path(self, myloc, enloc):
        if myloc[0] == enloc[0]:
            def check_loop(start, end):
                if start[0] > end[0]:
                    x = start[0] - 1
                    start = [x,start[1]]
                    if start == end:
                        return True
                    elif app.grid[start[0]][start[1]] != '':
                        return False
                    else:
                        return check_loop(start, end)
                elif start[0] < end[0]:
                    x = start[0] + 1
                    start = [x,start[1]]
                    if start == end:
                        return True
                    elif app.grid[start[0]][start[1]] != '':
                        return False
                    else:
                        return check_loop(start, end)
            return check_loop(myloc[:], enloc[:])
        elif myloc[1] == enloc[1]:
            def check_loop(start, end):
                if start[0] > end[0]:
                    x = start[0] - 1
                    start = [x, start[1]]
                    if start == end:
                        return True
                    elif app.grid[start[0]][start[1]] != '':
                        return False
                    else:
                        return check_loop(start, end)
                elif start[0] < end[0]:
                    x = start[0] + 1
                    start = [x, start[1]]
                    if start == end:
                        return True
                    elif app.grid[start[0]][start[1]] != '':
                        return False
                    else:
                        return check_loop(start, end)
            return check_loop(myloc[:], enloc[:])
        else:
            return False
            
    def charge_attack(self, ents_list, tar):
        global selected
        effect1 = mixer.Sound('Sound_Effects/minotaur_charge_attack.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, -1)
        self.init_move_anims()
        app.ent_dict[self.number+'top'].init_move_anims()
        selected = [self.number, self.number+'top']
        id = self.number
        start_sqr = self.loc[:]
        goals = [c for c in app.coords if dist(c, app.ent_dict[tar].loc) == 1]
        path = bfs(start_sqr, goals, app.grid) 
        end_sqr = path[-1]
        begin = path[0]
        end = path[1]
        x = begin[0]*100+50-app.moved_right
        y = begin[1]*100+50-app.moved_down
        endx = end[0]*100+50-app.moved_right
        endy = end[1]*100+50-app.moved_down
        def move_loop(id, x, y, endx, endy, start_sqr, end_sqr, path, acm):
            acm += 10
            if acm >= 40:
                app.ent_dict[id+'top'].rotate_image()
                self.rotate_image()
                acm = 0
            if x > endx:
                x -= 10
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.delete(id+'top')
                app.canvas.create_image(x, y, image = app.ent_dict[id+'top'].img, tags = (id+'top','large'))
            if x < endx: 
                x += 10
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.delete(id+'top')
                app.canvas.create_image(x, y, image = app.ent_dict[id+'top'].img, tags = (id+'top','large'))
            if y > endy: 
                y -= 10
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.delete(id+'top')
                app.canvas.create_image(x, y, image = app.ent_dict[id+'top'].img, tags = (id+'top','large'))
            if y < endy: 
                y += 10
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.delete(id+'top')
                app.canvas.create_image(x, y, image = app.ent_dict[id+'top'].img, tags = (id+'top','large'))
            try: app.canvas.tag_lower((self.tags), 'large')
            except: pass
            app.canvas.tag_lower((self.tags), 'maptop')
            app.canvas.tag_raise('cursor')
            if x == end_sqr[0]*100+50-app.moved_right and y == end_sqr[1]*100+50-app.moved_down: # END WHOLE MOVE
                self.finish_charge(end_sqr, start_sqr, tar, ents_list)
            elif x == endx and y == endy: # END PORTION OF PATH
                path = path[1:]
                begin = path[0]
                end = path[1]
                x = begin[0]*100+50-app.moved_right
                y = begin[1]*100+50-app.moved_down
                endx = end[0]*100+50-app.moved_right
                endy = end[1]*100+50-app.moved_down
                move_loop(id, x, y, endx, endy, start_sqr, end_sqr, path, acm)
            else: # CONTINUE LOOP
                root.after(33, lambda id = id, x = x, y = y, ex = endx, ey = endy, s = start_sqr, s2 = end_sqr, p = path, acm = acm : move_loop(id, x, y, ex, ey, s, s2, p, acm))
        move_loop(id, x, y, endx, endy, start_sqr, end_sqr, path, 0)
        
    def finish_charge(self, end_sqr, start_sqr, tar, ents_list):
        global selected
        sound_effects.stop()
        self.init_normal_anims()
        app.ent_dict[self.number+'top'].init_normal_anims()
        selected = []
        self.loc = end_sqr[:]
        app.grid[start_sqr[0]][start_sqr[1]] = ''
        app.grid[end_sqr[0]][end_sqr[1]] = self.number
        app.ent_dict[self.number+'top'].loc = [end_sqr[0],end_sqr[1]]
        root.after(666, lambda t = tar : app.get_focus(t))
        root.after(1333, lambda el = ents_list, t = tar : self.charge_hit(el, t)) # EXIT THROUGH ATTACK
        
    def charge_hit(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            effect1 = mixer.Sound('Sound_Effects/minotaur_attack.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            app.get_focus(id)
            app.ent_dict[self.number+'top'].init_attack_anims()
            my_agl = self.get_abl('agl')
            target_dodge = app.ent_dict[id].get_abl('dodge')
            if to_hit(my_agl, target_dodge) == True: # HIT
                my_str = self.get_abl('str')
                target_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, target_end)
                d += 2
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'crushing', 'Charge')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list, i = id : self.cleanup_charge(e, id)) # EXIT THROUGH CLEANUP_ATTACK()
            else: # MISS
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list, i = id : self.cleanup_charge(e, id))
            
    def cleanup_charge(self, ents_list, id):
        app.ent_dict[self.number+'top'].init_normal_anims()
        app.canvas.delete('text')
        if app.ent_dict[id].spirit <= 0:
            lock(app.kill, id)
            self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
        
    def pass_priority(self, ents_list):
        self.ai_end_turn(ents_list)
        
    #  Minotaur AI
    # if no other enemy is within atk range, will always attempt moving towards witch
    def do_ai(self, ents_list):
        if self.waiting == True:
            self.pass_priority(ents_list)
        else:
            # try charge witch, if do exit after
            w = app.p1_witch
            charge_ents = [k for k,v in app.action_target_ents().items() if 6 <= dist(v.loc, self.loc) <= 12 and (v.loc[0] == self.loc[0] or v.loc[1] == self.loc[1]) and self.clear_path(self.loc[:], v.loc[:]) == True and v.owner != self.owner]
            if 6 <= dist(app.ent_dict[w].loc, self.loc) <= 10 and (app.ent_dict[w].loc[0] == self.loc[0] or app.ent_dict[w].loc[1] == self.loc[1]) and self.clear_path(self.loc[:], app.ent_dict[w].loc[:]) == True:
                self.charge_attack(ents_list, w)
            # try charge others, if do exit after
            elif charge_ents != []:
                tar = choice(charge_ents)
                self.charge_attack(ents_list, tar)
            elif intersect(self.legal_moves(), [c for c in app.coords for k,v in app.ent_dict.items() if v.owner != self.owner and dist(c, v.loc) == 1 and app.grid[c[0]][c[1]] == '']) != []: # Can move to and atk an ent
                goals = [c for c in app.coords for k,v in app.ent_dict.items() if v.owner != self.owner and dist(c, v.loc) == 1 and app.grid[c[0]][c[1]] == '']
                path = bfs(self.loc[:], goals, app.grid)
                self.minotaur_move(ents_list, path[-1])
            else: # pursue witch and stomp
                # if no path on grid, use egrid, then stomp
                goals = [c for c in app.coords if dist(c, app.ent_dict[w].loc) == 1] # doesn't matter if they are occupied here
                path = bfs(self.loc[:], goals, app.grid)
                if path == None:
                    egrid = deepcopy(app.grid)
                    ent_locs = [v.loc for k,v in app.ent_dict.items() if v != self]
                    for eloc in ent_locs:
                        egrid[eloc[0]][eloc[1]] = '' # EGRID NOW EMPTIED OF ENTS
                    path = bfs(self.loc[:], goals, egrid)
                moves = intersect(self.legal_moves(), path)
                move = reduce(lambda a,b : a if dist(a, self.loc) > dist(b, self.loc) else b, moves)
                self.minotaur_move(ents_list, move, stomp = True)
            
    def minotaur_move(self, ents_list, endloc, stomp = False):
        global selected
        effect1 = mixer.Sound('Sound_Effects/minotaur_move.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, -1)
        self.init_move_anims()
        app.ent_dict[self.number+'top'].init_move_anims()
        selected = [self.number, self.number+'top']
        id = self.number
        end_sqr = endloc[:] # redundant naming of vars
        path = bfs(self.loc, [end_sqr], app.grid) # end_sqr must be put in list
        begin = path[0]
        end = path[1]
        x = begin[0]*100+50-app.moved_right
        y = begin[1]*100+50-app.moved_down
        endx = end[0]*100+50-app.moved_right
        endy = end[1]*100+50-app.moved_down
        def move_loop(id, x, y, endx, endy, start_sqr, end_sqr, path, acm):
            acm += 10
            if acm >= 40:
                app.ent_dict[id+'top'].rotate_image()
                self.rotate_image()
                acm = 0
            if x > endx:
                x -= 10
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.delete(id+'top')
                app.canvas.create_image(x, y, image = app.ent_dict[id+'top'].img, tags = (id+'top','large'))
            elif x < endx: 
                x += 10
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.delete(id+'top')
                app.canvas.create_image(x, y, image = app.ent_dict[id+'top'].img, tags = (id+'top','large'))
            if y > endy: 
                y -= 10
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.delete(id+'top')
                app.canvas.create_image(x, y, image = app.ent_dict[id+'top'].img, tags = (id+'top','large'))
            elif y < endy: 
                y += 10
                app.canvas.delete(id)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.delete(id+'top')
                app.canvas.create_image(x, y, image = app.ent_dict[id+'top'].img, tags = (id+'top','large'))
            try: app.canvas.tag_lower((self.tags), 'large')
            except: pass
            app.canvas.tag_lower((self.tags), 'maptop')
            app.canvas.tag_raise('cursor')
            if x == end_sqr[0]*100+50-app.moved_right and y == end_sqr[1]*100+50-app.moved_down: # END WHOLE MOVE
                self.finish_move(end_sqr, start_sqr, ents_list, stomp)
            elif x == endx and y == endy: # END PORTION OF PATH
                path = path[1:]
                begin = path[0]
                end = path[1]
                x = begin[0]*100+50-app.moved_right
                y = begin[1]*100+50-app.moved_down
                endx = end[0]*100+50-app.moved_right
                endy = end[1]*100+50-app.moved_down
                move_loop(id, x, y, endx, endy, start_sqr, end_sqr, path, acm)
            else: # CONTINUE LOOP
                root.after(66, lambda id = id, x = x, y = y, ex = endx, ey = endy, s = start_sqr, s2 = end_sqr, p = path, acm = acm : move_loop(id, x, y, ex, ey, s, s2, p, acm))
        move_loop(id, x, y, endx, endy, self.loc, end_sqr, path, 0)
        
    def finish_move(self, end_sqr, start_sqr, ents_list, stomp):
        global selected
        sound_effects.stop()
        self.init_normal_anims()
        app.ent_dict[self.number+'top'].init_normal_anims()
        selected = []
        self.loc = end_sqr[:]
        app.grid[start_sqr[0]][start_sqr[1]] = ''
        app.grid[end_sqr[0]][end_sqr[1]] = self.number
        app.ent_dict[self.number+'top'].loc = [end_sqr[0],end_sqr[1]]
        if stomp == True:
            self.stomp(ents_list)
        else:
            # MAKE ATTACK ON ANY ENEMY ENT WITHIN RANGE
            atk_sqrs = self.legal_attacks()
            if atk_sqrs != []:
                any = atk_sqrs[0]
                id = app.grid[any[0]][any[1]]
                root.after(666, lambda t = id : app.get_focus(t))
                root.after(1333, lambda el = ents_list, t = id : self.do_attack(el, t)) # EXIT THROUGH ATTACK
            else:
                self.ai_end_turn()
#     
    def do_attack(self, ents_list, id):
        if self.attack_used == True:
            self.cleanup_attack(ents_list, id)
        else:
            effect1 = mixer.Sound('Sound_Effects/minotaur_attack.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
            app.get_focus(id)
            app.ent_dict[self.number+'top'].init_attack_anims()
            my_agl = self.get_abl('agl')
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:
                my_str = self.get_abl('str')
                target_end = app.ent_dict[id].get_abl('end')
                d = damage(my_str, target_end)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'crushing', 'Crush')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list, i = id : self.cleanup_attack(e, id)) # EXIT THROUGH CLEANUP_ATTACK()
            else:
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(2666, lambda e = ents_list, i = id : self.cleanup_attack(e, id))
        
            
    def cleanup_attack(self, ents_list, id):
#         self.init_normal_anims()
        app.ent_dict[self.number+'top'].init_normal_anims()
        try: 
            app.canvas.delete('text')
        except: pass
        if app.ent_dict[id].spirit <= 0:
            lock(app.kill, id)
            self.ai_end_turn(ents_list)
        else:
            self.ai_end_turn(ents_list)
        
    def legal_attacks(self):
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                id = app.grid[c[0]][c[1]]
                if id != '' and id != 'block':
                    if app.ent_dict[id].owner != self.owner:
                        sqrs.append(c)
        return sqrs
        
    # all non-flying ents w/i range 8 take 8-dist(self.loc,id.loc) and are moved randomly (psi-push)
    # changing to 'pull' ents towards minotaur, move to sqr that minimizes dist between
    def stomp(self, ents_list):
        app.focus_square(self.loc)
        def stomp_sound():
            effect1 = mixer.Sound('Sound_Effects/minotaur_stomp.ogg')
            effect1.set_volume(1)
            sound_effects.play(effect1, 0)
        # insert start_stomp_anims() here
        self.init_stomp_anims()
        app.ent_dict[self.number+'top'].init_stomp_anims()
        # insert stomp vis
        def earthquake_loop(ents_list, ids):
            global selected
            if ids == []:
                self.cleanup_stomp(ents_list)
            else:
                id = ids[0]
                ids = ids[1:]
                app.get_focus(id)
                loc = app.ent_dict[id].loc[:]
                d = 6-dist(self.loc, loc)
                if d < 0:
                    d = 0
                pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'elec', 'Stomp')
                post = app.ent_dict[id].spirit
                d = pre - post
                if d > 0:
                    app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = str(d)+' spirit', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = str(d)+' spirit', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(loc[0]*100-app.moved_right+49, loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(loc[0]*100-app.moved_right+50, loc[1]*95-app.moved_down+100, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    name = 'dethlok'+str(app.death_count)
                    app.death_count += 1
                    app.dethloks[name] = tk.IntVar(0)
                    root.after(666, lambda id = id, name = name : app.kill(id, name))
                    root.wait_variable(app.dethloks[name])
                    earthquake_loop(ents_list, ids)
                else: # ENT NOT KILLED, INSERT PSI PUSH
                    start_loc = app.ent_dict[id].loc[:]
                    # recursively check adj sqr of ent that minimizes dist from minotaur
                    sqr = reduce(lambda a,b : a if dist(a, self.loc) < dist(b, self.loc) else b, [s for s in app.coords if dist(start_loc, s) == 1])
                    if app.grid[sqr[0]][sqr[1]] == '':
                        sqr2 = reduce(lambda a,b : a if dist(a, self.loc) < dist(b, self.loc) else b, [s for s in app.coords if dist(sqr, s) == 1])
                        if app.grid[sqr2[0]][sqr2[1]] == '':
                            dest = sqr2
                        else:
                            dest = sqr
                    else:
                        dest = start_loc[:]
                    # end destination logic
                    x = start_loc[0]*100+50-app.moved_right
                    y = start_loc[1]*100+50-app.moved_down
                    endx = dest[0]*100+50-app.moved_right
                    endy = dest[1]*100+50-app.moved_down
                    if start_loc != dest: # do move then go to next eq loop, else go to next eq loop
                        selected = [id]
                        def finish_psionic_push(tar, end_loc, start_loc):
                            global selected
                            selected = []
                            app.ent_dict[tar].loc = end_loc[:]
                            app.grid[start_loc[0]][start_loc[1]] = ''
                            app.grid[end_loc[0]][end_loc[1]] = tar
                            root.after(1888, lambda t = 'text' : app.canvas.delete(t))
                            root.after(1999, lambda el = ents_list, ids = ids : earthquake_loop(el, ids))
                        def psi_move_loop(ent, x, y, endx, endy, sqr, start_sqr):
                            if x % 25 == 0 and y % 25 == 0:
                                app.ent_dict[ent].rotate_image()
                                app.canvas.delete(ent)
                                app.canvas.create_image(x, y, image = app.ent_dict[ent].img, tags = app.ent_dict[ent].tags)
                            if x > endx:
                                x -= 10
                                app.canvas.move(ent, -10, 0)
                            elif x < endx: 
                                x += 10
                                app.canvas.move(ent, 10, 0)
                            if y > endy: 
                                y -= 10
                                app.canvas.move(ent, 0, -10)
                            elif y < endy: 
                                y += 10
                                app.canvas.move(ent, 0, 10)
                            try: app.canvas.tag_lower(app.ent_dict[ent].tags, 'large')
                            except: pass
                            app.canvas.tag_lower(app.ent_dict[ent].tags, 'maptop')
                            if x == endx and y == endy:
                                root.after(666, lambda e = ent, s = sqr, ss = start_sqr : finish_psionic_push(e, s, ss))
                            else:
                                root.after(50, lambda id = id, x = x, y = y, endx = endx, endy = endy, s = sqr, s2 = start_sqr : psi_move_loop(id, x, y, endx, endy, s, s2))
                        psi_move_loop(id, x, y, endx, endy, dest, start_loc)
                    else:
                        root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                        root.after(1666, lambda el = ents_list, ids = ids : earthquake_loop(el, ids))
            # first call of eq loop, called if affected ents exist
        ents = [k for k,v in app.ent_dict.items() if v.immovable != True and v.move_type != 'ethereal' and v.move_type != 'flying' and v.type != 'large']
        root.after(2333, self.init_normal_anims)
        root.after(2333, app.ent_dict[self.number+'top'].init_normal_anims)
        root.after(2333, stomp_sound)
        root.after(2555, lambda el = ents_list, ids = ents : earthquake_loop(el, ids))
        
    def cleanup_stomp(self, ents_list):
        app.canvas.delete('text')
        self.ai_end_turn(ents_list)
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
# lvl 2 some tank gains, becomes more agile/trick fighter than brute force 
# (throw, whirlwind, howl FB, rage)
class Warrior(Summon):
    def __init__(self, name, img, loc, owner, number, level):
        if level == 1:
            self.actions = {'Move':self.move, 'Slash':self.slash, 'Leap':self.leap}
            self.attack_used = False
            self.str = 6
            self.agl = 6
            self.end = 5
            self.dodge = 3
            self.psyche = 3
            self.spirit = 23
            self.move_range = 3
            self.level = level
        elif level == 2:
            self.actions = {'Move':self.move, 'Slash':self.slash, 'Leap':self.leap, 'Throw':self.throw, 'Rage':self.rage, 'Whirlwind':self.whirlwind}
            self.attack_used = False
            self.str = 7
            self.agl = 7
            self.end = 5
            self.dodge = 5
            self.psyche = 3
            self.spirit = 31
            self.move_range = 4
            self.level = level
        self.move_type = 'charge'
        self.weak = ['magick', 'fire', 'elec', 'cold']
        self.resist = ['slashing', 'crushing', 'poison']
        self.leap_used = False
        anims = [a for r,d,a in walk('./animations/Leap/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        self.leap_anims = []
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Leap/' + anim))
            self.leap_anims.append(a)
        super().__init__(name, img, loc, owner, number)
        
    def init_leap_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        for i, anim in enumerate(self.leap_anims):
            self.anim_dict[i] = anim
        self.img = self.anim_dict[0]
        
    # DEBUG, finish
    def whirlwind(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_whirlwind)
        sqrs = [c for c in app.coords if dist(self.loc, c) == 1]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = sqrs : self.do_whirlwind(event = e, sqrs = s)) 
        b = tk.Button(app.context_menu, text = 'Confirm Whirlwind', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = sqrs : self.do_whirlwind(event = e, sqrs = s))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_whirlwind(self, event = None, sqrs = None):
#         effect1 = mixer.Sound('Sound_Effects/whirlwind.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        self.attack_used = True
        self.init_attack_anims()
        app.cleanup_squares()
        app.depop_context(event = None)
        app.unbind_all()
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Whirlwind', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Whirlwind', justify = 'center', fill = 'indianred', font = ('Andale Mono', 16), tags = 'text')
        ents = [k for k,v in app.ent_dict.items() if dist(v.loc, self.loc) == 1 and v.owner != self.owner and v.type != 'large']
        if ents == []:
            root.after(1666, self.finish_whirlwind)
        else:
            root.after(1666, self.init_normal_anims)
            self.whirlwind_loop(ents)
    
    def whirlwind_loop(self, ents):
        if ents == []:
            self.finish_whirlwind()
        else:
            id = ents[0]
            ents = ents[1:]
            sqr = app.ent_dict[id].loc[:]
            un = 'Whirlwind'+str(app.effects_counter)
            app.effects_counter += 1
            app.vis_dict[un] = Vis(name = 'Warrior_Slash', loc = sqr[:])
            app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = un)
            def cleanup_whirlwind_vis(un):
                app.canvas.delete(un)
                del app.vis_dict[un]
                app.canvas.delete('text')
            my_agl = self.get_abl('agl')
            if my_agl < 3:
                my_agl = 1
            else:
                my_agl -= 2
            target_agl = app.ent_dict[id].get_abl('agl')
            if to_hit(my_agl, target_agl) == True:
                my_str = self.get_abl('str')
                target_end = app.ent_dict[id].get_abl('end')
                pre = app.ent_dict[id].spirit
                d = damage(my_str, target_end)
                lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Whirlwind')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_', ' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_', ' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    cleanup_whirlwind_vis(un)
                    name = 'dethlok'+str(app.death_count)
                    app.death_count += 1
                    app.dethloks[name] = tk.IntVar(0)
                    root.after(666, lambda id = id, name = name : app.kill(id, name))
                    app.wait_variable(app.dethloks[name])
                    self.whirlwind_loop(ents)
                else:
                    root.after(1555, lambda un = un : cleanup_whirlwind_vis(un))
                    root.after(1666, lambda ents = ents : self.whirlwind_loop(ents))
            else:
                app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                root.after(1555, lambda un = un : cleanup_whirlwind_vis(un))
                root.after(1666, lambda ents = ents : self.whirlwind_loop(ents))
        
        
    def finish_whirlwind(self, event = None):
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)
        app.cleanup_squares()
        
    def rage(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_rage)
        sqrs = [self.loc[:]]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_rage(event = e, sqr = sqr, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Confirm Rage', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.do_rage(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_rage(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        if 'Rage' in [v.name for k,v in self.effects_dict.items()]:
            return
#         effect1 = mixer.Sound('Sound_Effects/rage.ogg')
#         effect1.set_volume(.5)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+94, text = 'Rage', justify = 'center', fill = 'black', font = ('Andale Mono', 16), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+95, text = 'Rage', justify = 'center', fill = 'indianred', font = ('Andale Mono', 16), tags = 'text')
#         app.vis_dict['Rage'] = Vis(name = 'Rage', loc = sqr[:])
#         vis = app.vis_dict['Rage']
#         app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = vis.img, tags = 'Rage')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+49, self.loc[1]*100-app.moved_down+74, text = 'Attempt Dispel Effects\n +1 str, +1 end, +4 psy', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
        app.canvas.create_text(self.loc[0]*100-app.moved_right+50, self.loc[1]*100-app.moved_down+75, text = 'Attempt Dispel Effects\n +1 str, +1 end, +4 psy', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
        to_remove = []
        for k,v in self.effects_dict.items():
            if v.dispel(+6) == True:
                to_remove.append(k)
        for k in to_remove:
            del self.effects_dict[k]
        # add effects
        def rage_effect(stat):
            return stat+1
        self.str_effects.append(rage_effect)
        self.end_effects.append(rage_effect)
        def rage_effect2(stat):
            return stat+4
        self.psyche_effects.append(rage_effect2)
        def undo(id):
            self.str_effects.remove(rage_effect)
            self.end_effects.remove(rage_effect)
            self.psyche_effects.remove(rage_effect2)
            pre = self.spirit
            d = 3
            lock(apply_damage, self, self, -d, 'magick', 'Rage')
            post = self.spirit
            d = pre - post
            sqr = self.loc[:]
            app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+74, text = '3 spirit rage', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+75, text = '3 spirit rage', justify = 'center', fill = 'indianred', font = ('Andale Mono', 13), tags = 'text')
            if self.spirit <= 0:
                app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+94, text = self.name.replace('_', ' ') + ' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+95, text = self.name.replace('_', ' ') + ' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                name = 'Dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(666, lambda id = self.number, name = name : app.kill(id, name))
                app.wait_variable(app.dethloks[name])
            return 'Not None'
        u = partial(undo, id)
        self.effects_dict['Rage'] = Effect(name = 'Rage', undo_func = u, duration = 4, level = 8)
        root.after(2666, self.finish_rage)
        
    def finish_rage(self, event = None):
        try: 
            del app.vis_dict['Rage']
            app.canvas.delete('Rage')
        except: pass
        app.depop_context(event = None)
        app.canvas.delete('text')
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        
        
    def throw(self, event = None):
        if self.attack_used == True:
            return
#         root.unbind('<q>')
#         root.unbind('<a>')
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_throw)
        sqrs = []
        for c in app.coords:
            if dist(c, self.loc) == 1:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.choose_target(e, sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqr = grid_pos, sqrs = sqrs : self.choose_target(event = e, sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def choose_target(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if app.ent_dict[id].type == 'large':
            return
        if app.ent_dict[id].immovable == True:
            return
        app.depop_context(event = None)
        app.unbind_all()
        app.rebind_arrows()
        root.bind('<q>', self.cleanup_throw)
        distance = 3
        app.cleanup_squares()
        sqrs = self.doorway_squares(distance)
        if sqrs == []:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+59-app.moved_down, text = 'No Available Area', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+60-app.moved_down, text = 'No Available Area', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
            root.after(999, self.cleanup_throw)
        else:
            app.animate_squares(sqrs)
            root.bind('<a>', lambda e, id = id, sqr = grid_pos, sqrs = sqrs : self.do_throw(e, id = id, sqr = sqr, sqrs = sqrs))
            b = tk.Button(app.context_menu, text = 'Choose Location', font = ('chalkduster', 24), fg = 'tan3', wraplength = 190, highlightbackground = 'tan3', command = lambda e = None, id = id, sqr = grid_pos, sqrs = sqrs : self.do_throw(e, id, sqr, sqrs))
            b.pack(side = 'top')
            app.context_buttons.append(b)
    
    def do_throw(self, event = None, id = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        self.attack_used = True
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
#         effect1 = mixer.Sound('Sound_Effects/throw.ogg')
#         effect1.set_volume(.4)
#         sound_effects.play(effect1, 0)
        oldloc = app.ent_dict[id].loc[:]
        newloc = sqr[:]
#         app.vis_dict['Gate'] = Vis(name = 'Gate', loc = oldloc[:])
#         vis = app.vis_dict['Gate']
#         app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = vis.img, tags = 'Gateway')
        root.after(1666, lambda newloc = newloc, id = id : self.finish_throw(newloc, id))
        
    def finish_throw(self, newloc, id):
        app.grid[app.ent_dict[id].loc[0]][app.ent_dict[id].loc[1]] = ''
        app.canvas.delete(id)
        app.ent_dict[id].loc = newloc[:]
        app.grid[newloc[0]][newloc[1]] = id
#         try: 
#             del app.vis_dict['Gate']
#             app.canvas.delete('Gate')
#         except: pass
#         app.vis_dict['Gate'] = Vis(name = 'Gate', loc = newloc[:])
#         vis = app.vis_dict['Gate']
        root.after(1666, lambda id = id, newloc = newloc : self.place_entity(id, newloc))
        
    def place_entity(self, id, newloc):
#         del app.vis_dict['Gate']
#         app.canvas.delete('Gate')
        app.canvas.create_image(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = app.ent_dict[id].tags)
        try: app.canvas.tag_lower((app.ent_dict[id].tags), 'large')
        except: pass
        app.canvas.tag_lower((app.ent_dict[id].tags), 'maptop')
        root.after(666, self.cleanup_throw)
    
    def doorway_squares(self, distance):
        sqr_list = []
        for c in app.coords:
            if dist(c, self.loc) <= distance: 
                if app.grid[c[0]][c[1]] == '':
                    sqr_list.append(c)
        return sqr_list
    
    def cleanup_throw(self, event = None):
#         try:
#             del app.vis_dict['Gate']
#             app.canvas.delete('Gate')
#         except: pass
        app.canvas.delete('text')
        app.depop_context(event = None)
        app.cleanup_squares()
        app.rebind_all()
        
#     def guard(self, event = None):
#         if self.attack_used == True:
#             return
#         app.unbind_nonarrows()
#         root.bind('<q>', self.cancel_attack)
#         sqrs = [c for c in app.coords if 1 <= dist(self.loc, c) <= 3]
#         app.animate_squares(sqrs)
#         app.depop_context(event = None)
#         root.bind('<a>', lambda e, sqrs = sqrs, sqr = grid_pos : self.do_guard(event = e, sqrs = sqrs, sqr = sqr)) 
#         b = tk.Button(app.context_menu, text = 'Confirm Guard', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs, sqr = grid_pos : self.do_guard(event = e, sqrs = sqrs, sqr = sqr))
#         b.pack(side = 'top')
#         app.context_buttons.append(b)
#         
#     def do_guard(self, event = None, sqrs = None, sqr = None):
#         if sqr not in sqrs:
#             return
#         id = app.grid[sqr[0]][sqr[1]]
#         if id == '' or id == 'block':
#             return
#         if app.ent_dict[id].owner != self.owner:
#             return
#         self.attack_used = True
#         effect1 = mixer.Sound('Sound_Effects/guard.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
#         app.depop_context(event = None)
#         app.unbind_all()
#         app.cleanup_squares()
#         app.vis_dict['Guard'] = Vis(name = 'Guard', loc = sqr[:])
#         app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Guard'].img, tags = 'Guard')
#         app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+84, text = 'Guard', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
# 
#         app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+85, text = 'Guard', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
#         # EFFECT
#         def guard_effect(attacker, defender, amount, type, redir_obj = None):
#             if amount < 0:
#                 app.canvas.create_text(defender.loc[0]*100-app.moved_right+49, defender.loc[1]*100-app.moved_down+94, text = 'Guard Redirect', justify = 'center', fill = 'black', font = ('Andale Mono', 12), tags = 'guard_text')
#                 app.canvas.create_text(defender.loc[0]*100-app.moved_right+50, defender.loc[1]*100-app.moved_down+95, text = 'Guard Redirect', justify = 'center', fill = 'white', font = ('Andale Mono', 12), tags = 'guard_text')
#                 app.get_focus(redir_obj.number)
#                 pre = redir_obj.spirit
#                 lock(apply_damage, attacker, redir_obj, amount, type)
#                 post = redir_obj.spirit
#                 d = pre - post
#                 app.canvas.create_text(redir_obj.loc[0]*100-app.moved_right+49, redir_obj.loc[1]*100-app.moved_down+74, text = str(d)+' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 12), tags = 'guard_text')
#                 app.canvas.create_text(redir_obj.loc[0]*100-app.moved_right+50, redir_obj.loc[1]*100-app.moved_down+75, text = str(d)+' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 12), tags = 'guard_text')
#                 root.after(1888, lambda t = 'guard_text' : app.canvas.delete(t))
#                 # check for guard death...
#                 if redir_obj.spirit <= 0:
#                     app.canvas.create_text(defender.loc[0]*100-app.moved_right+49, defender.loc[1]*100-app.moved_down+14, text = 'Guard Death', justify = 'center', fill = 'black', font = ('Andale Mono', 12), tags = 'guard_text')
#                     app.canvas.create_text(defender.loc[0]*100-app.moved_right+50, defender.loc[1]*100-app.moved_down+15, text = 'Guard Death', justify = 'center', fill = 'white', font = ('Andale Mono', 12), tags = 'guard_text')
#                     name = 'dethlok'+str(app.death_count)
#                     app.death_count += 1
#                     app.dethloks[name] = tk.IntVar(0)
#                     root.after(999, lambda id = redir_obj.number, name = name : app.kill(id, name))
#                     root.wait_variable(app.dethloks[name])
#                     defender.defense_effects.remove(guard_effect)
#                     defender.effects_dict.remove(guard_effect)
#                 return 0
#             else:
#                 return amount
#         f = partial(guard_effect, redir_obj = self)
#         app.ent_dict[id].defense_effects.append(f)
#         # give self a death trigger to remove guard from obj
#         def death_trigger(obj, f):
#             app.canvas.create_text(obj.loc[0]*100-app.moved_right+49, obj.loc[1]*100-app.moved_down+34, text = 'Guard Removed', justify = 'center', fill = 'black', font = ('Andale Mono', 12), tags = 'guard_text')
#             app.canvas.create_text(obj.loc[0]*100-app.moved_right+50, obj.loc[1]*100-app.moved_down+35, text = 'Guard Removed', justify = 'center', fill = 'white', font = ('Andale Mono', 12), tags = 'guard_text')
#             root.after(2222, lambda t = 'guard_text' : app.canvas.delete(t))
#             obj.defense_effects.remove(f)
#         dt = partial(death_trigger, app.ent_dict[id], f)
#         self.death_triggers.append(dt)
#         def un(i, f, dt):
#             self.death_triggers.remove(dt)
#             app.ent_dict[id].defense_effects.remove(f)
#             return None
#         u = partial(un, id, f, dt)
#         # EOT FUNC
#         def nothing():
#             return None
#         eot = nothing
#         n = 'Guard' + str(app.effects_counter)
#         app.ent_dict[id].effects_dict[n] = Effect(name = 'Guard', info = 'Guard, redir dmg', eot_func = eot, undo = u, duration = 3, level = 8)
#         root.after(2666, lambda e = None: self.cancel_attack(e))
        
    def leap(self, event = None):
        if self.leap_used == True:
            return
#         root.unbind('<a>')
#         root.unbind('<q>')
        app.unbind_nonarrows()
        root.bind('<q>', self.cancel_attack)
        sqrs = []
        for c in app.coords:
            if dist(self.loc, c) <= 3 and app.grid[c[0]][c[1]] == '':
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqrs = sqrs, sqr = grid_pos : self.do_leap(event = e, sqrs = sqrs, sqr = sqr)) 
        b = tk.Button(app.context_menu, text = 'Confirm Leap', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs, sqr = grid_pos : self.do_leap(event = e, sqrs = sqrs, sqr = sqr))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_leap(self, event = None, sqrs = None, sqr = None):
        global selected
        if sqr not in sqrs:
            return
        self.leap_used = True
        self.init_leap_anims()
#         effect1 = mixer.Sound('Sound_Effects/leap.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        endx = sqr[0]*100+50-app.moved_right
        endy = sqr[1]*100+50-app.moved_down
        start_sqr = self.loc[:]
        end_sqr = sqr[:]
        selected = [self.number]
        total_distance = abs(x - endx) + abs(y - endy)
        tic = total_distance/7
        if x == endx:
            xstep = 0
            ystep = 10
        elif y == endy:
            xstep = 10
            ystep = 0
        else:
            slope = Fraction(abs(x - endx), abs(y - endy))
            # needs to be moving at least 10 pixels, xstep + ystep >= 10
            xstep = slope.numerator
            ystep = slope.denominator
            while xstep + ystep < 10:
                xstep *= 2
                ystep *= 2
        # need to call rotate_image every tic
        def leap_loop(x, y, endx, endy, start_sqr, end_sqr, acm, tic, xstep, ystep):
            if acm >= tic:
                acm = 0
                self.rotate_image()
                app.canvas.delete(self.number)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if x > endx:
                acm += xstep
                x -= xstep
                app.canvas.delete(self.number)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.tag_raise(self.number)
            elif x < endx:
                acm += xstep
                x += xstep
                app.canvas.delete(self.number)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.tag_raise(self.number)
            if y > endy:
                acm += ystep
                y -= ystep
                app.canvas.delete(self.number)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.tag_raise(self.number)
            elif y < endy:
                acm += ystep
                y += ystep
                app.canvas.delete(self.number)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
                app.canvas.tag_raise(self.number)
            if abs(x - endx) < 13 and abs(y - endy) < 13:
                self.finish_leap(end_sqr, start_sqr) # EXIT
            else: # CONTINUE LOOP
                root.after(43, lambda x = x, y = y, e = endx, e2 = endy, s = start_sqr, s2 = end_sqr, acm = acm, tic = tic, xs = xstep, ys = ystep : leap_loop(x, y, e, e2, s, s2, acm, tic, xs, ys))
        leap_loop(x, y, endx, endy, start_sqr, end_sqr, tic+1, tic, xstep, ystep)
            
            
    def finish_leap(self, end_sqr, start_sqr):
        global selected
        selected = []
        self.loc = end_sqr[:]
        app.grid[start_sqr[0]][start_sqr[1]] = ''
        app.grid[end_sqr[0]][end_sqr[1]] = self.number
        self.init_normal_anims()
        app.rebind_all()
#         app.canvas.delete('text')
#         try: 
#             del app.vis_dict['Warrior_Slash']
#             app.canvas.delete('Warrior_Slash')
#         except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        
        
    def slash(self, event = None):
        if self.attack_used == True:
            return
#         root.unbind('<a>')
#         root.unbind('<q>')
        app.unbind_nonarrows()
        root.bind('<q>', self.cancel_attack)
        sqrs = []
        for c in app.coords:
            if dist(self.loc, c) == 1:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, sqrs = sqrs, sqr = grid_pos : self.check_hit(event = e, sqrs = sqrs, sqr = sqr)) 
        b = tk.Button(app.context_menu, text = 'Confirm Attack', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs, sqr = grid_pos : self.check_hit(event = e, sqrs = sqrs, sqr = sqr))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def check_hit(self, event = None, sqrs = None, sqr = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        self.attack_used = True
        self.init_attack_anims()
        effect1 = mixer.Sound('Sound_Effects/warrior_attack.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        app.vis_dict['Warrior_Slash'] = Vis(name = 'Warrior_Slash', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Warrior_Slash'].img, tags = 'Warrior_Slash')
        my_agl = self.get_abl('agl')
        target_agl = app.ent_dict[id].get_abl('agl')
        if to_hit(my_agl, target_agl) == True:
            root.after(1999, lambda id = id : self.do_attack(id))
        else:
            app.canvas.create_text(sqr[0]*100-app.moved_right+49, sqr[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            root.after(1999, self.cancel_attack)
        
    def do_attack(self, id):
        my_str = self.get_abl('str')
        target_end = app.ent_dict[id].get_abl('end')
        d = damage(my_str, target_end)
        def cleanup_slash():
            del app.vis_dict['Warrior_Slash']
            app.canvas.delete('Warrior_Slash')
            app.cleanup_squares()
            self.init_normal_anims()
        root.after(666, cleanup_slash)
        lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Slash')
        root.after(666, self.cancel_attack)
    
    def cancel_attack(self, event = None):
        self.init_normal_anims()
        app.canvas.delete('text')
        try: 
            del app.vis_dict['Warrior_Slash']
            app.canvas.delete('Warrior_Slash')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
    
    def legal_moves(self):
        loc = self.loc
        mvlist = []
        coords = app.coords[:]
        # need to stop movement when obstructed, DEBUG make more concise/clear
        for c in app.coords:
            if loc[0]-1 == c[0] and c[1] == loc[1] and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
                n = [c[0]-1, c[1]]
                if n in coords:
                    if  app.grid[n[0]][n[1]] == '':
                        mvlist.append(n)
                        n = [n[0]-1, n[1]]
                        if n in coords:
                            if  app.grid[n[0]][n[1]] == '':
                                mvlist.append(n)
            elif loc[0]+1 == c[0] and c[1] == loc[1] and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
                n = [c[0]+1, c[1]]
                if n in coords:
                    if  app.grid[n[0]][n[1]] == '':
                        mvlist.append(n)
                        n = [n[0]+1, n[1]]
                        if n in coords:
                            if  app.grid[n[0]][n[1]] == '':
                                mvlist.append(n)
            elif c[0] == loc[0] and loc[1]-1 == c[1] and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
                n = [c[0], c[1]-1]
                if n in coords:
                    if  app.grid[n[0]][n[1]] == '':
                        mvlist.append(n)
                        n = [n[0], n[1]-1]
                        if n in coords:
                            if  app.grid[n[0]][n[1]] == '':
                                mvlist.append(n)
            elif c[0] == loc[0] and loc[1]+1 == c[1] and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
                n = [c[0], c[1]+1]
                if n in coords:
                    if  app.grid[n[0]][n[1]] == '':
                        mvlist.append(n)
                        n = [n[0], n[1]+1]
                        if n in coords:
                            if  app.grid[n[0]][n[1]] == '':
                                mvlist.append(n)
        mvlist = list(filter(lambda x : dist(x, self.loc) <= self.get_abl('move_range'), mvlist))
        return mvlist
                    
                    
    # confuse, target must make psyche check before attack
    # fuse trap, set global effect on sqr, when effect ends all ents within range 2 take 5 dmg 
class Familiar_Homonculus(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'Mesmerize':self.mesmerize, 'Fuse Trap':self.fuse_trap, 'move':self.move}
        self.attack_used = False
        self.str = 2
        self.agl = 5
        self.end = 5
        self.dodge = 6
        self.psyche = 5
        self.spirit = 11
        self.move_range = 5
        self.move_type = 'normal'
        self.resist = ['magick', 'fire']
        self.weak = ['crushing', 'acid']
        super().__init__(name, img, loc, owner, number)
        def familiar_trigger():
            if self.owner == 'p1':
                witch = app.p1_witch
            else:
                witch = app.p2_witch
            loc = app.ent_dict[witch].loc[:]
            app.focus_square(loc)
#             app.ent_dict[witch].set_attr('spirit', -3)
            lock(apply_damage, app.ent_dict[witch], app.ent_dict[witch], -3, 'magick', 'Familiar Death')
            app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = '3 spirit, Familiar Death', font = ('Andale Mono', 13), fill = 'white', tags = 'familiar_death')
            root.after(2333, lambda t = 'familiar_death' : app.canvas.delete(t))
            if app.ent_dict[witch].spirit <= 0:
                app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+95-app.moved_down, text = app.ent_dict[witch].name.replace('_', ' ')+' Killed...', font = ('Andale Mono', 13), fill = 'white', tags = 'self_death')
                name = 'dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(2333, lambda id = app.ent_dict[witch].name, n = name : app.kill(id, n))
                root.wait_variable(app.dethloks[name])
        self.death_triggers.append(familiar_trigger)
                    
                    
    def fuse_trap(self, event = None):
        if self.attack_used == True:
            return
        app.depop_context(event = None)
        root.unbind('<q>')
        root.unbind('<a>')
        root.bind('<q>', self.cleanup_fuse_trap)
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 5]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_fuse_trap(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Square For Fuse Trap', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_fuse_trap(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    # place in unoccupied sqr?
    def do_fuse_trap(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        if app.grid[sqr[0]][sqr[1]] != '':
            return
        visuals = [v.name for k,v in app.vis_dict.items() if v.loc == sqr]
        if 'Fuse_Trap' in visuals:
            return
        effect1 = mixer.Sound('Sound_Effects/fuse_trap.ogg')
        effect1.set_volume(.07)
        sound_effects.play(effect1, 0)
        self.attack_used = True
        app.unbind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        uniq_name = 'Fuse_Trap' + str(app.effects_counter)
        app.effects_counter += 1
        app.vis_dict[uniq_name] = Vis(name = 'Fuse_Trap', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[uniq_name].img, tags = uniq_name)
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = 'Fuse Trap', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        
        # change to Local_Effect on sqr
        if 'Fuse_Trap' not in [v.name for k,v in app.loc_effects_dict[tuple(sqr)].effects_dict.items()]:
            un = 'Fuse_Trap' + str(app.effects_counter)
            app.effects_counter += 1
            app.vis_dict[un] = Vis(name = 'Fuse_Trap', loc = sqr[:])
            app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = un)
            
            # on undo dmg each ent within range 3 of self.loc
            def undo(s, un):
                del app.vis_dict[un]
                app.canvas.delete(un)
                app.focus_square(s)
                effect1 = mixer.Sound('Sound_Effects/fuse_explosion.ogg')
                effect1.set_volume(1)
                sound_effects.play(effect1, 0)
                ents = [k for k,v in app.ent_dict.items() if dist(v.loc, s) <= 3 and v.type != 'large']
                def clean_explosion(n):
                    del app.vis_dict[n]
                    app.canvas.delete(n)
                    app.canvas.delete('text')
                def fuse_loop(ents):
                    if ents == []:
                        return 'Not None'
                    else:
                        id = ents[0]
                        ents = ents[1:]
                        loc = app.ent_dict[id].loc[:]
                        n = 'Fuse_Explosion'+str(app.effects_counter)
                        app.effects_counter += 1
                        app.vis_dict[n] = Vis(name = 'Fuse_Explosion', loc = loc[:])
                        app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = n)
                        app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = 'Fuse Trap 5 spirit', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = 'Fuse Trap 5 spirit', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                        lock(apply_damage, self, app.ent_dict[id], -5, 'explosive', 'Fuse Trap')
                        if app.ent_dict[id].spirit <= 0:
                            app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+94-app.moved_down, text = app.ent_dict[id].name.replace('_', ' ') + ' Killed...', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                            app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+95-app.moved_down, text = app.ent_dict[id].name.replace('_', ' ') + ' Killed...', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                            name = 'Dethlok'+str(app.death_count)
                            app.death_count += 1
                            app.dethloks[name] = tk.IntVar(0)
                            root.after(2333, lambda n = n : clean_explosion(n))
                            root.after(2666, lambda id = id, name = name : app.kill(id, name))
                            app.wait_variable(app.dethloks[name])
                            fuse_loop(ents)
                        else:
                            root.after(2333, lambda n = n : clean_explosion(n))
                            root.after(2666, lambda ents = ents : fuse_loop(ents))
                fuse_loop(ents)
            u = partial(undo, sqr[:], un)
            app.loc_effects_dict[tuple(sqr)].effects_dict[un] = Local_Effect(name = 'Fuse_Trap', undo = u, duration = 3, level = 4, loc = sqr[:], avoid = 4)
        self.cleanup_fuse_trap()
                    
    def cleanup_fuse_trap(self, event = None):
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        app.canvas.delete('text')
                    
    def mesmerize(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.cancel_mesmerize)
        sqrs = []
        for c in app.coords:
            if dist(self.loc, c) <= 3:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_mesmerize(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Confirm Mesmerize', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_mesmerize(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    # add mesmerize fail text
    def do_mesmerize(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        effs = [k for k in app.ent_dict[id].effects_dict.keys()]
        if 'Mesmerize' in effs:
            return
        effect1 = mixer.Sound('Sound_Effects/mesmerize.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.attack_used = True
        # add confuse effect, at start of turn unit makes psyche check, on fail unit gets attack_used set to True and takes 5 dmg
#         def mesmerize_effect():
#             pass
        def un():
            return None
        # SOT FUNC
        def mesmerized(tar):
            app.get_focus(tar)
            # make psyche check
            if app.ent_dict[tar].save_check('psyche', mod = 2) == False:
                app.ent_dict[tar].attack_used = True
#                 app.ent_dict[tar].set_attr('spirit', -5)
                pre = app.ent_dict[id].spirit
                lock(apply_damage, app.ent_dict[id], app.ent_dict[id], -5, 'crushing', 'Mesmerized')
                post = app.ent_dict[id].spirit
                d = pre - post
                app.canvas.create_text(app.ent_dict[tar].loc[0]*100+50-app.moved_right, app.ent_dict[tar].loc[1]*100+70-app.moved_down, text = d+' Spirit, mesmerized', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                if app.ent_dict[tar].spirit <= 0:
                    app.canvas.create_text(app.ent_dict[tar].loc[0]*100+50-app.moved_right, app.ent_dict[tar].loc[1]*100+90-app.moved_down, text = app.ent_dict[tar].name.replace('_',' ') + '\nKilled...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            else:
                app.canvas.create_text(app.ent_dict[tar].loc[0]*100+50-app.moved_right, app.ent_dict[tar].loc[1]*100+70-app.moved_down, text = 'Mesmerize Save', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            return 'Not None'
            
        sot = partial(mesmerized, id)
        app.ent_dict[id].effects_dict['Mesmerize'] = Effect(sot_func = sot, name = 'Mesmerize', undo_func = un, duration = 4, level = 5)
        
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = 'Mesmerize', fill = 'white', font = ('Andale Mono', 14), tags = 'text')
        app.vis_dict['Mesmerize'] = Vis(name = 'Mesmerize', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Mesmerize'].img, tags = 'Mesmerize')
        root.after(2999, self.cancel_mesmerize)
        
        
    def cancel_mesmerize(self, event = None):
        app.unbind_all()
        app.rebind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        app.canvas.delete('text')
        try: 
            del app.vis_dict['Mesmerize']
            app.canvas.delete('Mesmerize')
        except: pass
                    
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist

class Lesser_Demon(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'Dire Charm':self.dire_charm, 'Baleful Stare':self.baleful_stare, 'Brambles':self.brambles, 'Move': self.move}
        self.attack_used = False
        self.str = 3
        self.agl = 4
        self.end = 4
        self.dodge = 5
        self.psyche = 6
        self.spirit = 16
        self.move_range = 4
        self.move_type = 'normal'
        super().__init__(name, img, loc, owner, number)
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
        
    def brambles(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_brambles)
        sqrs = []
        for c in app.coords:
            if 1 <= dist(self.loc, c) <= 5:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_brambles(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Choose Target Brambles', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_brambles(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_brambles(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        if app.grid[sqr[0]][sqr[1]] == '' or app.grid[sqr[0]][sqr[1]] == 'block':
            return
#         self.init_attack_anims()
#         effect1 = mixer.Sound('Sound_Effects/brambles.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+9-app.moved_down, text = 'Brambles', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+10-app.moved_down, text = 'Brambles', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        ss = [c for c in app.coords if dist(sqr, c) <= 2]
        ents = [app.grid[s[0]][s[1]] for s in ss if app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
        ents = [e for e in ents if app.ent_dict[e].owner != self.owner]
        if ents == []:
            root.after(1666, self.finish_brambles)
        else:
            def brambles_loop(ents):
                if ents == []:
                    self.finish_brambles()
                else:
                    id = ents[0]
                    ents = ents[1:]
                    app.get_focus(id)
                    s = app.ent_dict[id].loc[:]
                    u = 'Brambles' + str(app.effects_counter)
                    app.effects_counter += 1
                    app.vis_dict[u] = Vis(name = 'Brambles', loc = s)
                    app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[u].img, tags = 'Brambles')
                    # ADD brambles effects, fail dodge save take damage, fail str save have normal movement inhibited
                    if app.ent_dict[id].save_check('dodge', mod = -1) == False:
                        my_psyche = self.get_abl('psyche')
                        tar_end = app.ent_dict[id].get_abl('end')
                        d = damage(my_psyche, tar_end)
                        app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+74-app.moved_down, text = str(d)+' spirit', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+75-app.moved_down, text = str(d)+' spirit', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                        lock(apply_damage, self, app.ent_dict[id], -d, 'slashing', 'Brambles')
                        if app.ent_dict[id].spirit <= 0:
                            app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+90-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                            name = 'Dethlok'+str(app.death_count)
                            app.death_count += 1
                            app.dethloks[name] = tk.IntVar(0)
                            root.after(2222, lambda u = u : self.cleanup_brambles(u))
                            root.after(2333, lambda id = id, name = name : app.kill(id, name))
                            app.wait_variable(app.dethloks[name])
                            brambles_loop(ents)
                        elif app.ent_dict[id].move_type == 'normal':
                            if app.ent_dict[id].save_check('str', mod = -1) == False:
                                app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+95-app.moved_down, text = 'Movement Reduced', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                                def brambles_move(move_range):
                                    move_range -= 1
                                    if move_range <= 1:
                                        return 1
                                    else:
                                        return move_range
                                app.ent_dict[id].move_effects.append(brambles_move)
                                def un(i):
                                    app.ent_dict[i].move_effects.remove(brambles_move)
                                    return None
                                uf = partial(un, id)
                                n = 'Brambles' + str(app.effects_counter)
                                app.ent_dict[id].effects_dict[n] = Effect(name = 'Brambles', undo_func = uf, duration = 1, level = 5)
                                root.after(2666, lambda name = u : self.cleanup_brambles(name))
                                root.after(2999, lambda ents = ents : brambles_loop(ents))
                            else:
                                root.after(2666, lambda name = u : self.cleanup_brambles(name))
                                root.after(2999, lambda ents = ents : brambles_loop(ents))
                        else:# MOVE TYPE NOT NORMAL
                            root.after(2666, lambda name = u : self.cleanup_brambles(name))
                            root.after(2999, lambda ents = ents : brambles_loop(ents))
                    else:
                        root.after(2666, lambda name = u : self.cleanup_brambles(name))
                        root.after(2999, lambda ents = ents : brambles_loop(ents))
            brambles_loop(ents)
            
    def cleanup_brambles(self, name):
         app.canvas.delete('Brambles')
         del app.vis_dict[name]
         app.canvas.delete('text')
            
    def finish_brambles(self, event = None):
        try:
            ks = list(app.vis_dict.keys())
            for k in ks:
                if k.startswith('Brambles') == True:
                    del app.vis_dict[k]
            app.canvas.delete('Brambles')
        except: pass
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)
    
        
    def baleful_stare(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_baleful_stare)
        sqrs = []
        for c in app.coords:
            if 1 <= dist(self.loc, c) <= 3:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_baleful_stare(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Choose Target Baleful Stare', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos[:], sqrs = sqrs : self.do_baleful_stare(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_baleful_stare(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        if app.grid[sqr[0]][sqr[1]] == '' or app.grid[sqr[0]][sqr[1]] == 'block':
            return
        id = app.grid[sqr[0]][sqr[1]]
        efs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Baleful_Stare' in efs:
            return
#         self.init_attack_anims()
#         effect1 = mixer.Sound('Sound_Effects/baleful_stare.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        self.attack_used = True
        visloc = app.ent_dict[id].loc[:]
        app.vis_dict['Baleful_Stare'] = Vis(name = 'Baleful_Stare', loc = visloc)
        app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Baleful_Stare'].img, tags = 'Baleful_Stare')
        my_psyche = self.get_abl('psyche')
        target_end = app.ent_dict[id].get_abl('end')
        if to_hit(my_psyche, target_end) == True:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Baleful Stare Hit', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            # baleful effect
            def baleful_stare_effect(stat):
                stat -= 1
                if stat < 1:
                    return 1
                else:
                    return stat
            f = baleful_stare_effect
            app.ent_dict[id].psyche_effects.append(f)
            def un(i):
                app.ent_dict[i].psyche_effects.remove(baleful_stare_effect)
                return None
            p = partial(un, id)
            # EOT FUNC
            def take_1(tar, lockname = None):
                app.get_focus(tar)
                lock(apply_damage, self, app.ent_dict[tar], -1, 'acid', 'Baleful Stare')
                root.after(1333, lambda ln = lockname : app.dethloks[ln].set(1))
            n = 'Baleful_Stare' + str(app.effects_counter)
            eot = partial(take_1, id)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Baleful_Stare', eot_func = eot, undo_func = p, duration = 9, level = 5)
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Baleful Stare Missed', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        root.after(3333, lambda e = None : self.finish_baleful_stare(event = e))
        
    def finish_baleful_stare(self, event = None):
#         self.init_normal_anims()
        app.rebind_all()
        app.canvas.delete('text')
        try: 
            del app.vis_dict['Baleful_Stare']
            app.canvas.delete('Baleful_Stare')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        
    # enem ents w/i rang3 make psy check or autohit self dmg str v end
    def dire_charm(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_dire_charm)
        sqrs = [c for c in app.coords if 1 <= dist(self.loc, c) <= 3]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = sqrs : self.do_dire_charm(event = e, sqrs = s)) 
        b = tk.Button(app.context_menu, text = 'Confirm Dire Charm', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs : self.do_dire_charm(event = e, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_dire_charm(self, event = None, sqrs = None):
        self.attack_used = True
#         effect1 = mixer.Sound('Sound_Effects/dire_charm.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        ents = [k for k,v in app.ent_dict.items() if v.loc in sqrs and v.owner != self.owner and v.type != 'large']
        app.vis_dict['Dire_Charm'] = Vis(name = 'Dire_Charm', loc = self.loc[:])
        app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict['Dire_Charm'].img, tags = 'Dire_Charm')
        def cleanup_charm(n):
            del app.vis_dict[n]
            app.canvas.delete(n)
            app.canvas.delete('text')
        def dire_charm_loop(ents):
            if ents == []:
                root.after(2666, lambda n = 'Dire_Charm' : cleanup_charm(n))
                root.after(2999, self.finish_dire_charm)
            else:
                id = ents[0]
                ents = ents[1:]
                s = app.ent_dict[id].loc[:]
                app.focus_square(s)
                uniq = 'Dire_Charm'+str(app.effects_counter)
                app.effects_counter += 1
                app.vis_dict[uniq] = Vis(name = 'Dire_Charmed', loc = s)
                app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[uniq].img, tags = 'Dire_Charm')
                if app.ent_dict[id].save_check('psyche', mod = -3) == True:# SAVE
                    app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+74-app.moved_down, text = 'Psyche Save', font = ('Andale Mono', 13), fill = 'black', tags = 'text')

                    app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+75-app.moved_down, text = 'Psyche Save', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                    root.after(2666, lambda n = uniq : cleanup_charm(n))
                    root.after(2999, lambda ents = ents : dire_charm_loop(ents))
                else:
                    tar_str = app.ent_dict[id].get_abl('str')
                    tar_end = app.ent_dict[id].get_abl('end')
                    d = damage(tar_str, tar_end)
                    pre = app.ent_dict[id].spirit
#                     app.ent_dict[id].set_attr('spirit', -d)
                    lock(apply_damage, self, app.ent_dict[id], -d, 'crushing', 'Dire Charmed')
                    post = app.ent_dict[id].spirit
                    d = pre - post
                    app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+74-app.moved_down, text = 'Attack Self '+str(d)+' spirit', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+75-app.moved_down, text = 'Attack Self '+str(d)+' spirit', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                    if app.ent_dict[id].spirit <= 0:
                        app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+94-app.moved_down, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                        app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+95-app.moved_down, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                        name = 'Dethlok'+str(app.death_count)
                        app.death_count += 1
                        app.dethloks[name] = tk.IntVar(0)
                        root.after(2666, lambda n = uniq : cleanup_charm(n))
                        root.after(2999, lambda id = id, name = name : app.kill(id, name))
                        app.wait_variable(app.dethloks[name])
                        dire_charm_loop(ents)
                    else:
                        root.after(2666, lambda n = uniq : cleanup_charm(n))
                        root.after(2999, lambda ents = ents : dire_charm_loop(ents))
        dire_charm_loop(ents)
            
            
    def finish_dire_charm(self, event = None):
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)


class Cenobite(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'Strength Through Wounding':self.strength_through_wounding, 'Flesh Hooks': self.flesh_hooks, 'Hellfire': self.hellfire, 'Move': self.move}
        self.attack_used = False
        self.str = 6
        self.agl = 6
        self.end = 6
        self.dodge = 6
        self.psyche = 6
        self.spirit = 16
        self.move_range = 6
        self.move_type = 'normal'
        self.weak = ['cold']
        self.resist = ['slashing', 'fire', 'magick', 'elec']
        super().__init__(name, img, loc, owner, number)
        
    # all w/i rang3 take 2, friendly get +2 end, +2 psy for 2 turns
    def strength_through_wounding(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_strength_through_wounding)
        sqrs = [c for c in app.coords if 1 <= dist(self.loc, c) <= 3]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = sqrs : self.do_strength_through_wounding(event = e, sqrs = s)) 
        b = tk.Button(app.context_menu, text = 'Confirm Strength Through Wounding', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs : self.do_strength_through_wounding(event = e, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_strength_through_wounding(self, event = None, sqrs = None):
        self.attack_used = True
        effect1 = mixer.Sound('Sound_Effects/strength_through_wounding.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        ents = [k for k,v in app.ent_dict.items() if v.loc in sqrs and v.type != 'large']
        def cleanup_stw(n):
            del app.vis_dict[n]
            app.canvas.delete(n)
            app.canvas.delete('text')
        def stw_loop(ents):
            if ents == []:
                self.finish_strength_through_wounding()
            else:
                id = ents[0]
                ents = ents[1:]
                s = app.ent_dict[id].loc[:]
#                 app.ent_dict[id].set_attr('spirit', -2)
                lock(apply_damage, self, app.ent_dict[id], -2, 'magick', 'Strength Through Wounding')
                u = 'Strength_Through_Wounding' + str(app.effects_counter) # not an effect, just need unique int
                app.effects_counter += 1 # that is why this is incr manually here, no Effect init
                app.vis_dict[u] = Vis(name = 'Strength_Through_Wounding', loc = s)
                app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[u].img, tags = u)
                app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+74-app.moved_down, text = '2 spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')

                app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+75-app.moved_down, text = '2 spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'ivory3', tags = 'text')
                if app.ent_dict[id].spirit <= 0:
                    app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+94-app.moved_down, text = app.ent_dict[id].name + ' Killed...', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+95-app.moved_down, text = app.ent_dict[id].name + ' Killed...', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                    name = 'Dethlok'+str(app.death_count)
                    app.death_count += 1
                    app.dethloks[name] = tk.IntVar(0)
                    root.after(2666, lambda u = u : cleanup_stw(u))
                    root.after(2999, lambda id = id, name = name : app.kill(id, name))
                    app.wait_variable(app.dethloks[name])
                    stw_loop(ents)
                # give stat bonus if friendly and not dead
                elif app.ent_dict[id].owner == app.active_player and 'Strength_Through_Wounding' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
                    app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+94-app.moved_down, text = '+2 End, Psy', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+95-app.moved_down, text = '+2 End, Psy', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                    def strength_through_wounding_effect(stat):
                        stat += 2
                        return stat
                    f = strength_through_wounding_effect
                    app.ent_dict[id].end_effects.append(f)
                    app.ent_dict[id].psyche_effects.append(f)
                    n = 'Strength_Through_Wounding' + str(app.effects_counter)
                    def un(i, func):
                        app.ent_dict[i].end_effects.remove(func)
                        app.ent_dict[i].psyche_effects.remove(func)
                        return None
                    p = partial(un, id, f)
                    n = 'Strength_Through_Wounding' + str(app.effects_counter)
                    app.ent_dict[id].effects_dict[n] = Effect(name = 'Strength_Through_Wounding', undo_func = p, duration = 2, level = 4)
                    root.after(2666, lambda u = u : cleanup_stw(u))
                    root.after(2999, lambda ents = ents : stw_loop(ents))
                else:
                    root.after(2666, lambda u = u : cleanup_stw(u))
                    root.after(2999, lambda ents = ents : stw_loop(ents))
        stw_loop(ents)
        
    def finish_strength_through_wounding(self, event = None):
#         self.init_normal_anims()
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        app.depop_context(event = None)
        
    # give ranged attack to friendly ent
    def flesh_hooks(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.finish_flesh_hooks)
        sqrs = [c for c in app.coords if dist(self.loc, c) <= 3 and c != self.loc]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_flesh_hooks(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Bestow Flesh Hooks', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_flesh_hooks(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_flesh_hooks(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if app.ent_dict[id].owner != self.owner:
            return
        if isinstance(app.ent_dict[id], (Bard, Trickster, Warrior, Shadow, Plaguebearer)) == False:
            return
        if 'Hook Attack' in app.ent_dict[id].get_actions().keys():
            return
        self.attack_used = True
#         self.init_attack_anims()
        effect1 = mixer.Sound('Sound_Effects/flesh_hooks.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        app.vis_dict['Flesh_Hooks'] = Vis(name = 'Flesh_Hooks', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Flesh_Hooks'].img, tags = 'Flesh_Hooks')
        app.canvas.create_text(sqr[0]*100-app.moved_right+50, sqr[1]*100-app.moved_down+90, text = 'Flesh Hooks', justify = 'center', fill = 'white', font = ('Andale Mono', 14), tags = 'text')
        # add action to ent
        def hook_attack(event = None, obj = None):
            if obj.attack_used == True:
                return
            app.unbind_nonarrows()
            root.bind('<q>', lambda e, obj = obj : cancel_attack(obj = obj))
            sqrs = []
            for c in app.coords:
                if 1 <= dist(obj.loc, c) <= 3:
                    sqrs.append(c)
            app.animate_squares(sqrs)
            app.depop_context(event = None)
            root.bind('<a>', lambda e, sqrs = sqrs, sqr = grid_pos, obj = obj : check_hit(event = e, sqrs = sqrs, sqr = sqr, obj = obj)) 
            b = tk.Button(app.context_menu, text = 'Confirm Hook Attack', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs, sqr = grid_pos, obj = obj : check_hit(event = e, sqrs = sqrs, sqr = sqr, obj = obj))
            b.pack(side = 'top')
            app.context_buttons.append(b)
            # INNER-INNER FUNCS, context must be passed to obj receiving this action
            def check_hit(event = None, sqrs = None, sqr = None, obj = None):
                if sqr not in sqrs:
                    return
                id = app.grid[sqr[0]][sqr[1]]
                if id == '' or id == 'block':
                    return
                if id not in app.action_target_ents().keys():
                    return
                obj.attack_used = True
#                 obj.init_attack_anims()
                effect1 = mixer.Sound('Sound_Effects/hook_attack.ogg')
                effect1.set_volume(1)
                sound_effects.play(effect1, 0)
                app.depop_context(event = None)
                app.unbind_all()
                app.cleanup_squares()
                visloc = app.ent_dict[id].loc[:]
                app.vis_dict['Hook_Attack'] = Vis(name = 'Hook_Attack', loc = visloc)
                app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Hook_Attack'].img, tags = 'Hook_Attack')
                my_psyche = obj.get_abl('psyche')
                target_dodge = app.ent_dict[id].get_abl('dodge')
                if to_hit(my_psyche, target_dodge) == True:
                    my_end = obj.get_abl('end')
                    target_end = app.ent_dict[id].get_abl('end')
                    d = damage(my_end, target_end)
                    pre = app.ent_dict[id].spirit
                    lock(apply_damage, obj, app.ent_dict[id], -d, 'piercing', 'Hook Attack')
                    post = app.ent_dict[id].spirit
                    d = pre - post
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    if app.ent_dict[id].spirit <= 0:
                        app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+89, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                        app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+90, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                        name = 'Dethlok'+str(app.death_count)
                        app.death_count += 1
                        app.dethloks[name] = tk.IntVar(0)
                        root.after(2666, lambda e = None, obj = obj : cancel_attack(e, obj))
                        root.after(2999, lambda id = id, name = name : app.kill(id, name))
                        app.wait_variable(app.dethloks[name])
                    else:
                        root.after(2666, lambda e = None, obj = obj : cancel_attack(event = e, obj = obj))
                else:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    root.after(2666, lambda e = None, obj = obj : cancel_attack(event = e, obj = obj))
            # INNER INNER FUNC
            def cancel_attack(event = None, obj = None):
                obj.init_normal_anims() # to init attack anims, provide them for each possible unit that can gain hook_attack
                app.rebind_all()
                app.canvas.delete('text')
                try:
                    del app.vis_dict['Hook_Attack']
                    app.canvas.delete('Hook_Attack')
                except: pass
                app.depop_context(event = None)
                app.cleanup_squares()
            # END INNER-INNER FUNCS
        # ADD ACTION TO TARGET
        p = partial(hook_attack, obj = app.ent_dict[id])
#         app.ent_dict[id].actions['Hook Attack'] = p
        def add_hook_attack(actions = None, func = None):
            actions['Hook Attack'] = func
            return actions
        p2 = partial(add_hook_attack, func = p)
        app.ent_dict[id].action_effects.append(p2)
        def hook_effect():
            pass
        f = hook_effect
        def un(i, func):
            app.ent_dict[i].action_effects.remove(func)
#             del app.ent_dict[i].actions['Hook Attack']
            return None
        p = partial(un, id, p2)
        n = 'Hook_Attack' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Hook_Attack', undo_func = p, duration = 3, level = 6)
        root.after(2666, self.finish_flesh_hooks)
        
    def finish_flesh_hooks(self, event = None):
#         self.init_normal_anims()
        try:
            del app.vis_dict['Flesh_Hooks']
            app.canvas.delete('Flesh_Hooks')
        except: pass
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
        app.canvas.delete('text')
        app.depop_context(event = None)
        
    # damage and possible burn to target
    # vis, self 'glows', target flames
    def hellfire(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.cancel_hellfire)
        sqrs = []
        for c in app.coords:
            if 1 <= dist(self.loc, c) <= 2:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_hellfire(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Confirm Hellfire', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos[:], sqrs = sqrs : self.do_hellfire(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_hellfire(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        self.attack_used = True
#         self.init_attack_anims()
        effect1 = mixer.Sound('Sound_Effects/beleths_command.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        visloc = app.ent_dict[id].loc[:]
        app.vis_dict['Hellfire'] = Vis(name = 'Hellfire', loc = visloc)
        app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Hellfire'].img, tags = 'Hellfire')
        my_psyche = self.get_abl('psyche')
        target_psyche = app.ent_dict[id].get_abl('psyche')
        if to_hit(my_psyche, target_psyche) == True:
            target_end = app.ent_dict[id].get_abl('end')
            d = damage(my_psyche, target_end)
            pre = app.ent_dict[id].spirit
            lock(apply_damage, self, app.ent_dict[id], -d, 'fire', 'Hellfire')
            post = app.ent_dict[id].spirit
            d = pre - post
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+74-app.moved_down, text = 'Hit! '+str(d)+' spirit', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Hit! '+str(d)+' spirit', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            if app.ent_dict[id].spirit <= 0:
                app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+94-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+95-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                name = 'Dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(2666, self.cancel_hellfire)
                root.after(2999, lambda id = id, name = name : app.kill(id, name))
                app.wait_variable(app.dethloks[name])
            else:# SAVE to avoid burn
                if app.ent_dict[id].save_check('end', mod = -1) == False:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+94-app.moved_down, text = 'Burned', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+95-app.moved_down, text = 'Burned', justify ='center', font = ('Andale Mono', 13), fill = 'orangered2', tags = 'text')
                # burn effect, every time burned ent takes spirit dmg it takes that much dmg plus 2
                    def burn_effect(attacker, defender, amount, type):
                        if amount < 0 and (type == 'melee' or type == 'ranged'):
                            app.canvas.create_text(defender.loc[0]*100+49-app.moved_right, defender.loc[1]*100+54-app.moved_down, text = '+2 spirit burn', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                            app.canvas.create_text(defender.loc[0]*100+50-app.moved_right, defender.loc[1]*100+55-app.moved_down, text = '+2 spirit burn', justify ='center', font = ('Andale Mono', 13), fill = 'orangered2', tags = 'text')
                            root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                            amount -= 2
                            return (amount, 1666)
                        else:
                            return (amount, 0)
                    app.ent_dict[id].defense_effects.append(burn_effect)
                    def un(i):
                        app.ent_dict[i].defense_effects.remove(burn_effect)
                        return None
                    p = partial(un, id)
                    n = 'Burn' + str(app.effects_counter)
                    app.ent_dict[id].effects_dict[n] = Effect(name = 'Burn', undo_func = p, duration = 3, level = 4)
                root.after(2666, lambda e = None : self.cancel_hellfire(event = e))
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+74-app.moved_down, text = 'Miss!', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Miss!', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            root.after(2666, lambda e = None : self.cancel_hellfire(event = e))
        
    def cancel_hellfire(self, event = None):
#         self.init_normal_anims()
        app.rebind_all()
        app.canvas.delete('text')
        try: 
            del app.vis_dict['Hellfire']
            app.canvas.delete('Hellfire')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
    # ensure only one at a time, on death witch loses spirit, flight for movement (not blocked by obstacles)
    # casts poison sting, darkness, 
    # darkness, global effect that affects sqrs within distance 3, any movement originating in one of these sqrs is reduced to distance 2, only affects ents that use 'normal' movement (non-teleport)
    # poison sting, agl versus dodge to hit check, on success target gets 'poison' effect, -1 str 2 dmg for 3 turns, stackable, range 2
class Familiar_Imp(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'Poison Sting':self.poison_sting, 'Darkness':self.darkness, 'Flying Move':self.flying_move}
        self.attack_used = False
        self.str = 2
        self.agl = 6
        self.end = 3
        self.dodge = 7
        self.psyche = 6
        self.spirit = 9
        self.move_range = 5
        self.move_type = 'flying'
        self.resist = ['fire', 'elec', 'cold', 'poison']
        self.weak = ['crushing', 'acid']
        super().__init__(name, img, loc, owner, number)
        def familiar_trigger():
            if self.owner == 'p1':
                witch = app.p1_witch
            else:
                witch = app.p2_witch
            loc = app.ent_dict[witch].loc[:]
#             app.ent_dict[witch].set_attr('spirit', -3)
            lock(apply_damage, app.ent_dict[witch], app.ent_dict[witch], -3, 'magick', 'Familiar Death')
            app.focus_square(loc)
            app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = '3 Spirit, Familiar Death', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = '3 Spirit, Familiar Death', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            root.after(2333, lambda t = 'text' : app.canvas.delete(t))
            if app.ent_dict[witch].spirit <= 0:
                app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+94-app.moved_down, text = app.ent_dict[witch].name.replace('_', ' ')+' Killed...', fill = 'black', font = ('Andale Mono', 13), tags = 'self_death')
                app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+95-app.moved_down, text = app.ent_dict[witch].name.replace('_', ' ')+' Killed...', fill = 'white', font = ('Andale Mono', 13), tags = 'self_death')
                name = 'dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(2333, lambda id = app.ent_dict[witch].name, n = name : app.kill(id, n))
                root.wait_variable(app.dethloks[name])
        self.death_triggers.append(familiar_trigger)
        
        
    def darkness(self, event = None):
#         loc_effects = [v.name for k,v in app.loc_effects_dict.items()]
#         if 'Darkness' in g_effects:
#             return
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.cancel_attack)
        sqrs = []
        for c in app.coords:
            if dist(self.loc, c) <= 5:
                sqrs.append(c)
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_darkness(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Confirm Darkness', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_darkness(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
    def do_darkness(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        effect1 = mixer.Sound('Sound_Effects/darkness.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        self.attack_used = True
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Darkness', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Darkness', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        # create vis on every sqr within distance 3 from sqr
        affected_sqrs = [c for c in app.coords if dist(c, sqr) <= 2 and app.grid[c[0]][c[1]] != 'block']
        for s in affected_sqrs:
            if 'Darkness' not in [v.name for k,v in app.loc_effects_dict[tuple(s)].effects_dict.items()]:
                un = 'Darkness' + str(app.effects_counter)
                app.effects_counter += 1
                app.vis_dict[un] = Vis(name = 'Darkness', loc = s[:])
                app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = un)
                def dark_move(move_range):
                    move_range -= 2
                    if move_range <= 1:
                        return 1
                    else:
                        return move_range
                p = partial(dark_move)
                app.loc_effects_dict[tuple(s)].move_effects.append(p)
                def undo(s, un, p_dark_move):
                    app.loc_effects_dict[tuple(s)].move_effects.remove(p_dark_move)
                    del app.vis_dict[un]
                    app.canvas.delete(un)
                u = partial(undo, s, un, p)
                app.loc_effects_dict[tuple(s)].effects_dict[un] = Local_Effect(name = 'Darkness', undo = u, duration = 2, level = 3, loc = s[:], avoid = 6)
        self.cleanup_darkness()
        
    def cleanup_darkness(self, event = None):
        app.unbind_all()
        app.rebind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        try: app.canvas.delete('text')
        except: pass
        
        
    def poison_sting(self, event = None):
        if self.attack_used == True:
            return
        root.unbind('<a>')
        root.unbind('<q>')
        root.bind('<q>', self.cancel_attack)
        sqrs = [c for c in app.coords if 1 <= dist(self.loc,c) <= 3]
        app.animate_squares(sqrs)
        app.depop_context(event = None)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.check_hit(event = e, sqr = s, sqrs = sqrs)) 
        b = tk.Button(app.context_menu, text = 'Confirm Poison Sting', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos[:], sqrs = sqrs : self.check_hit(event = e, sqr = s, sqrs = sqrs))
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
        
    # add directional vis
    # create dart object on origin sqr, rotate image based on slope and direction of line from origin to target?
    def check_hit(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        if app.grid[sqr[0]][sqr[1]] == '' or app.grid[sqr[0]][sqr[1]] == 'block':
            return
        self.attack_used = True
#         self.init_attack_anims()
        effect1 = mixer.Sound('Sound_Effects/poison_sting.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        id = app.grid[sqr[0]][sqr[1]]
        visloc = app.ent_dict[id].loc[:]
        app.vis_dict['Poison_Sting'] = Vis(name = 'Poison_Sting', loc = visloc)
        app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Poison_Sting'].img, tags = 'Poison_Sting')
        my_agl = self.get_abl('agl')
        target_dodge = app.ent_dict[id].get_abl('dodge')
        if to_hit(my_agl, target_dodge) == True:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+74-app.moved_down, text = 'Hit!', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Hit!', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            # poison str effect
            def poison_sting_effect(stat):
                stat -= 1
                if stat < 1:
                    return 1
                else:
                    return stat
            f = poison_sting_effect
            app.ent_dict[id].str_effects.append(f)
            def un(i):
                app.ent_dict[i].str_effects.remove(poison_sting_effect)
                return None
            p = partial(un, id)
            # EOT FUNC
            def take_2(tar, lockname = None):
                app.get_focus(tar)
                lock(apply_damage, self, app.ent_dict[tar], -2, 'poison', 'Poison Sting')
                root.after(1333, lambda ln = lockname : app.dethloks[ln].set(1))
            eot = partial(take_2, id)
            n = 'Poison_Sting' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Poison_Sting', eot_func = eot, undo_func = p, duration = 4, level = 4)
        else:
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+74-app.moved_down, text = 'Miss!', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Miss!', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        root.after(2666, lambda e = None : self.cancel_attack(event = e))
        
    def cancel_attack(self, event):
        self.init_normal_anims()
        app.rebind_all()
        app.canvas.delete('text')
        try: 
            del app.vis_dict['Poison_Sting']
            app.canvas.delete('Poison_Sting')
        except: pass
        app.depop_context(event = None)
        app.cleanup_squares()
    
    def legal_moves(self):
        loc = self.loc
        mvlist = []
        for c in app.coords:
            if dist(c, loc) <= self.get_abl('move_range') and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist
                    
                    
class Hunting_Hawk(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {}
        self.attack_used = False
        self.str = 2
        self.agl = 8
        self.end = 2
        self.dodge = 9
        self.psyche = 3
        self.spirit = 9
        self.move_range = 6
        self.move_type = 'flying'
        self.attack_range = 4
        self.resist = ['magick', 'fire', 'elec', 'cold', 'poison', 'acid']
        self.weak = ['piercing', 'slashing']
        super().__init__(name, img, loc, owner, number)
        def eot(lockname = None):
            self.effects_dict['control'].duration += 1 # permanent effect
            # move hawk to sqr w/i moverange that is w/i attackrange(5) and maximally distant from all enemies and then atk
            # if no enemies w/i attack range, move to a random sqr w/i move range
            els = [v.loc for k,v in app.all_ents().items() if v.owner != self.owner]
            sqrs = [s for s in app.coords for el in els if dist(s,el) <= self.attack_range]
            moves = self.legal_moves()
            gs = intersect(sqrs, moves)
            if gs == []:
                # move to rand sqr in moves
                if moves == []:
                    # cannot move at all, attempt attack wo moving
                    ents = [k for k,v in app.all_ents().items() if dist(v.loc,self.loc) <= self.attack_range and v.owner != self.owner]
                    if ents == []:
                        root.after(666, lambda ln = lockname : app.dethloks[ln].set(1))
                    else:
                        id = choice(ents)
                        root.after(666, lambda id = id, ln = lockname : self.hawk_attack(id, ln))
                else:
                    move = choice(moves)
                    root.after(666, lambda m = move : self.hawk_move(m))
            else:
                g = reduce(lambda a,b : a if sum([dist(a,el) for el in els]) > sum([dist(b,el) for el in els]) else b, gs)
                app.focus_square(g)
                root.after(666, lambda sqr = g[:], ln = lockname : self.hawk_move(sqr, ln))
        e = partial(eot)
        def undo():
            return None
        self.effects_dict['control'] = Effect(name = self.owner+"'s Hawk", eot_func = e, undo_func = undo, duration = 666, level = 666)
                
    def hawk_attack(self, id, lockname):
        my_agl = self.get_abl('agl')
        tar_agl = app.ent_dict[id].get_abl('agl')
        if to_hit(my_agl, tar_agl) == True:
            my_str = self.get_abl('str')
            tar_end = app.ent_dict[id].get_abl('end')
            pre = app.ent_dict[id].spirit
            d = damage(my_str, tar_end)
            lock(apply_damage, self, app.ent_dict[id], -d, 'piercing', 'Hawk Attack')
            post = app.ent_dict[id].spirit
            d = pre - post
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+74-app.moved_down, text = 'Hit! '+str(d)+' spirit', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Hit! '+str(d)+' spirit', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            if app.ent_dict[id].spirit <= 0:
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+94, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+95, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                name = 'Dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(1666, lambda id = id, name = name : app.kill(id, name))
                app.wait_variable(app.dethloks[name])
                root.after(999, lambda ln = lockname : app.dethloks[ln].set(1))
            else:
                root.after(999, lambda ln = lockname : app.dethloks[ln].set(1))
        else: # miss
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+49-app.moved_right, app.ent_dict[id].loc[1]*100+74-app.moved_down, text = 'Miss!', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
            app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+75-app.moved_down, text = 'Miss!', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            root.after(999, lambda ln = lockname : app.dethloks[ln].set(1))

    def hawk_move(self, sqr, lockname):
        global selected
        selected = [self.number]
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        endx = sqr[0]*100+50-app.moved_right
        endy = sqr[1]*100+50-app.moved_down
        start_sqr = self.loc[:]
        end_sqr = sqr[:]
        total_distance = abs(x - endx) + abs(y - endy)
        # tic doesnt matter for circular image loop, would need to make flying_anims and switch to
        tic = 30 #total_distance/9 # Magic Number debug, number of images for vis
        if x == endx:
            xstep = 0
            ystep = 10
        elif y == endy:
            xstep = 10
            ystep = 0
        else:
            slope = Fraction(abs(x - endx), abs(y - endy))
            # needs to be moving at least 10 pixels, xstep + ystep >= 10
            xstep = slope.numerator
            ystep = slope.denominator
            while xstep + ystep < 10:
                xstep *= 2
                ystep *= 2
        def flying_arc(x, y, endx, endy, start_sqr, end_sqr, acm, tic, xstep, ystep):
            if acm >= tic:
                acm = 0
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if x > endx:
                acm += xstep
                x -= xstep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            elif x < endx:
                acm += xstep
                x += xstep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if y > endy:
                acm += ystep
                y -= ystep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            elif y < endy:
                acm += ystep
                y += ystep
                self.rotate_image()
                app.canvas.delete(self.tags)
                app.canvas.create_image(x, y, image = self.img, tags = self.tags)
            if abs(x - endx) < 13 and abs(y - endy) < 13:
                self.finish_move( end_sqr, start_sqr, lockname)
            else: # CONTINUE LOOP
                root.after(66, lambda x = x, y = y, e = endx, e2 = endy, s = start_sqr, s2 = end_sqr, acm = acm, tic = tic, xs = xstep, ys = ystep : flying_arc(x, y, e, e2, s, s2, acm, tic, xs, ys))
        flying_arc(x, y, endx, endy, start_sqr, end_sqr, tic+1, tic, xstep, ystep)

    def finish_move(self, end, start, lockname):
#         sound_effects.stop()
        global selected
        selected = []
        self.loc = end[:]
        app.grid[start[0]][start[1]] = ''
        app.grid[end[0]][end[1]] = self.number
        self.move_used = True
        # if enemy w/i range: atk else done
        ents = [k for k,v in app.all_ents().items() if dist(v.loc,self.loc) <= self.attack_range and v.owner != self.owner]
        if ents == []:
            root.after(1999, lambda ln = lockname : app.dethloks[ln].set(1))
        else:
            id = choice(ents)
            root.after(666, lambda id = id, ln = lockname : self.hawk_attack(id, ln))
    
    def legal_moves(self):
        loc = self.loc
        mvlist = []
        for c in app.coords:
            if dist(c, loc) <= self.get_abl('move_range') and app.grid[c[0]][c[1]] == '':
                mvlist.append(c)
        return mvlist
                    
                    
class Witch(Entity):
    def __init__(self, name, img, loc, owner):
        self.actions = {'Spell':self.spell, 'Summon':self.summon, 'Move':self.move}
        self.summon_cap = 6
        self.summon_level = 1
        self.summon_count = 0
        self.cantrip_used = False
        self.arcane_used = False
        self.summon_used = False
        self.arcane_dict = {}
        self.cantrip_dict = {}
        self.summon_ids = 0
        self.move_type = 'normal'
        if name == 'Agnes_Sampson':
            self.cantrip_dict['Psionic_Push'] = (self.psionic_push, 0)
            self.cantrip_dict["Minerva's_Gift"] = (self.minervas_gift, 0)
            self.cantrip_dict['Bewitch'] = (self.bewitch, 0)
            self.cantrip_dict['Read_the_Stars'] = (self.read_the_stars, 0)
            self.cantrip_dict['Energize'] = (self.energize, 0)
            self.cantrip_dict['Psi_Blades'] = (self.psi_blades, 0)
            self.cantrip_dict['Cosmic_Sight'] = (self.cosmic_sight, 0)
            self.arcane_dict['Plague'] = (self.plague, 6)
            self.arcane_dict['Pestilence'] = (self.pestilence, 6)
            self.arcane_dict['Curse_of_Oriax'] = (self.curse_of_oriax, 7)
            self.arcane_dict['Demonic_Sight'] = (self.demonic_sight, 3)
            self.arcane_dict['Molecular_Subversion'] = (self.molecular_subversion, 4)
            self.arcane_dict['Plutonian_Cloak'] = (self.plutonian_cloak, 4)
            self.arcane_dict['Hidden_From_the_Stars'] = (self.hidden_from_the_stars, 6)
            self.arcane_dict['Gravity'] = (self.gravity, 5)
            self.arcane_dict["Beleth's_Command"] = (self.beleths_command, 8)
            self.str = 4
            self.agl = 3
            self.end = 4
            self.dodge = 4
            self.psyche = 6
            self.spirit = 40
            self.magick = 75
            self.move_range = 3
            self.weak = ['elec', 'slashing']
            self.resist = ['poison', 'fire']
        elif name == 'Fakir_Ali':
            self.cantrip_dict['Boiling_Blood'] = (self.boiling_blood, 0)
            self.cantrip_dict['Dark_Sun'] = (self.dark_sun, 0)
            self.cantrip_dict['Meditate'] = (self.meditate, 0)
            self.arcane_dict['Horrid_Wilting'] = (self.horrid_wilting,5)
            self.arcane_dict['Disintegrate'] = (self.disintegrate, 4)
            self.arcane_dict['Mummify'] = (self.mummify, 5)
            self.arcane_dict['Immolate'] = (self.immolate, 9)
            self.arcane_dict['Command_of_Osiris'] = (self.command_of_osiris, 5)
            self.str = 3
            self.agl = 4
            self.end = 6
            self.dodge = 3
            self.psyche = 5
            self.spirit = 50
            self.magick = 70
            self.move_range = 3
            self.weak = ['crushing']
            self.resist = ['slashing', 'piercing', 'fire']
        elif name == 'Morgan_LeFay':
            self.actions['Move'] = self.flying_move
            self.cantrip_dict['Fleet_of_Paw'] = (self.fleet_of_paw, 0)
            self.cantrip_dict['Hunting_Hawk'] = (self.hunting_hawk, 0)
            self.cantrip_dict['Entangle'] = (self.entangle, 0)
#             self.spell_dict['Enchant'] = (self.enchant, 4)
#             self.spell_dict['Counterspell'] = (self.counterspell, 3)
#             self.spell_dict["Nature's_Wrath"] = (self.natures_wrath, 5)
#             self.spell_dict["Ceridwen's_Command"] = (self.ceridwens_command, 6)
#             self.spell_dict['Wild_Hunt'] = (self.wild_hunt, 7)
            self.str = 2
            self.agl = 5
            self.end = 3
            self.dodge = 6
            self.psyche = 5
            self.spirit = 35
            self.magick = 85
            self.move_range = 4
            self.weak = ['magick']
            self.resist = ['fire', 'elec', 'cold', 'acid', 'poison']
        super().__init__(name, img, loc, owner, type = 'normal')
        
    # clean protagonist object (Witch) between levels
    def reset_transient_vars(self):
        self.action_effects = []
        self.summon_ids = 0
        self.cantrip_used = False
        self.arcane_used = False
        self.summon_used = False
        self.spirit = self.base_spirit
        self.magick = self.base_magick
        self.str_effects = []
        self.agl_effects = []
        self.end_effects = []
        self.dodge_effects = []
        self.psyche_effects = []
        self.attack_effects = []
        self.defense_effects = []
        self.resist_effects = []
        self.weak_effects = []
        self.type_effects = []
        self.move_effects = []
        self.death_triggers = []
        self.move_used = False
        self.effects_dict = {}
        self.summon_count = 0
    
    def summon(self, event = None):
        if self.summon_used == True:
            return
        app.depop_context(event = None)
        root.bind('1', lambda e, cls = 'Warrior' : self.place_summon(e, cls))
        root.bind('2', lambda e, cls = 'Trickster' : self.place_summon(e, cls))
        root.bind('3', lambda e, cls = 'Shadow' : self.place_summon(e, cls))
        root.bind('4', lambda e, cls = 'Bard': self.place_summon(e, cls))
        root.bind('5', lambda e, cls = 'Plaguebearer' : self.place_summon(e, cls))
        b1 = tk.Button(app.context_menu, text = '1:Warrior', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, cls = 'Warrior' : self.place_summon(e, cls))
        b1.pack(side = 'top', pady = 2)
        app.context_buttons.append(b1)
        b2 = tk.Button(app.context_menu, text = '2:Trickster', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, cls = 'Trickster' : self.place_summon(e, cls))
        b2.pack(side = 'top', pady = 2)
        app.context_buttons.append(b2)
        b3 = tk.Button(app.context_menu, text = '3:Shadow', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, cls = 'Shadow' : self.place_summon(e, cls))
        b3.pack(side = 'top', pady = 2)
        app.context_buttons.append(b3)
        b4 = tk.Button(app.context_menu, text = '4:Bard', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, cls = 'Bard' : self.place_summon(e, cls))
        b4.pack(side = 'top', pady = 2)
        app.context_buttons.append(b4)
        b5 = tk.Button(app.context_menu, text = '5:Plaguebearer', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, cls = 'Plaguebearer' : self.place_summon(e, cls))
        b5.pack(side = 'top', pady = 2)
        app.context_buttons.append(b5)
        b6 = tk.Button(app.context_menu, text = 'Cancel', font = ('chalkduster', 24), highlightbackground = 'tan3', fg='tan3', command = self.cancel_placement)
        b6.pack(side = 'top')
        app.context_buttons.append(b6)
    
    def cancel_placement(self, event = None):
        app.depop_context(event = None)
        app.cleanup_squares()
        app.unbind_all()
        app.rebind_all()
#         for x in range(1,4):
#             root.unbind(str(x))
#         root.unbind('<q>')
#         root.bind('<q>', app.depop_context)
#         root.unbind('<a>')
#         root.bind('<a>', app.populate_context)

    
    def place_summon(self, event, type):
        if self.summon_count >= self.summon_cap:
            return
#         root.unbind('<q>')
#         root.unbind('<a>')
#         for x in range(1,4):
#             root.unbind(str(x))
        app.unbind_nonarrows()
        root.bind('<q>', self.cancel_placement)
        app.depop_context(event = None)
        sqrs = [c for c in app.coords if dist(c, self.loc) == 1 and app.grid[c[0]][c[1]] == '']
        app.animate_squares(sqrs)
        if type == 'Warrior':
            cls = Warrior
        elif type == 'Trickster':
            cls = Trickster
        elif type == 'Shadow':
            cls = Shadow
        elif type == 'Bard':
            cls = Bard
        elif type == 'Plaguebearer':
            cls = Plaguebearer
        cmd = lambda e = None, x = cls, y = sqrs, s = grid_pos : self.place(e, summon = x, sqrs = y, sqr = s)
        root.bind('<a>', lambda e, x = cls, y = sqrs, s = grid_pos : self.place(e, x, y, s))
        b = tk.Button(app.context_menu, text = 'Place '+type, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', wraplength = 190, command = cmd)
        b.pack(side = 'top')
        app.context_buttons.append(b)
        
        
    def place(self, event, summon, sqrs, sqr):
        if sqr not in sqrs:
            return
        app.unbind_all()
        root.bind('<q>', app.depop_context)
        root.bind('<a>', app.populate_context)
        # SOUND
        effect1 = mixer.Sound('Sound_Effects/summon.ogg')
        effect1.set_volume(.7)
        sound_effects.play(effect1, 0)
        # place visual summon
        app.vis_dict['Summon'] = Vis(name = 'Summon', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Summon'].img, tags = 'Summon')
        if app.active_player == 'p1':
            number = 'a' + str(self.summon_ids)
            self.summon_ids += 1
            self.summon_count += 1
        elif app.active_player == 'p2':
            number = 'b' + str(self.summon_ids)
            self.summon_ids += 1
            self.summon_count += 1
        if summon == Warrior:
            name = 'Warrior'
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Warrior.png'))
        elif summon == Trickster:
            name = 'Trickster'
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Trickster.png'))
        elif summon == Shadow:
            name = 'Shadow'
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Shadow.png'))
        elif summon == Bard:
            name = 'Bard'
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Bard.png'))
        elif summon == Plaguebearer:
            name = 'Plaguebearer'
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Plaguebearer.png'))
        s = summon(name = name, img = img, loc = sqr[:], owner = app.active_player, number = number, level = self.summon_level)
        app.cleanup_squares()
        app.depop_context(event = None)
        # separate here to finish summon vis, place ent after a sec or two
        root.after(1999, lambda s = s, sqr = sqr, id = number : self.finish_place(s, sqr, id))
        
    def finish_place(self, summon, sqr, id):
        app.ent_dict[id] = summon
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = summon.img, tags = summon.tags)
        app.grid[sqr[0]][sqr[1]] = id
        self.summon_used = True
        app.canvas.delete('Summon')
        del app.vis_dict['Summon']
        app.unbind_all()
        app.rebind_all()
        
    def legal_moves(self):
        loc = self.loc[:]
        mvlist = []
        sqr_cost_map = {}
        def findall(loc, start, distance):
            if start > distance:
                return
            adj = [c for c in app.coords if dist(c, loc) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                if tuple(s) in sqr_cost_map:
                    if sqr_cost_map[tuple(s)] < start:
                        continue
                sqr_cost_map[tuple(s)] = start
                if s not in mvlist:
                    mvlist.append(s)
                findall(s, start+1, distance)
        findall(loc, 1, self.get_abl('move_range'))
        return mvlist
        
    def spell(self, event = None):
#         if self.spell_used == True:
#             return
        app.depop_context(event = None)
#         root.unbind('<a>')
#         root.unbind('<q>')
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_spell)
        b1 = tk.Button(app.context_menu, wraplength = 190, text = 'Cantrip', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = self.cantrip)
        b1.pack(side = 'top', pady = 2)
        app.context_buttons.append(b1)
        root.bind(str(1), self.cantrip)
        b2 = tk.Button(app.context_menu, wraplength = 190, text = 'Arcane', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = self.arcane)
        b2.pack(side = 'top', pady = 2)
        app.context_buttons.append(b2)
        root.bind(str(2), self.arcane)
        
    def cantrip(self, event = None):
        if self.cantrip_used == True:
            return
        app.depop_context(event = None)
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_spell)
        tup_list = list(self.cantrip_dict.items())
        self.page_spells(tup_list = tup_list, index = 0)
        
    def arcane(self, event = None):
        if self.arcane_used == True:
            return
        app.depop_context(event = None)
        app.unbind_nonarrows()
        root.bind('<q>', self.cleanup_spell)
        tup_list = list(self.arcane_dict.items())
        self.page_spells(tup_list = tup_list, index = 0)
        
    def page_spells(self, event = None, tup_list = None, index = None):
        app.depop_context(event = None)
        for i, name_spellcosttuple in enumerate(tup_list[index:index+7]):
            name = name_spellcosttuple[0]
            name = name.replace('_', ' ')
            spell = name_spellcosttuple[1][0]
            cost = name_spellcosttuple[1][1]
            i += 1
            b1 = tk.Button(app.context_menu, wraplength = 190, text = str(i) +' : '+ name + ' •'+str(cost), font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = spell)
            b1.pack(side = 'top', pady = 2)
            if cost > self.magick:
                b1.config(state = 'disabled')
            else:
                root.bind(str(i), spell)
            app.context_buttons.append(b1)
            b1.bind('<Button-2>', lambda event, b = b1, n = name : app.action_info(event, name = n, button = b))
        if index > 0:
            b4 = tk.Button(app.context_menu, text = '9 : Prev', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda t = tup_list, i = index-7 : self.page_spells(tup_list = t, index = i))
            b4.pack(side = 'top')
            root.bind(str(9), lambda e, t = tup_list, i = index-7 : self.page_spells(tup_list = t, index = i))
            app.context_buttons.append(b4)
        if len(tup_list) > len(tup_list[:index+7]):
            b3 = tk.Button(app.context_menu, text = '8 : Next', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda t = tup_list, i = index+7 : self.page_spells(tup_list = t, index = i))
            b3.pack(side = 'top')
            root.bind(str(8), lambda e, t = tup_list, i = index+7 : self.page_spells(tup_list = t, index = i))
            app.context_buttons.append(b3)
            b2 = tk.Button(app.context_menu, text = 'Cancel', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = self.cleanup_spell)
            b2.pack(side = 'top')
            app.context_buttons.append(b2)
    
    def cleanup_spell(self, event = None, name = None):
        global selected, selected_vis
        app.unbind_all()
        self.init_normal_anims()
        app.cleanup_squares()
        app.depop_context(event = None)
        try: 
            del app.vis_dict[name]
            app.canvas.delete(name)
        except: pass
        try: app.canvas.delete('text')
        except: pass
        selected = []
        selected_vis = []
        app.rebind_all()
        
        
        # SPELLS
        # available to all through powerups
    # drain_life cantrip, deal 2 to any enemy target, heal 2 spirit?
    # exchange positions of friendly summon and enemy summon, or any two summons?
    # cantrip boost stats of a summon for multiple turns, non-stacking?
    
    # destroy familiar..., make a little taller and resemble the imp in some way, image should be combo of imp and homunc
    def summon_lesser_demon(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Summon_Lesser_Demon' : self.cleanup_spell(name = name))
        ents = [app.grid[s[0]][s[1]] for s in app.coords if dist(self.loc, s) <= 3 and app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
        familiars = [id for id in ents if app.ent_dict[id].owner == self.owner and (app.ent_dict[id].name == 'Familiar_Imp' or app.ent_dict[id].name == 'Familiar_Homunculus')]
        sqrs = []
        for id in familiars:
            sqrs.append(app.ent_dict[id].loc[:])
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_summon_lesser_demon(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Familiar To Transform', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_summon_lesser_demon(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_summon_lesser_demon(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        my_ent_names = [v.name for k,v in app.ent_dict.items() if v.owner == self.owner]
        if 'Lesser_Demon' in my_ent_names:
            return
        id = app.grid[sqr[0]][sqr[1]]
#         self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/summon_lesser_demon.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.canvas.delete(id)
        app.grid[app.ent_dict[id].loc[0]][app.ent_dict[id].loc[1]] = ''
        del app.ent_dict[id]
        app.vis_dict['Summon'] = Vis(name = 'Summon', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Summon'].img, tags = 'Summon')
        root.after(1666, lambda s = sqr : self.finish_summon_lesser_demon(s))
        root.after(2666, self.cleanup_summon_lesser_demon)
        root.after(2999, lambda name = 'Summon_Lesser_Demon' : self.cleanup_spell(name = name))
        
    def finish_summon_lesser_demon(self, sqr):
        num = self.summon_ids
        self.summon_ids += 1
        if self.owner == 'p1':
            prefix = 'a'
        else:
            prefix = 'b'
        id = prefix + str(num)
        img = ImageTk.PhotoImage(Image.open('summon_imgs/Lesser_Demon.png'))
        app.ent_dict[id] = Lesser_Demon(name = 'Lesser_Demon', img = img, loc = sqr[:], owner = self.owner, number = id)
        app.grid[sqr[0]][sqr[1]] = id
        
    def cleanup_summon_lesser_demon(self):
        del app.vis_dict['Summon']
        app.canvas.delete('Summon')
    
    
    def summon_cenobite(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Summon_Cenobite' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 3 and app.grid[s[0]][s[1]] == '']
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_summon_cenobite(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Location', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_summon_cenobite(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_summon_cenobite(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        if app.grid[sqr[0]][sqr[1]] != '':
            return
        my_ent_names = [v.name for k,v in app.ent_dict.items() if v.owner == self.owner]
        if 'Cenobite' in my_ent_names:
            return
        self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/summon_cenobite.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Summon'] = Vis(name = 'Summon', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Summon'].img, tags = 'Summon')
        root.after(1666, lambda s = sqr : self.finish_summon_cenobite(s))
        root.after(2666, self.cleanup_summon_cenobite)
        root.after(2999, lambda name = 'Summon_Cenobite' : self.cleanup_spell(name = name))
        
    def finish_summon_cenobite(self, sqr):
        num = self.summon_ids
        self.summon_ids += 1
        if self.owner == 'p1':
            prefix = 'a'
        else:
            prefix = 'b'
        id = prefix + str(num)
        img = ImageTk.PhotoImage(Image.open('summon_imgs/Cenobite.png'))
        app.ent_dict[id] = Cenobite(name = 'Cenobite', img = img, loc = sqr[:], owner = self.owner, number = id)
        app.grid[sqr[0]][sqr[1]] = id
        
    def cleanup_summon_cenobite(self):
        del app.vis_dict['Summon']
        app.canvas.delete('Summon')
        
# Agnes' spells center around Death/Decay/Disease/Telekinetics/Cosmology
    # target summon may move again this turn
    def energize(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Energize' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_energize(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Energize', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_energize(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_energize(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if not isinstance(app.ent_dict[id], Summon):
            return
        self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/energize.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.cantrip_used = True
        app.ent_dict[id].move_used = False
        app.vis_dict['Energize'] = Vis(name = 'Energize', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Energize'].img, tags = 'Energize')
        root.after(2999, lambda  name = 'Energize' : self.cleanup_spell(name = name))
    
    # target summon gets +2 agl, +2 psyche for one turn
    def minervas_gift(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = "Minerva's_Gift" : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 2]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_minervas_gift(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Gift', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_minervas_gift(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_minervas_gift(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if isinstance(app.ent_dict[id], Witch):
            return
        self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/scrye.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.cantrip_used = True
        app.vis_dict["Minerva's_Gift"] = Vis(name = "Minerva's_Gift", loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict["Minerva's_Gift"].img, tags = "Minerva's_Gift")
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = '+2 agl\n+2 psyche\n+1 spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = '+2 agl\n+2 psyche\n+1 spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        apply_heal(self, app.ent_dict[id], 1)
        def minervas_gift_effect(stat):
            stat += 2
            return stat
        f = minervas_gift_effect
        app.ent_dict[id].agl_effects.append(f)
        app.ent_dict[id].psyche_effects.append(f)
        def un(i):
            app.ent_dict[i].agl_effects.remove(minervas_gift_effect)
            app.ent_dict[i].psyche_effects.remove(minervas_gift_effect)
            return None
        p = partial(un, id)
        n = "Minerva's_Gift" + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = "Minerva's_Gift", undo_func = p, duration = 1, level = 4)
        root.after(2999, lambda  name = "Minerva's_Gift" : self.cleanup_spell(name = name))

    # target gains psyshield (friendly or foe, non-witch) 2 turns (cannot target with most spells, anything that checks app.spell_target_ents())
    def bewitch(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Bewitch' : self.cleanup_spell(name = name))
        # test visual lag from 'blinking' whole map
        # alternatively only blink the sqrs with legal targets
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 20]
        sqrs = [s for s in sqrs if app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_bewitch(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Bewitch', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_bewitch(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_bewitch(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if isinstance(app.ent_dict[id], Witch):
            return
        if id not in app.spell_target_ents().keys():
            return
        if 'Bewitch' in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
            return
        self.init_cast_anims()
#         effect1 = mixer.Sound('Sound_Effects/scrye.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.cantrip_used = True
        app.vis_dict['Bewitch'] = Vis(name = 'Bewitch', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Bewitch'].img, tags = 'Bewitch')
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Psy-shield', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Psy-shield', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        def bewitch_effect(types):
            return types+['psyshield']
        p = partial(bewitch_effect)
        app.ent_dict[id].type_effects.append(p)
        def undo(id, func):
            app.ent_dict[id].type_effects.remove(func)
        u = partial(undo, id, p)
        n = 'Bewitch' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Bewitch', undo_func = u, duration = 1, level = 4)
        root.after(2666, lambda  name = 'Bewitch' : self.cleanup_spell(name = name))

    def read_the_stars(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Read_the_Stars' : self.cleanup_spell(name = name))
        root.bind('<a>', self.do_read_the_stars)
        b = tk.Button(app.context_menu, text = 'Confirm Read the Stars', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None : self.do_read_the_stars(e))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_read_the_stars(self, event):
#         self.init_cast_anims()
#         effect1 = mixer.Sound('Sound_Effects/meditate.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        self.cantrip_used = True
        id = self.name
        sqr = self.loc[:]
        app.vis_dict['Read_the_Stars'] = Vis(name = 'Read_the_Stars', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Read_the_Stars'].img, tags = 'Read_the_Stars')
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Read the Stars', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Read the Stars', justify = 'center', font = ('Andale Mono', 13), fill = 'antiquewhite2', tags = 'text')
        def cleanup_read():
            app.canvas.delete('text')
            del app.vis_dict['Read_the_Stars']
            app.canvas.delete('Read_the_Stars')
        # caster and all friendly summons get atk efct that adds 1 to magick type, lasts 1 turn
        ids = [k for k,v in app.all_ents().items() if v.owner == self.owner]
        root.after(1555, cleanup_read)
        root.after(1666, lambda ids = ids : self.continue_read_the_stars(ids))
        
    def continue_read_the_stars(self, ids):
        def read_loop(ids):
            if ids == []:
                self.cleanup_spell(name = 'Read_the_Stars')
            else:
                id = ids[0]
                ids = ids[1:]
                app.get_focus(id)
                u = 'Read_the_Stars'+str(app.effects_counter)
                app.effects_counter += 1
                sqr = app.ent_dict[id].loc[:]
                app.vis_dict[u] = Vis(name = 'Read_the_Stars', loc = sqr[:])
                app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[u].img, tags = u)
                app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = '+1 magick dmg', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = '+1 magick dmg', justify = 'center', font = ('Andale Mono', 13), fill = 'antiquewhite2', tags = 'text')
                def cleanup_read(name):
                    app.canvas.delete('text')
                    del app.vis_dict[name]
                    app.canvas.delete(name)
                def rts_atk(atkr, dfndr, amt, type):
                    if type == 'magick':
                        amt -= 1
                        return (amt, 0)
                    else:
                        return (amt, 0)
                p = partial(rts_atk)
                app.ent_dict[id].attack_effects.append(p)
                def undo(id, func):
                    app.ent_dict[id].attack_effects.remove(func)
                    return None
                un = partial(undo, id, p)
                n = 'Read_the_Stars' + str(app.effects_counter)
                app.ent_dict[id].effects_dict[n] = Effect(name = 'Read_the_Stars', undo_func = un, duration = 1, level = self.get_abl('psyche'))
                root.after(1555, lambda name = u : cleanup_read(name))
                root.after(1666, lambda ids = ids : read_loop(ids))
        read_loop(ids)
                
                

    # give Bard ONLY a psy based adj melee atk
    def psi_blades(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Psi_Blades' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if dist(self.loc, s) == 1]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_psi_blades(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Psi Blades', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_psi_blades(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_psi_blades(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if not isinstance(app.ent_dict[id], Bard):
            return
        if id not in app.spell_target_ents().keys():
            return
        self.init_cast_anims()
#         effect1 = mixer.Sound('Sound_Effects/scrye.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.cantrip_used = True
        app.vis_dict['Psi_Blades'] = Vis(name = 'Psi_Blades', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Psi_Blades'].img, tags = 'Psi_Blades')
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Psi Blades', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Psi Blades', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        def psi_slash(event = None, obj = None):
            if obj.attack_used == True:
                return
            app.unbind_nonarrows()
            root.bind('<q>', lambda e, obj = obj : cancel_attack(obj = obj))
            sqrs = [s for s in app.coords if dist(s,obj.loc) == 1]
            app.animate_squares(sqrs)
            app.depop_context(event = None)
            root.bind('<a>', lambda e, sqrs = sqrs, sqr = grid_pos, obj = obj : check_hit(event = e, sqrs = sqrs, sqr = sqr, obj = obj)) 
            b = tk.Button(app.context_menu, text = 'Confirm Psi Slash', wraplength = 190, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs, sqr = grid_pos, obj = obj : check_hit(event = e, sqrs = sqrs, sqr = sqr, obj = obj))
            b.pack(side = 'top')
            app.context_buttons.append(b)
            # INNER-INNER FUNCS, context must be passed to obj receiving this action
            def check_hit(event = None, sqrs = None, sqr = None, obj = None):
                if sqr not in sqrs:
                    return
                id = app.grid[sqr[0]][sqr[1]]
                if id == '' or id == 'block':
                    return
                if id not in app.action_target_ents().keys():
                    return
                obj.attack_used = True
#                 obj.init_attack_anims()
#                 effect1 = mixer.Sound('Sound_Effects/hook_attack.ogg')
#                 effect1.set_volume(1)
#                 sound_effects.play(effect1, 0)
                app.depop_context(event = None)
                app.unbind_all()
                app.cleanup_squares()
                visloc = app.ent_dict[id].loc[:]
                app.vis_dict['Psi_Slash'] = Vis(name = 'Psi_Slash', loc = visloc)
                app.canvas.create_image(visloc[0]*100+50-app.moved_right, visloc[1]*100+50-app.moved_down, image = app.vis_dict['Psi_Slash'].img, tags = 'Psi_Slash')
                my_psyche = obj.get_abl('psyche')
                target_agl = app.ent_dict[id].get_abl('agl')
                if to_hit(my_psyche, target_agl) == True:
                    target_end = app.ent_dict[id].get_abl('end')
                    d = damage(my_psyche, target_end)
                    pre = app.ent_dict[id].spirit
                    lock(apply_damage, obj, app.ent_dict[id], -d, 'slashing', 'Psi Slash')
                    post = app.ent_dict[id].spirit
                    d = pre - post
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+74, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+75, text = 'Hit! ' + str(d) + ' spirit', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    if app.ent_dict[id].spirit <= 0:
                        app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+89, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                        app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+90, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                        name = 'Dethlok'+str(app.death_count)
                        app.death_count += 1
                        app.dethloks[name] = tk.IntVar(0)
                        root.after(2666, lambda e = None, obj = obj : cancel_attack(e, obj))
                        root.after(2999, lambda id = id, name = name : app.kill(id, name))
                        app.wait_variable(app.dethloks[name])
                    else:
                        root.after(2666, lambda e = None, obj = obj : cancel_attack(event = e, obj = obj))
                else:
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+49, app.ent_dict[id].loc[1]*100-app.moved_down+89, text = 'Miss!', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
                    app.canvas.create_text(app.ent_dict[id].loc[0]*100-app.moved_right+50, app.ent_dict[id].loc[1]*100-app.moved_down+90, text = 'Miss!', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
                    root.after(2666, lambda e = None, obj = obj : cancel_attack(event = e, obj = obj))
            # INNER INNER FUNC
            def cancel_attack(event = None, obj = None):
                obj.init_normal_anims() # to init attack anims, provide them for each possible unit that can gain hook_attack
                app.rebind_all()
                app.canvas.delete('text')
                try:
                    del app.vis_dict['Psi_Slash']
                    app.canvas.delete('Psi_Slash')
                except: pass
                app.depop_context(event = None)
                app.cleanup_squares()
            # END INNER-INNER FUNCS
        # ADD ACTION TO TARGET
        p = partial(psi_slash, obj = app.ent_dict[id])
        def add_psi_slash(actions = None, func = None):
            actions['Psi Slash'] = func
            return actions
        p2 = partial(add_psi_slash, func = p)
        app.ent_dict[id].action_effects.append(p2)
        def un(i, func):
            app.ent_dict[i].action_effects.remove(func)
            return None
        p = partial(un, id, p2)
        n = 'Psi_Slash' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Psi_Slash', undo_func = p, duration = 3, level = self.get_abl('psyche'))
        root.after(2666, lambda  name = "Psi_Blades" : self.cleanup_spell(name = name))
        
    def foul_familiar(self, event = None):
        names = [v.name for k,v in app.ent_dict.items() if v.owner == self.owner]
        if 'Familiar_Imp' in names or 'Familiar_Homonculus' in names or 'Familiar_Pseudodragon' in names:
            return
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Foul_Familiar' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 2]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_foul_familiar(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Location', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_foul_familiar(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
    
    def do_foul_familiar(self, event = None, sqr = None, sqrs = None):
        if sqr not in sqrs:
            return
        loc = app.grid[sqr[0]][sqr[1]]
        if loc != '':
            return
#         self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/foul_familiar.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.cantrip_used = True
        app.vis_dict['Foul_Familiar'] = Vis(name = 'Foul_Familiar', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Foul_Familiar'].img, tags = 'Foul_Familiar')
        # summon familiar based on witch
        num = self.summon_ids
        self.summon_ids += 1
        if self.owner == 'p1':
            prefix = 'a'
        else:
            prefix = 'b'
        id = prefix + str(num)
        if self.name == 'Agnes_Sampson':
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Familiar_Imp.png'))
            app.ent_dict[id] = Familiar_Imp(name = 'Familiar_Imp', img = img, loc = sqr[:], owner = self.owner, number = id)
            app.grid[sqr[0]][sqr[1]] = id
        elif self.name == 'Fakir_Ali':
            img = ImageTk.PhotoImage(Image.open('summon_imgs/Familiar_Homonculus.png'))
            app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = img, tags = id)
            app.ent_dict[id] = Familiar_Homonculus(name = 'Familiar_Homonculus', img = img, loc = sqr[:], owner = self.owner, number = id)
            app.grid[sqr[0]][sqr[1]] = id
        
        root.after(666, lambda  name = 'Foul_Familiar' : self.cleanup_spell(name = name))
    
    # create 'tomb' in current location, tomb is summon entity with no movement or attacks that doesnt count towards summon cap, teleport self to new location, only 1 tomb can exist at a time
    def entomb(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Entomb' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 7 and app.grid[s[0]][s[1]] == '']
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_entomb(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Location', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_entomb(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_entomb(self, event, sqr, sqrs):
        global selected
        names = [v.name for k,v in app.ent_dict.items() if v.name == 'Tomb' and v.owner == self.owner]
        if names != []:
            return
        if sqr not in sqrs:
            return
        loc = app.grid[sqr[0]][sqr[1]]
        if loc != '':
            return
#         self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/strength_through_wounding.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        self.magick -= self.arcane_dict['Entomb'][1]
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        selected = [self.tags]
        app.canvas.delete(self.tags)
        oldloc = self.loc[:]
        # ENTOMB VIS
        app.vis_dict['Entomb'] = Vis(name = 'Entomb', loc = oldloc[:])
        app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = app.vis_dict['Entomb'].img, tags = 'Entomb')
        # CREATE TOMB ENTITY
        if self.owner == 'p1':
            prefix = 'a'
        else:
            prefix = 'b'
        id = prefix + str(self.summon_ids)
        self.summon_ids += 1
        img = ImageTk.PhotoImage(Image.open('summon_imgs/Tomb.png'))
        app.ent_dict[id] = Tomb(name = 'Tomb', img = img, loc = oldloc[:], owner = self.owner, number = id)
        app.grid[oldloc[0]][oldloc[1]] = id
        newloc = sqr[:]
#         app.vis_dict['Entomb'] = Vis(name = 'Entomb', loc = oldloc)
#         app.canvas.create_image(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+50-app.moved_down, image = app.vis_dict['Entomb'].img, tags = 'Entomb')
        app.canvas.create_text(oldloc[0]*100+50-app.moved_right, oldloc[1]*100+75-app.moved_down, text = 'Entomb', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        root.after(2666, lambda loc = newloc : self.finish_entomb(loc))
        
    def finish_entomb(self, loc):
        del app.vis_dict['Entomb']
        app.canvas.delete('Entomb')
        app.vis_dict['Entomb'] = Vis(name = 'Entomb', loc = loc[:])
        app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict['Entomb'].img, tags = 'Entomb')
        selected = []
        self.loc = loc[:]
        app.grid[loc[0]][loc[1]] = self.tags
        root.after(1333, lambda x = loc[0]*100+50-app.moved_right, y = loc[1]*100+50-app.moved_down, i = self.img, t = self.tags : app.canvas.create_image(x, y, image = i, tags = t))
#         app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = self.img, tags = self.tags)
        root.after(2999, lambda  name = 'Entomb' : self.cleanup_spell(name = name))
        

    # deal damage equal to spirit lost
    def vengeance(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Vengeance' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_vengeance(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Vengeance', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_vengeance(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
    
    def do_vengeance(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
#         self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/vengeance.ogg')
        effect1.set_volume(.08)
        sound_effects.play(effect1, 0)
        self.magick -= self.arcane_dict['Vengeance'][1]
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        d = self.base_spirit - self.spirit
#         app.ent_dict[id].set_attr('spirit', -d)
        lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Vengeance')
        app.vis_dict['Vengeance'] = Vis(name = 'Vengeance', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Vengeance'].img, tags = 'Vengeance')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = 'Vengeance\n'+str(d)+' Spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        if app.ent_dict[id].spirit <= 0:
            app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+100-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            name = 'dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(2333, lambda id = id, n = name : app.kill(id, n))
            root.wait_variable(app.dethloks[name])
            self.cleanup_spell(name = 'Vengeance')
        else:
            root.after(2666, lambda  name = 'Vengeance' : self.cleanup_spell(name = name))
      
    # lose 3 spirit, all summons within range 2 may act again?
    def hatred(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Hatred' : self.cleanup_spell(name = name))
#         coords = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        root.bind('<a>', self.do_hatred)
        b = tk.Button(app.context_menu, text = 'Confirm Hatred', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = self.do_hatred)
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_hatred(self, event = None):
#         self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/hatred.ogg')
        effect1.set_volume(.07)
        sound_effects.play(effect1, 0)
        self.magick -= self.arcane_dict['Hatred'][1]
        app.unbind_all()
        app.depop_context(event = None)
        self.arcane_used = True
        ents = [k for k,v in app.ent_dict.items() if v.owner == 'p1' and v.type != 'large']
        for id in ents:
            sqr = app.ent_dict[id].loc[:]
            uniq_name = 'Hatred'+str(app.effects_counter)
            app.effects_counter += 1
            app.ent_dict[id].attack_used = False
            def clean_hatred(name):
                del app.vis_dict[name]
                app.canvas.delete(name)
            root.after(3666, lambda name = uniq_name : clean_hatred(name))
            app.vis_dict[uniq_name] = Vis(name = 'Hatred', loc = sqr)
            app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[uniq_name].img, tags = 'Hatred')
            app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = 'Hatred', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')

        root.after(3666, lambda  name = 'Hatred' : self.cleanup_spell(name = name))
        
        
    # target gets -2 psyche for 4 turns (does not stack), takes psyche versus end damage on cast
    def torment(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Torment' : self.cleanup_spell(name = name))
#         coords = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_torment(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Torment', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_torment(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
    
    def do_torment(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
#         self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/torment.ogg')
        effect1.set_volume(.07)
        sound_effects.play(effect1, 0)
        self.magick -= self.arcane_dict['Torment'][1]
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        my_psyche = self.get_abl('psyche')
        tar_end = app.ent_dict[id].get_abl('end')
        d = damage(my_psyche, tar_end)
#         app.ent_dict[id].set_attr('spirit', -d)
        lock(apply_damage, self, app.ent_dict[id], -d, 'magick', 'Torment')
        app.vis_dict['Torment'] = Vis(name = 'Torment', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Torment'].img, tags = 'Torment')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = 'Torment\n'+str(d)+' Spirit', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        if app.ent_dict[id].spirit <= 0:
            app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+100-app.moved_down, text = app.ent_dict[id].name.replace('_',' ')+' Killed...', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
            name = 'dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(2666, lambda id = id, n = name : app.kill(id, n))
            root.wait_variable(app.dethloks[name])
            self.cleanup_spell(name = 'Torment')
        else:
            effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
            if 'Torment' not in effs:
                def torment_effect(stat):
                    stat -= 2
                    if stat < 1:
                        return 1
                    else:
                        return stat
                f = torment_effect
                app.ent_dict[id].psyche_effects.append(f)
                def un(i):
                    app.ent_dict[i].psyche_effects.remove(torment_effect)
                    return None
                p = partial(un, id)
                n = 'Torment' + str(app.effects_counter)
                app.ent_dict[id].effects_dict[n] = Effect(name = 'Torment', undo_func = p, duration = 7, level = self.get_abl('psyche'))
            root.after(2999, lambda  name = 'Torment' : self.cleanup_spell(name = name))

    # destroy a summon you own to deal dmg to adj ents
    def pain(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Pain' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_pain(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Pain', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_pain(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_pain(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if app.ent_dict[id].owner != self.owner or not isinstance(app.ent_dict[id], Summon):
            return
        effect1 = mixer.Sound('Sound_Effects/pain.ogg')
        effect1.set_volume(.07)
        sound_effects.play(effect1, 0)
        self.magick -= self.arcane_dict['Pain'][1]
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Pain'] = Vis(name = 'Pain', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Pain'].img, tags = 'Pain')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = 'Pain', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        root.after(1777, lambda  name = 'Pain' : self.cleanup_spell(name = name))
#         self.init_cast_anims()
        # kill here and handle death triggers, then make explosion
        loc = app.ent_dict[id].loc[:]
        name = 'dethlok'+str(app.death_count)
        app.death_count += 1
        app.dethloks[name] = tk.IntVar(0)
        root.after(666, lambda id = id, name = name : app.kill(id, name))
        root.wait_variable(app.dethloks[name])
        root.after(1666, lambda loc = loc : self.continue_pain(loc))
        
    def continue_pain(self, loc):
        sqr = loc[:]
        adj_sqrs = [s for s in app.coords if dist(sqr, s) == 1 and app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
        adj_ents = [app.grid[s[0]][s[1]] for s in adj_sqrs]
        all_targets = adj_ents
        for id in all_targets:
            n = 'Pain' + str(app.effects_counter) # not an effect, just need unique int
            app.effects_counter += 1 # that is why this is incr manually here, no Effect init
            loc = app.ent_dict[id].loc[:]
            app.vis_dict[n] = Vis(name = 'Pain_Explode', loc = loc)
            def cleanup_vis(name):
                del app.vis_dict[name]
                app.canvas.delete(name)
            root.after(3666, lambda n = n : cleanup_vis(n))
            rand_start_anim = randrange(1,7)
            for i in range(rand_start_anim):
                app.vis_dict[n].rotate_image()
            app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = n)
            app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down-30, text = 'Pain', justify ='center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
            # Damage
            my_psyche = self.get_abl('psyche')
            tar_dodge = app.ent_dict[id].get_abl('dodge')
            d = damage(my_psyche, tar_dodge)
            d += 9
            app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = str(d)+' Spirit', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
#             app.ent_dict[id].set_attr('spirit', -d)
            lock(apply_damage, self, app.ent_dict[id], -d, 'explosive', 'Pain')
            if app.ent_dict[id].spirit <= 0:
                app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+100-app.moved_down, text = app.ent_dict[id].name.replace('_',' ') + '\nKilled...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                name = 'dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(2333, lambda id = id, n = name : app.kill(id, n))
                root.wait_variable(app.dethloks[name])
        root.after(2999, lambda  name = 'Pain' : self.cleanup_spell(name = name))
        
        
    # change to -3 random attr, affect every adj recursively
    def plague(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Plague' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 5]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_plague(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Plague', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_plague(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_plague(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        # target must be Summon, Witch, (future type...)
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
#         if not isinstance(app.ent_dict[id], (Witch, Summon)):
#              return
        # PLAGUE CANNOT BE STACKED WITH OTHER PLAGUES
        if 'Plague' in app.ent_dict[id].effects_dict.keys():
            return
        self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/plague.ogg')
        effect1.set_volume(2)
        sound_effects.play(effect1, 0)
        self.magick -= self.arcane_dict['Plague'][1]
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Plague', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Plague', font = ('Andale Mono', 14), fill = 'limegreen', tags = 'text')
        visited = [app.ent_dict[id].number]
        ents = [app.ent_dict[id].number]
        def cleanup_vis(name):
            del app.vis_dict[name]
            app.canvas.delete(name)
        def plague_loop(ents, visited):
            if ents == []:
                self.cleanup_spell(name = 'Plague')
            else:
                id = ents[0]
                ents = ents[1:]
                loc = app.ent_dict[id].loc
                u = 'Plague'+str(app.effects_counter)
                app.effects_counter += 1
                app.vis_dict[u] = Vis(name = 'Plague', loc = loc)
                app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[u].img, tags = u)
                def plague_effect(stat):
                    stat -= 3
                    if stat < 1:
                        return 1
                    else:
                        return stat
                f = plague_effect
                any = choice(range(1,6))
                if any == 1:
                    app.ent_dict[id].str_effects.append(f)
                    ef_type = 'str'
                elif any == 2:
                    app.ent_dict[id].end_effects.append(f)
                    ef_type = 'end'
                elif any == 3:
                    app.ent_dict[id].agl_effects.append(f)
                    ef_type = 'agl'
                elif any == 4:
                    app.ent_dict[id].dodge_effects.append(f)
                    ef_type = 'dodge'
                elif any == 5:
                    app.ent_dict[id].psyche_effects.append(f)
                    ef_type = 'psyche'
                def un(i, ef_type):
                    if ef_type == 'str':
                        app.ent_dict[i].str_effects.remove(plague_effect)
                    elif ef_type == 'end':
                        app.ent_dict[i].end_effects.remove(plague_effect)
                    elif ef_type == 'agl':
                        app.ent_dict[i].agl_effects.remove(plague_effect)
                    elif ef_type == 'dodge':
                        app.ent_dict[i].dodge_effects.remove(plague_effect)
                    elif ef_type == 'psyche':
                        app.ent_dict[i].psyche_effects.remove(plague_effect)
                    return None
                p_undo = partial(un, id, ef_type)
                n = 'Plague' + str(app.effects_counter)
                app.ent_dict[id].effects_dict['Plague'] = Effect(name = 'Plague', undo_func = p_undo, duration = 6, level = self.get_abl('psyche'))
                # get adj
                adj = [k for k,v in app.ent_dict.items() if dist(v.loc, loc) == 1 and k not in visited and v.type != 'large']
                adj = [id for id in adj if 'Plague' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]]
                ents += adj
                visited += adj
                root.after(2222, lambda u = u : cleanup_vis(u))
                root.after(1999, lambda ents = ents, v = visited : plague_loop(ents, v))
        plague_loop(ents, visited)

            
    # PSIONIC PUSH
    def psionic_push(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Psionic_Push' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_psionic_push(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Psionic Push', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_psionic_push(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_psionic_push(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        # target must be Summon, Witch, (future type...)
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if not isinstance(app.ent_dict[id], (Witch, Summon)):
             return
        # cannot target large
        if app.ent_dict[id].type == 'large' or app.ent_dict[id].immovable == True:
            return
        app.depop_context(event = None)
        app.cleanup_squares()
        loc = app.ent_dict[id].loc[:]
        ps = []
        ps.append(loc)
        for c in app.coords:
            if c[0] == (loc[0] + 1) and c[1] == loc[1] and app.grid[c[0]][c[1]] == '':
                ps.append(c)
                n = [loc[0]+2, loc[1]]
                if n in app.coords:
                    if n[0] == (loc[0] + 2) and n[1] == loc[1] and app.grid[n[0]][n[1]] == '':
                        ps.append(n)
            elif c[0] == (loc[0] - 1) and c[1] == loc[1] and app.grid[c[0]][c[1]] == '':
                n = [loc[0]-2, loc[1]]
                ps.append(c)
                if n in app.coords:
                    if n[0] == (loc[0] - 2) and n[1] == loc[1] and app.grid[n[0]][n[1]] == '':
                        ps.append(n)
            elif c[0] == loc[0] and c[1] == (loc[1] + 1) and app.grid[c[0]][c[1]] == '':
                n = [loc[0], loc[1]+2]
                ps.append(c)
                if n in app.coords:
                    if n[0] == loc[0] and n[1] == (loc[1] + 2) and app.grid[n[0]][n[1]] == '':
                        ps.append(n)
            elif c[0] == loc[0] and c[1] == (loc[1] - 1) and app.grid[c[0]][c[1]] == '':
                n = [loc[0], loc[1]-2]
                ps.append(c)
                if n in app.coords:
                    if n[0] == loc[0] and n[1] == (loc[1] - 2) and app.grid[n[0]][n[1]] == '':
                        ps.append(n)
        app.animate_squares(ps)
        root.bind('<a>', lambda e, id = id, s = grid_pos, sqrs = ps : self.choose_psi_square(event = e, id = id, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Square to Push', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, id = id, s = grid_pos, sqrs = ps : self.choose_psi_square(e, id, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
            
    def choose_psi_square(self, event, id, sqr, sqrs):
        global selected, selected_vis
        if sqr not in sqrs:
            return
        self.cantrip_used = True
        self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/psionic_push.ogg')
        effect1.set_volume(.3)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        start_loc = app.ent_dict[id].loc[:]
        app.vis_dict['Psionic_Push'] = Vis(name = 'Psionic_Push', loc = start_loc)
        app.canvas.create_image(start_loc[0]*100+50-app.moved_right, start_loc[1]*100+50-app.moved_down, image = app.vis_dict['Psionic_Push'].img, tags = 'Psionic_Push')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Psionic Push', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Psionic Push', font = ('Andale Mono', 14), fill = 'lightgreen', tags = 'text')
        x = start_loc[0]*100+50-app.moved_right
        y = start_loc[1]*100+50-app.moved_down
        endx = sqr[0]*100+50-app.moved_right
        endy = sqr[1]*100+50-app.moved_down
        if start_loc != sqr:
            selected = [id]
            selected_vis = ['Psionic_Push']
        def psi_move_loop(vis, ent, x, y, endx, endy, sqr, start_sqr):
            if x % 25 == 0 and y % 25 == 0:
                app.vis_dict[vis].rotate_image()
                app.ent_dict[ent].rotate_image()
                app.canvas.delete(vis)
                app.canvas.delete(ent)
                app.canvas.create_image(x, y, image = app.vis_dict[vis].img, tags = 'Psionic_Push')
                app.canvas.create_image(x, y, image = app.ent_dict[ent].img, tags = app.ent_dict[ent].tags)
            if x > endx:
                x -= 10
                app.canvas.move(vis, -10, 0)
                app.canvas.move(ent, -10, 0)
            elif x < endx: 
                x += 10
                app.canvas.move(vis, 10, 0)
                app.canvas.move(ent, 10, 0)
            if y > endy: 
                y -= 10
                app.canvas.move(vis, 0, -10)
                app.canvas.move(ent, 0, -10)
            elif y < endy: 
                y += 10
                app.canvas.move(vis, 0, 10)
                app.canvas.move(ent, 0, 10)
            app.canvas.tag_raise(vis)
            try: app.canvas.tag_lower(app.ent_dict[ent].tags, 'large')
            except: pass
            app.canvas.tag_lower(app.ent_dict[ent].tags, 'maptop')
            if x == endx and y == endy:
                root.after(666, lambda e = ent, s = sqr, ss = start_sqr : self.finish_psionic_push(tar = e, end_loc = s, start_loc = ss))
            else:
                root.after(50, lambda p = 'Psionic_Push', id = id, x = x, y = y, endx = endx, endy = endy, s = sqr, s2 = start_sqr : psi_move_loop(p, id, x, y, endx, endy, s, s2))
        if sqr == start_loc:
            self.finish_psionic_push(id, sqr, start_loc)
        else:
            psi_move_loop('Psionic_Push', id, x, y, endx, endy, sqr, start_loc)
        
    def finish_psionic_push(self, tar, end_loc, start_loc):
        global selected, selected_vis
        app.ent_dict[tar].loc = end_loc[:]
        app.grid[start_loc[0]][start_loc[1]] = ''
        app.grid[end_loc[0]][end_loc[1]] = tar
        adj_sqrs = [c for c in app.coords if dist(c, end_loc) == 1]
        adj_ents = [k for k,v in app.ent_dict.items() if dist(v.loc, end_loc) == 1 and v.type != 'large']
        if adj_ents != []:
            # hit tar and adj_ents
            adj_ents.append(tar)
            tar_str = app.ent_dict[tar].get_abl('str')
            for ent in adj_ents:
                if app.ent_dict[ent].save_check('agl', mod = 1) == False:
                    d = damage(tar_str, app.ent_dict[ent].get_abl('end'))
                    lock(apply_damage, app.ent_dict[tar], app.ent_dict[ent], -d, 'crushing', 'Psionic Push')
#                     post = app.ent_dict[ent].spirit
#                     d = pre - post
#                     app.canvas.create_text(app.ent_dict[ent].loc[0]*100+49-app.moved_right, app.ent_dict[ent].loc[1]*100+74-app.moved_down, text = str(d) + ' spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
#                     app.canvas.create_text(app.ent_dict[ent].loc[0]*100+50-app.moved_right, app.ent_dict[ent].loc[1]*100+75-app.moved_down, text = str(d) + ' spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
#                     if app.ent_dict[ent].spirit <= 0:
#                         app.canvas.create_text(app.ent_dict[ent].loc[0]*100+49-app.moved_right, app.ent_dict[ent].loc[1]*100+94-app.moved_down, text = app.ent_dict[ent].name.replace('_',' ') + ' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
#                         app.canvas.create_text(app.ent_dict[ent].loc[0]*100+50-app.moved_right, app.ent_dict[ent].loc[1]*100+95-app.moved_down, text = app.ent_dict[ent].name.replace('_',' ') + ' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
#                         name = 'Dethlok'+str(app.death_count)
#                         app.death_count += 1
#                         app.dethloks[name] = tk.IntVar(0)
                    def cleanup_psi():
                        try:
                            app.canvas.delete('text')
                            app.canvas.delete('Psionic_Push')
                            del app.vis_dict['Psionic_Push']
                        except:
                            pass
                    root.after(1999, cleanup_psi)
#                         root.after(2666, lambda id = ent, name = name : app.kill(id, name))
#                         app.wait_variable(app.dethloks[name])
                else:# Miss
                    app.canvas.create_text(app.ent_dict[ent].loc[0]*100+49-app.moved_right, app.ent_dict[ent].loc[1]*100+69-app.moved_down, text = 'Agility\nSave',justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
                    app.canvas.create_text(app.ent_dict[ent].loc[0]*100+50-app.moved_right, app.ent_dict[ent].loc[1]*100+70-app.moved_down, text = 'Agility\nSave',justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
            root.after(1666, lambda s = 'Psionic_Push' : self.cleanup_spell(name = s))
        else:
            root.after(666, lambda s = 'Psionic_Push' : self.cleanup_spell(name = s))
        
    # deal dmg to targ and w/i r3 of targ, decr dmg with distance, main targ gets death_trigger pass this death_trigger EOT 1 spirit
    def pestilence(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 5]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_pestilence(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Area For Pestilence', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_pestilence(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_pestilence(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
#         id = app.grid[sqr[0]][sqr[1]]
#         if id == '' or id == 'block':
#             return
        loc = sqr[:]
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        effect1 = mixer.Sound('Sound_Effects/pestilence.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        self.arcane_used = True
        self.magick -= self.arcane_dict['Pestilence'][1]
        self.init_cast_anims()
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Pestilence', justify ='center', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Pestilence', justify ='center', font = ('Andale Mono', 16), fill = 'gray75', tags = 'text')
        # do all vis now, staggered
        def pestil_vis_loop(index):
            for sqr in [s for s in app.coords if dist(s, loc) == index]:
                n = 'Pestilence' + str(app.effects_counter) # not an effect, just need unique int
                app.effects_counter += 1 # that is why this is incr manually here, no Effect init
                app.vis_dict[n] = Vis(name = 'Pestilence', loc = sqr[:])
                def cleanup_vis(name):
                    del app.vis_dict[name]
                    app.canvas.delete(name)
                app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = n)
                root.after(2666, lambda n = n : cleanup_vis(n))
            if index == 3:
                ents = [k for k,v in app.all_ents().items() if dist(v.loc, loc) <= 3]
                self.continue_pestilence(ents, loc)
            else:
                root.after(666, lambda j = index+1 : pestil_vis_loop(j))
        pestil_vis_loop(0)
        
    # dmg ents based on dist from sqr (main target)
    def continue_pestilence(self, ents, sqr):
        def pestil_loop(ents):
            if ents == []:
                self.cleanup_spell(name = 'Pestilence')
            else:
                id = ents[0]
                ents = ents[1:]
                loc = app.ent_dict[id].loc[:]
                app.focus_square(loc)
                # DAMAGE
                my_psyche = self.get_abl('psyche')
                tar_end = app.ent_dict[id].get_abl('end')
                tar_psyche = app.ent_dict[id].get_abl('psyche')
                d = damage(my_psyche, (tar_psyche+tar_end)//2)
                d -= dist(loc, sqr)*2
                if d < 1:
                    d = 1
#                 pre = app.ent_dict[id].spirit
                lock(apply_damage, self, app.ent_dict[id], -d, 'poison', 'Pestilence')
#                 post = app.ent_dict[id].spirit
#                 d = pre - post
#                 app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+74-app.moved_down, text = str(d)+' spirit', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
#                 app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = str(d)+' spirit', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
# #                 app.ent_dict[id].set_attr('spirit', -d)
#                 if app.ent_dict[id].spirit <= 0:
#                     app.canvas.create_text(loc[0]*100+49-app.moved_right, loc[1]*100+94-app.moved_down, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
#                     app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+95-app.moved_down, text = app.ent_dict[id].name.replace('_',' ') + ' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
#                     name = 'Dethlok'+str(app.death_count)
#                     app.death_count += 1
#                     app.dethloks[name] = tk.IntVar(0)
#                     root.after(1666, lambda id = id, name = name : app.kill(id, name))
#                     app.wait_variable(app.dethloks[name])
                if id in app.all_ents().keys() and app.ent_dict[id].loc == sqr and 'Pestilence' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
                    def pestil_death_trigger(obj = None):
                        adj = [k for k,v in app.all_ents().items() if dist(v.loc, obj.loc) == 1 and 'Pestilence' not in [j.name for i,j in v.effects_dict.items()]]
                        for id,s in [(k,v.loc) for k,v in app.all_ents().items() if k in adj]:
                            n = 'Pestilence' + str(app.effects_counter) # not an effect, just need unique int
                            app.effects_counter += 1 # that is why this is incr manually here, no Effect init
                            app.vis_dict[n] = Vis(name = 'Pestilence', loc = s[:])
                            app.canvas.create_text(s[0]*100+49-app.moved_right, s[1]*100+74-app.moved_down, text = 'Pestilence', justify ='center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                            app.canvas.create_text(s[0]*100+50-app.moved_right, s[1]*100+75-app.moved_down, text = 'Pestilence', justify ='center', font = ('Andale Mono', 13), fill = 'gray88', tags = 'text')
                            def cleanup_vis(name):
                                del app.vis_dict[name]
                                app.canvas.delete(name)
                                app.canvas.delete('text')
                            app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = n)
                            root.after(2222, lambda n = n : cleanup_vis(n))
                            p_inner = partial(pestil_death_trigger, obj = app.ent_dict[id])
                            app.ent_dict[id].death_triggers.append(p_inner)
                            # INNER effect given by death trigger of original target
                            def un():
                                return None
                            def take_1(tar, lockname = None):
                                app.get_focus(tar)
                                lock(apply_damage, self, app.ent_dict[tar], -1, 'poison', 'Pestilence')
                                root.after(1333, lambda ln = lockname : app.dethloks[ln].set(1))
                            eot = partial(take_1, id)
                            n = 'Pestilence' + str(app.effects_counter)
                            app.ent_dict[id].effects_dict[n] = Effect(name = 'Pestilence', eot_func = eot, undo_func = un, duration = 20, level = self.get_abl('psyche'))
                    # END inner effect passed on death trigger
                    p_death = partial(pestil_death_trigger, app.ent_dict[id])
                    app.ent_dict[id].death_triggers.append(p_death)
                    def un():
                        return None
                    # EOT FUNC
                    def take_1(tar, lockname = None):
                        app.get_focus(tar)
                        lock(apply_damage, self, app.ent_dict[tar], -1, 'poison', 'Pestilence')
                        root.after(1333, lambda ln = lockname : app.dethloks[ln].set(1))
                    eot = partial(take_1, id)
                    n = 'Pestilence' + str(app.effects_counter)
                    app.ent_dict[id].effects_dict[n] = Effect(name = 'Pestilence', eot_func = eot, undo_func = un, duration = 20, level = self.get_abl('psyche'))
                root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                root.after(1666, lambda ents = ents : pestil_loop(ents))
        app.canvas.delete('text')
        pestil_loop(ents)
    
    # CURSE OF ORIAX
    def curse_of_oriax(self, event = None):
        # Any target is inflicted with 'curse', while cursed takes 2 spirit damage at end of every owner's turn and minus 1 to every stat (not spirit, magick, movement)
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_curse_of_oriax(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Curse of Oriax', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_curse_of_oriax(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_curse_of_oriax(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Curse_of_Oriax' in effs:
            return
        if not isinstance(app.ent_dict[id], (Witch, Summon)):
             return
        self.magick -= self.arcane_dict['Curse_of_Oriax'][1]
        effect1 = mixer.Sound('Sound_Effects/curse_of_oriax.ogg')
        effect1.set_volume(1.4)
        sound_effects.play(effect1, 0)
        self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Curse_of_Oriax'] = Vis(name = 'Curse_of_Oriax', loc = sqr)
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Curse_of_Oriax'].img, tags = 'Curse_of_Oriax')
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+99-app.moved_down, text = 'Curse\nof\nOriax', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+100-app.moved_down, text = 'Curse\nof\nOriax', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        # DO Curse_of_Oriax EFFECTS
        def curse_of_oriax_effect(stat):
            stat -= 1
            if stat < 1:
                return 1
            else:
                return stat
        f = curse_of_oriax_effect
        app.ent_dict[id].str_effects.append(f)
        app.ent_dict[id].end_effects.append(f)
        app.ent_dict[id].agl_effects.append(f)
        app.ent_dict[id].dodge_effects.append(f)
        app.ent_dict[id].psyche_effects.append(f)
        def un(i):
            app.ent_dict[i].str_effects.remove(curse_of_oriax_effect)
            app.ent_dict[i].end_effects.remove(curse_of_oriax_effect)
            app.ent_dict[i].agl_effects.remove(curse_of_oriax_effect)
            app.ent_dict[i].dodge_effects.remove(curse_of_oriax_effect)
            app.ent_dict[i].psyche_effects.remove(curse_of_oriax_effect)
            return None
        p = partial(un, id)
        # EOT FUNC
        def take_2(tar, lockname = None):
            app.get_focus(tar)
            lock(apply_damage, self, app.ent_dict[tar], -2, 'magick', 'Curse of Oriax')
            root.after(1999, lambda ln = lockname : app.dethloks[ln].set(1))
        eot = partial(take_2, id)
        n = 'Curse_of_Oriax' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Curse_of_Oriax', eot_func = eot, undo_func = p, duration = 6, level = self.get_abl('psyche'))
        root.after(3666, lambda  name = 'Curse_of_Oriax' : self.cleanup_spell(name = name))
        
        
    def molecular_subversion(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 3]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_molecular_subversion(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Molecular Subversion', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_molecular_subversion(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_molecular_subversion(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Molecular_Subversion' in effs:
            return
        self.magick -= self.arcane_dict['Molecular_Subversion'][1]
#         effect1 = mixer.Sound('Sound_Effects/gravity.ogg')
#         effect1.set_volume(.9)
#         sound_effects.play(effect1, 0)
        self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Molecular_Subversion'] = Vis(name = 'Molecular_Subversion', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Molecular_Subversion'].img, tags = 'Molecular_Subversion')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Molecular Subversion', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Molecular Subversion', justify = 'center', font = ('Andale Mono', 14), fill = 'olivedrab2', tags = 'text')
        # change to remove resists / add acid explsv wkns
        def molsub_resist_effect(rs):
            return []
        app.ent_dict[id].resist_effects.append(molsub_resist_effect)
        def molsub_wkns_effect(ws):
            return ws + ['acid', 'explosive']
        app.ent_dict[id].weak_effects.append(molsub_wkns_effect)
        def un(i):
            app.ent_dict[i].resist_effects.remove(molsub_resist_effect)
            app.ent_dict[i].weak_effects.remove(molsub_wkns_effect)
            return None
        p = partial(un, id)
        n = 'Molecular_Subversion' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Molecular_Subversion', undo_func = p, duration = 9, level = self.get_abl('psyche'))
        root.after(3666, lambda  name = 'Molecular_Subversion' : self.cleanup_spell(name = name))
        
        
    def plutonian_cloak(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_plutonian_cloak(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Plutonian Cloak', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_gravity(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_plutonian_cloak(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Plutonian_Cloak' in effs:
            return
        self.magick -= self.arcane_dict['Plutonian_Cloak'][1]
#         effect1 = mixer.Sound('Sound_Effects/gravity.ogg')
#         effect1.set_volume(.9)
#         sound_effects.play(effect1, 0)
        self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Plutonian_Cloak'] = Vis(name = 'Plutonian_Cloak', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Plutonian_Cloak'].img, tags = 'Plutonian_Cloak')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Plutonian Cloak', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Plutonian Cloak', justify = 'center', font = ('Andale Mono', 14), fill = 'orchid1', tags = 'text')
        def plut_cloak_effect(atkr, dfndr, amt, type):
            if type == 'slashing' or type == 'crushing' or type == 'piercing':
                if 'Plutonian_Invis' in [v.name for k,v in dfndr.effects_dict.items()]:
                    return (amt, 0)
                else:
                    def plu_invis(types):
                        return types+['invis']
                    p = partial(plu_invis)
                    dfndr.type_effects.append(p)
                    def undo(id, func):
                        app.ent_dict[id].type_effects.remove(func)
                    u = partial(undo, dfndr.number, p)
                    n = 'Plutonian_Cloak' + str(app.effects_counter)
                    dfndr.effects_dict[n] = Effect(name = 'Plutonian_Invis', undo_func = u, duration = 1, level = self.get_abl('psyche'))
                    return (amt, 0)
            elif type == 'magick':
                if 'Plutonian_Psyshield' in [v.name for k,v in dfndr.effects_dict.items()]:
                    return (amt, 0)
                else:
                    def plu_psysh(types):
                        return types+['psyshield']
                    p = partial(plu_psysh)
                    dfndr.type_effects.append(p)
                    def undo(id, func):
                        app.ent_dict[id].type_effects.remove(func)
                    u = partial(undo, dfndr.number, p)
                    n = 'Plutonian_Cloak' + str(app.effects_counter)
                    dfndr.effects_dict[n] = Effect(name = 'Plutonian_Psyshield', undo_func = u, duration = 1, level = self.get_abl('psyche'))
                    return (amt, 0)
            else:
                return (amt, 0)
        app.ent_dict[id].defense_effects.append(plut_cloak_effect)
        def undo(id):
            app.ent_dict[id].defense_effects.remove(plut_cloak_effect)
        p = partial(undo, id)
        n = 'Plutonian_Cloak' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Plutonian_Cloak', undo_func = p, duration = 9, level = self.get_abl('psyche'))
        root.after(2666, lambda  name = 'Plutonian_Cloak' : self.cleanup_spell(name = name))
        
        
    def hidden_from_the_stars(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 2]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_hfts(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Hidden From the Stars', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_hfts(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_hfts(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Hidden_From_the_Stars' in effs:
            return
        self.magick -= self.arcane_dict['Hidden_From_the_Stars'][1]
#         effect1 = mixer.Sound('Sound_Effects/.ogg')
#         effect1.set_volume(.9)
#         sound_effects.play(effect1, 0)
        self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Hidden_From_the_Stars'] = Vis(name = 'Hidden_From_the_Stars', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Hidden_From_the_Stars'].img, tags = 'Hidden_From_the_Stars')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Hidden From the Stars', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Hidden From the Stars', justify = 'center', font = ('Andale Mono', 14), fill = 'turquoise', tags = 'text')
        def hfts_dodge_effect(stat):
            return stat+2
        def hfts_end_effect(stat):
            return stat+2
        app.ent_dict[id].dodge_effects.append(hfts_dodge_effect)
        app.ent_dict[id].end_effects.append(hfts_end_effect)
        def hfts_effect(types, id = None):
            return types+['psyshield']
        p = partial(hfts_effect, id = id)
        app.ent_dict[id].type_effects.append(p)
        def un(i, func):
            app.ent_dict[i].dodge_effects.remove(hfts_dodge_effect)
            app.ent_dict[i].end_effects.remove(hfts_end_effect)
            app.end_dict[i].type_effects.remove(func)
            return None
        u = partial(un, id,)
        n = 'Hfts' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Hidden_From_the_Stars', undo_func = u, duration = 7, level = self.get_abl('psyche'))
        root.after(2111, lambda  name = 'Hidden_From_the_Stars' : self.cleanup_spell(name = name))
        
        
    def cosmic_sight(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Cosmic_Sight' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 3]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_cosmic_sight(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Cosmic Sight', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_cosmic_sight(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_cosmic_sight(self, event, sqr, sqrs):
        self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/meditate.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.cleanup_squares()
        app.depop_context(event = None)
        self.cantrip_used = True
        id = self.name
        sqr = self.loc[:]
        app.vis_dict['Cosmic_Sight'] = Vis(name = 'Cosmic_Sight', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Cosmic_Sight'].img, tags = 'Cosmic_Sight')
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Cosmic Sight', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Cosmic Sight', justify = 'center', font = ('Andale Mono', 13), fill = 'turquoise', tags = 'text')
        # all enemy w/i range 3 make psy save(-1) or lose psyshield
        ids = [k for k,v in app.all_ents().items() if v.loc in sqrs and v.owner != self.owner and 'psyshield' in v.get_types()]
        if ids == []:
            root.after(1666, lambda  name = 'Cosmic_Sight' : self.cleanup_spell(name = name))
        else:
            root.after(1666, lambda ids = ids : self.continue_cosmic_sight(ids))
    
    def continue_cosmic_sight(self, ids):
        def cosmic_loop(ids):
            if ids == []:
                root.after(1666, lambda  name = 'Cosmic_Sight' : self.cleanup_spell(name = name))
            else:
                id = ids[0]
                ids = ids[1:]
                app.get_focus(id)
                if app.ent_dict[id].save_check('psyche',mod = -1) == False:
                    un = 'Cosmic_Sight'+str(app.effects_counter)
                    app.effects_counter += 1
                    def clean_cosmic_sight(name):
                        app.canvas.delete(name)
                        del app.vis_dict[name]
                        app.canvas.delete('text')
                    sqr = app.ent_dict[id].loc[:]
                    app.vis_dict[un] = Vis(name = 'Cosmic_Sight', loc = sqr[:])
                    app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = un)
                    app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Psyshield Removed', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Psyshield Removed', justify = 'center', font = ('Andale Mono', 13), fill = 'turquoise', tags = 'text')
                    def cosmic_effect(types, id = None):
                        while 'psyshield' in app.ent_dict[id].types:
                            app.ent_dict[id].types.remove('psyshield')
                        return types
                    p = partial(cosmic_effect, id = id)
                    app.ent_dict[id].type_effects.append(p)
                    def undo(id, func):
                        app.ent_dict[id].type_effects.remove(func)
                    u = partial(undo, id, p)
                    n = 'Cosmic_Sight' + str(app.effects_counter)
                    app.ent_dict[id].effects_dict[n] = Effect(name = 'Cosmic_Sight', undo_func = u, duration = 5, level = self.get_abl('psyche'))
                    root.after(1555, lambda un = un : clean_cosmic_sight(un))
                    root.after(1666, lambda ids = ids : cosmic_loop(ids))
                else:
                    # Save Successful
                    sqr = app.ent_dict[id].loc[:]
                    app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Psyche Save', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
                    app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Psyche Save', justify = 'center', font = ('Andale Mono', 13), fill = 'turquoise', tags = 'text')
                    root.after(1555, lambda t = 'text' : app.canvas.delete(t))
                    root.after(1666, lambda ids = ids : cosmic_loop(ids))
        cosmic_loop(ids)
        
        
    def demonic_sight(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 2]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_demonic_sight(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Demonic Sight', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_demonic_sight(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_demonic_sight(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        if 'Demonic_Sight' in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
            return
        self.magick -= self.arcane_dict['Demonic_Sight'][1]
#         effect1 = mixer.Sound('Sound_Effects/gravity.ogg')
#         effect1.set_volume(.9)
#         sound_effects.play(effect1, 0)
        self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Demonic_Sight'] = Vis(name = 'Demonic_Sight', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Demonic_Sight'].img, tags = 'Demonic_Sight')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Demonic Sight', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Demonic Sight', justify = 'center', font = ('Andale Mono', 14), fill = 'olivedrab2', tags = 'text')
        def demonic_invis(types):
            while 'invis' in types:
                types.remove('invis')
            return types
        p = partial(demonic_invis)
        app.ent_dict[id].type_effects.append(p)
        def undo(id, func):
            app.ent_dict[id].type_effects.remove(func)
        u = partial(undo, id, p)
        n = 'Demonic_Sight' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Demonic_Sight', undo_func = u, duration = 6, level = self.get_abl('psyche'))
        
        
        root.after(2666, lambda  name = 'Demonic_Sight' : self.cleanup_spell(name = name))
        
        
    def gravity(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if 1 <= dist(self.loc, s) <= 9]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_gravity(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Gravity', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_gravity(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_gravity(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Gravity' in effs:
            return
        if app.ent_dict[id].immovable == True:
            return
        self.magick -= self.arcane_dict['Gravity'][1]
        effect1 = mixer.Sound('Sound_Effects/gravity.ogg')
        effect1.set_volume(.9)
        sound_effects.play(effect1, 0)
        self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Gravity'] = Vis(name = 'Gravity', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Gravity'].img, tags = 'Gravity')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Gravity', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Gravity', justify = 'center', font = ('Andale Mono', 14), fill = 'olivedrab2', tags = 'text')
        # DO gravity EFFECTS
        def gravity_agil_effect(stat):
            stat -= 1
            if stat < 1:
                return 1
            else:
                return stat
        def gravity_dodge_effect(stat):
            stat -= 2
            if stat < 1:
                return 1
            else:
                return stat
        app.ent_dict[id].agl_effects.append(gravity_agil_effect)
        app.ent_dict[id].dodge_effects.append(gravity_dodge_effect)
        def gravity_move(move_range):
            if move_range < 2:
                return move_range
            else:
                return 2
        app.ent_dict[id].move_effects.append(gravity_move)
        def un(i):
            app.ent_dict[i].agl_effects.remove(gravity_agil_effect)
            app.ent_dict[i].dodge_effects.remove(gravity_dodge_effect)
            app.ent_dict[i].move_effects.remove(gravity_move)
            return None
        p = partial(un, id)
        n = 'Gravity' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Gravity', undo_func = p, duration = 4, level = self.get_abl('psyche'))
        root.after(3666, lambda  name = 'Gravity' : self.cleanup_spell(name = name))
        
    # change to: must choose ranged tar, rang2-6, lightning strike main tar, still do adj fire
    def beleths_command(self, event = None):
        app.depop_context(event = None)
        sqrs = [c for c in app.coords if 2 <= dist(self.loc, c) <= 7]
        app.animate_squares(sqrs)
        root.bind('<q>', self.cleanup_spell)
        root.bind('<a>', lambda e, sqr = grid_pos, sqrs = sqrs : self.do_beleths_command(sqr = sqr, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = "Beleth's Command Target", wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda sqr = grid_pos, sqrs = sqrs : self.do_beleths_command(sqr = sqr, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_beleths_command(self, event = None, sqr = None, sqrs = None):
        global selected_vis
        if self.move_used == True:
            return
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if id not in app.spell_target_ents().keys():
            return
        self.magick -= self.arcane_dict["Beleth's_Command"][1]
        effect1 = mixer.Sound('Sound_Effects/beleths_command.ogg')
        effect1.set_volume(.7)
        sound_effects.play(effect1, 0)
        self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        self.move_used = True
        app.focus_square(self.loc)
        app.vis_dict["Beleth's_Command"] = Vis(name = "Beleth's_Command", loc = self.loc)
        app.canvas.create_image(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+50-app.moved_down, image = app.vis_dict["Beleth's_Command"].img, tags = "Beleth's_Command")
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+9-app.moved_down, text = "Beleth's Command", justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+10-app.moved_down, text = "Beleth's Command", justify = 'center', font = ('Andale Mono', 14), fill = 'olivedrab', tags = 'text')
        # LIGHTNING VIS
        selected_vis.append("Beleth's_Lightning")
        loc = app.ent_dict[id].loc[:]
        def cleanup_lightning():
            app.canvas.delete("Beleth's_Lightning")
            del app.vis_dict["Beleth's_Lightning"]
        app.vis_dict["Beleth's_Lightning"] = Vis(name = "Beleth's_Lightning", loc = loc)
        app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict["Beleth's_Lightning"].img, tags = "Beleth's_Lightning")
        x2 = loc[0]*100+50-app.moved_right
        y2 = loc[1]*100+50-app.moved_down
        def beleths_lightning(timeout):
            if timeout > 0:
                app.vis_dict["Beleth's_Lightning"].rotate_image()
                app.canvas.delete("Beleth's_Lightning")
                app.canvas.create_image(x2, y2, image = app.vis_dict["Beleth's_Lightning"].img, tags = "Beleth's_Lightning")
                timeout -= 1
                root.after(60, lambda t = timeout : beleths_lightning(t))
            else:
                cleanup_lightning()
        app.get_focus(id)
        beleths_lightning(8)
        # BURN AT STAKE LOOP
        selected_vis = ["Beleth's_Command"]
        def cleanup_beleths_fire():
            app.canvas.delete("Beleth's_Command")
            del app.vis_dict["Beleth's_Command"]
        x = self.loc[0]*100+50-app.moved_right
        y = self.loc[1]*100+50-app.moved_down
        def beleths_loop(timeout):
            if timeout > 0:
                app.vis_dict["Beleth's_Command"].rotate_image()
                app.canvas.delete("Beleth's_Command")
                app.canvas.create_image(x, y, image = app.vis_dict["Beleth's_Command"].img, tags = "Beleth's_Command")
                app.canvas.tag_lower("Beleth's_Command", (self.tags))
                timeout -= 1
                root.after(99, lambda t = timeout : beleths_loop(t))
            else:
                cleanup_beleths_fire()
        beleths_loop(30)
        # LIGHTNING EFFECTS ranged target, dmg, stun chance, -1 psy -1 end
        my_psyche = self.get_abl('psyche')
        tar_psyche = app.ent_dict[id].get_abl('psyche')
        tar_end = app.ent_dict[id].get_abl('end')
        amt = (tar_psyche + tar_end) // 2
        d1 = damage(my_psyche, amt)
        s1 = app.ent_dict[id].loc[:]
        lock(apply_damage, self, app.ent_dict[id], -d1, 'elec', 'Lightning Strike')
        # if tar still alive, stun chance and -1 efcts
        if id in app.all_ents().keys() and app.ent_dict[id].save_check('str', mod = 0) == False and 'Paralyze' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]: # Fail Save
            app.canvas.create_text(s1[0]*100-app.moved_right+49, s1[1]*100-app.moved_down+94, text = 'Stun 1 turn...', justify = 'center', fill = 'black', font = ('Andale Mono', 13), tags = 'text')
            app.canvas.create_text(s1[0]*100-app.moved_right+50, s1[1]*100-app.moved_down+95, text = 'Stun 1 turn...', justify = 'center', fill = 'white', font = ('Andale Mono', 13), tags = 'text')
            if app.num_players == 2:
                def beleths_stun_effect(actions = None):
                    return {}
                p_stun = partial(beleths_stun_effect)
                app.ent_dict[id].action_effects.append(p_stun)
            else:
                def paralyze_ai(ents_list, id = None):
                    app.ent_dict[id].ai_end_turn(ents_list)
                f = partial(paralyze_ai, id = id)
                app.ent_dict[id].do_ai = f
            def un(i, func = None):
                if app.num_players == 2:
                    app.ent_dict[i].action_effects.remove(func)
                else:
                    p2 = partial(app.ent_dict[i].__class__.do_ai, app.ent_dict[i]) # PUT BACK AI ROUTINE
                    app.ent_dict[i].do_ai = p2
                return None
            if app.num_players == 2:
                p = partial(un, id, func = p_stun)
            else:
                p = partial(un, id)
            n = 'Paralyze' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Paralyze', undo_func = p, duration = 1, level = self.get_abl('psyche'))
            # -1 -1 to tar
            if "Beleth's_Command" not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
                def b_command_effect(stat):
                    stat -= 1
                    if stat < 1:
                        return 1
                    else:
                        return stat
                app.ent_dict[id].end_effects.append(b_command_effect)
                app.ent_dict[id].psyche_effects.append(b_command_effect)
                def un(i):
                    app.ent_dict[i].end_effects.remove(b_command_effect)
                    app.ent_dict[i].psyche_effects.remove(b_command_effect)
                    return None
                p = partial(un, id)
                n = "Beleth's_Command" + str(app.effects_counter)
                app.ent_dict[id].effects_dict[n] = Effect(name = "Beleth's_Command", undo_func = p, duration = 5, level = self.get_abl('psyche'))
        ents = [k for k,v in app.all_ents().items() if dist(v.loc, self.loc) == 1]
        root.after(2555, lambda t = 'text' : app.canvas.delete(t))
        root.after(2666, lambda ents = ents : self.finish_beleths(ents))
        
    def finish_beleths(self, ents):
        for e in ents:
            s = app.ent_dict[e].loc[:]
            app.focus_square(s)
#             app.canvas.delete('text')
            uniq_name = 'Immolate'+str(app.effects_counter)
            app.effects_counter += 1
            app.vis_dict[uniq_name] = Vis(name = 'Immolate', loc = s) # using Immolate animations
            app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[uniq_name].img, tags = "Beleth's_Command")
            lock(apply_damage, self, app.ent_dict[e], -9, 'fire', 'Witchfire')
            def clean_beleths_command(n):
                del app.vis_dict[n]
                app.canvas.delete(n)
            root.after(3666, lambda n = uniq_name : clean_beleths_command(n))
        # DO Beleth's Command EFFECTS ON CASTER
        effs = [v.name for k,v in self.effects_dict.items()]
        if "Beleth's_Command" not in effs:
            def beleths_command_effect(stat):
                stat += 1
                return stat
            f = beleths_command_effect
            self.end_effects.append(f)
            self.psyche_effects.append(f)
            def un(i):
                app.ent_dict[i].end_effects.remove(beleths_command_effect)
                app.ent_dict[i].psyche_effects.remove(beleths_command_effect)
                return None
            p = partial(un, self.number)
            self.effects_dict["Beleth's_Command"] = Effect(name = "Beleth's_Command", undo_func = p, duration = 5, level = self.get_abl('psyche'))
        root.after(3666, lambda  name = "Beleth's_Command" : self.cleanup_spell(name = name))
        
        
# FAKIR ALI SPELLS
        # Ali's spells center around Heat/Fire/Resistance/Mummification
    def meditate(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Meditate' : self.cleanup_spell(name = name))
        root.bind('<a>', self.do_meditate)
        b = tk.Button(app.context_menu, text = 'Confirm Meditate', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None : self.do_meditate(e))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_meditate(self, event):
#         self.init_cast_anims()
        effect1 = mixer.Sound('Sound_Effects/meditate.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        self.cantrip_used = True
        id = self.name
        sqr = self.loc[:]
        app.vis_dict['Meditate'] = Vis(name = 'Meditate', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Meditate'].img, tags = 'Meditate')
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Meditate', justify = 'center', font = ('Andale Mono', 13), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Meditate', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        # DO Meditate EFFECTS
        def meditate_effect(stat):
            stat += 2
            return stat
        f = meditate_effect
        app.ent_dict[id].psyche_effects.append(f)
############################################
        def meditate_move(move_range):
            return move_range + 2
        app.ent_dict[id].move_effects.append(meditate_move)
        def un(i):
            app.ent_dict[i].psyche_effects.remove(meditate_effect)
            app.ent_dict[i].move_effects.remove(meditate_move)
            return None
        p = partial(un, id)
        n = 'Meditate' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Meditate', undo_func = p, duration = 1, level = self.get_abl('psyche'))
        root.after(3666, lambda  name = 'Meditate' : self.cleanup_spell(name = name))
        
        
        
    def horrid_wilting(self, event = None):
        # make attack (psyche versus str) spirit damage, on any target within range 4 and all adjacent enemy units
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Horrid_Wilting' : self.cleanup_spell(name = name))
#         coords = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_horrid_wilting(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Horrid Wilting', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_horrid_wilting(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_horrid_wilting(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        if app.grid[sqr[0]][sqr[1]] == '' or app.grid[sqr[0]][sqr[1]] == 'block':
            return
        effect1 = mixer.Sound('Sound_Effects/horrid_wilting.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        self.arcane_used = True
        self.magick -= self.arcane_dict['Horrid_Wilting'][1]
        adj_sqrs = [s for s in app.coords if dist(sqr, s) == 1 and app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
        adj_ents = [app.grid[s[0]][s[1]] for s in adj_sqrs] #if app.ent_dict[app.grid[s[0]][s[1]]].owner != self.owner] 
        all_targets = adj_ents + [app.grid[sqr[0]][sqr[1]]]
        for id in all_targets:
            n = 'Horrid_Wilting' + str(app.effects_counter) # not an effect, just need unique int
            app.effects_counter += 1 # that is why this is incr manually here, no Effect init
            loc = app.ent_dict[id].loc[:]
            app.vis_dict[n] = Vis(name = 'Horrid_Wilting', loc = loc)
            def cleanup_vis(name):
                del app.vis_dict[name]
                app.canvas.delete(name)
            root.after(3666, lambda n = n : cleanup_vis(n))
            rand_start_anim = randrange(1,7)
            for i in range(rand_start_anim):
                app.vis_dict[n].rotate_image()
            app.canvas.create_image(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down, image = app.vis_dict[n].img, tags = n)
            app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+50-app.moved_down-30, text = 'Horrid Wilting', justify ='center', font = ('Andale Mono', 13), fill = 'wheat2', tags = 'text')
            # DAMAGE
            my_psyche = self.get_abl('psyche')
            tar_end = app.ent_dict[id].get_abl('end')
            d = damage(my_psyche, tar_end)
            app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+75-app.moved_down, text = str(d)+' Spirit', justify ='center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
#             app.ent_dict[id].set_attr('spirit', -d)
            lock(apply_damage, self, app.ent_dict[id], -d, 'acid', 'Horrid Wilting')
            if app.ent_dict[id].spirit <= 0:
                app.canvas.create_text(loc[0]*100+50-app.moved_right, loc[1]*100+100-app.moved_down, text = app.ent_dict[id].name.replace('_',' ') + '\nKilled...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                name = 'Dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(2666, lambda id = id, name = name : app.kill(id, name))
                app.wait_variable(app.dethloks[name])
        root.after(3666, lambda  name = 'Horrid_Wilting' : self.cleanup_spell(name = name))
        
        
    def boiling_blood(self, event = None):
        app.depop_context(event = None)
#         root.unbind('<a>')
#         root.unbind('<q>')
        app.unbind_nonarrows()
        root.bind('<q>', lambda name = 'Boiling_Blood' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if dist(self.loc, s) == 1]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_boiling_blood(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Boiling Blood', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_boiling_blood(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_boiling_blood(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        if not isinstance(app.ent_dict[id], Warrior):
            return
        effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Boiling_Blood' in effs:
            return
        effect1 = mixer.Sound('Sound_Effects/boiling_blood.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        self.cantrip_used = True
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        app.vis_dict['Boiling_Blood'] = Vis(name = 'Boiling_Blood', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Boiling_Blood'].img, tags = 'Boiling_Blood')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = 'Boiling\nBlood', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        # DO Boiling_Blood EFFECTS
        def boiling_blood_str_effect(stat):
            stat += 5
            return stat
        def boiling_blood_end_effect(stat):
            return 1
        app.ent_dict[id].str_effects.append(boiling_blood_str_effect)
        app.ent_dict[id].end_effects.append(boiling_blood_end_effect)
        def un(i):
            app.ent_dict[i].str_effects.remove(boiling_blood_str_effect)
            app.ent_dict[i].end_effects.remove(boiling_blood_end_effect)
            return None
        p = partial(un, id)
        # EOT FUNC
        def take_1(tar, lockname = None):
            app.get_focus(tar)
            lock(apply_damage, self, app.ent_dict[tar], -1, 'fire', 'Boiling Blood')
            root.after(1333, lambda ln = lockname : app.dethloks[ln].set(1))
        eot = partial(take_1, id)
        n = 'Boiling_Blood' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Boiling_Blood', eot_func = eot, undo_func = p, duration = 4, level = self.get_abl('psyche'))
        root.after(3666, lambda  name = 'Boiling_Blood' : self.cleanup_spell(name = name))
        
    
        
    def dark_sun(self, event = None):
        # Any one 'shadow' summon within range 2 gets an extra attack if they have already attacked once this turn
        app.depop_context(event = None)
#         root.unbind('<a>')
#         root.unbind('<q>')
        app.unbind_nonarrows()
        root.bind('<q>', lambda name = 'Dark_Sun' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 2]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_dark_sun(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Dark Sun', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_dark_sun(e, s, sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_dark_sun(self, event, sqr, sqrs):
        global selected_vis
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if not isinstance(app.ent_dict[id], Shadow):
            return
        effect1 = mixer.Sound('Sound_Effects/dark_sun.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        self.cantrip_used = True
        app.depop_context(event = None)
        app.unbind_all()
        app.cleanup_squares()
        app.ent_dict[id].attack_used = False
        app.vis_dict['Dark_Sun'] = Vis(name = 'Dark_Sun', loc = sqr[:]) #[sqr[0],sqr[1]-1])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Dark_Sun'].img, tags = 'Dark_Sun')
        app.canvas.create_text(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+50-app.moved_down+40, text = 'Dark Sun', justify ='center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        selected_vis = ['Dark_Sun']
        def dark_sun_loop(starty, endy, x):
            if starty > endy:
                app.vis_dict['Dark_Sun'].rotate_image()
                app.canvas.delete('Dark_Sun')
                app.canvas.create_image(x, starty, image = app.vis_dict['Dark_Sun'].img, tags = 'Dark_Sun')
                starty -= 10
                app.canvas.move('Dark_Sun', 0, -10)
                app.canvas.tag_raise('Dark_Sun')
            if starty == endy:
                root.after(1333, lambda  name = 'Dark_Sun' : self.cleanup_spell(name = name))
            else:
                root.after(299, lambda sy = starty, ey = endy, x = x : dark_sun_loop(sy, ey, x))
                
        locy = sqr[1]*100+70-app.moved_down
        locx = sqr[0]*100+50-app.moved_right
        dark_sun_loop(locy, locy-90, locx)
        
        
    # change mummify, too good with leap still make useful combo, disable leap
    def mummify(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 3]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_mummify(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Mummify', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_mummify(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_mummify(self, event, sqr, sqrs):
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        if id == '' or id == 'block':
            return
        effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Mummify' in effs:
            return
        effect1 = mixer.Sound('Sound_Effects/mummify.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        self.magick -= self.arcane_dict['Mummify'][1]
#         self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Mummify'] = Vis(name = 'Mummify', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Mummify'].img, tags = 'Mummify')
        app.canvas.create_text(self.loc[0]*100+49-app.moved_right, self.loc[1]*100+94-app.moved_down, text = 'Mummify', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, self.loc[1]*100+95-app.moved_down, text = 'Mummify', justify = 'center', font = ('Andale Mono', 14), fill = 'darkgoldenrod', tags = 'text')
        # DO Mummify EFFECTS
        def mummify_effect(stat):
            stat += 4
            return stat
        f = mummify_effect
        app.ent_dict[id].end_effects.append(f)
        def mummy_moves(move_range):
            if move_range < 2:
                return move_range
            else:
                return 1
        app.ent_dict[id].move_effects.append(mummy_moves)
        def un(i):
            app.ent_dict[i].end_effects.remove(mummify_effect)
            app.ent_dict[i].move_effects.remove(mummy_moves)
            return None
        p = partial(un, id)
        n = 'Mummify' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Mummify', undo_func = p, duration = 7, level = self.get_abl('psyche'))
        root.after(3666, lambda  name = 'Mummify' : self.cleanup_spell(name = name))
        
        
        
    def immolate(self, event = None):
        # high psyche damage one target
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
#         coords = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 2]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_immolate(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Immolate', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_immolate(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_immolate(self, event, sqr, sqrs):
        if app.current_pos() == '' or app.current_pos() == 'block':
            return
        if sqr not in sqrs:
            return
        effect1 = mixer.Sound('Sound_Effects/immolate.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
        id = app.grid[sqr[0]][sqr[1]]
        self.magick -= self.arcane_dict['Immolate'][1]
#         self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Immolate'] = Vis(name = 'Immolate', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Immolate'].img, tags = 'Immolate')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+25-app.moved_down, text = 'Immolate', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        my_psyche = self.get_abl('psyche')
        tar_psyche = app.ent_dict[id].get_abl('psyche')
        d = damage(my_psyche, tar_psyche)
        d += 5
#         app.ent_dict[id].set_attr('spirit', -d)
        lock(apply_damage, self, app.ent_dict[id], -d, 'fire', 'Immolate')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+80-app.moved_down, text = str(d)+' Spirit', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
        if app.ent_dict[id].spirit <= 0:
            app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+95-app.moved_down, text = app.ent_dict[id].name.replace('_', ' ')+' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
            name = 'Dethlok'+str(app.death_count)
            app.death_count += 1
            app.dethloks[name] = tk.IntVar(0)
            root.after(2999, lambda id = id, name = name : app.kill(id, name))
            app.wait_variable(app.dethloks[name])
        root.after(3111, lambda  name = 'Immolate' : self.cleanup_spell(name = name))
        
        
    def disintegrate(self, event = None):
        # target gets -1 to all stats every turn (cumulative) and takes 1 spirit per turn
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, s = grid_pos, sqrs = sqrs : self.do_disintegrate(event = e, sqr = s, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Choose Target For Disintegrate', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, s = grid_pos, sqrs = sqrs : self.do_disintegrate(e, s, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_disintegrate(self, event, sqr, sqrs):
        if app.current_pos() == '' or app.current_pos() == 'block':
            return
        if sqr not in sqrs:
            return
        id = app.grid[sqr[0]][sqr[1]]
        effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
        if 'Disintegrate' in effs:
            return
        self.magick -= self.arcane_dict['Disintegrate'][1]
        effect1 = mixer.Sound('Sound_Effects/disintegrate.ogg')
        effect1.set_volume(1)
        sound_effects.play(effect1, 0)
#         self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        app.vis_dict['Disintegrate'] = Vis(name = 'Disintegrate', loc = sqr[:])
        app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Disintegrate'].img, tags = 'Disintegrate')
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+74-app.moved_down, text = 'Disintegrate', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = 'Disintegrate', justify = 'center', font = ('Andale Mono', 14), fill = 'antiquewhite', tags = 'text')
        # DO Disintegrate EFFECTS
        def disintegrate_effect(stat):
            stat -= 1
            if stat < 1:
                return 1
            else:
                return stat
        f = disintegrate_effect
        rnd = choice(range(5))
        if rnd == 0:
            app.ent_dict[id].str_effects.append(f)
        elif rnd == 1:
            app.ent_dict[id].end_effects.append(f)
        elif rnd == 2:
            app.ent_dict[id].agl_effects.append(f)
        elif rnd == 3:
            app.ent_dict[id].dodge_effects.append(f)
        elif rnd == 4:
            app.ent_dict[id].psyche_effects.append(f)
        def un(i, f):
            if f in app.ent_dict[i].str_effects:
                app.ent_dict[i].str_effects.remove(f)
            elif f in app.ent_dict[i].end_effects:
                app.ent_dict[i].end_effects.remove(f)
            elif f in app.ent_dict[i].agl_effects:
                app.ent_dict[i].agl_effects.remove(f)
            elif f in app.ent_dict[i].dodge_effects:
                app.ent_dict[i].dodge_effects.remove(f)
            elif f in app.ent_dict[i].psyche_effects:
                app.ent_dict[i].psyche_effects.remove(f)
            return None
        p = partial(un, id, f)
        # EOT FUNC
        def disint(tar, lockname = None):
            def disintegrate_effect(stat):
                stat -= 1
                if stat < 1:
                    return 1
                else:
                    return stat
            f = disintegrate_effect
            rnd = choice(range(5))
            if rnd == 0:
                app.ent_dict[tar].str_effects.append(f)
            elif rnd == 1:
                app.ent_dict[tar].end_effects.append(f)
            elif rnd == 2:
                app.ent_dict[tar].agl_effects.append(f)
            elif rnd == 3:
                app.ent_dict[tar].dodge_effects.append(f)
            elif rnd == 4:
                app.ent_dict[tar].psyche_effects.append(f)
            def un(prev_undo, i, f):
                prev_undo()
                if f in app.ent_dict[i].str_effects:
                    app.ent_dict[i].str_effects.remove(f)
                elif f in app.ent_dict[i].end_effects:
                    app.ent_dict[i].end_effects.remove(f)
                elif f in app.ent_dict[i].agl_effects:
                    app.ent_dict[i].agl_effects.remove(f)
                elif f in app.ent_dict[i].dodge_effects:
                    app.ent_dict[i].dodge_effects.remove(f)
                elif f in app.ent_dict[i].psyche_effects:
                    app.ent_dict[i].psyche_effects.remove(f)
                return None
            for k,v in app.ent_dict[tar].effects_dict.items():
                if v.name == 'Disintegrate':
                    key = k
            app.ent_dict[tar].effects_dict[k].undo = partial(un, app.ent_dict[tar].effects_dict[k].undo, tar, f)
            app.get_focus(tar)
            lock(apply_damage, self, app.ent_dict[tar], -1, 'acid', 'Disintegrate')
            root.after(1333, lambda ln = lockname : app.dethloks[ln].set(1))
        eot = partial(disint, id)
        n = 'Disintegrate' + str(app.effects_counter)
        app.ent_dict[id].effects_dict[n] = Effect(name = 'Disintegrate', eot_func = eot, undo_func = p, duration = 6, level = self.get_abl('psyche'))
        root.after(3111, lambda  name = 'Disintegrate' : self.cleanup_spell(name = name))
        
        
        
    # all friendly ents within range 3 get +1 all attrs and heals 1 spirit, all enemy ents get -1 all attrs and loses 1 spirit, lasts 3 turns, does not stack
    def command_of_osiris(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', self.cleanup_spell)
#         coords = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        sqrs = [s for s in app.coords if dist(self.loc, s) <= 4]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e, sqrs = sqrs : self.do_command_of_osiris(event = e, sqrs = sqrs))
        b = tk.Button(app.context_menu, text = 'Confirm Command of Osiris', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None, sqrs = sqrs : self.do_command_of_osiris(e, sqrs = sqrs))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_command_of_osiris(self, event, sqrs):
        self.magick -= self.arcane_dict['Command_of_Osiris'][1]
#         self.init_cast_anims()
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.arcane_used = True
        ents = [app.grid[s[0]][s[1]] for s in sqrs if app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
        friendly_ents = [e for e in ents if app.ent_dict[e].owner == self.owner]
        enemy_ents = [e for e in ents if app.ent_dict[e].owner != self.owner]
        # SUN VIS
        app.vis_dict['Osiris_Sun'] = Vis(name = 'Osiris_Sun', loc = [self.loc[0],self.loc[1]-4])
        app.canvas.create_image(self.loc[0]*100+50-app.moved_right, (self.loc[1]-4)*100+50-app.moved_down, image = app.vis_dict['Osiris_Sun'].img, tags = 'Command_of_Osiris')
        app.canvas.create_text(self.loc[0]*100+50-app.moved_right, (self.loc[1]-3)*100+95-app.moved_down, text = 'Command of Osiris', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        def cleanup_sun():
            del app.vis_dict['Osiris_Sun']
            app.canvas.delete('Osiris_Sun')
        root.after(3666, cleanup_sun)
        # FRIENDLY ENTS
        for id in friendly_ents:
            effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
            if 'Command_of_Osiris' in effs:
                continue
            sqr = app.ent_dict[id].loc[:]
            uniq_name = 'Command_of_Osiris' + str(app.effects_counter)
            app.effects_counter += 1
            app.vis_dict[uniq_name] = Vis(name = 'Command_of_Osiris', loc = sqr)
            app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[uniq_name].img, tags = 'Command_of_Osiris')
            app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = '+1 Stats\n+1 Spirit', justify = 'center', font = ('Andale Mono', 12), fill = 'white', tags = 'text')
            # CLEANUP UNIQUE VIS
            def cleanup_osiris(n):
                del app.vis_dict[n]
                app.canvas.delete(n)
            root.after(3666, lambda n = uniq_name : cleanup_osiris(n))
            # SPIRIT
            if app.ent_dict[id].spirit < app.ent_dict[id].base_spirit:
#                 app.ent_dict[id].set_attr('spirit', 1)
                apply_heal(self, app.ent_dict[id], 1)
            # DO Command of Osiris EFFECTS
            def osiris_effect(stat):
                stat += 1
                return stat
            app.ent_dict[id].str_effects.append(osiris_effect)
            app.ent_dict[id].end_effects.append(osiris_effect)
            def un(i):
                app.ent_dict[i].str_effects.remove(osiris_effect)
                app.ent_dict[i].end_effects.remove(osiris_effect)
                return None
            p = partial(un, id)
            n = 'Command_of_Osiris' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Command_of_Osiris', undo_func = p, duration = 9, level = self.get_abl('psyche'))
        #  ENEMY ENTS
        for id in enemy_ents:
            effs = [v.name for k,v in app.ent_dict[id].effects_dict.items()]
            if 'Command_of_Osiris' in effs:
                continue
            sqr = app.ent_dict[id].loc[:]
            uniq_name = 'Command_of_Osiris' + str(app.effects_counter)
            app.effects_counter += 1
            app.vis_dict[uniq_name] = Vis(name = 'Command_of_Osiris', loc = sqr)
            app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict[uniq_name].img, tags = 'Command_of_Osiris')
            app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+75-app.moved_down, text = '-1 Stats\n-1 Spirit', justify = 'center', font = ('Andale Mono', 12), fill = 'white', tags = 'text')
            # CLEANUP UNIQUE VIS
            def cleanup_osiris(n):
                del app.vis_dict[n]
                app.canvas.delete(n)
            root.after(3666, lambda n = uniq_name : cleanup_osiris(n))
            # SPIRIT
#             app.ent_dict[id].set_attr('spirit', -1)
            lock(apply_damage, self, app.ent_dict[id], -1, 'magick', 'Osiris')
            if app.ent_dict[id].spirit <= 0:
                app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+100-app.moved_down, text = app.ent_dict[id].name+' Killed...', justify = 'center', font = ('Andale Mono', 13), fill = 'white', tags = 'text')
                name = 'Dethlok'+str(app.death_count)
                app.death_count += 1
                app.dethloks[name] = tk.IntVar(0)
                root.after(2666, lambda id = id, name = name : app.kill(id, name))
                app.wait_variable(app.dethloks[name])
            # DO Command of Osiris EFFECTS
            def osiris_effect(stat):
                stat -= 1
                if stat < 1:
                    return 1
                else:
                    return stat
            app.ent_dict[id].str_effects.append(osiris_effect)
            app.ent_dict[id].end_effects.append(osiris_effect)
            def un(i):
                app.ent_dict[i].str_effects.remove(osiris_effect)
                app.ent_dict[i].end_effects.remove(osiris_effect)
                return None
            p = partial(un, id)
            n = 'Command_of_Osiris' + str(app.effects_counter)
            app.ent_dict[id].effects_dict[n] = Effect(name = 'Command_of_Osiris', undo_func = p, duration = 9, level = self.get_abl('psyche'))
        root.after(3666, lambda  name = 'Command_of_Osiris' : self.cleanup_spell(name = name))
        
# MORGAN SPELLS
        # Morgan's spells center around Nature/Earth/Weather/Illusion
        
    def fleet_of_paw(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Fleet_of_Paw' : self.cleanup_spell(name = name))
        root.bind('<a>', self.do_fleet_of_paw)
        b = tk.Button(app.context_menu, text = 'Confirm Fleet of Paw', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None : self.do_fleet_of_paw(e))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
        
    def do_fleet_of_paw(self, event):
#         self.init_cast_anims()
#         effect1 = mixer.Sound('Sound_Effects/meditate.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        self.cantrip_used = True
        id = self.name
        sqr = self.loc[:]
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Fleet of Paw', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Fleet of Paw', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
        def cleanup_fop(un):
            app.canvas.delete(un)
            del app.vis_dict[un]
            app.canvas.delete('text')
        def fop_loop(ents):
            if ents == []:
                self.cleanup_spell('Fleet_of_Paw')
            else:
                id = ents[0]
                ents = ents[1:]
                if 'Fleet_of_Paw' not in [v.name for k,v in app.ent_dict[id].effects_dict.items()]:
                    app.get_focus(id)
                    s = app.ent_dict[id].loc[:]
                    un = 'FOP' + str(app.effects_counter)
                    app.vis_dict['Fleet_of_Paw'] = Vis(name = 'Fleet_of_Paw', loc = s)
                    app.canvas.create_image(s[0]*100+50-app.moved_right, s[1]*100+50-app.moved_down, image = app.vis_dict[un].img, tags = un)
                    def fop_move(r):
                        return r + 1
                    p = partial(fop_move)
                    app.ent_dict[id].move_effects.append(p)
                    def un(id, f):
                        app.ent_dict[id].move_effects.remove(f)
                        return None
                    u = partial(un, id, p)
                    app.ent_dict[id].effects_dict[un] = Effect(name = 'Fleet_of_Paw', undo_func = u, duration = 1, level = self.get_abl('psyche'))
                    root.after(1555, lambda un = un : cleanup_fop(un))
                    root.after(1666, lambda ents = ents : fop_loop(ents))
                else:
                    fop_loop(ents)
        root.after(1555, lambda t = 'text' : app.canvas.delete(t))
        ents = [k for k,v in app.ent_dict.items() if v.owner == self.owner and isinstance(v, (Bard, Trickster, Shadow, Warrior, Plaguebearer))]
        root.after(1666, lambda ents = ents : fop_loop(ents))
                    
                    
    def hunting_hawk(self, event = None):
        app.depop_context(event = None)
        root.bind('<q>', lambda name = 'Hunting_Hawk' : self.cleanup_spell(name = name))
        sqrs = [s for s in app.coords if s == self.loc]
        app.animate_squares(sqrs)
        root.bind('<a>', lambda e : self.do_hunting_hawk(event = e))
        b = tk.Button(app.context_menu, text = 'Confirm Hunting Hawk', wraplength = 190, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda e = None : self.do_hunting_hawk(e))
        b.pack(side = 'top', pady = 2)
        app.context_buttons.append(b)
    
    def do_hunting_hawk(self, event = None):
        if 'Hunting_Hawk' in [v.name for k,v in app.ent_dict.items() if v.owner == self.owner]:
            return
#         self.init_cast_anims()
#         effect1 = mixer.Sound('Sound_Effects/hunting_hawk.ogg')
#         effect1.set_volume(1)
#         sound_effects.play(effect1, 0)
        app.unbind_all()
        app.depop_context(event = None)
        app.cleanup_squares()
        self.cantrip_used = True
        sqrs = [s for s in app.coords if app.grid[s[0]][s[1]] == '']
        sqr = choice(sqrs)
        app.focus_square(sqr)
        app.vis_dict['Summon'] = Vis(name = 'Summon', loc = sqr[:])
        def clean_summon():
            app.canvas.delete('Summon')
            del app.vis_dict['Summon']
        root.after(1555, clean_summon)
        app.canvas.create_text(sqr[0]*100+49-app.moved_right, sqr[1]*100+84-app.moved_down, text = 'Hunting Hawk', justify = 'center', font = ('Andale Mono', 14), fill = 'black', tags = 'text')
        app.canvas.create_text(sqr[0]*100+50-app.moved_right, sqr[1]*100+85-app.moved_down, text = 'Hunting Hawk', justify = 'center', font = ('Andale Mono', 14), fill = 'white', tags = 'text')
#         app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.vis_dict['Summon'].img, tags = 'Hunting_Hawk')
        num = self.summon_ids
        self.summon_ids += 1
        if self.owner == 'p1':
            prefix = 'a'
        else:
            prefix = 'b'
        id = prefix + str(num)
        img = ImageTk.PhotoImage(Image.open('summon_imgs/Hunting_Hawk.png'))
        app.ent_dict[id] = Hunting_Hawk(name = 'Hunting_Hawk', img = img, loc = sqr[:], owner = self.owner, number = id)
        app.grid[sqr[0]][sqr[1]] = id
        root.after(1666, lambda  name = 'Hunting_Hawk' : self.cleanup_spell(name = name))
    
    
    
    def entangle():
        pass
        
    def enchant(self, event = None):
            # any summon within range 4 has attrs (str, agl, end, dodge, psyche) set to 5 until 3 opp turns have passed, prevents further modification while active
        print('enchant')
        
    def wild_hunt(self, event = None):
            # Creates 3 summons within range 2 of caster or up to 3 if not enough squares available, first is Boar (stats 3,3,3,2,2,4,0) movement range 2 attack any adjacent, second is wolf (2,3,2,4,2,3,0) movement range 3 attack any adjacent, third is hawk (2,4,2,4,3,2,0) movement range 4 not impeded by other units/obstacles attack any adjacent
        print('wild_hunt')
        
    def ceridwens_command(self, event = None):
            # Command rules apply, caster cannot move, all squares within range 2 of caster become 'water' (impassable terrain) any ents currently occupying these squares are moved to a random square 'at edge' (closest available square to edge of water squares or first unoccupied square if all 'edge' squares are occupied), at end of turn caster heals 4 spirit, lasts until caster has 3 turns end (healing happens first)
        print('ceridwens_command')
        
    def natures_wrath(self, event = None):
            # Choose a square within range 5, all ents within range 2 of square must 'to hit' their inverted agl versus dodge at the end of every caster's turn, those that 'hit' suffer 3 spirit damage, lasts 3 caster's turns (effect happens 'before' end turn, effects happen 3 times)
        print('natures_wrath')
        
    def counterspell(self, event = None):
            # Choose a spell effect 'in play', make 'to hit' psyche versus effect's owner's psyche, on success cancel all effects from the spell (call its cleanup function) and effect's owner takes magick damage psyche versus psyche
        print('counterspell')
        
    
    
class VerticalScrolledFrame(tk.Frame): 
    '''
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    '''
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, relief = 'raised', troughcolor = 'black', highlightbackground = 'black', width = 13)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg = 'black',
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)
        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window = interior, anchor = 'nw')
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.ent_dict = {}
        self.sqr_dict = {}
        self.vis_dict = {}
        self.image_holder = []
        self.global_effects_dict = {}
        self.active_player = 'p1'
        self.num_players = 1
        self.moved_right = 0
        self.moved_down = 0
        self.context_buttons = []
        self.help_buttons = []
        self.dethloks = {}
        self.death_count = 0
        self.cycle_q = []
        self.enemy_cycle_q = []
        self.current_ent = ''
        # list to hold entity that is being animated as 'attacking'
        self.attacking = [] # is this still used?
        self.effects_counter = 0 # used for uniquely naming Effects with the same prefix/name
        self.p1_witch = ''
        self.p2_witch = ''
        self.two_player_map_num = 0
        self.turn_counter = 0
        self.info = {'Summon':'Summon 1 wolf per turn', 
        'Move':'Move along an unobstructed path', 
        'Spell':'Cast 1 cantrip and 1 arcane spell per turn', 
        'Pestilence':'Psyche vs (psyche+endurance)/2 dmg to a target, each unit within range 3 takes same dmg minus distance from target. Main target gets effect that does 1 poison dmg at end of turn. When a unit with pestilence effect dies, all adjacent units get pestilence effect if they do not possess it already. Effect lasts 20 turns at level of caster psyche.', 
        'Plague':'Any unit and each unit connected by occupied adjacent sqrs (counting units without pestilence effect) gets -3 to a random ability. Lasts 6 turns at level of caster psyche', 
        'Gravity':'A unit gets move range reduced to maximum of 2, -1 agility and -2 dodge. Lasts 4 turns at level of caster psyche.', 
        "Beleth's Command":'Caster cannot use move action before or after casting this turn. A non-adjacent unit is struck by lightning, taking psyche vs (psyche+endurance)/2 magick dmg. Upon failing a strength save(-1) the unit cannot make any actions (unless it is granted new ones) for its next turn. That unit then gains an effect of -1 psyche and -1 endurance for 5 turns at level of caster psyche. Then, all adjacent units to the caster take 9 magick dmg. The caster gains +1 psyche +1 endurance effect if not already possessed, lasting 5 turns.', 
        'Curse of Oriax':'A unit gets -1 to each ability and takes 2 magick dmg at end of turn. Lasts 6 turns at level of caster psyche.', 
        'Scrye':'A wolf gets +2 agility +2 psyche for the remainder of this turn.', 
        'Psionic Push':'A unit is pushed to any location (including its current) within range 2 as long as the path is unobstructed. After push, if there are any adjacent units then each plus original target make agility save(+1). A failed save means the unit takes a melee attack from the pushed unit using strength(of pushed unit) vs endurance(of unit receiving attack) (the pushed unit attacks itself upon a failed save after ending a push adjacent to other units, ending the push on a location with no adjacent units results in no attacks).', 
        'Energize':'A summon who has already used a move, flying move or mist move action may move again this turn.', 
        'Boiling Blood':'Target Warrior gets +5 strength and endurance reduced to 1 for 4 turns at level of caster psyche', 
        'Dark Sun':'Target Shadow may use an action again if it already used an action this turn.', 
        'Meditate':'Caster gets +2 psyche and increase move range by 2 until end of turn.', 
        'Command of Osiris':'All friendly units within range 3 of caster are healed 1 spirit and get an effect, if they do not have it already, that grants +1 strength +1 endurance. All enemy units within range 3 of caster take 1 magick damage and get an effect, if they do not have it already, that gives -1 strength -1 endurance. Lasts 9 turns at the level of caster psyche', 
        'Disintegrate':'A unit gets an effect which causes -1 to a random ability at the end of its owner turn. The unit also takes 1 magick damage. Lasts 6 turns at level of caster psyche.', 
        'Horrid Wilting':'Target and each adjacent unit each take magick damage from caster, psyche vs endurance',
        'Mummify':'Target gets effect which reduces movement to maximum of 1 and also grants +4 endurance. Lasts 7 turns at level of caster psyche.', 
        'Immolate':'Target takes magick damage from caster, (psyche vs psyche)+5 ', 
        'Hatred':'All summons may use another action if they have already used an action this turn.', 
        'Vengeance':'Target takes damage equal to spirit lost by caster (current spirit minus max spirit).', 
        'Torment':'Target takes magick damage from caster, psyche vs endurance, and gets an effect that gives -2 psyche. Lasts 7 turns at level of caster psyche.', 
        'Pain':'Destroy one of your own summons to damage the units adjacent to the summon, (psyche vs dodge)+9', 
        'Entomb':'Teleport to the chosen location, leaving a tomb in your place. The tomb is a summon but has no movement or actions. Its abilities are: str 1, agl 1, end 5, dodge 1, psyche 5, spirit 20',
        'Foul Familiar':'Summon an Imp(agnes), Homunculus(ali), or Faerie Dragon(morgan). Limit 1 familiar in play at a time. Familiar death causes 3 magick dmg to owner.', 
        'Summon Lesser Demon':'Transform a familiar into a lesser demon thrall. Does not cause loss of spirit due to familiar death.', 
        'Summon Cenobite':'Summon a cenobite, a demon priest of suffering', 
        'Mist Move':'Move without being obstructed by obstacles.', 
        'Drain Life':'to hit: psyche vs psyche, dmg: minimum(1 OR (psyche vs psyche)/2)+1 (range of about 2 to half of normal psyche vs psyche dmg). Caster is healed equal to the amount of dmg successfully dealt.', 
        'Muddle':'If target fails a psyche save(+1), it gets an end of turn effect causing it to attack itself. It attempts a hit with its own agility (always 50%, unless affected by its own attack or defense effects). A successful hit causes strength vs endurance (its own) melee dmg. Lasts 3 turns at level 5.', 
        'Tendrils of Chaos':'2 to-hit attempts are made against the target: the first, psyche vs agl, target gets -1 to its move range unless it already has this move range effect. The second, psyche vs str, gives -1 to a random ability besides strength and can be given multiple times to the same unit. Both effects last 5 turns at level 6.', 
        'Warpfire':'Target location which does not already have a warpfire effect has a warpfire placed on it. At the start of each players turn, 2 magick damage is done to any unit occupying the location. After this, each unit within range 3 of the warpfire is teleported to a random location within the same range.', 
        'Phase Shift':'Switch between the Shadow Wolf and Shadow Mist forms. Counts as action.', 
        'Dark Shroud':'Target Warrior, Bard, Trickster, or Plaguebearer and all other of all these types within range 3 of the target heal 2 spirit up to their max spirit and receive +1 dodge if they do not already have the effect. Effect lasts for 3 turns at level 3.', 
        'Shadow Strike':'Agility versus dodge to-hit. Strength versus endurance determines damage. Type is ranged.', 
        'Stalk':'If target fails a dodge save(-3), it gets an effect which causes ranged damage dealt to it to be increased by 2. Lasts 11 turns at level 7.', 
        'Darkblast':'If used on a friendly unit, attempt to dispel(+2) any 1 effect and if the unit is a warrior, trickster, bard, or plaguebearer, then heal it 3 spirit. If used on an enemy unit, a successful to-hit (agl vs dodge) does damage (str vs end)/2 (minimum 2) and after the attack attempts to dispel(+2) any 1 effect on the target.', 
        'Slash':'Agility versus agility to-hit. Strength versus endurance determines damage. Range 1, type melee.', 
        'Leap':'Move over obstacles to any square within range 3. Movement effects do not affect the range of Leap unless specifically noted. Does not count as either an action or a move. Can only be used once per turn.', 
        'Rage':'Dispel(+6) current effects, gain +1 str, +1 end, +4 psy, take 3 dmg on effect end, lasts 4 turns.', 
        'Throw':'Move an adjacent unit to a location up to distance 3 from Warrior',
        'Whirlwind':'Attack each adjacent unit. To-hit: agl-2 vs agl, damage: str vs end', 
        'Pyrotechnics':'Do 2 ranged damage to any target within range 3, auto hit.', 
        'Simulacrum':'Target within range 4 gets +3 agility and +3 dodge. Lasts 3 turns at level 4. Cannot cast on target if it already has simulacrum effect.', 
        'Gate':'Target unit within range 2 is teleported to any square within range 5 of the caster.',
        'Mortar':'All units within range 2 of target square within range 6-8 must make a dodge save or take a random amount of ranged damage between 1-3.', 
        'Tracer Grenade':'All units within range 2 of target square within range 6-8 get tracer effect if they do not already have it. Effect gives -2 dodge for 6 turns at level 5.', 
        'Doubling Cube':'Target unit and all friendly units within range 2 of target get double effect if they do not already have it. Effect causes any melee or ranged attack made against unit to force attacker to make a psyche save(-1). On fail, the attackers dmg is halved (rounded down). Lasts 6 turns at level 5', 
        'Unholy Chant':'All other friendly units within range 2 get +1 to all stats for the remainder of the turn at level 4.', 
        'Discord':'Target within range 5 is attacked using psyche versus psyche to-hit. Damage is psyche versus psyche divided by 2 rounded down and added to 1 (about half normal formula, minimum 2). Type magick.', 
        'Esuna':'Target within range 4 has each effect attempted to dispel(+0).',
        'Moonlight':'Target Warrior, Shadow, Plaguebearer, or Trickster is healed 4 spirit up to its max spirit.', 
        'Aura':'Target Warrior, Shadow, Plaguebearer, or Trickster and all of these types within range 2 of target heal up to 3 spirit.', 
        'Tranquility':'Dispel(0) attempt all effects on a location', 
        'Pox':'Each adjacent, non-plaguebearer, unit gets pox effect if it does not already have it. Effect causes 2 poison damage at end of turn. Lasts 4 turns at level 6.', 
        'Paralyze':'If target fails a strength save(-1), it gets an effect which causes melee and ranged dmg to be halved(rounded down) and its move range reduced to 1. Lasts 2 turns at level 6.', 
        'Scarab Gestation':'Target adjacent enemy gets a death trigger that creates a scarab under your control, scarab has str 2, agl 3, end 3, dodge 3, psyche 2, spirit 9, move range 5, and bite attack (melee, range 1) agility vs agility to-hit, str vs end damage.', 
        'Bite':'Scarab bites an adjacent unit. To-hit: agl vs agl, damage: str vs end, melee.', 
        'Scarab Swarm':'Transform a scarab into a flying scarab swarm with the following abilities: str 4, agl 6, end 5, dodge 6, psyche 4, spirit 19, move range 6 (flying, same bite attack).', 
        'Spore Cloud':'Target location gets effect: +2 dodge, -2 received ranged or melee damage for occupant. Lasts 3 full turns (removed at the end of your turn after the next) at level 8.', 
        'Darkness':'Target location and each location within range 3 of target get darkness effect if location does not already have darkness effect. Any unit attempting to move when in a darkness location has its move range reduced by 2 to a minimum of 1. Lasts 2 turns at level 3.', 
        'Poison Sting':'to-hit: agility vs dodge. On successful hit, target gets effect that causes -1 strength and 2 poison dmg at end of turn. Target may have multiple copies of same effect. Lasts 4 turns at level 5. ', 
        'Flying Move':'Move without being impeded by obstacles.', 
        'Brambles':'Target unit and all enemy units within range 2 must make a dodge save(-1) or take psyche vs endurance dmg. Units must also make a strength save(-1) if they have normal movement type, and on fail get an effect that reduces move range by 1 to a minimum of 1. Lasts 1 turn at level 5.', 
        'Baleful Stare':'to-hit: psyche vs endurance. On successful hit, target gets effect that causes -1 psyche and 1 magick dmg at end of turn. Lasts 9 turns at level 5.', 
        'Dire Charm':'All enemy units within range 3 of caster must make a psyche save(-3) or attack themselves. The attack against self is auto-hit and strength vs endurance dmg (the units own strength and endurance).', 
        'Hellfire':'to-hit: psyche vs psyche. Dmg is psyche vs endurance. Target makes endurance save(-1) or receives burn effect. Burn causes dmg from melee and ranged sources to deal an extra 2 dmg. Lasts 3 turns at level 4.', 
        'Flesh Hooks':'Target summon receives a ranged attack action called hook attack. Hook attack is to-hit: psyche vs dodge and dmg: endurance vs endurance. Lasts 3 turns at level 6.', 
        'Strength Through Wounding':'All units (friendly and enemy) within range 3 of caster take 2 magick dmg. All friendly units gain effect of +2 endurance and +2 psyche. Lasts 2 turns at level 4.', 
        'Fuse Trap':'expect to change. NOTES: causes damage on undo. Even though damage is applied with lock, undo funcs do not, in any other case, need time (they can happen as fast as the program logic calls them)', 
        'Mesmerize':'Target gets an effect which causes a psyche save(+2) at the start of its turn. A failure causes it to count as having used its action for the turn (it may still move or regain the ability to use an action through some means). It also does 5 melee damage to itself.',
        'Hook Attack':'To-hit: psyche vs dodge. Dmg: end vs end (piercing).',
        'Psi Blades':"Psychic blades emanate from a Bard's hands, granting a psyche-based slashing attack. Lasts 3 turns at the level of caster psyche.",
        'Psi Slash':'To-hit: psyche vs agl. Dmg: psyche vs end (slashing).',
        'Molecular Subversion':'The very structure of a creature begins to dissolve. Target gains an effect that removes resistances (resistances may be gained through effects cast after this spell). Also gives an effect that adds weakness to acid and explosive dmg. Lasts 9 turns at level of caster psyche.',
        'Plutonian Cloak':'A friendly summon gets a defense effect. When taking damage, if the type is slashing, piercing, or crushing, this summon gains invisibility (untargetable with physical actions) until the end of its turn. If the type is magick, the summon gains psyshield (untargetable with spells) until the end of its turn. Invisibility or psyshield are not added if the summon already has the same type. Lasts 9 turns (each instance of either invisibility or psyshield last 1 turn).',
        'Hidden From the Stars':'A summon gains +2 end, +2 dodge, and psyshield for 7 turns.',
        'Cosmic Sight':'All enemy units within range 3 of caster make psyche check (-1) or get an effect lasting 5 turns which strips psyshield (effects applied later may grant psyshield while this is still in effect).',
        'Bewitch':'Any summon, friendly or enemy, gains an effect granting psyshield until its next end of turn. Level 4',
        'Read the Stars':'Caster and all friendly summons gain attack effect that increases magick type damage by 1. Lasts 1 turn.',
        "Minerva's Gift":'A summon heals 1 spirit and gains +2 psyche, +2 agility for 1 turn.',
        'Demonic Sight':'Any target without this effect gets an effect that strips invisibility. Lasts 6 turns (summon must be targetable by spells).'}
        self.sqr_anims = {}
        anims = [a for r,d,a in walk('animations/move/')][0]
        anims = [a for a in anims[:] if a[0] != '.']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/move/' + anim))
            self.sqr_anims[i] = a
        
        self.aura_anims = {}
        anims = [a for r,d,a in walk('animations/Aura/')][0]
        anims = [a for a in anims[:] if a[0] != '.']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Aura/' + anim))
            self.aura_anims[i] = a
        
        self.mortar_anims = {}
        anims = [a for r,d,a in walk('animations/Mortar/')][0]
        anims = [a for a in anims[:] if a[0] != '.']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Mortar/' + anim))
            self.mortar_anims[i] = a
        
        self.pestilence_anims = {}
        anims = [a for r,d,a in walk('animations/Pestilence/')][0]
        anims = [a for a in anims[:] if a[0] != '.']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Pestilence/' + anim))
            self.pestilence_anims[i] = a
            
        self.plague_anims = {}
        anims = [a for r,d,a in walk('animations/Plague/')][0]
        anims = [a for a in anims[:] if a[0] != '.']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/Plague/' + anim))
            self.plague_anims[i] = a
            
        self.choose_num_players()
        
        # Luminari 280
        # Herculanum 240
        # Papyrus 240
    def choose_num_players(self):
#         background_music.music.load('Ove Melaa - Dead, Buried and Cold.ogg')
        sound1 = mixer.Sound('Music/Ove Melaa - Dead, Buried and Cold.ogg')
        background_music.play(sound1, -1)
        sound1.set_volume(0.6)
        self.title_screen = ImageTk.PhotoImage(Image.open('titleScreen999.png').resize((root.winfo_screenwidth(),root.winfo_screenheight())))
        self.game_title = tk.Canvas(root, width = root.winfo_screenwidth(), bg = 'black', highlightthickness = 0, height = root.winfo_screenheight())
        self.game_title.create_image(0,0, image =self.title_screen, anchor = 'nw')
        self.game_title.pack(side = 'top')
        
        self.one_player = tk.Button(root, text = 'Campaign', fg = 'tan3', highlightbackground = 'tan3', font = ('chalkduster', 24), command = lambda num = 1 : self.num_chose(num))
        self.game_title.create_window(root.winfo_screenwidth()/2, root.winfo_screenheight()-120, anchor='s', window = self.one_player)
        
        self.two_player = tk.Button(root, text = 'Duel', fg = 'tan3', highlightbackground = 'tan3', font = ('chalkduster', 24), command = lambda num = 2 : self.num_chose(num))
        self.game_title.create_window(root.winfo_screenwidth()/2, root.winfo_screenheight()-70, anchor='s', window = self.two_player)
        
        self.load_button = tk.Button(root, text = 'Load Campaign', fg = 'tan3', highlightbackground = 'tan3', font = ('chalkduster', 24), command = self.try_load)
        self.game_title.create_window(root.winfo_screenwidth()/2, root.winfo_screenheight()-20, anchor='s', window = self.load_button)
        
    def try_load(self):
        saves = [s for r,d,s in walk('save_games/')][0]
        saves = [s for s in saves[:] if s[0] != '.']
        # create a button for each save and a cancel button
        self.scroll_frame = VerticalScrolledFrame(root)
        self.game_title.create_window(root.winfo_screenwidth()/2 + root.winfo_screenwidth()/8, root.winfo_screenheight()-220, anchor = 'nw', window = self.scroll_frame)
        self.game_title.saves_buttons = []
        for s in saves:
            # expand filename into readable
            with open('save_games/'+s, 'r') as f:
#                 obj = load(f)
                name = f.readline().strip('\n')
                if name == 'Agnes_Sampson':
                    img = ImageTk.PhotoImage(Image.open('avatars/Agnes_Sampson.png'))
                    obj = Witch(name = 'Agnes_Sampson', img = img, loc = [0,0], owner = 'p1')
                elif name == 'Fakir_Ali':
                    img = ImageTk.PhotoImage(Image.open('avatars/Fakir_Ali.png'))
                    obj = Witch(name = 'Fakir_Ali', img = img, loc = [0,0], owner = 'p1')
                cantrips = eval(f.readline().strip('\n'))
                arcane = eval(f.readline().strip('\n'))
                sum_cap = int(f.readline().strip('\n'))
                b_str = int(f.readline().strip('\n'))
                b_agl = int(f.readline().strip('\n'))
                b_end = int(f.readline().strip('\n'))
                b_dodge = int(f.readline().strip('\n'))
                b_psyche = int(f.readline().strip('\n'))
                b_spirit = int(f.readline().strip('\n'))
                b_magick = int(f.readline().strip('\n'))
                area = int(f.readline().strip('\n'))
                summon_level = int(f.readline().strip('\n'))
                if 'Foul_Familiar' in cantrips:
                    obj.cantrip_dict['Foul_Familiar'] = (obj.foul_familiar, 0)
                if 'Hatred' in arcane:
                    obj.arcane_dict['Hatred'] = (obj.hatred, 9)
                if 'Vengeance' in arcane:
                    obj.arcane_dict['Vengeance'] = (obj.vengeance, 13)
                if 'Pain' in arcane:
                    obj.arcane_dict['Pain'] = (obj.pain, 7)
                if 'Torment' in arcane:
                    obj.arcane_dict['Torment'] = (obj.torment, 7)
                if 'Entomb' in arcane:
                    obj.arcane_dict['Entomb'] = (obj.entomb, 4)
                if 'Summon_Cenobite' in arcane:
                    obj.arcane_dict['Summon_Cenobite'] = (obj.summon_cenobite, 9)
                if 'Summon_Lesser_Demon' in arcane:
                    obj.arcane_dict['Summon_Lesser_Demon'] = (obj.summon_lesser_demon, 9)
                obj.summon_cap = sum_cap
                obj.base_str = b_str
                obj.str = b_str
                obj.base_agl = b_agl
                obj.agl = b_agl
                obj.base_end = b_end
                obj.end = b_end
                obj.base_dodge = b_dodge
                obj.dodge = b_dodge
                obj.base_psyche = b_psyche
                obj.psyche = b_psyche
                obj.base_spirit = b_spirit
                obj.spirit = b_spirit
                obj.base_magick = b_magick
                obj.magick = b_magick
                obj.current_area = area
                obj.summon_level = summon_level
                cmd = lambda obj = obj : self.load_game(obj)
                b = tk.Button(self.scroll_frame.interior, text = s, width = 13, wraplength = 190, fg = 'indianred', highlightbackground = 'black', font = ('chalkduster', 24), relief = 'raised', command = cmd)
                b.pack() 
                self.game_title.saves_buttons.append(b)
        cancel_b = tk.Button(self.scroll_frame.interior, text = 'Cancel', bg = 'black', fg = 'black', width = 13, highlightbackground = 'black', font = ('chalkduster', 24), relief = 'raised', command = self.scroll_frame.destroy)
        cancel_b.pack(side = 'bottom')
        self.game_title.saves_buttons.append(cancel_b)
                
    def load_game(self, obj):
        self.game_title.destroy()
        obj.move_type = 'normal'
        self.load_map_triggers(map_number = obj.current_area, protaganist_object = obj)
        
    def num_chose(self, num):
        self.num_players = num
        self.game_title.destroy()
        self.one_player.destroy()
        self.two_player.destroy()
        del self.title_screen
        del self.game_title
        del self.one_player
        del self.two_player
        if self.num_players == 2:
            self.choose_map()
        else:
        # first choose_witch() here
            self.choose_witch(player_num = 1)
#             self.load_map_triggers(map_number = 0)
            
    # make each branch load the intro scene for level, with 'continue' button when done reading/displaying to call create_map_curs_context
    def load_map_triggers(self, map_number, witch = None, protaganist_object = None):
        background_music.stop()
        if map_number == 0: # FIRST AREA, NO 'CONTINUATION from previous level' BY PASSING PROTAG OBJECT
            # CLEANUP FROM CHOOSE_WITCH
            try:
                self.avatar_popup.destroy()
                del self.wrapped_funcs
            except:
                pass
            self.p1_witch = witch
            sound1 = mixer.Sound('Music/heroic_demise.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(0.4)
            self.map_triggers = []
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
            ############## GODHAND
#             def summon_trick():
#                 all = [v.name for k,v in self.ent_dict.items() if v.owner == 'p1']
#                 if 'Bard' in all:
#                     return 'victory'
#                 else:
#                     return None
#             self.map_triggers.append(summon_trick)
            ################
            def kill_all_enemies():
                all = [k for k,v in self.ent_dict.items() if v.owner == 'p2']
                if all == []:
                    return 'victory'
                else:
                    return None
            self.map_triggers.append(kill_all_enemies)
            if protaganist_object:
                self.load_intro_scene(map_number, protaganist_object = protaganist_object)
            else:
                self.load_intro_scene(map_number)# DONT NEED PROTAG OBJECT ON FIRST AREA
#             self.create_map_curs_context(map_number)
    # SECOND LEVEL
        elif map_number == 1:
            self.map_triggers = []
            sound1 = mixer.Sound('Music/Caves of sorrow.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(1.6)
#             def summon_trick():
#                 all = [v.name for k,v in self.ent_dict.items() if v.owner == 'p1']
#                 if 'Bard' in all:
#                     return 'victory'
#                 else:
#                     return None
#             self.map_triggers.append(summon_trick)
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
            def kill_all_undead():
                all = [k for k,v in self.ent_dict.items() if v.owner == 'p2']
                if all == []:
                    return 'victory'
                else:
                    return None
            self.map_triggers.append(kill_all_undead)
            
            self.load_intro_scene(map_number, protaganist_object = protaganist_object)
#             self.create_map_curs_context(map_number, protaganist_object = protaganist_object)
    # THRID LEVEL 
        elif map_number == 2:
            sound1 = mixer.Sound('Music/arabesque.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(0.3)
            self.map_triggers = []
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
#             def summon_trick():
#                 all = [v.name for k,v in self.ent_dict.items() if v.owner == 'p1']
#                 if 'Bard' in all:
#                     return 'door'
#                 else:
#                     return None
#             self.map_triggers.append(summon_trick)
#             depending on which is killed, load certain level
#             knight near stairway is b7, knight near doorway is b8
            def kill_stair_knight():
                all_knights = [v.number for k,v in self.ent_dict.items() if v.name == 'Undead_Knight']
                if 'b7' not in all_knights and 'b8' in all_knights:
                    return 'stairway'
                else:
                    return None
            self.map_triggers.append(kill_stair_knight)
            def kill_door_knight():
                all_knights = [v.number for k,v in self.ent_dict.items() if v.name == 'Undead_Knight']
                if 'b8' not in all_knights and 'b7' in all_knights:
                    return 'door'
                else:
                    return None
            self.map_triggers.append(kill_door_knight)
#             def kill_one_undead_knight(): # change to kill both handling
#                 all_knights = [v.name for k,v in self.ent_dict.items() if v.name == 'Undead_Knight']
#                 if len(all_knights) <= 1:
#                     return 'victory'
#                 else:
#                     return None
#             self.map_triggers.append(kill_one_undead_knight)
            
            self.load_intro_scene(map_number, protaganist_object = protaganist_object)
#             self.create_map_curs_context(map_number, protaganist_object = protaganist_object)
        elif map_number == 121:
            sound1 = mixer.Sound('Music/field_of_dreams.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(1)
            self.map_triggers = []
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
            #   CREATE SPARKLES
            def create_sparkles():
                app.vis_dict['Sparkle1'] = Vis(name = 'Sparkle', loc = [28,15])
                app.canvas.create_image(2800+50-app.moved_right, 1500+50-app.moved_down, image = app.vis_dict['Sparkle1'].img, tags = 'Sparkle1')
                app.vis_dict['Sparkle2'] = Vis(name = 'Sparkle', loc = [11,1])
                app.canvas.create_image(1100+50-app.moved_right, 100+50-app.moved_down, image = app.vis_dict['Sparkle2'].img, tags = 'Sparkle2')
                self.map_triggers.remove(create_sparkles)
            self.map_triggers.append(create_sparkles)
            # victory, kill ghost
            def kill_ghost():
                if 'b1' not in [k for k in self.ent_dict.keys()]:
                    return 'victory'
                else:
                    return None
            self.map_triggers.append(kill_ghost)
            # trigger ghost
            def ghost_teleport1():
                if app.ent_dict['b1'].spirit < 50:
                    if app.grid[7][2] != '':
                        empt_coords = [c for c in app.coords if app.grid[c[0]][c[1]] == '']
                        sqr = choice(empt_coords)
                    else:
                        sqr = [7,2]
                    oldloc = app.ent_dict['b1'].loc[:]
                    app.grid[oldloc[0]][oldloc[1]] = ''
                    app.ent_dict['b1'].loc = sqr[:]
                    app.grid[sqr[0]][sqr[1]] = 'b1'
                    app.canvas.delete('b1')
                    app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.ent_dict['b1'].img, tags = 'b1')
                    self.map_triggers.remove(ghost_teleport1)
            self.map_triggers.append(ghost_teleport1)
            def ghost_teleport2():
                if app.ent_dict['b1'].spirit < 30:
                    if app.grid[26][17] != '':
                        empt_coords = [c for c in app.coords if app.grid[c[0]][c[1]] == '']
                        sqr = choice(empt_coords)
                    else:
                        sqr = [26,17]
                    oldloc = app.ent_dict['b1'].loc[:]
                    app.grid[oldloc[0]][oldloc[1]] = ''
                    app.ent_dict['b1'].loc = sqr[:]
                    app.grid[sqr[0]][sqr[1]] = 'b1'
                    app.canvas.delete('b1')
                    app.canvas.create_image(sqr[0]*100+50-app.moved_right, sqr[1]*100+50-app.moved_down, image = app.ent_dict['b1'].img, tags = 'b1')
                    self.map_triggers.remove(ghost_teleport2)
            self.map_triggers.append(ghost_teleport2)
            # READ BOOK
            def read_book():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [27,15]:
                    del app.vis_dict['Sparkle1']
                    app.canvas.delete('Sparkle1')
                    app.unbind_all()
                    self.book121 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_121_book)
                    app.canvas.create_window(2700-app.moved_right, 1500-app.moved_down, window = self.book121)
                    self.book121_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_121_book)
                    app.canvas.create_window(2700-app.moved_right+25, 1500-app.moved_down+33, window = self.book121_cancel)
                    self.map_triggers.remove(read_book)
            self.map_triggers.append(read_book)
            def inspect_painting():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [11,2]:
                    del app.vis_dict['Sparkle2']
                    app.canvas.delete('Sparkle2')
                    app.unbind_all()
                    self.painting121 = tk.Button(root, text = 'Inspect Painting', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.inspect_121_painting)
                    app.canvas.create_window(1100-app.moved_right, 200-app.moved_down, window = self.painting121)
                    self.painting121_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_121_painting)
                    app.canvas.create_window(1100-app.moved_right+25, 200-app.moved_down+34, window = self.painting121_cancel)
                    self.map_triggers.remove(inspect_painting)
            self.map_triggers.append(inspect_painting)
            self.load_intro_scene(map_number, protaganist_object = protaganist_object)
        # LABYRINTH 
        elif map_number == 21:
            sound1 = mixer.Sound('Music/Blackmoor_Colossus.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(0.3)
            self.map_triggers = []
            self.revenant_rate = 0
            self.top2 = Image.open('1_player_map_fog/map21/2_top.png')
            self.bot2 = Image.open('1_player_map_fog/map21/2.png')
#             def summon_trick():
#                 all = [v.name for k,v in self.ent_dict.items() if v.owner == 'p1']
#                 if 'Bard' in all:
#                     return 'victory'
#                 else:
#                     return None
#             self.map_triggers.append(summon_trick)
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
            
            def area_sixteen():
                if app.ent_dict[app.p1_witch].loc in [[13,16],[13,17],[13,18],[13,19],[13,20]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[14,16],[14,17],[15,16],[15,17],[16, 16], [17, 16], [18, 16], [19, 16], [20, 16], [21, 16], [22, 16], [23, 16], [24, 16], [25, 16], [26, 16], [27, 16],[27,17],[27,18],[27,19],[27,20],[27,21],[26,21],[25,21],[25,20],[25,19],[17, 19], [18, 19], [19, 19], [20, 19], [21, 19], [22, 19], [23, 19], [24, 19],[14, 20], [15, 20], [16, 20], [17, 20], [18, 20], [19, 20]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/16_top.png')
                    bot = Image.open('1_player_map_fog/map21/16.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    if app.active_player == 'p1':
                        app.rebind_all()
                    self.map_triggers.remove(area_sixteen)

            # Ghost place 1, add ghost to coord 35,35
            # when ghost below N hp, move to final spot at 2,2 in area 9 which should only be revealed after area 8
            # add revenants or revenant generation...
            # 29,26 and 31,30 add trig to summon revs on turn 2
            # certain areas, once revealed, generate revenants every N turns, area 1 (start area), area 4 at 30,8, area 15 at 30, 34 and 32, 24, other revs are only placed and not generated/summoned
            def area_fifteen():
                if app.ent_dict[app.p1_witch].loc in [[5,37],[4,37]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[6, 37], [7, 37], [8, 37], [9, 37], [10, 37], [11, 37], [12, 37], [13, 37], [14, 37], [15, 37], [16, 37], [17, 37], [18, 37], [19, 37], [20, 37], [21, 37], [22, 37], [23, 37], [24, 37], [25, 37], [26, 37], [27, 37], [28, 37], [29, 37], [30, 37], [31, 37], [32, 37],[24, 36], [25, 36], [26, 36], [27, 36], [28, 36], [29, 36], [30, 36], [31, 36], [32, 36], [33, 36], [34, 36], [35, 36], [36, 36], [37, 36], [38, 36],[24, 35], [25, 35], [26, 35], [27, 35], [28, 35], [29, 35], [30, 35], [31, 35], [32, 35], [33, 35], [34, 35], [34, 34], [34, 37], [35, 34], [36, 34], [36, 37], [35, 37], [38, 34], [38, 37], [35, 35], [36, 35], [37, 35], [38, 35],[24, 34], [25, 34], [26, 34], [27, 34], [28, 34], [29, 34], [30, 34], [31, 34], [32, 34]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/15_top.png')
                    bot = Image.open('1_player_map_fog/map21/15.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_fifteen)
                    # PLACE GHOST
                    img = ImageTk.PhotoImage(Image.open('summon_imgs/Ghost.png'))
                    app.grid[35][35] = 'b2'
                    app.ent_dict['b2'] = Ghost(name = 'Ghost', img = img, loc = [35,35], owner = 'p2', number = 'b2')
                    app.canvas.create_image(3550-app.moved_right, 3550-app.moved_down, image = app.ent_dict['b2'].img, tags = 'b2')
                    # FIRST GHOST DEATH TRIG, in case it dies before teleporting (should be removed before
                    # second area routine in ghost ai 
                    def ghost_death():
                        if 'b2' not in app.ent_dict.keys():
                            return 'victory'
                    app.map_triggers.append(ghost_death)
                    # PLACE SPARKLE
                    app.vis_dict['Sparkle1'] = Vis(name = 'Sparkle', loc = [35,34])
                    app.canvas.create_image(3500+50-app.moved_right, 3400+50-app.moved_down, image = app.vis_dict['Sparkle1'].img, tags = 'Sparkle1')
                    def read_book():
                        loc = app.ent_dict[app.p1_witch].loc[:]
                        if app.active_player == 'p1' and loc == [35,34]:
                            del app.vis_dict['Sparkle1']
                            app.canvas.delete('Sparkle1')
                            app.unbind_all()
                            self.book21 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_21_book)
                            app.canvas.create_window(3500-app.moved_right, 3400-app.moved_down, window = self.book21)
                            self.book21_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_21_book)
                            app.canvas.create_window(3500-app.moved_right+25, 3400-app.moved_down+33, window = self.book21_cancel)
                            self.map_triggers.remove(read_book)
                    self.map_triggers.append(read_book)
                    if app.active_player == 'p1':
                        app.rebind_all()
            
            def area_fourteen():
                if app.ent_dict[app.p1_witch].loc in [[7,24],[6,24]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[7,25],[7, 26], [7, 27], [7, 28], [7, 29], [7, 30], [7, 31],[8, 30], [9, 30], [10, 30], [11, 30], [12, 30], [13, 30], [14, 30], [15, 30], [16, 30], [17, 30], [18, 30], [19, 30], [20, 30], [21, 30], [22, 30], [23, 30], [24, 30],[8, 31], [9, 31], [10, 31], [11, 31], [12, 31], [13, 31], [14, 31], [15, 31], [16, 31], [17, 31], [18, 31], [19, 31], [20, 31], [21, 31], [22, 31], [23, 31], [24, 31],[22,32],[22,33],[7, 34], [8, 34], [9, 34], [10, 34], [11, 34], [12, 34], [13, 34], [14, 34], [15, 34], [16, 34], [17, 34], [18, 34], [19, 34], [20, 34], [21, 34], [22, 34]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/14_top.png')
                    bot = Image.open('1_player_map_fog/map21/14.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    if app.active_player == 'p1':
                        app.rebind_all()
                    self.map_triggers.remove(area_fourteen)

            
            def area_thirteen():
                if app.ent_dict[app.p1_witch].loc in [[1,24],[1,23]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    self.map_triggers.append(area_fifteen)
                    coords = [[1,25],[1,26],[1,27],[1,28],[2,27],[2,28],[3,27],[3,28],[4,27],[4,28],[5,27],[5,28],[5, 29], [5, 30], [5, 31], [5, 32], [5, 33], [5, 34], [5, 35], [5, 36], [5, 37],[4, 33], [4, 34], [4, 35], [4, 36], [4, 37],[3, 31], [3, 32], [3, 33], [3, 34], [3, 35], [3, 36], [3, 37],[2, 31], [2, 32], [2, 33], [2, 34], [2, 35], [2, 36], [2, 37],[1, 31], [1, 32], [1, 33], [1, 34], [1, 35], [1, 36], [1, 37]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/13_top.png')
                    bot = Image.open('1_player_map_fog/map21/13.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_thirteen)
                    if app.active_player == 'p1':
                        app.rebind_all()
            self.map_triggers.append(area_thirteen)
            
            def area_twelve():
                if app.ent_dict[app.p1_witch].loc in [[12,20],[11,20],[4,19],[5,19],[6,19],[5,13],[5,12]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    self.map_triggers.append(area_fourteen)
                    coords = [[4,13],[3,13],[2,13],[1,13],[1, 14], [1, 15], [1, 16], [1, 17], [1, 18], [1, 19], [1, 20], [1, 21], [1, 22], [1, 23], [1, 24],[3, 13], [3, 14], [3, 15], [3, 16], [3, 17], [3, 18], [3, 19], [3, 20], [3, 21], [3, 22], [3, 23], [3, 24],[4,24],[5,24],[5,23],[5,22],[6,22],[6,23],[6,24],[7,22],[7,23],[7,24],[8,23],[8,22],[9,23],[9,22],[10,23],[10,22],[11,23],[11,22],[12,23],[12,22],[11,21],[12,21]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/12_top.png')
                    bot = Image.open('1_player_map_fog/map21/12.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_twelve)
                    # when revealing 12, if 11 not revealed then reveal it
                    if area_eleven in self.map_triggers:
                        area_eleven(alt = True)
                    if app.active_player == 'p1':
                        app.rebind_all()
            self.map_triggers.append(area_twelve)
            
            def area_eleven(alt = False):
                if app.ent_dict[app.p1_witch].loc in [[14,11],[14,12],[14,13]] or alt == True:
                    app.unbind_all()
                    self.revenant_rate += 1
                    self.map_triggers.append(area_sixteen)
                    coords = [[13,11],[13,12],[13,13],[12,11],[12,12],[12,13],[11,11],[11,12],[11,13],[11, 14], [11, 15], [11, 16], [11, 17], [11, 18], [11, 19], [11, 20],[12,18],[12,19],[12,20],[13,16],[13,17],[13,18],[13,19],[13,20],[10,15],[9,15],[9,16],[9,17],[9,18],[9,19],[8,19],[7,19],[6,19],[5,19],[10,11],[10,12],[9,11],[9,12],[8,11],[8,12],[7,11],[7,12],[7,13],[7,14],[7,15],[7,16],[6,16],[5,16],[4,19]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/11_top.png')
                    bot = Image.open('1_player_map_fog/map21/11.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_eleven)
                    if app.active_player == 'p1':
                        app.rebind_all()
            self.map_triggers.append(area_eleven)
#             
            def area_ten():
                if app.ent_dict[app.p1_witch].loc in [[16,9],[16,10],[4,13],[3,13]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[5, 8], [6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [11, 8], [12, 8], [13, 8], [14, 8], [15, 8], [16, 8],[5,9],[5,10],[5,11],[5,12],[5,13]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/10_top.png')
                    bot = Image.open('1_player_map_fog/map21/10.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_ten)
                    if app.active_player == 'p1':
                        app.rebind_all()
            self.map_triggers.append(area_ten)
#             
            def area_nine():
                if app.ent_dict[app.p1_witch].loc in [[3,5],[4,5]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[3,6],[3,7],[3,8],[3,9],[3,10],[2,10],[1,10],[1,2],[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[1,9],[2,2],[3,2],[4,2]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/9_top.png')
                    bot = Image.open('1_player_map_fog/map21/9.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_nine)
                    if app.active_player == 'p1':
                        app.rebind_all()
#             
            def area_eight():
                if app.ent_dict[app.p1_witch].loc in [[24,9],[24,10]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    self.map_triggers.append(area_nine)
                    coords = [[18, 8], [19, 8], [20, 8], [21, 8], [22, 8], [23, 8], [24, 8],[18,7],[18,6],[18,5],[3, 5], [4, 5], [5, 5], [6, 5], [7, 5], [8, 5], [9, 5], [10, 5], [11, 5], [12, 5], [13, 5], [14, 5], [15, 5], [16, 5],[17,5]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/8_top.png')
                    bot = Image.open('1_player_map_fog/map21/8.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_eight)
                    if app.active_player == 'p1':
                        app.rebind_all()
                        
            def area_seven():
                if app.ent_dict[app.p1_witch].loc in [[26,9],[26,10]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[26,8],[26,7],[26,6],[26,5],[25,5],[24,5],[23,5],[22,5],[21,5],[20,5]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/7_top.png')
                    bot = Image.open('1_player_map_fog/map21/7.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_seven)
                    if app.active_player == 'p1':
                        app.rebind_all()
#             
            def area_six():
                if app.ent_dict[app.p1_witch].loc in [[38,2],[37,2]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[7, 2], [8, 2], [9, 2], [10, 2], [11, 2], [12, 2], [13, 2], [14, 2], [15, 2], [16, 2], [17, 2], [18, 2], [19, 2], [20, 2], [21, 2], [22, 2], [23, 2], [24, 2], [25, 2], [26, 2], [27, 2], [28, 2], [29, 2], [30, 2], [31, 2], [32, 2], [33, 2], [34, 2], [35, 2], [36, 2]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/6_top.png')
                    bot = Image.open('1_player_map_fog/map21/6.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    # PLACE SPARKLE
                    app.vis_dict['Sparkle2'] = Vis(name = 'Sparkle', loc = [7,2])
                    app.canvas.create_image(700+50-app.moved_right, 200+50-app.moved_down, image = app.vis_dict['Sparkle2'].img, tags = 'Sparkle2')
                    def open_chest():
                        loc = app.ent_dict[app.p1_witch].loc[:]
                        if app.active_player == 'p1' and loc == [7,2]:
                            del app.vis_dict['Sparkle2']
                            app.canvas.delete('Sparkle2')
                            app.unbind_all()
                            self.chest21 = tk.Button(root, text = 'Open Chest', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.open_21_chest)
                            app.canvas.create_window(700-app.moved_right, 200-app.moved_down, window = self.chest21)
                            self.chest21_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_21_chest)
                            app.canvas.create_window(700-app.moved_right+25, 200-app.moved_down+33, window = self.chest21_cancel)
                            self.map_triggers.remove(open_chest)
                    self.map_triggers.append(open_chest)
                    self.map_triggers.remove(area_six)
                    if app.active_player == 'p1':
                        app.rebind_all()
#             
            def area_five():
                if app.ent_dict[app.p1_witch].loc in [[38,22],[38,23]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    self.map_triggers.append(area_six)
                    coords = [[38, 2], [38, 3], [38, 4], [38, 5], [38, 6], [38, 7], [38, 8], [38, 9], [38, 10], [38, 11], [38, 12], [38, 13], [38, 14], [38, 15], [38, 16], [38, 17], [38, 18], [38, 19], [38, 20], [38, 21],[37,2]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/5_top.png')
                    bot = Image.open('1_player_map_fog/map21/5.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_five)
                    if app.active_player == 'p1':
                        app.rebind_all()
            self.map_triggers.append(area_five)
#             
            def area_four():
                if app.ent_dict[app.p1_witch].loc in [[35,22],[35,23]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[35, 7], [35, 8], [35, 9], [35, 10], [35, 11], [35, 12], [35, 13], [35, 14], [35, 15], [35, 16], [35, 17], [35, 18], [35, 19], [35, 20], [35, 21],[29,7],[30,7],[31,7],[32,7],[33,7],[34,7],[29,8],[30,8],[31,8],[32,8],[33,8],[34,8]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/4_top.png')
                    bot = Image.open('1_player_map_fog/map21/4.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_four)
                    if app.active_player == 'p1':
                        app.rebind_all()
            self.map_triggers.append(area_four)
#             
            def area_three():
                if app.ent_dict[app.p1_witch].loc in [[33,22],[33,23]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    coords = [[33,21],[33,20],[33,19],[33,18],[33,17],[33,16],[33,15],[33,14],[33,13],[33,12]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                    top = Image.open('1_player_map_fog/map21/3_top.png')
                    bot = Image.open('1_player_map_fog/map21/3.png')
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_three)
                    if app.active_player == 'p1':
                        app.rebind_all()
            self.map_triggers.append(area_three)
            
            def area_two():
                if app.ent_dict[app.p1_witch].loc in [[29,22],[30,22],[31,22]]:
                    app.unbind_all()
                    self.revenant_rate += 1
                    self.map_triggers.append(area_seven)
                    self.map_triggers.append(area_eight)
                    coords = [[29,21],[30,21],[31,21],[29,20],[30,20],[31,20],[29,19],[30,19],[31,19],[29,18],[30,18],[31,18],[29,17],[30,17],[31,17],[29,16],[30,16],[31,16],[29,15],[30,15],[31,15],[29,14],[30,14],[31,14],[29,13],[30,13],[31,13],[29,12],[30,12],[31,12],[28,12],[28,13],[27,12],[27,13],[26,12],[26,13],[25,12],[25,13],[24,12],[24,13],[23,12],[23,13],[22,12],[22,13],[21,12],[21,13],[20,12],[20,13],[19,12],[19,13],[18,12],[18,13],[17,12],[17,13],[16,12],[16,13],[15,12],[15,13],[14,12],[14,13],[16,11],[17,11],[18,11],[19,11],[20,11],[21,11],[22,11],[16,10],[16,9],[14,11],[24,11],[24,10],[24,9],[26,11],[26,10],[26,9]]
                    for c in coords:
                        app.grid[c[0]][c[1]] = ''
                        
#                     top = Image.open('1_player_map_fog/map21/2_top.png')
#                     bot = Image.open('1_player_map_fog/map21/2.png')
                    top = self.top2
                    bot = self.bot2
                    
                    newbot = self.map_bottom_image
                    newtop = self.map_top_image
                    newbot = Image.alpha_composite(newbot, bot)
                    newtop = Image.alpha_composite(newtop, top)
                    self.map_bottom_image = newbot
                    self.map_top_image = newtop
                    self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
                    self.map_top = ImageTk.PhotoImage(self.map_top_image)
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_bottom, tags = ('map','mapbottom'))
                    self.canvas.create_image(0-app.moved_right, 0-app.moved_down, anchor = 'nw', image = self.map_top, tags = ('map','maptop'))
                    app.canvas.tag_lower('mapbottom')
                    self.map_triggers.remove(area_two)
                    if app.active_player == 'p1':
                        app.rebind_all()
            self.map_triggers.append(area_two)
            
            self.load_intro_scene(map_number, protaganist_object = protaganist_object)
            
        elif map_number == 22:
            sound1 = mixer.Sound('Music/Dark_Amulet.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(0.4)
            self.map_triggers = []
#             def summon_trick():
#                 all = [v.name for k,v in self.ent_dict.items() if v.owner == 'p1']
#                 if 'Bard' in all:
#                     return 'victory'
#                 else:
#                     return None
#             self.map_triggers.append(summon_trick)
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
            # SPARKLE
            def create_sparkle1():
                app.vis_dict['Sparkle1'] = Vis(name = 'Sparkle', loc = [22,8])
                app.canvas.create_image(2200+50-app.moved_right, 800+50-app.moved_down, image = app.vis_dict['Sparkle1'].img, tags = 'Sparkle1')
                self.map_triggers.remove(create_sparkle1)
            self.map_triggers.append(create_sparkle1)
            def inspect_column():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [22,9]:
                    del app.vis_dict['Sparkle1']
                    app.canvas.delete('Sparkle1')
                    app.unbind_all()
                    self.column22 = tk.Button(root, text = 'Inspect Column', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.inspect_22_column)
                    app.canvas.create_window(2200-app.moved_right, 900-app.moved_down, window = self.column22)
                    self.column22_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_22_column)
                    app.canvas.create_window(2200-app.moved_right+25, 900-app.moved_down+33, window = self.column22_cancel)
                    self.map_triggers.remove(inspect_column)
            self.map_triggers.append(inspect_column)
            def awaken_orcs():
                sqrs_near = [s for s in app.coords if dist(app.ent_dict['b7'].loc,s) <= 7 or dist(app.ent_dict['b8'].loc,s) <= 7]
                player_ent_locs = [v.loc for k,v in app.ent_dict.items() if v.owner == 'p1']
                sentinel = False
                for loc in player_ent_locs:
                    if loc in sqrs_near:
                        sentinel = True
                if app.ent_dict['b1'].spirit < 127 or sentinel == True:
                    app.ent_dict['b7'].waiting = False
                    app.ent_dict['b8'].waiting = False
                    self.map_triggers.remove(awaken_orcs)
            self.map_triggers.append(awaken_orcs)
            def awaken_dragon():
                sqrs = [s for s in app.coords if dist(s, app.ent_dict['b1'].loc) <= 9]
                ents = [app.grid[s[0]][s[1]] for s in sqrs if app.grid[s[0]][s[1]] != '' and app.grid[s[0]][s[1]] != 'block']
                for ent in ents:
                    if app.ent_dict[ent].owner == 'p1':
                        app.ent_dict['b1'].waiting = False
                        self.map_triggers.remove(awaken_dragon)
                        break
            self.map_triggers.append(awaken_dragon)
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
            def kill_dragon():
                if 'b1' not in app.ent_dict.keys():
                    return 'victory'
            self.map_triggers.append(kill_dragon)
            self.load_intro_scene(map_number, protaganist_object = protaganist_object)
        elif map_number == 122:
            sound1 = mixer.Sound('Music/Dark_Descent.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(0.3)
            self.map_triggers = []
#             def summon_trick():
#                 all = [v.name for k,v in self.ent_dict.items() if v.owner == 'p1']
#                 if 'Bard' in all:
#                     return 'victory'
#                 else:
#                     return None
#             self.map_triggers.append(summon_trick)
            # SPARKLE
            def create_sparkle1():
                app.vis_dict['Sparkle1'] = Vis(name = 'Sparkle', loc = [7,1])
                app.canvas.create_image(700+50-app.moved_right, 100+50-app.moved_down, image = app.vis_dict['Sparkle1'].img, tags = 'Sparkle1')
                self.map_triggers.remove(create_sparkle1)
            self.map_triggers.append(create_sparkle1)
            # BOOK TRIGGER
            def read_book():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [7,2]:
                    del app.vis_dict['Sparkle1']
                    app.canvas.delete('Sparkle1')
                    app.unbind_all()
                    self.book122 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_122_book)
                    app.canvas.create_window(700-app.moved_right, 200-app.moved_down, window = self.book122)
                    self.book122_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_122_book)
                    app.canvas.create_window(700-app.moved_right+25, 200-app.moved_down+33, window = self.book122_cancel)
                    self.map_triggers.remove(read_book)
            self.map_triggers.append(read_book)
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
            def kill_warlock():
                if 'b1' not in app.ent_dict.keys():
                    return 'victory'
            self.map_triggers.append(kill_warlock)
            self.load_intro_scene(map_number, protaganist_object = protaganist_object)
        # LEVEL 3 SANCTUM ENTRYWAY
        elif map_number == 3:
            sound1 = mixer.Sound('Music/radakan - old crypt.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(0.8)
            self.map_triggers = []
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
#             def summon_trick():
#                 all = [v.name for k,v in self.ent_dict.items() if v.owner == 'p1']
#                 if 'Bard' in all:
#                     return 'victory'
#                 else:
#                     return None
#             self.map_triggers.append(summon_trick)
            def kill_all():
                ents = app.ent_dict.keys()
                if 'b0' not in ents and 'b1' not in ents and 'b2' not in ents:
                    return 'victory'
            self.map_triggers.append(kill_all)
            # BOOK AND SPARKLE 1
            def create_sparkle1():
                app.vis_dict['Sparkle1'] = Vis(name = 'Sparkle', loc = [1,29])
                app.canvas.create_image(100+50-app.moved_right, 2900+50-app.moved_down, image = app.vis_dict['Sparkle1'].img, tags = 'Sparkle1')
                self.map_triggers.remove(create_sparkle1)
            self.map_triggers.append(create_sparkle1)
            def read_book1():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [2,29]:
                    del app.vis_dict['Sparkle1']
                    app.canvas.delete('Sparkle1')
                    app.unbind_all()
                    self.book3_1 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_3_1_book)
                    app.canvas.create_window(100-app.moved_right, 2900-app.moved_down, window = self.book3_1)
                    self.book3_1_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_3_1_book)
                    app.canvas.create_window(100-app.moved_right+25, 2900-app.moved_down+33, window = self.book3_1_cancel)
                    self.map_triggers.remove(read_book1)
            self.map_triggers.append(read_book1)
            # BOOK AND SPARKLE 2
            def create_sparkle2():
                app.vis_dict['Sparkle2'] = Vis(name = 'Sparkle', loc = [18,29])
                app.canvas.create_image(1800+50-app.moved_right, 2900+50-app.moved_down, image = app.vis_dict['Sparkle2'].img, tags = 'Sparkle2')
                self.map_triggers.remove(create_sparkle2)
            self.map_triggers.append(create_sparkle2)
            def read_book2():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [17,29]:
                    del app.vis_dict['Sparkle2']
                    app.canvas.delete('Sparkle2')
                    app.unbind_all()
                    self.book3_2 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_3_2_book)
                    app.canvas.create_window(1800-app.moved_right, 2900-app.moved_down, window = self.book3_2)
                    self.book3_2_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_3_2_book)
                    app.canvas.create_window(1800-app.moved_right+25, 2900-app.moved_down+33, window = self.book3_2_cancel)
                    self.map_triggers.remove(read_book2)
            self.map_triggers.append(read_book2)
            # BOOK AND SPARKLE 3
            def create_sparkle3():
                app.vis_dict['Sparkle3'] = Vis(name = 'Sparkle', loc = [1,19])
                app.canvas.create_image(100+50-app.moved_right, 1900+50-app.moved_down, image = app.vis_dict['Sparkle3'].img, tags = 'Sparkle3')
                self.map_triggers.remove(create_sparkle3)
            self.map_triggers.append(create_sparkle3)
            def read_book3():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [2,19]:
                    del app.vis_dict['Sparkle3']
                    app.canvas.delete('Sparkle3')
                    app.unbind_all()
                    self.book3_3 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_3_3_book)
                    app.canvas.create_window(100-app.moved_right, 1900-app.moved_down, window = self.book3_3)
                    self.book3_3_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_3_3_book)
                    app.canvas.create_window(100-app.moved_right+25, 1900-app.moved_down+33, window = self.book3_3_cancel)
                    self.map_triggers.remove(read_book3)
            self.map_triggers.append(read_book3)
            # BOOK AND SPARKLE 4
            def create_sparkle4():
                app.vis_dict['Sparkle4'] = Vis(name = 'Sparkle', loc = [18,19])
                app.canvas.create_image(1800+50-app.moved_right, 1900+50-app.moved_down, image = app.vis_dict['Sparkle4'].img, tags = 'Sparkle4')
                self.map_triggers.remove(create_sparkle4)
            self.map_triggers.append(create_sparkle4)
            def read_book4():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [17,19]:
                    del app.vis_dict['Sparkle4']
                    app.canvas.delete('Sparkle4')
                    app.unbind_all()
                    self.book3_4 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_3_4_book)
                    app.canvas.create_window(1800-app.moved_right, 1900-app.moved_down, window = self.book3_4)
                    self.book3_4_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_3_4_book)
                    app.canvas.create_window(1800-app.moved_right+25, 1900-app.moved_down+33, window = self.book3_4_cancel)
                    self.map_triggers.remove(read_book4)
            self.map_triggers.append(read_book4)
            # BOOK AND SPARKLE 5
            def create_sparkle5():
                app.vis_dict['Sparkle5'] = Vis(name = 'Sparkle', loc = [18,9])
                app.canvas.create_image(1800+50-app.moved_right, 900+50-app.moved_down, image = app.vis_dict['Sparkle5'].img, tags = 'Sparkle5')
                self.map_triggers.remove(create_sparkle5)
            self.map_triggers.append(create_sparkle5)
            def read_book5():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [17,9]:
                    del app.vis_dict['Sparkle5']
                    app.canvas.delete('Sparkle5')
                    app.unbind_all()
                    self.book3_5 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_3_5_book)
                    app.canvas.create_window(1800-app.moved_right, 900-app.moved_down, window = self.book3_5)
                    self.book3_5_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_3_5_book)
                    app.canvas.create_window(1800-app.moved_right+25, 900-app.moved_down+33, window = self.book3_5_cancel)
                    self.map_triggers.remove(read_book5)
            self.map_triggers.append(read_book5)
            # BOOK AND SPARKLE 6
            def create_sparkle6():
                app.vis_dict['Sparkle6'] = Vis(name = 'Sparkle', loc = [1,9])
                app.canvas.create_image(100+50-app.moved_right, 900+50-app.moved_down, image = app.vis_dict['Sparkle6'].img, tags = 'Sparkle6')
                self.map_triggers.remove(create_sparkle6)
            self.map_triggers.append(create_sparkle6)
            def read_book6():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [2,9]:
                    del app.vis_dict['Sparkle6']
                    app.canvas.delete('Sparkle6')
                    app.unbind_all()
                    self.book3_6 = tk.Button(root, text = 'Read Book', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.read_3_6_book)
                    app.canvas.create_window(200-app.moved_right, 900-app.moved_down, window = self.book3_6)
                    self.book3_6_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_3_6_book)
                    app.canvas.create_window(200-app.moved_right+25, 900-app.moved_down+33, window = self.book3_6_cancel)
                    self.map_triggers.remove(read_book6)
            self.map_triggers.append(read_book6)
            
            def awaken_group_2(): 
                friendly_ent_locs = [v.loc for k,v in app.ent_dict.items() if v.owner == 'p1']
                for loc in friendly_ent_locs:
                    if loc[1] < 19:
                        app.ent_dict['b1'].waiting = False
                        app.ent_dict['b2'].waiting = False
                        app.ent_dict['b7'].waiting = False
                        app.ent_dict['b8'].waiting = False
                        app.ent_dict['b9'].waiting = False
                        app.ent_dict['b10'].waiting = False
                        self.map_triggers.remove(awaken_group_2)
                        break
            self.map_triggers.append(awaken_group_2)
            self.load_intro_scene(map_number, protaganist_object = protaganist_object)
        elif map_number == 4:
            sound1 = mixer.Sound('Music/The Peculiar Habits of the Cave Hermits.ogg')
            background_music.play(sound1, -1)
            sound1.set_volume(0.8)
            self.map_triggers = []
            def self_death():
                if app.p1_witch not in app.ent_dict.keys():
                    return 'game over'
            self.map_triggers.append(self_death)
            # powerup sparkle, added after death of firemage
            def create_sparkle1():
                app.vis_dict['Sparkle1'] = Vis(name = 'Sparkle', loc = [5,5])
                app.canvas.create_image(500+50-app.moved_right, 500+50-app.moved_down, image = app.vis_dict['Sparkle1'].img, tags = 'Sparkle1')
                self.map_triggers.remove(create_sparkle1)
            self.map_triggers.append(create_sparkle1)
            def inspect_baphomet_statue():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [5,5]:
                    del app.vis_dict['Sparkle1']
                    app.canvas.delete('Sparkle1')
                    app.unbind_all()
                    self.baphomet_statue = tk.Button(root, text = 'Inspect Statue', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.baphomet_statue)
                    app.canvas.create_window(500-app.moved_right, 500-app.moved_down, window = self.baphomet_statue)
                    self.baphomet_statue_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_baphomet_statue)
                    app.canvas.create_window(500-app.moved_right+25, 500-app.moved_down+33, window = self.baphomet_statue_cancel)
                    self.map_triggers.remove(inspect_baphomet_statue)
            # powerup sparkle, added after death of earthmage
            def create_sparkle2():
                app.vis_dict['Sparkle2'] = Vis(name = 'Sparkle', loc = [34,5])
                app.canvas.create_image(3400+50-app.moved_right, 500+50-app.moved_down, image = app.vis_dict['Sparkle2'].img, tags = 'Sparkle2')
                self.map_triggers.remove(create_sparkle2)
            self.map_triggers.append(create_sparkle2)
            def inspect_astrolabe():
                loc = app.ent_dict[app.p1_witch].loc[:]
                if app.active_player == 'p1' and loc == [34,5]:
                    del app.vis_dict['Sparkle2']
                    app.canvas.delete('Sparkle2')
                    app.unbind_all()
                    self.astrolabe = tk.Button(root, text = 'Inspect Device', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.astrolabe)
                    app.canvas.create_window(3400-app.moved_right, 500-app.moved_down, window = self.astrolabe)
                    self.astrolabe_cancel = tk.Button(root, text = 'Leave Alone', font = ('chalkduster', 18), highlightbackground = 'black', fg = 'indianred', command = self.cancel_astrolabe)
                    app.canvas.create_window(3400-app.moved_right+25, 500-app.moved_down+33, window = self.astrolabe_cancel)
                    self.map_triggers.remove(inspect_astrolabe)
            # victory condition for level is death of final elemental mage (water), appended after airmage death
            def watermage_death():
                if 'Water_Mage' not in [v.name for k,v in app.ent_dict.items()]:
                    return 'victory'
            # airmage death trigger, appended after earthmage death
            def airmage_death():
                if 'Air_Mage' not in [v.name for k,v in app.ent_dict.items()]:
                    # kill air elementals (find by name not id)
                    for id in list(app.ent_dict.keys()):
                        if app.ent_dict[id].name == 'Air_Elemental':
                            app.ent_dict[id].death_triggers = []
                            name = 'Dethlok'+str(app.death_count)
                            app.death_count += 1
                            app.dethloks[name] = tk.IntVar(0)
                            root.after(666, lambda id = id, name = name : app.kill(id, name))
                            app.wait_variable(app.dethloks[name])
                    # spawn water mage
                    img = ImageTk.PhotoImage(Image.open('summon_imgs/Water_Mage.png'))
                    num = app.effects_counter
                    app.effects_counter += 1
                    # find open spawn square
                    sqrs = [[x,y] for x in range(17,24) for y in range(14,20) if app.grid[x][y] == '']
                    loc = choice(sqrs)
                    app.ent_dict['b'+str(num)] = Water_Mage(name = 'Water_Mage', img = img, loc = loc[:], owner = 'p2', number = 'b'+str(num))
                    app.grid[loc[0]][loc[1]] = 'b'+str(num)
                    self.map_triggers.remove(airmage_death)
                    self.map_triggers.append(watermage_death)
            # earthmage death trigger, appended after firemage death
            def earthmage_death():
                if 'Earth_Mage' not in [v.name for k,v in app.ent_dict.items()]:
                    # add sparkle2 powerup
                    self.map_triggers.append(inspect_astrolabe)
                    # kill earth elementals (find by name not id)
                    for id in list(app.ent_dict.keys()):
                        if app.ent_dict[id].name == 'Earth_Elemental':
                            app.ent_dict[id].death_triggers = []
                            name = 'Dethlok'+str(app.death_count)
                            app.death_count += 1
                            app.dethloks[name] = tk.IntVar(0)
                            root.after(666, lambda id = id, name = name : app.kill(id, name))
                            app.wait_variable(app.dethloks[name])
                    # spawn air mage
                    img = ImageTk.PhotoImage(Image.open('summon_imgs/Air_Mage.png'))
                    num = app.effects_counter
                    app.effects_counter += 1
                    # find open spawn square
                    sqrs = [[x,y] for x in range(17,24) for y in range(14,20) if app.grid[x][y] == '']
                    loc = choice(sqrs)
                    app.ent_dict['b'+str(num)] = Air_Mage(name = 'Air_Mage', img = img, loc = loc[:], owner = 'p2', number = 'b'+str(num))
                    app.grid[loc[0]][loc[1]] = 'b'+str(num)
                    self.map_triggers.remove(earthmage_death)
                    self.map_triggers.append(airmage_death)
            # add firemage death trigger
            def firemage_death():
                if 'b0' not in app.ent_dict.keys():
                    # add sparkle1 powerup
                    self.map_triggers.append(inspect_baphomet_statue)
                    # kill fire elementals (find by name not id)
                    for id in list(app.ent_dict.keys()):
                        if app.ent_dict[id].name == 'Fire_Elemental':
                            app.ent_dict[id].death_triggers = []
                            name = 'Dethlok'+str(app.death_count)
                            app.death_count += 1
                            app.dethloks[name] = tk.IntVar(0)
                            root.after(666, lambda id = id, name = name : app.kill(id, name))
                            app.wait_variable(app.dethloks[name])
                    # spawn earth mage
                    img = ImageTk.PhotoImage(Image.open('summon_imgs/Earth_Mage.png'))
                    num = app.effects_counter
                    app.effects_counter += 1
                    # find open spawn square
                    sqrs = [[x,y] for x in range(17,24) for y in range(14,20) if app.grid[x][y] == '']
                    loc = choice(sqrs)
                    app.ent_dict['b'+str(num)] = Earth_Mage(name = 'Earth_Mage', img = img, loc = loc[:], owner = 'p2', number = 'b'+str(num))
                    app.grid[loc[0]][loc[1]] = 'b'+str(num)
                    self.map_triggers.remove(firemage_death)
                    self.map_triggers.append(earthmage_death)
            self.map_triggers.append(firemage_death)
            self.load_intro_scene(map_number, protaganist_object = protaganist_object)
    # END OF GAME
        else:
            print('you are winner hahaha')
        
    # Move trigger funcs for organization?
    # baphomet trigger
    def baphomet_statue(self):
        app.unbind_all()
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.canvas.create_text(loc[0]*100-app.moved_right-1, loc[1]*100-app.moved_down+84, text = 'Summon Cenobite Learned...', justify = 'center', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Summon Cenobite Learned...', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        app.ent_dict[app.p1_witch].arcane_dict['Summon_Cenobite'] = (app.ent_dict[app.p1_witch].summon_cenobite, 9)
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_baphomet_statue()
        
    def cancel_baphomet_statue(self):
        self.baphomet_statue.destroy()
        self.baphomet_cancel.destroy()
        app.rebind_all()
        
    # astrolabe trigger
    def astrolabe(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.canvas.create_text(loc[0]*100-app.moved_right-1, loc[1]*100-app.moved_down+84, text = 'Astrolabe', justify = 'center', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Astrolabe', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        app.ent_dict[app.p1_witch].arcane_dict['Summon_Lesser_Demon'] = (app.ent_dict[app.p1_witch].summon_lesser_demon, 7)
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_astrolabe()
        
    def cancel_astrolabe(self):
        self.astrolabe.destroy()
        self.astrolabe_cancel.destroy()
        app.rebind_all()
    
    def read_3_1_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Permanent +20 Magick', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        app.ent_dict[app.p1_witch].base_magick += 20
        app.ent_dict[app.p1_witch].magick += 20
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_3_1_book()
        
    def cancel_3_1_book(self):
        self.book3_1.destroy()
        self.book3_1_cancel.destroy()
        app.rebind_all()
        
    def read_3_2_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Permanent +10 Spirit', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        app.ent_dict[app.p1_witch].base_spirit += 10
        app.ent_dict[app.p1_witch].spirit += 10
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_3_2_book()
        
    def cancel_3_2_book(self):
        self.book3_2.destroy()
        self.book3_2_cancel.destroy()
        app.rebind_all()
        
    def read_3_3_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Summon Cap +1', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        app.ent_dict[app.p1_witch].summon_cap += 1
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_3_3_book()
        
    def cancel_3_3_book(self):
        self.book3_3.destroy()
        self.book3_3_cancel.destroy()
        app.rebind_all()
        
    def read_3_4_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Permanent Endurance +1', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        app.ent_dict[app.p1_witch].base_end += 1
        app.ent_dict[app.p1_witch].end += 1
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_3_4_book()
        
    def cancel_3_4_book(self):
        self.book3_4.destroy()
        self.book3_4_cancel.destroy()
        app.rebind_all()
        
    def read_3_5_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.ent_dict[app.p1_witch].arcane_dict['Entomb'] = (app.ent_dict[app.p1_witch].entomb, 4)
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Arcane Spell\n-ENTOMB-\nLearned', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_3_5_book()
        
    def cancel_3_5_book(self):
        self.book3_5.destroy()
        self.book3_5_cancel.destroy()
        app.rebind_all()
        
    def read_3_6_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.ent_dict[app.p1_witch].cantrip_dict['Foul_Familiar'] = (app.ent_dict[app.p1_witch].foul_familiar, 0)
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Cantrip Spell\n-FOUL FAMILIAR-\nLearned', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_3_6_book()
        
    def cancel_3_6_book(self):
        self.book3_6.destroy()
        self.book3_6_cancel.destroy()
        app.rebind_all()
        
    def inspect_22_column(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.ent_dict[app.p1_witch].arcane_dict['Hatred'] = (app.ent_dict[app.p1_witch].hatred, 9)
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Arcane Spell\n-HATRED-\nLearned', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_22_column()
        
    def cancel_22_column(self):
        self.column22.destroy()
        self.column22_cancel.destroy()
        app.rebind_all()
    
    def read_122_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.ent_dict[app.p1_witch].arcane_dict['Torment'] = (app.ent_dict[app.p1_witch].torment, 7)
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Arcane Spell\n-TORMENT-\nLearned', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_122_book()
        
    def cancel_122_book(self):
        self.book122.destroy()
        self.book122_cancel.destroy()
        app.rebind_all()
    
    def read_21_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.ent_dict[app.p1_witch].summon_level = 2
        app.canvas.create_text(loc[0]*100-app.moved_right-1, loc[1]*100-app.moved_down+84, text = 'Summons gain experience...', justify = 'center', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Summons gain experience...', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_21_book()
        
    def cancel_21_book(self):
        self.book21.destroy()
        self.book21_cancel.destroy()
        app.rebind_all()
    
    def open_21_chest(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.ent_dict[app.p1_witch].arcane_dict['Vengeance'] = (app.ent_dict[app.p1_witch].vengeance, 13)
        app.canvas.create_text(loc[0]*100-app.moved_right-1, loc[1]*100-app.moved_down+84, text = 'Arcane Spell\n-VENGEANCE-\nLearned', justify = 'center', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Arcane Spell\n-VENGEANCE-\nLearned', justify = 'center', font = ('Andale Mono', 16), fill = 'antiquewhite3', tags = 'text')
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_21_chest()
        
    def cancel_21_chest(self):
        self.chest21.destroy()
        self.chest21_cancel.destroy()
        app.rebind_all()
    
    def read_121_book(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.ent_dict[app.p1_witch].arcane_dict['Pain'] = (app.ent_dict[app.p1_witch].pain, 7)
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Arcane Spell\n-PAIN-\nLearned', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_121_book()
        
    def cancel_121_book(self):
        self.book121.destroy()
        self.book121_cancel.destroy()
        app.rebind_all()
        
    def inspect_121_painting(self):
        loc = app.ent_dict[app.p1_witch].loc[:]
        app.ent_dict[app.p1_witch].summon_level = 2
        app.canvas.create_text(loc[0]*100-app.moved_right-1, loc[1]*100-app.moved_down+84, text = 'Summons gain experience...', justify = 'center', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
        app.canvas.create_text(loc[0]*100-app.moved_right, loc[1]*100-app.moved_down+85, text = 'Summons gain experience...', justify = 'center', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
        root.after(2999, lambda t = 'text' : app.canvas.delete(t))
        self.cancel_121_painting()
        
    def cancel_121_painting(self):
        self.painting121.destroy()
        self.painting121_cancel.destroy()
        app.rebind_all()
        
        
    def load_intro_scene(self, map_number = None, protaganist_object = None):
        self.intro_scene = ImageTk.PhotoImage(Image.open('intro_scenes/intro_scene'+str(map_number)+'.png').resize((root.winfo_screenwidth(),root.winfo_screenheight())))
        self.intro_canvas = tk.Canvas(root, width = root.winfo_screenwidth(), bg = 'black', highlightthickness = 0, height = root.winfo_screenheight())
        self.intro_canvas.create_image(0,0, image =self.intro_scene, anchor = 'nw')
        self.intro_canvas.pack(side = 'top')
        filename = 'intro_scene_texts/intro_scene_text'+str(map_number)+'.txt'
        with open(filename) as f:
            text = f.read()
        self.intro_text = tk.Label(root, text = text, wraplength = root.winfo_screenwidth()-90, bg = 'black', fg = 'indianred', font = ('kokonor', 18))
        self.intro_canvas.create_window(root.winfo_screenwidth()/2, root.winfo_screenheight()-180, anchor='s', window = self.intro_text)
# CONT OR SAVE BUTTONS        
        self.start_area_button = tk.Button(root, text = 'Start Area', fg = 'tan3', highlightbackground = 'tan3', font = ('chalkduster', 24), command = lambda n = map_number, po = protaganist_object : self.create_map_curs_context(n,po))
        self.intro_canvas.create_window(root.winfo_screenwidth()/2-100, root.winfo_screenheight()-80, anchor='s', window = self.start_area_button)
        
    # ONLY CALLED IN 2 PLAYER MODE
    def choose_map(self):
        self.choosemap = tk.Label(root, text = 'Choose Map', fg = 'tan3', bg = 'black', font = ('chalkduster', 38))
        self.choosemap.pack()
        # CHOOSE MAPS
        maps = [m for r,d,m in walk('./2_player_map_portraits')][0]
        maps = [m for m in maps[:] if m[0] != '.']
        self.map_button_list = []
        self.tmp_mapimg_dict = {}
        for i,map in enumerate(maps):
            b = tk.Button(root)
            cmd = lambda indx = i : self.map_choice_cleanup(indx)
            photo = ImageTk.PhotoImage(Image.open('./2_player_map_portraits/' + map).resize((300,300)))
            self.tmp_mapimg_dict['map'+str(i)] = photo
            b.config(image = self.tmp_mapimg_dict['map'+str(i)], bg = 'black', highlightbackground = 'tan3', command = cmd)
            # DEBUG packing will have to be fixed here for different screen sizes
            b.pack(side = 'left', padx = 55)
            self.map_button_list.append(b)
        
    def map_choice_cleanup(self, map_number):
        self.two_player_map_num = map_number
        self.choosemap.destroy()
        del self.tmp_mapimg_dict
        for b in self.map_button_list:
            b.destroy()
        del self.map_button_list
        self.choose_witch(player_num = 1)
#         self.create_map_curs_context(map_number)
        
        
        # IF PROTAG, LOAD PROTAG AND DO NOT RE-INIT WITCH
    def create_map_curs_context(self, map_number, protaganist_object = None):
        global curs_pos, grid_pos
        self.map_number = map_number
        try: self.intro_canvas.destroy()
        except: pass
        # GET MAP DIMENSIONS
        if self.num_players == 1:
            filename = '1_player_map_info/map' + str(map_number) + '.txt'
        else:
            filename = '2_player_map_info/map' + str(map_number) + '.txt'
        with open(filename) as f:
            self.map_info = f.read().splitlines()
        self.map = 'map' + str(map_number)
        self.map_width = int(self.map_info[0])
        self.map_height = int(self.map_info[1])
        # CREATE GRID FROM MAP DIMENSIONS
        col = self.map_width//100
        row = self.map_height//100
        self.grid = [[''] * row for i in range(col)]
        self.coords = [[x,y] for x in range(self.map_width//100) for y in range(self.map_height//100)]
        self.loc_effects_dict = dict([(tuple(c), Loc(c)) for c in app.coords])
        # START LOC
        if self.num_players == 1:
            self.start_loc = eval(self.map_info[2])
        else:
            self.start_loc = eval(self.map_info[2])[0]
            self.p2_start_loc = eval(self.map_info[2])[1]
        # LOAD MAP / GRID INFO / IMPASSABLE TERRAIN
        terrain = eval(self.map_info[3])
        for coord in terrain:
            self.grid[coord[0]][coord[1]] = 'block'
        # CONTEXT MENU
        self.con_bg = ImageTk.PhotoImage(Image.open('texture2.png').resize(( 200, root.winfo_screenheight())))
        self.context_menu = tk.Canvas(root, bg = 'black', bd=0, highlightthickness=0, relief='raised', height = root.winfo_screenheight(), width = 200)
        self.context_menu.pack_propagate(0)
        self.context_menu.pack(side = 'left', fill = 'both', expand = 'false')
        self.context_menu.create_image(0, 0, anchor = 'nw', image = self.con_bg)
        # CANVAS
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        if self.map_width < width:
            width = self.map_width
        if self.map_height < height:
            height = self.map_height
        self.canvas = tk.Canvas(root, width = width, bg = 'black', height = height, bd=0, highlightthickness=0, relief='raised')
        self.canvas.pack()
        # MAP
        if self.num_players == 1:
            fname = '1_player_maps/'
            topfname = '1_player_map_tops/'
        else:
            fname = '2_player_maps/'
            topfname = '2_player_map_tops/'
        self.map_bottom_image = Image.open(fname + 'map'+str(map_number)+'.png')
        self.map_bottom = ImageTk.PhotoImage(self.map_bottom_image)
#         self.map_bottom = ImageTk.PhotoImage(Image.open(fname + 'map'+str(map_number)+'.png'))
#         self.image_holder.append(map_bottom)
        self.map_top_image = Image.open(topfname + 'map_top'+str(map_number)+'.png')
        self.map_top = ImageTk.PhotoImage(self.map_top_image)
        self.canvas.create_image(0, 0, anchor='nw', image= self.map_bottom, tags=('mapbottom','map'))
        self.canvas.create_image(0, 0, anchor='nw', image= self.map_top, tags = ('maptop','map'))
        # CURSOR
        self.cursor_img = ImageTk.PhotoImage(Image.open("cursor.png").resize((100,100)))
        self.vis_dict['cursor'] = Vis(name = 'cursor', loc = [0,0])
        curs_pos = [0,0]
        grid_pos = [0,0]
        self.canvas.create_image(0, 0, image=self.cursor_img, tags='cursor')
        # CHOOSE WITCH IF 2 PLAYER OR FIRST LEVEL
        if protaganist_object:
            self.load_witch(witch = protaganist_object.name, player_num = 1, protaganist_object = protaganist_object)
        else:# LOADING FIRST LEVEL, NOT SAVE GAME
            self.load_witch(witch = self.p1_witch, player_num = 1, protaganist_object = None)
#             self.choose_witch()
        
    # Called twice for 2player mode, first call defaults to first player choice, second call passes player_num = 2
    def choose_witch(self, player_num = 1):
        self.avatar_popup = tk.Toplevel(root)
        self.avatar_popup.attributes('-topmost', 'true')
        self.avatar_popup.attributes("-fullscreen", True)
        self.avatar_popup.config(bg = 'black')
#         self.avatar_popup.grab_set()
        label = tk.Label(self.avatar_popup, text = 'Choose Player ' + str(player_num) + ' Witch', font = ('chalkduster', 36), fg = 'indianred', bg = 'black')
        label.pack(side = 'top')
        if player_num == 1:
            witches = [w for r,d,w in walk('./portraits/')][0]
            witches = [w for w in witches[:] if w[0] != '.']
        elif player_num == 2:
            witches = [w for r,d,w in walk('./portraits')][0]
            witches = [w for w in witches[:] if w[0] != '.']
            p1_w_fname = self.p1_witch + '.png'
            witches.remove(p1_w_fname)
        self.avatar_popup.witch_widgets = []
        self.avatar_popup.img_dict = {}
        self.wrapped_funcs = []
        for i,witch in enumerate(witches):
            f = tk.Frame(self.avatar_popup, bg = 'black')
            f.pack(side = 'left')
            self.avatar_popup.witch_widgets.append(f)
            b = tk.Button(f)
            # change below to call load_map_trigger(witchname)
            if player_num == 1 and self.num_players == 2:
                def wrap(somePartial, witch_name):
                    self.p1_witch = witch_name
                    somePartial()
                p1 = partial(self.choose_witch, player_num = 2)
                p = partial(wrap, p1, witch[:-4])
            elif player_num == 2 and self.num_players == 2:
                def wrap(somePartial, witch_name):
                    self.p2_witch = witch_name
                    somePartial()
                p1 = partial(self.create_map_curs_context, map_number = self.two_player_map_num)
                p = partial(wrap, p1, witch[:-4])
            else:
                p = partial(self.load_map_triggers, map_number = 0, witch = witch[:-4])
#             p = partial(self.load_witch, witch[:-4], player_num)
            cmd = lambda win = self.avatar_popup, p = p : self.release_wrapper(win, p)
            self.wrapped_funcs.append(p)
            photo = ImageTk.PhotoImage(Image.open('./portraits/' + witch))
            self.avatar_popup.img_dict[witch] = photo
            # DETERMINE HORIZONTAL PADDING BY SCREENSIZE
            # DEBUG ASSUMES 3 WITCHES, ASSUMES MINIMUM SCREEN WIDTH 900
            width = root.winfo_screenwidth()
            remainder_screen = width - (300 * len(witches))
            horz_pad = (remainder_screen//len(witches))//2
            b.config(image = self.avatar_popup.img_dict[witch],highlightbackground='tan3', font = ('chalkduster', 24), highlightthickness = 1, command = cmd)
            b.pack(side = 'top', padx = horz_pad)
            info = lambda w = witch[:-4] : self.show_avatar_info(w)
            b2 = tk.Button(f)
            whtspc_txt = witch[:-4].replace('_', ' ')
            b2.config(text = whtspc_txt, highlightbackground='tan3', highlightthickness= 1, fg = 'tan3', font = ('chalkduster', 24), command = info)
            b2.pack(side = 'bottom')
            self.avatar_popup.witch_widgets.append(b2)
            self.avatar_popup.witch_widgets.append(b)
        
    def load_witch(self, witch = None, player_num = None, protaganist_object = None):
        if player_num == 1:
            self.p1_witch = witch
            if self.num_players == 2:
                loc = [2,2]
            else:
                loc = self.start_loc
        elif player_num == 2:
            self.p2_witch = witch
            loc = self.p2_start_loc
        # if protaganist_object, instead load its data, RE-INIT IMAGES THAT CANNOT BE SERIALIZED BY PICKLE DUMP
        # changed from pickle to 'write attrs to encoded text file'... DEBUG
        # works but is ugly esp on load game...
        if protaganist_object:
            protaganist_object.loc = loc[:]
            witch_img = ImageTk.PhotoImage(Image.open('avatars/' + witch +'.png'))
            protaganist_object.img = witch_img
            protaganist_object.init_normal_anims()
            self.ent_dict[witch] = protaganist_object
        else:
            witch_img = ImageTk.PhotoImage(Image.open('avatars/' + witch +'.png'))
            self.ent_dict[witch] = Witch(name = witch, img = witch_img, loc = loc, owner = 'p' + str(player_num))
        self.canvas.create_image(self.ent_dict[witch].loc[0]*100+50-self.moved_right, self.ent_dict[witch].loc[1]*100+50-self.moved_down, image = self.ent_dict[witch].img, tags = self.ent_dict[witch].tags)
        self.grid[self.ent_dict[witch].loc[0]][self.ent_dict[witch].loc[1]] = witch
        # EXIT FOR 1 PLAYER
        if self.num_players == 1:
            # DEBUG LOAD BOT ENEMIES FOR PLAYER 1 HERE
            # LOAD 1 PLAYER MAP BOT UNITS
            lst = self.map_info[4:]
            c1 = 0
            end = len(lst)
            itlst = iter(lst)
            for x in itlst:
                img = eval(x)
                ent = eval(next(itlst))
                self.ent_dict[ent.number] = ent
                self.canvas.create_image(ent.loc[0]*100+50, ent.loc[1]*100+50, image = ent.img, tags = ent.tags)
                self.grid[self.ent_dict[ent.number].loc[0]][self.ent_dict[ent.number].loc[1]] = ent.number
                c1 += 1
                if c1 == end:
                    break
            root.after(999, self.start_turn)
            root.after(999, self.rebind_all)
            self.animate()
            self.start_level_popup()
            self.map_trigger_loop()
        # CHOOSE SECOND PLAYER WITCH
        elif self.num_players == 2 and player_num == 1:# and self.p2_witch == '':
            self.load_witch(witch = self.p2_witch, player_num = 2)
#             self.choose_witch(player_num = 2)
        # EXIT CHOOSING IF BOTH FINISHED AND START TURN
        else: #self.num_players == 2 and self.p2_witch != '':
            self.start_turn()
            self.animate()
        
    def start_level_popup(self):
        name = 'dethlok'+str(app.death_count)
        app.death_count += 1
#         app.dethloks[name] = tk.IntVar(0)
        def end(window, lockname):
#             app.dethloks[lockname].set(1)
            self.destroy_release(window)
        self.start_popup = tk.Toplevel()
        self.start_popup.grab_set()
        self.start_popup.attributes('-topmost', 'true')
        start_text = '''
        Defeat all the enemies...\n
        '''
        self.text = tk.Label(self.start_popup, text = start_text, font = ('chalkduster', 24), fg='indianred', bg = 'black')
        self.text.pack()
        self.close = tk.Button(self.start_popup, text = 'OK', font = ('chalkduster', 24), fg='tan3', command = lambda win = self.start_popup, ln = name : end(win, ln))
        self.close.pack()
#         root.wait_variable(app.dethloks[name])
        
            
    def start_turn(self):
        
        # INSERT new 'ONE-TURN' system, START HERE
        
        # process sot_effects for each Loc
        sot_loc_effects = [v for k,v in self.loc_effects_dict.items()]
        self.sot_loc_effect_loop(sot_loc_effects)
        
    # first handle sot effects for each Loc.sot_effects
    def sot_loc_effect_loop(self, sot_loc_effects):
        if sot_loc_effects == []:
            p = self.active_player
            ents_list = [v for k,v in app.ent_dict.items() if v.owner == p]
            ent = ents_list[0]
            self.sot_loop(ent, ents_list)
        else:
            ef = sot_loc_effects[0]
            sot_loc_effects = sot_loc_effects[1:]
            # ef should check that it still exists within the loc_effects_dict...
            if ef in [v for k,v in self.loc_effects_dict.items()] and ef.sot_func != None:
                self.focus_square(ef.loc)
                lock(ef.sot_func)
            self.sot_loc_effect_loop(sot_loc_effects)
        
    def sot_loop(self, ent, ents_list):
        ef_list = [v for k,v in ent.effects_dict.items()]
        if ef_list != []:
            ef = ef_list[0]
            self.sot_effects_loop(ef, ef_list, ent, ents_list)
        else: # NO EFFECTS FOR ENT, POP ENT_LIST, CHECK IF EMPTY, CONTINUE OR FINISH_START_TURN
            ents_list = ents_list[1:]
            if ents_list != []:
                ent = ents_list[0]
                self.sot_loop(ent, ents_list)
            else: # ENTS_LIST EMPTY, FINISH_START_TURN
                self.finish_start_turn()
            
    def sot_effects_loop(self, ef, ef_list, ent, ents_list):
        k = [k for k,v in self.ent_dict.items() if v == ent]
        if ef.sot_func != None:
            self.get_focus(k[0])
            lock(ef.sot_func)
            if ent.number not in app.all_ents().keys(): # ENT HAS DIED DURING THIS EFFECT
                ents_list = ents_list[1:]
                if ents_list != []:
                    root.after(1666, lambda e = ents_list[0], el = ents_list : self.sot_loop(e, el))
                else: # NO MORE ENTS, FINISH_END_TURN
                    root.after(1666, self.finish_start_turn)
            else:# CONTINUE PROCESSING THIS EFFECT 
                # MORE EFFECTS?
                ef_list = ef_list[1:]
                if ef_list != []: # MORE EFFECTS FOR THIS ENT
                    root.after(666, lambda ef = ef_list[0], efl = ef_list, en = ent, enl = ents_list : self.sot_effects_loop(ef, efl, en, enl))
                else: # NO MORE FOR THIS ENT, CHECK IF MORE ENTS
                    ents_list = ents_list[1:]
                    if ents_list != []: # MORE ENTS TO PROCESS EFFECTS FOR
#                         root.after(555, lambda t = 'text' : app.canvas.delete(t))
                        root.after(666, lambda e = ents_list[0], el = ents_list : self.sot_loop(e, el))
                    else: # NO MORE ENTS, FINISH_END_TURN
                        root.after(666, self.finish_start_turn)
        else:
            ef_list = ef_list[1:]
            if ef_list != []: # MORE EFFECTS FOR THIS ENT
                self.sot_effects_loop(ef_list[0], ef_list, ent, ents_list)
            else:
                ents_list = ents_list[1:]
                if ents_list != []: # MORE ENTS TO PROCESS EFFECTS FOR
                    self.sot_loop(ents_list[0], ents_list)
                else: # NO MORE ENTS, FINISH_END_TURN
                    self.finish_start_turn()
        
        
    def finish_start_turn(self):
        p = self.active_player
        if self.num_players == 1 and p == 'p1':
            self.rebind_all()
            self.get_focus(self.p1_witch)
        elif self.num_players == 2:
            self.rebind_all()
            w = self.p1_witch if p == 'p1' else self.p2_witch
            self.get_focus(w)
        elif self.num_players == 1 and p == 'p2':
            to_act = [x for x in self.ent_dict.keys() if self.ent_dict[x].owner == 'p2']
            root.after(1666, lambda ents = to_act : self.do_ai_loop(ents))
        
        
    # fix 'only some ents waiting' causes 'no enemies to act' text to appear
    def do_ai_loop(self, ents):
        global grid_pos
        if ents == []:
            waiting_status = [v.waiting for k,v in self.ent_dict.items() if v.owner == 'p2']
            if False not in waiting_status: # ARE ALL ENTS WAITING
                self.canvas.create_text(grid_pos[0]*100+49-self.moved_right, grid_pos[1]*100+49-self.moved_down, text = 'No Enemies to Act...', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
                self.canvas.create_text(grid_pos[0]*100+50-self.moved_right, grid_pos[1]*100+50-self.moved_down, text = 'No Enemies to Act...', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
                root.after(1999, lambda t = 'text' : self.canvas.delete(t))
            root.after(1999, self.end_turn)
        else:
        # CHECK FOR ENTS THAT DIED DURING AN AI ENT TURN
            for e in ents[:]:
                if e not in app.ent_dict.keys():
                    ents.remove(e)
            if ents == []:
                root.after(1666, self.end_turn)
            else:
                ent = ents[0]
                if self.ent_dict[ent].waiting == True: # IS THIS ENT WAITING
                    waiting_status = [v.waiting for k,v in self.ent_dict.items() if v.owner == 'p2']
                    if False not in waiting_status: # ARE ALL ENTS WAITING
                        self.canvas.create_text(grid_pos[0]*100+49-self.moved_right, grid_pos[1]*100+49-self.moved_down, text = 'No Enemies to Act...', font = ('Andale Mono', 16), fill = 'black', tags = 'text')
                        self.canvas.create_text(grid_pos[0]*100+50-self.moved_right, grid_pos[1]*100+50-self.moved_down, text = 'No Enemies to Act...', font = ('Andale Mono', 16), fill = 'white', tags = 'text')
                        root.after(1999, lambda t = 'text' : self.canvas.delete(t))
                        root.after(1999, self.end_turn)
                    else: # CONTINUE WITH ENTS NOT WAITING
                        ents = ents[1:]
        #                 if ents == []:
        #                     self.end_turn()
        #                 else:
                        self.do_ai_loop(ents)
                else:
                    self.get_focus(ent)
                    if self.ent_dict[ent].name == 'Kensai':# get rid of this...
                        self.ent_dict[ent].times_attacked = 0
                        self.ent_dict[ent].attacked_ids = []
                        self.ent_dict[ent].do_ai(ents)
                    else:
                        self.ent_dict[ent].do_ai(ents)
        
    # adding end of turn effects for LEVELS for 1 player...
    def end_turn(self, event = None):
        self.unbind_all()
        self.depop_context(event = None)
        # ADD EOT effects for single player levels
        if app.num_players == 1:
            # LABYRINTH
            if self.map_number == 21:
                # generate revenants based on app.revenant_rate, starts at 2
                total_revs = len([k for k,v in app.all_ents().items() if isinstance(v,Revenant)])
                if app.active_player == 'p1' and total_revs <= 4:
                    for i in range(min(2, app.revenant_rate//3)):
                        img = ImageTk.PhotoImage(Image.open('summon_imgs/Revenant.png'))
                        if self.effects_counter < 3: # prevent collision with existing ents
                            self.effects_counter += 3
                        counter = self.effects_counter
                        self.effects_counter += 1
                        id = 'b' + str(counter)
                        # get rand empty sqr
                        sqrs = [s for s in app.coords if app.grid[s[0]][s[1]] == '']
                        sqr = choice(sqrs)
                        app.grid[sqr[0]][sqr[1]] = id
                        app.ent_dict[id] = Revenant(name = 'Revenant', img = img, loc = sqr[:], owner = 'p2', number = id)
            # LIBRARY
            elif self.map_number == 121:
                if app.active_player == 'p1':
                    # get potential spawn sqrs
                    sqrs = [s for s in [[22,3],[23,3],[24,3],[22,4],[23,4],[24,4],[22,5],[23,5],[24,5]] if app.grid[s[0]][s[1]] == '']
                    if sqrs != []:
                        loc = choice(sqrs)
                        img = ImageTk.PhotoImage(Image.open('summon_imgs/Revenant.png'))
                        if self.effects_counter < 3:
                            self.effects_counter += 3
                        counter = self.effects_counter
                        self.effects_counter += 1
                        id = 'b' + str(counter)
                        app.grid[loc[0]][loc[1]] = id
                        app.ent_dict[id] = Revenant(name = 'Revenant', img = img, loc = loc[:], owner = 'p2', number = id)
        
        # first do EOT loop, rest of this becomes finish_end_turn()
        # get list of all ents, pass in first ent, loop pops front and calls 
        # handle global effects
#         eot_loc_effects = reduce(lambda x,y : x+y, [v.eot_effects for k,v in self.loc_effects_dict.items()])
        eot_loc_effects = [v for k,v in self.loc_effects_dict.items()]
        self.eot_loc_effect_loop(eot_loc_effects)
        
    # first handle eot effects for each Loc.eot_effects
    def eot_loc_effect_loop(self, eot_loc_effects):
        if eot_loc_effects == []:
            Locs = [v for k,v in self.loc_effects_dict.items()]
            keys_local_efs_tuples = [(k,v) for L in Locs for k,v in L.effects_dict.items()]
            self.local_ef_loop(keys_local_efs_tuples)
        else:
            ef = eot_loc_effects[0]
            eot_loc_effects = eot_loc_effects[1:]
            if ef in [v for k,v in self.loc_effects_dict.items()] and ef.eot_func != None:
                self.focus_square(ef.loc)
                lock(ef.eot_func)
            root.after(666, lambda e = eot_loc_effects : eot_loc_effect_loop(e))
            
    # handle each Loc object, if it has Local_Effects that need to be durated/undone
    def local_ef_loop(self, keys_local_efs_tuples):
        x = keys_local_efs_tuples
        if x == []:
            ents_list = [v for k,v in self.ent_dict.items() if v.owner == self.active_player]
            if ents_list == []:
                self.finish_end_turn()
            else:
                self.eot_loop(ents_list[0], ents_list)
        else:
            pair = x[0]
            x = x[1:]
            key = pair[0]
            ef = pair[1]
            ef.duration -= 1
            if ef.duration == 0:
                del self.loc_effects_dict[tuple(ef.loc)].effects_dict[key]
                if ef.undo_func() == None:
                    self.local_ef_loop(x)
                else:
                    root.after(1999, lambda x = x : self.local_ef_loop(x))
            else:
                self.local_ef_loop(x)
        
        
    # HANDLE EACH ENT BY PASSING ENT AND ITS EFFECTS TO EFFECTS_LOOP
    def eot_loop(self, ent, ents_list): # ent is just the first elem of elist here...change all these funcs
        ef_list = [v for k,v in ent.effects_dict.items()]
        if ef_list != []:
            ef = ef_list[0]
            self.effects_loop(ef, ef_list, ent, ents_list)
        else: # NO EFFECTS FOR ENT, POP ENT_LIST, CHECK IF EMPTY, CONTINUE OR FINISH_END_TURN
            ents_list = ents_list[1:]
            if ents_list != []:
                ent = ents_list[0]
                self.eot_loop(ent, ents_list)
            else: # ENTS_LIST EMPTY, FINISH_END_TURN
                self.finish_end_turn()
            
    # when effect exec returns None, still need to durate, check for undo, check for more effects
    # exec an ef.eot_func, pop ef_list continue
    def effects_loop(self, ef, ef_list, ent, ents_list):
        k = [k for k,v in self.ent_dict.items() if v == ent]
        if ef.eot_func != None:
            self.get_focus(k[0])
            lock(ef.eot_func)
            if ent.number not in app.all_ents().keys(): # ENT HAS DIED DURING THIS EFFECT
                ents_list = ents_list[1:]
                if ents_list != []:
                    root.after(1666, lambda e = ents_list[0], el = ents_list : self.eot_loop(e, el))
                else: # NO MORE ENTS, FINISH_END_TURN
                    root.after(1666, self.finish_end_turn)
            else:# CONTINUE PROCESSING THIS EFFECT 
                # CHECK IF EFFECT DURATION ENDS AND CALL UNDO IF SO
                ef.duration -= 1
                if ef.duration <= 0:
                    ef.undo_func()
                    key = [k for k,v in ent.effects_dict.items() if v == ef]
                    del ent.effects_dict[key[0]]
                # MORE EFFECTS?
                ef_list = ef_list[1:]
                if ef_list != []: # MORE EFFECTS FOR THIS ENT
                    root.after(555, lambda t = 'text' : self.canvas.delete(t))
                    root.after(666, lambda ef = ef_list[0], efl = ef_list, en = ent, enl = ents_list : self.effects_loop(ef, efl, en, enl))
                else: # NO MORE FOR THIS ENT, CHECK IF MORE ENTS
                    ents_list = ents_list[1:]
                    if ents_list != []: # MORE ENTS TO PROCESS EFFECTS FOR
                        root.after(555, lambda t = 'text' : app.canvas.delete(t))
                        root.after(666, lambda e = ents_list[0], el = ents_list : self.eot_loop(e, el))
                    else: # NO MORE ENTS, FINISH_END_TURN
                        root.after(666, self.finish_end_turn)
        else:
            # CHECK IF EFFECT DURATION ENDS AND CALL UNDO IF SO
            ef.duration -= 1
            if ef.duration <= 0:
                ef.undo_func()
                # if ent was not killed in undo()
                if ent.number in app.ent_dict.keys():
                    key = [k for k,v in ent.effects_dict.items() if v == ef]
                    del ent.effects_dict[key[0]]
                    ef_list = ef_list[1:]
                    if ef_list != []:
                        self.effects_loop(ef_list[0], ef_list, ent, ents_list)
                    else:
                        ents_list = ents_list[1:]
                        if ents_list != []: # MORE ENTS TO PROCESS EFFECTS FOR
                            self.eot_loop(ents_list[0], ents_list)
                        else: # NO MORE ENTS, FINISH_END_TURN
                            self.finish_end_turn()
                else:# ent was killed, skip any potential remaining effects it has
                    ents_list = ents_list[1:]
                    ents_list = [k for k in app.ent_dict.keys() if k in ents_list]
                    if ents_list != []: # MORE ENTS TO PROCESS EFFECTS FOR
                        self.eot_loop(ents_list[0], ents_list)
                    else: # NO MORE ENTS, FINISH_END_TURN
                        self.finish_end_turn()
            else:
                ef_list = ef_list[1:]
                if ef_list != []: # MORE EFFECTS FOR THIS ENT
                    self.effects_loop(ef_list[0], ef_list, ent, ents_list)
                else:
                    ents_list = ents_list[1:]
                    if ents_list != []: # MORE ENTS TO PROCESS EFFECTS FOR
                        self.eot_loop(ents_list[0], ents_list)
                    else: # NO MORE ENTS, FINISH_END_TURN
                        self.finish_end_turn()
                
                    
    def finish_end_turn(self):
        self.canvas.delete('text') # deletes the last text object when exiting loops
        ents = [v for k,v in self.ent_dict.items()]
        for ent in ents:
            # RESET SPELLS / MOVEMENT / ATTACKS
            ent.move_used = False
            if isinstance(ent, Witch):
                ent.cantrip_used = False
                ent.arcane_used = False
                ent.summon_used = False
            elif isinstance(ent, Warrior):
                ent.leap_used = False
            if isinstance(ent, Summon):
                ent.attack_used = False
        if self.active_player == 'p1':
            self.unbind_all()
            self.active_player = 'p2'
        elif self.active_player == 'p2':
            app.turn_counter += 1
            self.active_player = 'p1'
        self.start_turn()
        # END TURN SEQUENCE
                    
                    
    def get_focus(self, id):
        while grid_pos[0] < self.ent_dict[id].loc[0]:
            self.move_curs(dir = 'Right')
        while grid_pos[0] > self.ent_dict[id].loc[0]:
            self.move_curs(dir = 'Left')
        while grid_pos[1] < self.ent_dict[id].loc[1]:
            self.move_curs(dir = 'Down')
        while grid_pos[1] > self.ent_dict[id].loc[1]:
            self.move_curs(dir = 'Up')
            
    def focus_square(self, s):
        while grid_pos[0] < s[0]:
            self.move_curs(dir = 'Right')
        while grid_pos[0] > s[0]:
            self.move_curs(dir = 'Left')
        while grid_pos[1] < s[1]:
            self.move_curs(dir = 'Down')
        while grid_pos[1] > s[1]:
            self.move_curs(dir = 'Up')
    
        
    def animate(self):
        global selected, selected_vis
        for ent in self.ent_dict.keys():
            if ent not in selected:
                self.ent_dict[ent].rotate_image()
                self.canvas.delete(ent)
                self.canvas.create_image(self.ent_dict[ent].loc[0]*100+50-self.moved_right, self.ent_dict[ent].loc[1]*100+50-self.moved_down, image = self.ent_dict[ent].img, tags = app.ent_dict[ent].tags)
                app.canvas.tag_lower((app.ent_dict[ent].tags), 'maptop')
        for sqr in self.sqr_dict.keys():
            self.sqr_dict[sqr].rotate_image()
            self.canvas.delete(sqr)
            self.canvas.create_image(self.sqr_dict[sqr].loc[0]*100+50-self.moved_right, self.sqr_dict[sqr].loc[1]*100+50-self.moved_down, image = self.sqr_dict[sqr].img, tags = sqr)
        try: app.canvas.tag_raise('large')
        except: pass
#         app.canvas.tag_raise('maptop')
        app.canvas.tag_raise('cursor')
        for vis in self.vis_dict.keys():
            if vis not in selected_vis:
                self.vis_dict[vis].rotate_image()
                self.canvas.delete(vis)
                if vis == 'cursor':
                    self.canvas.create_image(self.vis_dict[vis].loc[0]*100+50, self.vis_dict[vis].loc[1]*100+50, image = self.vis_dict[vis].img, tags = vis)
                else:
                    self.canvas.create_image(self.vis_dict[vis].loc[0]*100+50-self.moved_right, self.vis_dict[vis].loc[1]*100+50-self.moved_down, image = self.vis_dict[vis].img, tags = vis)
                    
                app.canvas.tag_raise(vis)
        try: # LOWER THE CURSOR BELOW MOVING ANIMATIONS (VIS)
            app.canvas.tag_lower(('cursor'), (selected_vis))
        except: pass
        try: app.canvas.tag_raise('text')
        except: pass
#         try: app.canvas.tag_raise('fog')
#         except: pass
        self.animate_id = root.after(300, self.animate)
        
        # MAP TRIGGER LOOP
        # ALL MAP TRIGGERS ARE FUNCTIONS THAT CHECK FOR CONDITIONS AND EITHER DO STUFF IN RESPONSE
        # OR IF THEY RETURN 'victory', END LEVEL
    # need to make specific for each level
    
    def victory_popup(self, lockname, alt_route = None):
        def end(window):
            self.destroy_release(window)
            app.dethloks[lockname].set(1)
            self.end_level(alt_route = alt_route)
        self.vic_popup = tk.Toplevel()
        self.vic_popup.grab_set()
        self.vic_popup.attributes('-topmost', 'true')
        vic_text = '''
        Victory Achieved, for now...\n
        '''
        self.text = tk.Label(self.vic_popup, text = vic_text, font = ('chalkduster', 24), fg='indianred', bg = 'black')
        self.text.pack()
        self.close = tk.Button(self.vic_popup, text = 'OK', font = ('chalkduster', 24), fg='tan3', command = lambda win = self.vic_popup : end(win))
        self.close.pack()
    
    def map_trigger_loop(self):
        if self.map_number == 0:
            for mt in self.map_triggers:
                result = mt()
                if result == 'victory':
                    app.unbind_all()
                    lock(app.victory_popup)
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        elif self.map_number == 1:
            for mt in self.map_triggers:
                result = mt()
                if result == 'victory':
                    app.unbind_all()
                    lock(app.victory_popup)
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        elif self.map_number == 2:
            for mt in self.map_triggers:
                result = mt()
                if result == 'stairway':
                    app.unbind_all()
                    lock(app.victory_popup, alt_route = 21)
                    break
                elif result == 'door':
                    app.unbind_all()
                    lock(app.victory_popup, alt_route = 121)
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        elif self.map_number == 121:
            for mt in self.map_triggers:
                result = mt()
                if result == 'victory':
                    app.unbind_all()
                    lock(app.victory_popup)
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        elif self.map_number == 21:
            for mt in self.map_triggers:
                result = mt()
                if result == 'victory':
                    app.unbind_all()
                    lock(app.victory_popup)
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        elif self.map_number == 22:
            for mt in self.map_triggers:
                result = mt()
                if result == 'victory':
                    app.unbind_all()
                    lock(app.victory_popup, alt_route = 3) 
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        elif self.map_number == 122:
            for mt in self.map_triggers:
                result = mt()
                if result == 'victory':
                    app.unbind_all()
                    lock(app.victory_popup, alt_route = 3) 
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        elif self.map_number == 3:
            for mt in self.map_triggers:
                result = mt()
                if result == 'victory':
                    app.unbind_all()
                    lock(app.victory_popup)
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        elif self.map_number == 4:
            for mt in self.map_triggers:
                result = mt()
                if result == 'victory':
                    app.unbind_all()
                    lock(app.victory_popup)
                    break
                elif result == 'game over':
                    self.reset()
                    break
            else:
                self.map_trigger_id = root.after(1666, self.map_trigger_loop)
        
    def end_level(self, alt_route = None):
        global curs_pos, selected, selected_vis, map_pos, grid_pos#, is_object_selected
        root.after_cancel(self.animate_id)
        root.after_cancel(self.map_trigger_id)
        # for each effect in witch and global, call its undo
        protaganist_object  = app.ent_dict[self.p1_witch]
        protaganist_object.reset_transient_vars()
        if alt_route:
            prev_map_num = int(self.map[3:])
            new_map_num = alt_route
        else:
            prev_map_num = int(self.map[3:])
            new_map_num = prev_map_num + 1
        for child in root.winfo_children():
            child.destroy()
        # THIS WORKS, JUST NEED TO CLEAN ALL VARS LIKE GRID, SELF.STUFF, GLOBALS
        # GLOBALS
        curs_pos = [2, 2]
        # is_object_selected = False
        selected = []
        selected_vis = []
        map_pos = [0, 0]
        grid_pos = [0,0]
        self.ent_dict = {}
        self.sqr_dict = {}
        self.vis_dict = {}
        self.loc_effects_dict = {}
        self.image_holder = []
        self.map_triggers = []
        self.active_player = 'p1'
        self.moved_right = 0
        self.moved_down = 0
        self.context_buttons = []
        self.help_buttons = []
        # list to hold entity that is being animated as 'attacking'
        self.attacking = []
        self.turn_counter = 0
        self.effects_counter = 0 # used for uniquely naming Effects with the same prefix/name
        self.death_count = 0
        self.dethloks = {}
        self.cycle_q = []
        self.enemy_cycle_q = []
        self.current_ent = ''
        # CALL IN-BETWEEN LEVEL SCREEN / VICTORY SCREEN
        # GIVE ANY STORYLINE RELATED TO FINISHED AND NEXT LEVEL
        # GIVE OPTION TO SAVE PROGRESS
        # WILL NEED, AT SOME POINT, TO SAVE ACTUAL WITCH OBJECT (NOT JUST STRING NAME), TO HOLD PERSISTENT CHANGES
        self.load_cutscene(prev_map_num, new_map_num, protaganist_object)
        
        
    def load_cutscene(self, prev_map_num, new_map_num, protaganist_object):
        # Make cutscene using background pictures and overlay unit models
        self.cut_scene = ImageTk.PhotoImage(Image.open('cut_scenes/cut_scene'+str(prev_map_num)+'.png').resize((root.winfo_screenwidth(),root.winfo_screenheight())))
        self.cut_canvas = tk.Canvas(root, width = root.winfo_screenwidth(), bg = 'black', highlightthickness = 0, height = root.winfo_screenheight())
        self.cut_canvas.create_image(0,0, image =self.cut_scene, anchor = 'nw')
        self.cut_canvas.pack(side = 'top')
        filename = 'cut_scene_texts/cut_scene_text'+str(prev_map_num)+'.txt'
        with open(filename) as f:
            text = f.read()
        self.cut_text = tk.Label(root, text = text, wraplength = root.winfo_screenwidth()-90, bg = 'black', fg = 'indianred', font = ('kokonor', 18))
        self.cut_canvas.create_window(root.winfo_screenwidth()/2, root.winfo_screenheight()-180, anchor='s', window = self.cut_text)
# CONT OR SAVE BUTTONS        
        self.next_area_button = tk.Button(root, text = 'Next Area', fg = 'tan3', highlightbackground = 'tan3', font = ('chalkduster', 24), command = lambda n = new_map_num, po = protaganist_object : self.next_area(n,po))
        self.cut_canvas.create_window(root.winfo_screenwidth()/2-100, root.winfo_screenheight()-80, anchor='s', window = self.next_area_button)
        self.save_game_button = tk.Button(root, text = 'Save Game', fg = 'tan3', highlightbackground = 'tan3', font = ('chalkduster', 24), command = lambda n = new_map_num, po = protaganist_object : self.save_game(n, po))
        self.cut_canvas.create_window(root.winfo_screenwidth()/2+100, root.winfo_screenheight()-80, anchor='s', window = self.save_game_button)
        
    def next_area(self, new_map_num, protaganist_object):
        self.cut_canvas.destroy()
        # LOAD NEXT MAP
        self.load_map_triggers(new_map_num, protaganist_object = protaganist_object)
        
    def save_game(self, new_map_num, protaganist_object):
        protaganist_object.current_area = new_map_num
        # make text input, put in cut_canvas with create_window
        self.save_game_button.destroy()
        text_var = tk.StringVar()
        text_var.set('filename')
        entry = tk.Entry(root, textvariable = text_var, font = ('Andale Mono', 15), highlightbackground = 'black')
        save_b = tk.Button(root, text = 'Save', font = ('chalkduster', 22), fg = 'tan3', highlightbackground = 'black', command = lambda t = text_var, p = protaganist_object : self.do_save(t, p))
        self.cut_canvas.create_window(root.winfo_screenwidth()/2+100, root.winfo_screenheight()-45, anchor='s', window = save_b)
        self.cut_canvas.create_window(root.winfo_screenwidth()/2+100, root.winfo_screenheight()-80, anchor='s', window = entry)
        
        
        # change from using pickle dump to write to text file, on load decode the written gibberish (make it gibberish in stored form)
    def do_save(self, text_var, protag_obj):
        fname = text_var.get()
        saves = [s for r,d,s in walk('./save_games')][0]
        saves = [s for s in saves[:] if s[0] != '.']
        if fname in saves:
            text_var.set('filename already exists')
            return
        with open('save_games/'+fname, 'w+') as f:
            text_var.set('game saved')
            ####********
            # strip attrs, write all spell names to file
            f.write(protag_obj.name+'\n')
            f.write(str(list(protag_obj.cantrip_dict.keys()))+'\n')
            f.write(str(list(protag_obj.arcane_dict.keys()))+'\n')
            f.write(str(protag_obj.summon_cap)+'\n')
            f.write(str(protag_obj.base_str)+'\n')
            f.write(str(protag_obj.base_agl)+'\n')
            f.write(str(protag_obj.base_end)+'\n')
            f.write(str(protag_obj.base_dodge)+'\n')
            f.write(str(protag_obj.base_psyche)+'\n')
            f.write(str(protag_obj.base_spirit)+'\n')
            f.write(str(protag_obj.base_magick)+'\n')
            f.write(str(protag_obj.current_area)+'\n')
            f.write(str(protag_obj.summon_level)+'\n')
            ####********
#             have to strip tkinter objects from protag obj
#             protag_obj.img = None
#             protag_obj.anim_dict = {}
            # below, get all needed attributes of protag_obj, do a rudimentary 'encoding' to disguise
            # on load, ensure values are 'legal'
            # 
#             dump(protag_obj, f)
    
    
    def populate_context(self, event):
        e = self.current_pos()
        if e == '' or e == 'block':
            return
        if e != app.current_ent:
            app.depop_context(event = None)
        elif self.context_buttons != []:
            return
        self.repop_help_buttons()
        expanded_name = self.ent_dict[e].name.replace('_',' ')
        # DEBUG make info button into label that holds the info
        self.cntxt_info_bg = ImageTk.PhotoImage(Image.open('page.png'))
        bg = tk.Canvas(self.context_menu, width = 190, height = 363, bg = 'burlywood4', bd=0, relief='raised', highlightthickness=0)
        bg.pack(side = 'top')
        bg.create_image(0,0, image = self.cntxt_info_bg, anchor = 'nw')
        text = expanded_name + '\n' + self.get_info_text(e)
        bg.create_text(15, 15, text=text, width = 190, anchor = 'nw', font = ('chalkduster', 16), fill = 'indianred')
        self.context_buttons.append(bg)
        if self.ent_dict[e].owner == self.active_player:
            # insert page actions
            tup_list = list(self.ent_dict[e].get_actions().items())
            self.page_actions(tup_list = tup_list, index = 0)
            
    def page_actions(self, event = None, tup_list = None, index = None):
        # destroy old buttons
        for b in self.context_buttons:
            if isinstance(b, tk.Button):
                b.destroy()
        self.repop_help_buttons()
        for i, name_action in enumerate(tup_list[index:index+5]):
            name = name_action[0].replace('_', ' ')
            action = name_action[1]
            i += 1
            root.bind(str(i), action)
            b1 = tk.Button(app.context_menu, wraplength = 190, text = str(i) +' : '+ name, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = action)
            b1.pack(side = 'top', pady = 2)
            app.context_buttons.append(b1)
            b1.bind('<Button-2>', lambda event, b = b1, n = name : app.action_info(event, name = n, button = b))
        if index > 0:
            b4 = tk.Button(app.context_menu, text = '9 : Prev', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda t = tup_list, i = index-5 : self.page_actions(tup_list = t, index = i))
            b4.pack(side = 'top')
            root.bind(str(9), lambda e, t = tup_list, i = index-5 : self.page_actions(tup_list = t, index = i))
            app.context_buttons.append(b4)
        if len(tup_list) > len(tup_list[:index+5]):
            b3 = tk.Button(app.context_menu, text = '8 : Next', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda t = tup_list, i = index+5 : self.page_actions(tup_list = t, index = i))
            b3.pack(side = 'top')
            root.bind(str(8), lambda e, t = tup_list, i = index+5 : self.page_actions(tup_list = t, index = i))
            app.context_buttons.append(b3)
        
    def depop_context(self, event):
        # unbind any potential numeric keys bound to relative actions
        try:
            for x in range(1, 10):
                root.unbind(str(x))
        except: pass
        for b in self.context_buttons:
            b.destroy()
        self.context_buttons = []
    
    
    def move_curs(self, event = None, dir = None):
        # need to either unbind arrows, or unbind as much as possible during execution without becoming rebound on ai turn
        if event == None:
            event = Dummy()
            event.keysym = None
        frame_width = self.canvas.winfo_width()
        frame_height = self.canvas.winfo_height()
        # map_pos is how much map has moved [x,y]
        # curs_pos is relative to screen (stays within around [0,0] to [9,6] relative to screen size
        # grid_pos is always absolute position of grid where cursor appears (relates to app.grid)
        if event.keysym == 'Left' or dir == 'Left':
            if curs_pos[0] > 1: # leftmost possible cursor position
                curs_pos[0] -= 1
                grid_pos[0] -= 1
                app.vis_dict['cursor'].loc = curs_pos[:]
                app.canvas.delete('cursor')
                app.canvas.create_image(curs_pos[0]*100+50,curs_pos[1]*100+50, image = app.vis_dict['cursor'].img, tags = 'cursor')
            elif map_pos[0] > 0 : # leftmost possible map position, always zero
                map_pos[0] -= 1
                self.move_map('Left')
                grid_pos[0] -= 1
        elif event.keysym == 'Right' or dir == 'Right':
            if grid_pos[0] == ((self.map_width//100) - 1):
                return
            if curs_pos[0] < ((frame_width//100)-1):
                curs_pos[0] += 1
                grid_pos[0] += 1
                app.vis_dict['cursor'].loc = curs_pos[:]
                app.canvas.delete('cursor')
                app.canvas.create_image(curs_pos[0]*100+50,curs_pos[1]*100+50, image = app.vis_dict['cursor'].img, tags = 'cursor')
            elif map_pos[0] < ((self.map_width//100)-(frame_width//100)-1):
                self.move_map('Right')
                map_pos[0] += 1
                grid_pos[0] += 1
        elif event.keysym == 'Up' or dir == 'Up':
            if curs_pos[1] > 1: # topmost
                curs_pos[1] -= 1
                grid_pos[1] -= 1
                app.vis_dict['cursor'].loc = curs_pos[:]
                app.canvas.delete('cursor')
                app.canvas.create_image(curs_pos[0]*100+50,curs_pos[1]*100+50, image = app.vis_dict['cursor'].img, tags = 'cursor')
            elif map_pos[1] > 0: # topmost, always zero
                self.move_map('Down')
                map_pos[1] -= 1
                grid_pos[1] -= 1
        elif event.keysym == 'Down' or dir == 'Down':
            if grid_pos[1] == ((self.map_height//100)-1):
                return
            if curs_pos[1] < ((frame_height//100)-1):
                curs_pos[1] += 1
                grid_pos[1] += 1
                app.vis_dict['cursor'].loc = curs_pos[:]
                app.canvas.delete('cursor')
                app.canvas.create_image(curs_pos[0]*100+50,curs_pos[1]*100+50, image = app.vis_dict['cursor'].img, tags = 'cursor')
            elif map_pos[1] < ((self.map_height//100)-(frame_height//100)-1):
                self.move_map('Up')
                map_pos[1] += 1
                grid_pos[1] += 1

    def move_map(self, direction):
        tmp = self.ent_dict.keys()
        ents = [x for x in tmp if x not in selected]
        pers_vis = [y for y in self.vis_dict.keys() if y not in selected_vis]
        if direction == 'Left':
            self.canvas.move('map', 100, 0)
            self.moved_right -= 100
            for ent in ents:
                self.canvas.move(ent, 100, 0)
            for vis in pers_vis:
                self.canvas.move(vis, 100, 0)
            for sqr in self.sqr_dict.keys():
                self.canvas.move(sqr, 100, 0)
        elif direction == 'Right':
            self.canvas.move('map', -100, 0)
            self.moved_right += 100
            for ent in ents:
                self.canvas.move(ent, -100, 0)
            for vis in pers_vis:
                self.canvas.move(vis, -100, 0)
            for sqr in self.sqr_dict.keys():
                self.canvas.move(sqr, -100, 0)
        elif direction == 'Up':
            self.canvas.move('map', 0, -100)
            self.moved_down += 100
            for ent in ents:
                self.canvas.move(ent, 0, -100)
            for vis in pers_vis:
                self.canvas.move(vis, 0,-100)
            for sqr in self.sqr_dict.keys():
                self.canvas.move(sqr, 0, -100)
        elif direction == 'Down':
            self.canvas.move('map', 0, 100)
            self.moved_down -= 100
            for ent in ents:
                self.canvas.move(ent, 0, 100)
            for vis in pers_vis:
                self.canvas.move(vis, 0, 100)
            for sqr in self.sqr_dict.keys():
                self.canvas.move(sqr, 0, 100)

    # Helper functions
    def help(self):
        self.help_popup = tk.Toplevel(bg = 'black')
        sb = tk.Scrollbar(self.help_popup)
        self.help_popup.grab_set()
        self.help_popup.attributes('-topmost', 'true')
#         self.help_popup.config(resize = False)
#         self.help_popup.geometry(root.winfo_screenwidth(), root.winfo_screenheight())
        def on_close():
            pass
        self.help_popup.protocol('WM_DELETE_WINDOW', on_close)
        help_text = '''
        R-click on spell or action buttons to see descriptions. L-click on map to move cursor. ',' and 'l' cycle cursor over friendly units. '.' and ';' cycle cursor over enemy units. Arrow keys move cursor around map. Press 'a' when cursor is over a unit to populate the context menu (left side of screen) with information. If you own the unit and it has available actions, then those will be in the context menu when you have selected the unit with 'a'. To cancel an action after you have chosen it, press 'q'. Your witch can cast one arcane spell AND one cantrip AND use one summon AND move once per turn. Your summons can move AND use one action per turn in most cases. Except, for example, Warriors may move, attack, and use leap to move again in one turn (leap does not count towards summon limit of 1 action and 1 movement per turn). Effects caused by units or spells may target either other units themselves or in some cases locations. Either can be dispelled with some modifier. A dispel is an attempt to remove the effect, the success of which depends on the level of the effect (higher level effects are harder to dispel). The dispel formula is random-value-between-neg1-and-101 compared to spell-level minus modifier. If the randomly generated value is higher, the effect is dispelled. Save-checks are implemented similarly. They have a modifier added to a units ability score which is then compared to a random value. Save-checks are used by units to determine whether they can avoid the effects of some spell or ability and higher ability scores or positive modifiers in your favor are desirable. The to-hit formula takes 2 values to be compared against each other (usually some ability of the attacker compared to some ability of the defender). The base to-hit percentage is 50% (for equal values being compared against each other). For every point of difference in favor of the attacker, 5% is added to the success rate, and vice versa (higher defender value will subtract 5% for each point of difference). To a maximum of 99% success and a minimum of 5%. The dmg formula similarly compares some ability score against another (usually a value of the attacker compared to a value of the defender). The base value for dmg when ability scores are equal is 4. For example, if the strength value 6 of the attacker is compared to the endurance value 6 of the defender, the scores are the same so the base rate of 4 dmg is applied. For each difference in values, 1 is added/subtracted to the value to a minimum of 1 with no maximum value. Ability scores tend to range between 1-10 (abilities cannot be lower than 1 even after reduction from effects, but have no maximum value). Multiple effects can be applied to abilities like strength, agility, etc and also move range. Multiple changes of abilities caused by effects are resolved in the order in which they were applied (the most recently added effect is resolved last). The abilities str, end, agl, dodge, psyche cannot be reduced to less than 1. Move range effects often will not allow move range to be modified to less than 1, but not always.
        '''
#         self.text = tk.List(self.help_popup, yscrollcommand = sb.set, text = help_text, wraplength = 750, font = ('chalkduster', 20), fg='indianred', bg = 'black')
        self.text = tk.Text(self.help_popup, yscrollcommand = sb.set, bg = 'black', fg = 'tan3', font = ('chalkduster', 20))
        self.text.insert('end', help_text)
        self.close = tk.Button(self.help_popup, text = 'Close', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda win = self.help_popup : self.destroy_release(win))
        self.close.pack()
        self.text.pack()
        sb.pack(side = 'right', fill = 'y')
        sb.config(command = self.text.yview)
        
    def get_info_text(self, ent):
        txt = ''
        txt += 'Str:' + str(self.ent_dict[ent].get_abl('str')) + '\n'
        txt += 'Agl:' + str(self.ent_dict[ent].get_abl('agl')) + '\n'
        txt += 'End:' + str(self.ent_dict[ent].get_abl('end')) + '\n'
        txt += 'Dodge:' + str(self.ent_dict[ent].get_abl('dodge')) + '\n'
        txt += 'Psyche:' + str(self.ent_dict[ent].get_abl('psyche')) + '\n'
        txt += 'Spirit:' + str(self.ent_dict[ent].spirit) + '\n'
        if isinstance(self.ent_dict[ent], Witch):# or isinstance(self.ent_dict[ent], Trickster):
            txt += 'Magick:' + str(self.ent_dict[ent].magick) + '\n'
            txt += 'Summon Cap: ' + str(self.ent_dict[ent].summon_cap) + '\n'
        for ef in self.ent_dict[ent].effects_dict.keys():
            txt += self.ent_dict[ent].effects_dict[ef].name.replace('_',' ') + '\n'
        types = set(self.ent_dict[ent].get_types())
        for t in types:
            txt += t + '\n'
        return txt
                 
    def confirm_end(self, event = None):
        self.unbind_all()
        self.depop_context(event = None)
        l = tk.Label(self.context_menu, text = 'End Your Turn?', fg = 'indianred', bg = 'black', wraplength = 190, relief = 'raised', font = ('chalkduster', 24))
        self.context_buttons.append(l)
        root.bind('<e>', self.end_turn)
        b1 = tk.Button(self.context_menu, text = 'END', fg = 'indianred', highlightbackground = 'tan3', font = ('chalkduster', 24), command = self.end_turn)
        b1.pack(side = 'bottom')
        self.context_buttons.append(b1)
        b2 = tk.Button(self.context_menu, text = 'Cancel', fg = 'indianred', highlightbackground = 'tan3', font = ('chalkduster', 24), command = self.cancel_end_turn)
        b2.pack(side = 'bottom')
        self.context_buttons.append(b2)
        l.pack(side = 'bottom')
        
    def cancel_end_turn(self):
        self.rebind_all()
        self.depop_context(event = None)
        
        
        # kokonor
    def show_avatar_info(self, witch):
        self.info_popup = tk.Toplevel()
        self.info_popup.grab_set()
        self.info_popup.attributes('-topmost', 'true')
        self.info_popup.title(witch)
        text = open('avatar_info/' + witch + '.txt', 'r').read()
        f = tk.Frame(self.info_popup, bg = 'black')
        f.pack()
        l = tk.Label(f, text = text, wraplength = root.winfo_screenwidth()-90, bg = 'black', fg = 'indianred', font = ('kokonor', 18))
        l.pack()
        close = tk.Button(f, text = 'close', font = ('chalkduster', 24), highlightbackground = 'black', command = lambda win = self.info_popup : self.destroy_release(win))
        close.pack()
    
    def animate_squares(self, sqrs):
        for i, sqr in enumerate(sqrs):
            img = ImageTk.PhotoImage(Image.open('animations/move/0.png'))
            self.sqr_dict['sqr'+str(i)] = Sqr(img, sqr)
            self.canvas.create_image(sqr[0]*100+50-self.moved_right, sqr[1]*100+50-self.moved_down, image = self.sqr_dict['sqr'+str(i)].img, tags = 'sqr'+str(i))
            
    def cleanup_squares(self):
        for s in app.sqr_dict.keys():
            app.canvas.delete(s)
        app.sqr_dict = {}
    
    def current_pos(self):
        return self.grid[grid_pos[0]][grid_pos[1]]
        
    def exit_fullscreen(self, event):
        root.attributes("-fullscreen", False)
        
    def destroy_release(self, popup):
        popup.grab_release()
        popup.destroy()
        
    def release_wrapper(self, window, partial):
        window.grab_release()
        window.destroy()
        partial()
        
    def kill(self, id, lockname):
        def trigger_loop(triggers):
            if triggers == []:
                root.after(666, lambda id = id, ln = lockname : self.finish_kill(id, ln))
            else:
                t = triggers[0]
                triggers = triggers[1:]
                t()
                root.after(2333, lambda ts = triggers : trigger_loop(ts))
        trigger_loop(app.ent_dict[id].death_triggers)

    def finish_kill(self, id, lockname):
        # DEBUG handle if killing witch
        # If witch is dead, show popup with victory/defeat
        self.canvas.delete(id)
        # destroy related 'top' image of large Ents
        if app.ent_dict[id].type == 'large_bottom':
            app.ent_dict[id].large_undo()
        self.grid[self.ent_dict[id].loc[0]][self.ent_dict[id].loc[1]] = ''
        del self.ent_dict[id]
        ents = [k for k,v in app.ent_dict.items() if v.owner == 'p1']
        en_ents = [k for k,v in app.ent_dict.items() if v.owner != 'p1']
        app.cycle_q = ents[:]
        app.enemy_cycle_q = en_ents[:]
#         if app.num_players == 2 or app.active_player == 'p1':
#             app.rebind_all()
        app.dethloks[lockname].set(1)

    def unbind_arrows(self):
        root.unbind('<Right>')
        root.unbind('<Left>')
        root.unbind('<Up>')
        root.unbind('<Down>')
        
    def rebind_arrows(self):
        root.bind('<Right>', app.move_curs)
        root.bind('<Left>', app.move_curs)
        root.bind('<Up>', app.move_curs)
        root.bind('<Down>', app.move_curs)
        app.canvas.bind('<Button-1>', app.jump_to_square)
        
    def unbind_nonarrows(self):
        root.unbind('<a>')
        root.unbind('<q>')
#         root.unbind('<,>')
#         root.unbind('<.>')
        for x in range(10):
            root.unbind(str(x))
            
    def unbind_all(self):
        for x in range(10):
            root.unbind(str(x))
        root.unbind('<Right>')
        root.unbind('<Left>')
        root.unbind('<Up>')
        root.unbind('<Down>')
        root.unbind('<a>')
        root.unbind('<q>')
        root.unbind('<,>')
        root.unbind('<.>')
        root.unbind('<l>')
        root.unbind('<;>')
        root.unbind('<e>')
        try: app.canvas.unbind('<Button-1>')
        except: pass
#         root.unbind('<Escape>')

    def rebind_all(self):
        root.bind('<Right>', app.move_curs)
        root.bind('<Left>', app.move_curs)
        root.bind('<Up>', app.move_curs)
        root.bind('<Down>', app.move_curs)
        root.bind('<a>', app.populate_context)
        root.bind('<q>', app.depop_context)
        root.bind('<,>', app.cycle_friendly_units)
        root.bind('<l>', app.de_cycle_friendly_units)
        root.bind('<.>', app.cycle_enemy_units)
        root.bind('<;>', app.de_cycle_enemy_units)
        app.canvas.bind('<Button-1>', app.jump_to_square)
#         root.bind('<Escape>', app.exit_fullscreen)
        # DEBUG ####
#         root.bind('<d>', app.debugger)

    def confirm_quit(self):
        self.depop_context(event = None)
        self.unbind_all()
    # Instead of label just paste a bunch of intrusive text across the main canvas
    # centered around the grid_pos
        l = tk.Label(self.context_menu, text = 'Confirm Quit', relief = 'raised', fg = 'indianred', bg = 'black', font = ('chalkduster', 24))
        self.context_buttons.append(l)
        b1 = tk.Button(self.context_menu, text = 'QUIT', fg = 'indianred', highlightbackground = 'tan3', font = ('chalkduster', 24), command = root.destroy)
        self.context_buttons.append(b1)
        b2 = tk.Button(self.context_menu, text = 'Cancel', fg = 'indianred', highlightbackground = 'tan3', font = ('chalkduster', 24), command = self.cancel_quit)
        b2.pack(side = 'bottom')
        b1.pack(side = 'bottom')
        self.context_buttons.append(b2)
        l.pack(side = 'bottom')

    def cancel_quit(self):
        self.depop_context(event = None)
#         for b in self.context_buttons:
#             b.destroy()
#         self.repop_help_buttons()
        self.rebind_all()
        
    def repop_help_buttons(self):
        menu_button = tk.Button(self.context_menu, text="Menu", font = ('chalkduster', 24), fg='indianred', highlightbackground = 'tan3', command=self.open_menu)
        menu_button.pack(side = 'bottom')
        self.context_buttons.append(menu_button)
        root.bind('<e>', self.confirm_end)
        end_turn_button = tk.Button(self.context_menu, text = 'End Turn', font = ('chalkduster', 24), highlightbackground = 'tan3', command = self.confirm_end)
        end_turn_button.pack(side = 'bottom')
        self.context_buttons.append(end_turn_button)
        
    def open_menu(self):
        self.depop_context(event = None)
        self.unbind_all()
        quit_button = tk.Button(self.context_menu, text="QUIT", font = ('chalkduster', 24), fg='indianred', highlightbackground = 'tan3', command=self.confirm_quit)
        quit_button.pack(side = 'bottom')
        self.context_buttons.append(quit_button)
        help_button = tk.Button(self.context_menu, text = 'Help', font = ('chalkduster', 24), fg='indianred', highlightbackground = 'tan3', command = self.help)
        help_button.pack(side = 'bottom')
        self.context_buttons.append(help_button)
        close_button = tk.Button(self.context_menu, text = 'Close Menu', font = ('chalkduster', 24), fg='indianred', highlightbackground = 'tan3', command = self.cancel_quit)
        close_button.pack(side = 'bottom')
        self.context_buttons.append(close_button)
        
    # called when you die in 1player mode
    def reset(self):
        from sys import executable, argv
        from os import execl
        python = executable
        execl(python, python, * argv)
        
    # cycle through units on your turn with SpaceBar
    def cycle_friendly_units(self, event = None):
        my_ents = [k for k,v in app.ent_dict.items() if v.owner == 'p1']
        for id in my_ents: # if ents has changed, reset the cycle order
            if id not in app.cycle_q:
                app.cycle_q = my_ents[:]
                break
        id = app.cycle_q[0] # after possible reset, grab first in line to focus
        app.cycle_q = app.cycle_q[1:]+[app.cycle_q[0]] # move to back of q
        app.focus_square(app.ent_dict[id].loc)

    def de_cycle_friendly_units(self, event = None):
        my_ents = [k for k,v in app.ent_dict.items() if v.owner == 'p1']
        for id in my_ents: # if ents has changed, reset the cycle order
            if id not in app.cycle_q:
                app.cycle_q = my_ents[:]
                break
        app.cycle_q = [app.cycle_q[-1]] + app.cycle_q[:-1] # put it back in front
        id = app.cycle_q[-1] # after possible reset, grab last in line to focus
        app.focus_square(app.ent_dict[id].loc)
        
    def cycle_enemy_units(self, event = None):
        en_ents = [k for k,v in app.ent_dict.items() if v.owner != 'p1']
        for id in en_ents: # if ents has changed, reset the cycle order
            if id not in app.enemy_cycle_q:
                app.enemy_cycle_q = en_ents[:]
                break
        id = app.enemy_cycle_q[0] # after possible reset, grab first in line to focus
        app.enemy_cycle_q = app.enemy_cycle_q[1:]+[app.enemy_cycle_q[0]] # move to back of q
        app.focus_square(app.ent_dict[id].loc)
        
    def de_cycle_enemy_units(self, event = None):
        en_ents = [k for k,v in app.ent_dict.items() if v.owner != 'p1']
        for id in en_ents: # if ents has changed, reset the cycle order
            if id not in app.enemy_cycle_q:
                app.enemy_cycle_q = en_ents[:]
                break
        app.enemy_cycle_q = [app.enemy_cycle_q[-1]] + app.enemy_cycle_q[:-1] # put it back in front
        id = app.enemy_cycle_q[-1]
        app.focus_square(app.ent_dict[id].loc)
        
        
    def jump_to_square(self, event):
        x = (event.x + app.moved_right)//100
        y = (event.y + app.moved_down)//100
        if (app.map_width//100)-1 <= x or (app.map_height//100)-1 <= y:
            return
        if x < 1 or y < 1:
            return
        app.focus_square([x,y])
        
    def all_ents(self):
        return {k:v for k,v in self.ent_dict.items() if v.type != 'large'}
        
    def spell_target_ents(self):
        return {k:v for k,v in self.ent_dict.items() if v.type != 'large' and 'psyshield' not in v.get_types()}
        
    def action_target_ents(self):
        return {k:v for k,v in self.ent_dict.items() if v.type != 'large' and 'invis' not in v.get_types()}
        
    # create popup with description of action name
    # ADD manually lookup name for all actions and spells
    def action_info(self, event = None, name = None, button = None):
        def end(window):
            self.destroy_release(window)
        self.info_popup = tk.Toplevel()
        self.info_popup.grab_set()
        self.info_popup.attributes('-topmost', 'true')
        def on_close():
            pass
        self.info_popup.protocol('WM_DELETE_WINDOW', on_close)
        info_text = name + '\n' + app.info[name]
        self.text = tk.Label(self.info_popup, text = info_text, wraplength = 400, font = ('chalkduster', 24), fg='indianred', bg = 'black')
        self.text.pack()
        self.close = tk.Button(self.info_popup, text = 'OK', font = ('chalkduster', 24), fg='tan3', command = lambda win = self.info_popup : end(win))
        self.close.pack()
#         self.info_popup.overrideredirect(1)
#         self.info_popup.lift()

        
    def debugger(self, event):
        print(app.ent_dict.keys())
        app.ent_dict[app.p1_witch].move_used = False
        app.ent_dict[app.p1_witch].summon_used = False
        app.ent_dict[app.p1_witch].arcane_used = False
        app.ent_dict[app.p1_witch].cantrip_used = False

root = tk.Tk()
app = App(master=root)

root.bind('<Right>', app.move_curs)
root.bind('<Left>', app.move_curs)
root.bind('<Up>', app.move_curs)
root.bind('<Down>', app.move_curs)
root.bind('<a>', app.populate_context)
root.bind('<q>', app.depop_context)
root.bind('<l>', app.de_cycle_friendly_units)
root.bind('<,>', app.cycle_friendly_units)
root.bind('<;>', app.de_cycle_enemy_units)
root.bind('<.>', app.cycle_enemy_units)
app.unbind_all()
# root.bind('<Escape>', app.exit_fullscreen)
#### DEBUG ####
root.bind('<d>', app.debugger)


root.configure(background = 'black')

root.attributes('-transparent', True)
root.attributes("-fullscreen", True)

width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry('%sx%s' % (width, height))

app.mainloop()