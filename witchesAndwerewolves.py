# Seems to be some kind of bug in shadow attack during confirm attack mouse clicks, have to click multiple times? maybe just not clicking properly with touchpad? yeah definitely had to click 2 or 3 times but only one print debug shows up 'succesful shadow attack' on hit

# During 'place summon' unbind/rebind 'a' to confirm placement

# to 'force focus / grab / prevent events' in canvases, have to do it manually with unbind/bind

# warriors seem maybe underpowered / too easy to avoid, maybe allow them to move back or sideways just one square

# balance right now might be more a problem of shadows being too consistent compared to other summons, am I making sure to exploit their 'stay on one color square' drawback?

# Need faster key for getting 'info', bind a key that immediately shows popup or populates context with info, maybe 'a' should immediately show info along with relevant context in context menu

# can use         self.confirm_end_popup.protocol("WM_DELETE_WINDOW", lambda win = self.confirm_end_popup : self.destroy_release(win))  .... edit for appropriate context, handle exit through window manager 'X' for Toplevel popups


# context menu: increase size, app holds lists of different 'areas', leftmost area holds portrait of active_player with 'turn' label on top of portrait which is always in view, next leftmost are context buttons which hold selected entity info/actions which are visible when able to be selected and not deferring to placement buttons, placement buttons are next leftmost and destroy other context buttons when selectable which are for confirming actions and selecting placement/choice of summons/attacks/spell effects, visualizations of attack/spell effects appear temporarily next to placement buttons, when effects of placement buttons happen or are canceled they are destroyed allowing for replacement of next selected context buttons, rightmost buttons are held in list called menu buttons which always stay in place during placement of context and placement buttons they are help/end turn/quit, when menu buttons are pressed quit/endturn destroy menu buttons and populate menu with 'confirm yes no' which when pressed destroy themselves and repopulate menu buttons, placement buttons take precedence and focus from all other buttons since no action should be taken until their effects/choices either happen or are canceled, context buttons disallow for further population of context until they are canceled with 'q' or turn ends or choice among them is made which populates placement buttons

# what happens to context_menu when attempting to populate with more buttons than it can hold

# what about Toplevel info screens allowing for 'exit' 'X' out? other events are blocked, should change to a large label over top of the main canvas which grab_set()

# make Witch movement an attr so it can be modified (spells,effects) to increase/decrease movement range
# make Warriors limited movement in same way as Witch, (cannot 'walk around' obstacles)
# tricksters and shadows should not be limited in the same way

# how would 'prevent targeting with spells or attacks' without modifying every attack/spell

# make trickster confuse shorter range, tried debuff agl, consider halving confuse dist

# center end turn 'yes / no' buttons

# how to represent 'barriers' / impassable terrain on map? how to show in grid, maybe a type of entity? can they be damaged?
# are some immovable terrain features and some created from spells? how does this affect placement / movement? would having a string in grid that isn't in ent_dict mess up any loops through its keys?

# do visualizations for warrior attack and damage, really need to make it obvious which summons are owned by who

# change 'z' for cancel move to 'q'

# fix dmg distribution

# show current player in context menu, consider making context menu larger, consider putting summon/spell choices in context menu
# maybe show portraits of selected units in context menu

# consider buffing stats on witches

# confirm 'quit'

# remember: whenever a unit is 'moved', its loc updated, also need to update its origin

# differentiate images for opposing players, color changes or overlays

# when 'q' is rebinded to cancel stuff (attack, placement), also rebind 'a' to confirm instead of needed mouseclick
# after populating context for selected unit you own, bind a key for each action?

# To prevent windowbar in popups, Instead of toplevels make windows in canvas, increase size of context menu to fit

# also/instead of 'antag_witch', make 'levels' or just a bunch of units that will be easier to program AI for
# currently would be extremely difficult to make challenging AI with equal sides

# start thinking about what map and map animation to use

# maybe take photo for portrait background instead of scroll texture

# splash screen?

import tkinter as tk
from tkinter import ttk
import os
from PIL import ImageTk,Image
from random import choice, randrange
from functools import partial
import time

curs_pos = [0, 0]
is_object_selected = False
selected = ''

map_pos = [0, 0]

grid_pos = [0,0]

# import pygame
# freq = 44100     # audio CD quality
# bitsize = -16    # unsigned 16 bit
# channels = 1     # 1 is mono, 2 is stereo
# buffer = 1024    # number of samples (experiment to get right sound)
# pygame.mixer.init(freq, bitsize, channels, buffer)
# pygame.mixer.music.set_volume(0.7) # optional volume 0 to 1.0
# pygame.mixer.music.load('bloodMilkandSky.mp3')
# pygame.mixer.music.play(-1, 0)

class Dummy():
    def __init__(self):
        pass

class Sqr():
    def __init__(self, img, loc):
        self.img = img
        self.loc = loc
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in os.walk('animations/move/')][0]
        anims = [a for a in anims[:] if a[0] != '.']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/move/' + anim))
            self.anim_dict[i] = a
            
    def rotate_image(self):
        total_imgs = len(self.anim_dict.keys())-1
        if self.anim_counter == total_imgs:
            self.anim_counter = 0
        else:
            self.anim_counter += 1
        self.img = self.anim_dict[self.anim_counter]

class Entity():
    def __init__(self, name, img, loc, owner):
        self.name = name
        self.img = img
        self.loc = loc
        self.owner = owner
        self.move_used = False
        # when ent moved by effect other than regular movement, must update origin also (square of origin at begin of turn)
        self.origin = []
        # buttons placed in context menu other than through 'populate_context', so they can be removed separately
        self.placement_buttons = []
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in os.walk('./animations/' + self.name + '/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/' + self.name + '/' + anim))
            self.anim_dict[i] = a
            
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
        anims = [a for r,d,a in os.walk('./attack_animations/' + self.name + '/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('attack_animations/' + self.name + '/' + anim))
            self.anim_dict[i] = a
            
    def init_normal_anims(self):
        self.anim_dict = {}
        self.anim_counter = 0
        anims = [a for r,d,a in os.walk('./animations/' + self.name + '/')][0]
        anims = [a for a in anims[:] if a[-3:] == 'png']
        for i, anim in enumerate(anims):
            a = ImageTk.PhotoImage(Image.open('animations/' + self.name + '/' + anim))
            self.anim_dict[i] = a
            
#     def rotate_attack_images(self):
#         # clear out anim dict and replace with attack anims
#         total_imgs = len(self.anim_dict.keys())-1
#         if self.anim_counter == total_imgs:
#             self.anim_counter = 0
#         else:
#             self.anim_counter += 1
#         self.img = self.anim_dict[self.anim_counter]
        
    def set_attr(self, attr, amount):
        if attr == 'str':
            self.str += amount
        elif attr == 'agl':
            self.agl += amount
        elif attr == 'end':
            self.end += amount
        elif attr == 'dodge':
            self.dodge += amount
        elif attr == 'psyche':
            self.psyche += amount
        elif attr == 'spirit':
            self.spirit += amount
        elif isinstance(self, Witch):
            if attr == 'magick':
                self. magick += amount
            
    def to_hit(self, a1, a2):
        base = 5
        dif = a1 - a2
        base += dif
        chance = base * 10
        rand = randrange(1, 100)
        if rand < chance:
            return True
        else:
            return False
            
    # add random element?
    def damage(self, a1, a2):
        base = 5
        dif = a1 - a2
        if base + dif < 1: return 1 
        else: return base + dif
            
    def info(self):
        self.info_popup = tk.Toplevel()
        self.info_popup.grab_set()
        self.info_popup.attributes('-topmost', 'true')
        self.info_popup.config(bg = 'black')
        info_label = tk.Label(self.info_popup, text = self.name +'\n'+ self.__class__.__name__, font = ('chalkduster', 20), fg = 'tan3', bg = 'black')
        info_label.pack()
        strength = tk.Label(self.info_popup, text = 'Strength : ' + str(self.str), font = ('chalkduster', 20), fg = 'tan3', bg = 'black')
        strength.pack()
        agl = tk.Label(self.info_popup, text = 'Agility : ' + str(self.agl), font = ('chalkduster', 20), fg = 'tan3', bg = 'black')
        agl.pack()
        end = tk.Label(self.info_popup, text = 'Endurance : ' + str(self.end), font = ('chalkduster', 20), fg = 'tan3', bg = 'black')
        end.pack()
        dodge = tk.Label(self.info_popup, text = 'Dodge : ' + str(self.dodge), font = ('chalkduster', 20), fg = 'tan3', bg = 'black')
        dodge.pack()
        psyche = tk.Label(self.info_popup, text = 'Psyche : ' + str(self.psyche), font = ('chalkduster', 20), fg = 'tan3', bg = 'black')
        psyche.pack()
        spirit = tk.Label(self.info_popup, text = 'Spirit : ' + str(self.spirit), font = ('chalkduster', 20), fg = 'tan3', bg = 'black')
        spirit.pack()
        if isinstance(self, Witch):
            magick = tk.Label(self.info_popup, text = 'Magick : ' + str(self.magick), font = ('chalkduster', 20), fg = 'tan3', bg = 'black')
            magick.pack()
        close = tk.Button(self.info_popup, text = 'close', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda win = self.info_popup : app.destroy_release(win))
        close.pack()
    

class Summon(Entity):
    def __init__(self, name, img, loc, owner, number):
        self.number = number
        super().__init__(name, img, loc, owner)
        
class Trickster(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'confuse':self.trickster_attack}
        self.attack_used = False
        self.str = 2
        self.agl = 3
        self.end = 2
        self.dodge = 4
        self.psyche = 5
        self.spirit = 10
        super().__init__(name, img, loc, owner, number)
        
        
        
    def trickster_attack(self):
        print('trickster attack called')
        if self.attack_used == True:
            return
        sqrs = []
        coord_pairs = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        for coord in coord_pairs:
            if abs(coord[0] - self.loc[0]) == 1 and coord[1] == self.loc[1]:
                sqrs.append(coord)
            elif coord[0] == self.loc[0] and abs(coord[1] - self.loc[1]) == 1:
                sqrs.append(coord)
        app.animate_squares(sqrs)
        app.depopulate_context(event = None)
        cmd = lambda s = sqrs: self.check_hit(s)
        b = tk.Button(app.context_menu, text = 'Confirm Confuse', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = cmd)
        b.pack(side = 'left')
        app.context_buttons.append(b)
        self.placement_buttons.append(b)
        root.unbind('<q>')
        root.bind('<q>', self.cancel_attack)
        
        
    def check_hit(self, sqrs):
        if grid_pos not in sqrs:
            return
        if app.current_pos() == '':
            return
        tar = app.current_pos()
        app.unbind_all()
        if self.to_hit(self.psyche, app.ent_dict[tar].psyche) == True:
            self.success = tk.Label(app.context_menu, text = 'Confuse Hit', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
            self.success.pack(side = 'left')
            app.after(900, lambda s = sqrs, t = tar:self.do_attack(sqrs, tar))
        else:
            self.miss = tk.Label(app.context_menu, text = 'Confuse Missed', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
            self.miss.pack(side = 'left')
            app.after(900, lambda win = self.miss : self.cancel_attack( event = None, win = win))
        self.attack_used = True
        
    def do_attack(self, sqrs, tar):
        self.success.destroy()
        # DEBUG need to rebind at least arrow keys to choose square, still need to be unbinding other keys 'a' 'q'
        app.rebind_all()
        root.unbind('q')
        root.unbind('a')
        dist = self.damage(self.agl, app.ent_dict[tar].dodge)
        app.depopulate_context(event = None)
        for b in self.placement_buttons:
            b.destroy()
        for s in app.sqr_dict.keys():
            app.canvas.delete(s)
        app.sqr_dict = {}
        sqrs = self.confuse_sqrs(dist)
        if sqrs == []:
            self.attack_used = True
            self.cancel_attack(event = None)
            return
        app.animate_squares(sqrs)
        b = tk.Button(app.context_menu, text = 'Choose Square', font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = lambda id = tar, s = sqrs : self.confuse(id, s))
        b.pack(side = 'left')
        self.placement_buttons.append(b)

    
    def confuse(self, id, sqrs):
        if grid_pos not in sqrs:
            return
        app.grid[app.ent_dict[id].loc[0]][app.ent_dict[id].loc[1]] = ''
        app.canvas.delete(id)
        oldloc = app.ent_dict[id].loc
        app.ent_dict[id].loc = grid_pos[:]
        app.ent_dict[id].origin = grid_pos[:]
        app.grid[grid_pos[0]][grid_pos[1]] = id
        app.canvas.create_image(app.ent_dict[id].loc[0]*100+50-app.moved_right, app.ent_dict[id].loc[1]*100+50-app.moved_down, image = app.ent_dict[id].img, tags = id)
        self.cancel_attack(event = None)
    
    def confuse_sqrs(self, dist):
        sqr_list = []
        coord_pairs = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        for coord in coord_pairs:
            if app.grid[coord[0]][coord[1]] == '':
                if abs(coord[0] - self.loc[0]) + abs(coord[1] - self.loc[1]) <= dist:
                    sqr_list.append(coord)
        return sqr_list
    
    # maybe rename to cleanup_attack and ensure every logical exit point goes here
    def cancel_attack(self, event, win = None):
        if win:
            win.destroy()
        app.depopulate_context(event = None)
        for b in self.placement_buttons:
            b.destroy()
        for s in app.sqr_dict.keys():
            app.canvas.delete(s)
        app.sqr_dict = {}
        app.rebind_all()
    
    def legal_moves(self):
        move_list = []
        coord_pairs = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        for coord in coord_pairs:
            if app.grid[coord[0]][coord[1]] == '':
                if abs(coord[0] - self.loc[0]) == 1 and abs(coord[1] - self.loc[1]) == 2:
                    move_list.append(coord)
                elif abs(coord[0] - self.loc[0]) == 2 and abs(coord[1] - self.loc[1]) == 1:
                    move_list.append(coord)
        return move_list
        

class Shadow(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'attack':self.shadow_attack}
        self.attack_used = False
        self.str = 3
        self.agl = 3
        self.end = 2
        self.dodge = 4
        self.psyche = 4
        self.spirit = 8
        super().__init__(name, img, loc, owner, number)
        
        
    def shadow_attack(self):
        if self.attack_used == True:
            return
        sqrs = []
        coord_pairs = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        # same for both players, attack on diag
        for coord in coord_pairs:
            if abs(coord[0] - self.loc[0]) == 1 and abs(coord[1] - self.loc[1]) == 1:
                sqrs.append(coord)
        app.animate_squares(sqrs)
        # create 'confirm attack' button
        app.depopulate_context(event = None)
        cmd = lambda s = sqrs: self.check_hit(s)
        b = tk.Button(app.context_menu, text = 'Confirm Attack', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = cmd)
        b.pack(side = 'left')
        app.context_buttons.append(b)
        self.placement_buttons.append(b)
        root.unbind('<q>')
        root.bind('<q>', self.cancel_attack)
        
    def check_hit(self, sqrs):
        if grid_pos not in sqrs:
            return
        if app.current_pos() == '':
            return
        tar = app.current_pos()
        app.unbind_all()
        if self.to_hit(self.str, app.ent_dict[tar].end) == True:
            print('successful shadow attack')
            # VISUAL TO HIT, go ahead and show dmg here also
            dmg = self.damage(self.psyche, app.ent_dict[tar].psyche)
            dmg //= 2
            if dmg == 0: dmg = 1
            self.success = tk.Label(app.context_menu, text = 'Attack Success!', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
            self.success.pack(side = 'left')
            self.damage = tk.Label(app.context_menu, text = str(dmg) + ' Spirit', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
            self.damage.pack(side = 'left')
            if isinstance(app.ent_dict[tar], Witch):
                self.magdmg = tk.Label(app.context_menu, text = str(dmg) + ' Magick', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
                self.magdmg.pack(side = 'left')
            root.after(900, lambda id = tar, dmg = dmg : self.do_attack(id, dmg))
        elif self.to_hit(self.str, app.ent_dict[tar].end) == False:
            self.miss = tk.Label(app.context_menu, text = 'Attack Missed!', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
            self.miss.pack(side = 'left')
            root.after(900, lambda win = self.miss : self.cancel_attack(event = None, win = win))
        self.attack_used = True
    
    def do_attack(self, id, dmg):
        self.success.destroy()
        self.damage.destroy()
        try:
            self.magdmg.destroy()
        except:
            pass
        if isinstance(app.ent_dict[id], Witch):
            app.ent_dict[id].set_attr('magick', -dmg)
        app.ent_dict[id].set_attr('spirit', -dmg)
        if app.ent_dict[id].spirit <= 0:
            app.kill(id)
        self.cancel_attack( event = None)
    
    def cancel_attack(self, event, win = None):
        if win:
            win.destroy()
        app.depopulate_context(event = None)
        for b in self.placement_buttons:
            b.destroy()
        for s in app.sqr_dict.keys():
            app.canvas.delete(s)
        app.sqr_dict = {}
        app.rebind_all()
    
    def legal_moves(self):
        move_list = []
        coord_pairs = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        for coord in coord_pairs:
        # move on diag, 3 sqrs, same for both players
            if app.grid[coord[0]][coord[1]] == '':
                if abs(coord[0] - self.loc[0]) == abs(coord[1] - self.loc[1]) and abs(coord[0] - self.loc[0]) <= 3:
                    move_list.append(coord)
        return move_list

        
class Warrior(Summon):
    def __init__(self, name, img, loc, owner, number):
        self.actions = {'attack':self.warrior_attack}
        self.attack_used = False
        self.str = 4
        self.agl = 4
        self.end = 4
        self.dodge = 2
        self.psyche = 2
        self.spirit = 13
        super().__init__(name, img, loc, owner, number)
        
        
    def warrior_attack(self):
        if self.attack_used == True:
            return
        sqrs = []
        coord_pairs = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        if app.active_player == 'p1':
            for coord in coord_pairs:
                if abs(coord[0] - self.loc[0]) == 1 and coord[1] == self.loc[1]:
                    sqrs.append(coord)
                elif abs(coord[0] - self.loc[0]) == 1 and coord[1]-1 == self.loc[1]:
                    sqrs.append(coord)
                elif coord[0] == self.loc[0] and coord[1]-1 == self.loc[1]:
                    sqrs.append(coord)
        elif app.active_player == 'p2':
            for coord in coord_pairs:
                if abs(coord[0] - self.loc[0]) == 1 and coord[1] == self.loc[1]:
                    sqrs.append(coord)
                elif abs(coord[0] - self.loc[0]) == 1 and coord[1]+1 == self.loc[1]:
                    sqrs.append(coord)
                elif coord[0] == self.loc[0] and coord[1]+1 == self.loc[1]:
                    sqrs.append(coord)
        app.animate_squares(sqrs)
        app.depopulate_context(event = None) 
        cmd = lambda s = sqrs: self.check_hit(s)
        b = tk.Button(app.context_menu, text = 'Confirm Attack', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = cmd)
        b.pack(side = 'left')
        app.context_buttons.append(b)
        self.placement_buttons.append(b)
        root.unbind('<q>')
        root.bind('<q>', self.cancel_attack)
        
    def check_hit(self, sqrs):
        if grid_pos not in sqrs:
            return
        if app.current_pos() == '':
            return
        tar = app.current_pos()
        app.unbind_all()
        if self.to_hit(self.agl, app.ent_dict[tar].dodge) == True:
            print('hit')
            # call self.init_attack_anims() here to replace self.anim_dict with other images
            # on exit, re init normal anims
            self.init_attack_anims()
            dmg = self.damage(self.str, app.ent_dict[tar].end)
            self.success = tk.Label(app.context_menu, text = 'Attack Hit!', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
            self.success.pack(side = 'left')
            self.dmg = tk.Label(app.context_menu, text = str(dmg) + ' Spirit', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
            self.dmg.pack(side = 'left')
            root.after(1200, lambda id = tar, dmg = dmg : self.do_attack(id, dmg))
        else:
            self.miss = tk.Label(app.context_menu, text = 'Attack Missed!', font = ('chalkduster', 24), fg = 'indianred', bg = 'tan2')
            self.miss.pack(side = 'left')
            root.after(1200, lambda win = self.miss : self.cancel_attack(event = None, win = win))
        self.attack_used = True
        
    def do_attack(self, id, dmg):
        self.success.destroy()
        self.dmg.destroy()
        app.ent_dict[id].set_attr('spirit', -dmg)
        if app.ent_dict[id].spirit <= 0:
            app.kill(id)
            print('target killed')
        self.cancel_attack(event = None)
        # re init normal anims 
        self.init_normal_anims()
    
    def cancel_attack(self, event, win = None):
        app.rebind_all()
        if win:
            win.destroy()
        app.depopulate_context(event = None)
        for b in self.placement_buttons:
            b.destroy()
        for s in app.sqr_dict.keys():
            app.canvas.delete(s)
        app.sqr_dict = {}
        self.init_normal_anims()
    
    def legal_moves(self):
        loc = self.loc
        mvlist = []
        coords = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        def findall(loc, start, dist):
            if start > dist:
                return
            # need different 'front' depending on player
            if app.active_player == 'p1':
                front = [c for c in coords if c[0] == loc[0] and c[1]-1 == loc[1] and app.grid[c[0]][c[1]] == '']
            elif app.active_player == 'p2':
                front = [c for c in coords if c[0] == loc[0] and c[1]+1 == loc[1] and app.grid[c[0]][c[1]] == '']
            for s in front:
                mvlist.append(s)
                findall(s, start+1, dist)
        findall(loc, 1, 3) 
        setlist = []
        for l in mvlist:
            if l not in setlist:
                setlist.append(l)
        return setlist
                    
class Witch(Entity):
    def __init__(self, name, img, loc, owner):
        self.actions = {'spell':self.spell, 'summon':self.summon}
        self.spell_used = False
        self.summon_used = False
        self.spell_dict = {}
        self.summon_dict = {}
        
        if name == 'Agnes_Sampson':
            self.spell_dict['Plague'] = self.plague
            self.spell_dict['Psionic Push'] = self.psionic_push
            self.spell_dict['Curse of Oriax'] = self.curse_of_oriax
            self.spell_dict['Gravity'] = self.gravity
            self.spell_dict["Beleth's Command"] = self.beleths_command
            self.str = 4
            self.agl = 2
            self.end = 3
            self.dodge = 3
            self.psyche = 4
            self.spirit = 75
            self.magick = 75
        elif name == 'Fakir_Ali':
            self.spell_dict['Horrid Wilting'] = self.horrid_wilting
            self.spell_dict['Boiling Blood'] = self.boiling_blood
            self.spell_dict['Dark Sun'] = self.dark_sun
            self.spell_dict['Command of Osiris'] = self.command_of_osiris
            self.spell_dict['Disintegrate'] = self.disintegrate
            self.str = 3
            self.agl = 2
            self.end = 5
            self.dodge = 3
            self.psyche = 3
            self.spirit = 85
            self.magick = 70
        elif name == 'Morgan_LeFay':
            self.spell_dict['Enchant'] = self.enchant
            self.spell_dict['Counterspell'] = self.counterspell
            self.spell_dict["Nature's Wrath"] = self.natures_wrath
            self.spell_dict["Noden's Command"] = self.nodens_command
            self.spell_dict['Wild Hunt'] = self.wild_hunt
            self.str = 2
            self.agl = 4
            self.end = 3
            self.dodge = 4
            self.psyche = 3
            self.spirit = 70
            self.magick = 85
            
        super().__init__(name, img, loc, owner)
        
    def spell(self):
        if self.spell_used == True:
            return
        # SPELL
        self.spell_popup = tk.Toplevel()
        self.spell_popup.grab_set()
        self.spell_popup.attributes('-topmost', 'true')
        for name, spell in self.spell_dict.items():
            b1 = tk.Button(self.spell_popup, text = name, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda win = self.spell_popup, func = self.spell_dict[name] : app.release_wrapper(win, func))
            b1.pack()
        b2 = tk.Button(self.spell_popup, text = 'Cancel', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda win = self.spell_popup : app.destroy_release(win))
        b2.pack()
    
    def summon(self):
        if self.summon_used == True:
            return
        self.summon_popup = tk.Toplevel()
        self.summon_popup.attributes('-topmost', 'true')
        self.summon_popup.grab_set()
        # commands need to pass through self.release_wrapper(win,partial) to grab_release
        b1 = tk.Button(self.summon_popup, text = 'Warrior', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda x = partial(self.place_summon, 'Warrior') : app.release_wrapper(self.summon_popup, x))
        b1.pack()
        b2 = tk.Button(self.summon_popup, text = 'Trickster', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda x = partial(self.place_summon, 'Trickster') : app.release_wrapper(self.summon_popup, x))
        b2.pack()
        b3 = tk.Button(self.summon_popup, text = 'Shadow', font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = lambda x = partial(self.place_summon, 'Shadow') : app.release_wrapper(self.summon_popup, x))
        b3.pack()
#         b4 = tk.Button(self.summon_popup, text = 'Bard', command = self.place_bard)
#         b4.pack()
#         b5 = tk.Button(self.summon_popup, text = 'Plaguebearer', command = self.place_plaguebearer)
#         b5.pack()
        b6 = tk.Button(self.summon_popup, text = 'Cancel', font = ('chalkduster', 24), highlightbackground = 'tan3', fg='tan3', command = lambda win = self.summon_popup : self.destroy_release(win))
        b6.pack()
    
    def cancel_placement(self, event):
        app.depopulate_context(event = None)
        for b in self.placement_buttons:
            b.destroy()
        for s in app.sqr_dict.keys():
            app.canvas.delete(s)
        app.sqr_dict = {}
        root.unbind('<q>')
        root.bind('<q>', app.depopulate_context)

    
    def place_summon(self, type):
        root.unbind('<q>')
        root.bind('<q>', self.cancel_placement)
        self.summon_popup.destroy()
        app.depopulate_context(event = None)
        coords = coord_pairs = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        sqrs = [c for c in coords if abs(c[0]-self.loc[0]) + abs(c[1]-self.loc[1]) == 1 and app.grid[c[0]][c[1]] == '']
        app.animate_squares(sqrs)
        if type == 'Warrior':
            cls = Warrior
        elif type == 'Trickster':
            cls = Trickster
        elif type == 'Shadow':
            cls = Shadow
        cmd = lambda x = cls, y = sqrs : self.place(x, y)
        b = tk.Button(app.context_menu, text = 'Place '+type, font = ('chalkduster', 24), fg='tan3', highlightbackground = 'tan3', command = cmd)
        b.pack(side = 'left')
        app.context_buttons.append(b)
        self.placement_buttons.append(b)
        
        
    def place(self, summon, sqrs):
        if grid_pos not in sqrs:
            return
        root.unbind('<q>')
        root.bind('<q>', app.depopulate_context)
        if app.active_player == 'p1':
            number = 'a' + str(len(self.summon_dict.keys()))
        elif app.active_player == 'p2':
            number = 'b' + str(len(self.summon_dict.keys()))
        if summon == Warrior:
            name = 'warrior'
            img = ImageTk.PhotoImage(Image.open('warrior.png'))
        elif summon == Trickster:
            name = 'trickster'
            img = ImageTk.PhotoImage(Image.open('trickster.png'))
        elif summon == Shadow:
            name = 'shadow'
            img = ImageTk.PhotoImage(Image.open('shadow.png'))
        s = summon(name = name, img = img, loc = grid_pos[:], owner = app.active_player, number = number)
        app.ent_dict[number] = s
        self.summon_dict[number] = s
        app.canvas.create_image(grid_pos[0]*100+50-app.moved_right, grid_pos[1]*100+50-app.moved_down, image = img, tags = number)
        app.grid[grid_pos[0]][grid_pos[1]] = number
        # DELETE SQUARES
        for s in app.sqr_dict.keys():
            app.canvas.delete(s)
        app.sqr_dict = {}
        for b in app.context_buttons:
            b.destroy()
        app.context_buttons = []
        self.summon_used = True
        
        # Need to incorporate 'magick cost' and rules for regenerating/regaining magick, probably certain squares that replenish a set amount every turn, or squares that appear for a limited amount of time/turns that replenish
# AGNES SPELLS
        # Agnes' spells center around Death/Decay/Disease/Telekinetics
    def plague(self):
            # Make attk (psyche versus end) on any summon within range 4 and all adjacent summons have attrs reduced to 1 (str, agl, end, dodge, psyche) lasting until 3 opp turns have passed
        print('plague')
        self.spell_used = True
    def psionic_push(self):
            # Make attk (psyche versus agl) against any target within range 4, move the target from square of origin in any lateral direction up to 4 squares but not through any obstacles (ents or impassable squares, not edge of map), if target 'collides' (movement stopped before 4 squares because of obstacle) target takes spirit damage (str versus end) and target takes damage (str versus end) if capable of taking spirit damage
        print('psionic push')
        self.spell_used = True
    def curse_of_oriax(self):
            # Any target is inflicted with 'curse', while cursed takes 2 spirit damage at end of every owner's turn and then afflicted ent may 'to hit self' (own strength versus own inverted end, 1 becomes 5, 5 becomes 1...) to end the curse, while afflicted with curse of oriax target may not be afflicted with any other curse conditions
        print('curse_of_oriax')
        self.spell_used = True
    def gravity(self):
            # Target ent within range 4 and all ents within range 2 of target may not move until two of their owner's turns have ended, targets are only affected by normal movement, can still be moved through spell/attack effects, if moved out of affected squares then no longer restricted movement, any ent moving into affected squares is immediately halted and is affected in the same way until spell ends
        print('gravity')
        self.spell_used = True
    def beleths_command(self):
            # Caster is affect by 'command', while affected cannot be affected by other 'command' effects until spell ends (one 'command' effect at a time), any ent using an attack against caster first must 'to hit' caster's psyche versus attacker's psyche, a success results in normal attack, failure causes spirit damage to attacker (caster's psyche versus attacker's end) and no effects from the attack, lasts until caster has 3 turns end
        print('beleths_command')
        self.spell_used = True
        
# FAKIR ALI SPELLS
        # Ali's spells center around Heat/Fire/Resistance/Mummification
    def horrid_wilting(self):
            # make attack (psyche versus str) spirit damage, on any target within range 4 and all adjacent enemy units
        print('horrid_wilting')
        self.spell_used = True
    def boiling_blood(self):
            # Caster takes spirit damage (own inverted psyche versus own end) and affects one 'warrior' summon within range 3, any attacks made by the affected target do +5 spirit damage if they would otherwise do any spirit damage, target's agl is increased to 5 if it is less than 5, end is reduced to 1, either value may be later modified but this modification takes precedence over previous effects, affected ent takes 1 spirit damage at the end of every owner's turn
        print('boiling_blood')
        self.spell_used = True
    def dark_sun(self):
            # Any caster owned 'shadow' summons within range 2 get an extra attack if they have already attacked once this turn
        print('dark_sun')
        self.spell_used = True
    def command_of_osiris(self):
            # Caster is affected by 'command' effect, normal 'command' rules apply as above, Caster cannot move, can still be moved by spell/attack effects, at end of caster's turn any adjacent ents take spirit damage (caster's psyche versus ent's end), all spirit damage done to caster is reduced to 1, lasts until caster has 3 turns end
        print('command_of_osiris')
        self.spell_used = True
    def disintegrate(self):
            # Caster must make 'to hit' psyche versus psyche on target summon within range 4, affected summon has attrs (str, agl, end, dodge, psyche) reduced to 1 and cannot move until 2 of its owners turns have ended, attrs or movement cannot be affected by other spells/attack effects
        print('disintegrate')
        self.spell_used = True
        
# MORGAN SPELLS
        # Morgan's spells center around Nature/Earth/Weather/Illusion
    def enchant(self):
            # any summon within range 4 has attrs (str, agl, end, dodge, psyche) set to 5 until 3 opp turns have passed, prevents further modification while active
        print('enchant')
        self.spell_used = True
    def wild_hunt(self):
            # Creates 3 summons within range 2 of caster or up to 3 if not enough squares available, first is Boar (stats 3,3,3,2,2,4,0) movement range 2 attack any adjacent, second is wolf (2,3,2,4,2,3,0) movement range 3 attack any adjacent, third is hawk (2,4,2,4,3,2,0) movement range 4 not impeded by other units/obstacles attack any adjacent
        print('wild_hunt')
        self.spell_used = True
    def nodens_command(self):
            # Command rules apply, caster cannot move, all squares within range 2 of caster become 'water' (impassable terrain) any ents currently occupying these squares are moved to a random square 'at edge' (closest available square to edge of water squares or first unoccupied square if all 'edge' squares are occupied), at end of turn caster heals 4 spirit, lasts until caster has 3 turns end (healing happens first)
        print('nodens_command')
        self.spell_used = True
    def natures_wrath(self):
            # Choose a square within range 5, all ents within range 2 of square must 'to hit' their inverted agl versus dodge at the end of every caster's turn, those that 'hit' suffer 3 spirit damage, lasts 3 caster's turns (effect happens 'before' end turn, effects happen 3 times)
        print('natures_wrath')
        self.spell_used = True
    def counterspell(self):
            # Choose a spell effect 'in play', make 'to hit' psyche versus effect's owner's psyche, on success cancel all effects from the spell (call its cleanup function) and effect's owner takes magick damage psyche versus psyche
        print('counterspell')
        self.spell_used = True
    
    # Maybe change name, used not only for finding legal moves, but sqrs within 3 spaces of entity that are unoccupied
    def legal_moves(self):
        loc = self.loc
        mvlist = []
        coords = [[x,y] for x in range(app.map_width//100) for y in range(app.map_height//100)]
        def findall(loc, start, dist):
            if start > dist:
                return
            adj = [c for c in coords if abs(c[0] - loc[0]) + abs(c[1] - loc[1]) == 1 and app.grid[c[0]][c[1]] == '']
            for s in adj:
                mvlist.append(s)
                findall(s, start+1, dist)
        findall(loc, 1, 3) 
        setlist = []
        for l in mvlist:
            if l not in setlist:
                setlist.append(l)
        return setlist

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.img_dict = {}
        self.ent_dict = {}
        self.sqr_dict = {}
        self.active_player = 'p1'
        self.opponent = 'computer'
        self.moved_right = 0
        self.moved_down = 0
        self.context_buttons = []
        # list to hold entity that is being animated as 'attacking'
        self.attacking = []
        
        
        self.choose_map()
        
    def choose_map(self):
        self.marquee = tk.Label(root, text = 'This Game Brought to you by', fg = 'tan3', bg = 'black', font=("chalkduster", 36))
        self.marquee.pack(side = 'top')
        self.production =tk.Label(root, text = '-HATRED-', fg = 'indianred', bg = 'black', font = ('herculanum', 46))
        self.production.pack(side = 'top')
        self.choosemap = tk.Label(root, text = 'Choose Map', fg = 'tan3', bg = 'black', font = ('chalkduster', 38))
        self.choosemap.pack()
        # CHOOSE MAPS
        maps = [m for r,d,m in os.walk('./maps')][0]
        self.map_button_list = []
        self.tmp_mapimg_dict = {}
        for i,map in enumerate(maps):
            b = tk.Button(root)
            cmd = lambda indx = i : self.load_map(indx)
            photo = ImageTk.PhotoImage(Image.open('./maps/' + map).resize((300,300)))
            self.tmp_mapimg_dict['map'+str(i)] = photo
            b.config(image = self.tmp_mapimg_dict['map'+str(i)], bg = 'black', highlightbackground = 'tan3', command = cmd)
            # DEBUG packing will have to be fixed here for different screen sizes
            b.pack(side = 'left', padx = 55)
            self.map_button_list.append(b)
            
    def load_map(self, map_number):
        self.marquee.destroy()
        self.production.destroy()
        self.choosemap.destroy()
        del self.tmp_mapimg_dict
        for b in self.map_button_list:
            b.destroy()
        del self.map_button_list
        self.create_map_curs_context(map_number)
            
    def help(self):
        self.help_popup = tk.Toplevel()
        self.help_popup.grab_set()
        self.help_popup.attributes('-topmost', 'true')
        help_text = '''
        You control witch in top left corner\n
        Spacebar selects an object for movement\n
        Press 'z' to cancel movement context\n
        Arrow keys move cursor around map\n
        Cursor over an object you control and press 'a' to see action options\n
        Press 'q' to cancel the context menu for a selected object\n
        Cursor over enemy controlled object and press 'a' for available info\n
        Your witch can cast one spell AND use one summon per turn AND move once\n
        Your summons can move AND use one action per turn\n
        '''
        self.text = tk.Label(self.help_popup, text = help_text, font = ('chalkduster', 24), fg='indianred', bg = 'black')
        self.text.pack()
        self.close = tk.Button(self.help_popup, text = 'Close', font = ('chalkduster', 24), fg='tan3', command = lambda win = self.help_popup : self.destroy_release(win))
        self.close.pack()
            
    def create_map_curs_context(self, map_number):
        # GET MAP DIMENSIONS
        filename = 'map_info/map' + str(map_number) + '.txt'
        with open(filename) as f:
            map_size = f.read().splitlines()
        self.map = 'map' + str(map_number)
        self.map_width = int(map_size[0])
        self.map_height = int(map_size[1])
        # CREATE GRID FROM MAP DIMENSIONS
        col = self.map_width//100
        row = self.map_height//100
        self.grid = [[''] * row for i in range(col)]
        # CONTEXT MENU
        self.con_bg = ImageTk.PhotoImage(Image.open('scroll.png').resize((root.winfo_screenwidth(), 50)))
        self.context_menu = tk.Canvas(root, bg = 'black', bd=0, highlightthickness=0, relief='ridge', width = root.winfo_screenwidth(), height = 50)
        self.context_menu.pack_propagate(0)
        self.context_menu.pack(side = 'top', fill = 'both', expand = 'false')
        self.context_menu.create_image(0, 0, anchor = 'nw', image = self.con_bg)
        # QUIT should have 'are you sure' popup
        self.quit = tk.Button(self.context_menu, text="QUIT", font = ('chalkduster', 24), fg='indianred', highlightbackground = 'tan3', command=self.confirm_quit)
        self.quit.pack(side = 'right')
        # END TURN
        self.end = tk.Button(self.context_menu, text = 'End Turn', font = ('chalkduster', 24), highlightbackground = 'tan3', command = self.confirm_end)
        self.end.pack(side = 'right')
        # HELP
        self.help_b = tk.Button(self.context_menu, text = 'Help', font = ('chalkduster', 24), fg='indianred', highlightbackground = 'tan3', command = self.help)
        self.help_b.pack(side = 'right')
        # CANVAS
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        if self.map_width < width:
            width = self.map_width
        if self.map_height < height:
            height = self.map_height
        self.canvas = tk.Canvas(root, width = width, bg = 'black', height = height, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()
        # MAP
        self.map_img = ImageTk.PhotoImage(Image.open('./maps/map'+str(map_number)+'.jpg').resize((self.map_width, self.map_height)))
        self.canvas.create_image(0, 0, anchor='nw', image=self.map_img, tags='map')

        
        # CURSOR
        self.cursor_img = ImageTk.PhotoImage(Image.open("cursor.png").resize((100,100)))
        self.canvas.create_image(0,0, anchor='nw', image=self.cursor_img, tags='curs')
        self.choose_witch()
        
        
    def choose_witch(self):
        self.avatar_popup = tk.Toplevel()
        self.avatar_popup.attributes('-topmost', 'true')
        self.avatar_popup.attributes("-fullscreen", True)
        self.avatar_popup.config(bg = 'black')
        self.avatar_popup.grab_set()
        label = tk.Label(self.avatar_popup, text = 'Choose Your Witch', font = ('chalkduster', 36), fg = 'indianred', bg = 'black')
        label.pack(side = 'top')
        witches = [w for r,d,w in os.walk('./portraits/')][0]
        witches = [w for w in witches[:] if w[0] != '.']
        self.avatar_popup.witch_widgets = []
        self.avatar_popup.img_dict = {}
        self.wrapped_funcs = []
        for i,witch in enumerate(witches):
            f = tk.Frame(self.avatar_popup, bg = 'black')
            f.pack(side = 'left')
            self.avatar_popup.witch_widgets.append(f)
            b = tk.Button(f)
            p = partial(self.load_witch, witch[:-4])
            cmd = lambda win = self.avatar_popup, p = p : self.release_wrapper(win, p)
            self.wrapped_funcs.append(p)
            photo = ImageTk.PhotoImage(Image.open('./portraits/' + witch))
            self.avatar_popup.img_dict[witch] = photo
            b.config(image = self.avatar_popup.img_dict[witch],highlightbackground='tan3', font = ('chalkduster', 24), highlightthickness = 1, command = cmd)
            b.pack(side = 'top', padx = 45)
            info = lambda w = witch[:-4] : self.show_avatar_info(w)
            b2 = tk.Button(f)
            whtspc_txt = witch[:-4].replace('_', ' ')
            b2.config(text = whtspc_txt, highlightbackground='tan3', highlightthickness= 1, fg = 'tan3', font = ('chalkduster', 24), command = info)
            b2.pack(side = 'bottom')
            self.avatar_popup.witch_widgets.append(b2)
            self.avatar_popup.witch_widgets.append(b)

    def show_avatar_info(self, witch):
        self.info_popup = tk.Toplevel()
        self.info_popup.grab_set()
        self.info_popup.attributes('-topmost', 'true')
        self.info_popup.title(witch)
        text = open('avatar_info/' + witch + '.txt', 'r').read()
        f = tk.Frame(self.info_popup)
        f.pack()
        l = tk.Label(f, text = text, font = ('chalkduster', 24))
        l.pack()
        close = tk.Button(self.info_popup, text = 'close', font = ('chalkduster', 24), highlightbackground = 'tan3', command = lambda win = self.info_popup : self.destroy_release(win))
        close.pack()
    
    def load_witch(self, witch):
        self.protag_witch = witch
        protag_witch_img = ImageTk.PhotoImage(Image.open('avatars/' + witch +'.png'))
        self.ent_dict[witch] = Witch(name = witch, img = protag_witch_img, loc = [1, 1], owner = 'p1')
        self.canvas.create_image(self.ent_dict[witch].loc[0]*100+50-self.moved_right, self.ent_dict[witch].loc[1]*100+50-self.moved_down, image = self.ent_dict[witch].img, tags = witch)
        self.grid[self.ent_dict[witch].loc[0]][self.ent_dict[witch].loc[1]] = witch
        self.place_antag()
    
    def place_antag(self):
        remain_witches = [w for r,d,w in os.walk('./avatars')][0]
        remain_witches = [w for w in remain_witches[:] if w[0] != '.']
        remain_witches = [w[:-4] for w in remain_witches[:]] 
        remain_witches.remove(self.protag_witch)
        self.antag_witch = choice(remain_witches)
        antag_witch_img = ImageTk.PhotoImage(Image.open('avatars/' + self.antag_witch +'.png'))
        self.ent_dict[self.antag_witch] = Witch(name = self.antag_witch, img = antag_witch_img, loc = [self.map_width//100-2, self.map_height//100-2], owner = 'p2')
        self.canvas.create_image(self.ent_dict[self.antag_witch].loc[0]*100+50-self.moved_right, self.ent_dict[self.antag_witch].loc[1]*100+50-self.moved_down, image = self.ent_dict[self.antag_witch].img, tags = self.antag_witch)
        self.grid[self.ent_dict[self.antag_witch].loc[0]][self.ent_dict[self.antag_witch].loc[1]] = self.antag_witch
        # ANIMATE / START_ACTION
        self.animate()
        self.start_turn()
        
    def start_turn(self):
        p = self.active_player
        print('start action')
        w = self.protag_witch if p == 'p1' else self.antag_witch
        self.get_focus(w)
        
    def confirm_end(self):
        self.confirm_end_popup = tk.Toplevel()
        self.confirm_end_popup.grab_set()
        self.confirm_end_popup.attributes('-topmost', 'true')
        self.confirm_end_popup.config(bg = 'black')
        self.confirm_end_popup.protocol("WM_DELETE_WINDOW", lambda win = self.confirm_end_popup : self.destroy_release(win))
        label = tk.Label(self.confirm_end_popup, text = 'End Your Turn?', fg = 'tan3', bg = 'black', font = ('chalkduster', 24))
        label.pack(side = 'top')
        b1 = tk.Button(self.confirm_end_popup, text = 'Yes', fg = 'tan3', font = ('chalkduster', 24), highlightbackground = 'tan3', command = lambda win = self.confirm_end_popup, func = self.end_turn : self.release_wrapper(win, func))
        b1.pack(side = 'left')
        b2 = tk.Button(self.confirm_end_popup, text = 'No', fg = 'tan3',font = ('chalkduster', 24), highlightbackground = 'tan3', command = lambda win = self.confirm_end_popup : self.destroy_release(win))
        b2.pack(side = 'left')
        
    def end_turn(self):
        print('end turn')
        self.depopulate_context(event = None)
        # clean all entity 'has_x' for active_player
        for ent in self.ent_dict.keys():
            if self.ent_dict[ent].owner == self.active_player:
                self.ent_dict[ent].move_used = False
                if isinstance(self.ent_dict[ent], Witch):
                    self.ent_dict[ent].spell_used = False
                    self.ent_dict[ent].summon_used = False
                elif isinstance(self.ent_dict[ent], Summon):
                    self.ent_dict[ent].attack_used = False
        # IF NO HUMAN OPPONENT, INSERT BOT ACTION HERE
        if self.active_player == 'p1':
            self.active_player = 'p2'
        else:
            self.active_player = 'p1'
        self.start_turn()
        
        
        
    def get_focus(self, w):
        while grid_pos[0] < self.ent_dict[w].loc[0]:
            self.move_curs(dir = 'Right')
        while grid_pos[0] > self.ent_dict[w].loc[0]:
            self.move_curs(dir = 'Left')
        while grid_pos[1] < self.ent_dict[w].loc[1]:
            self.move_curs(dir = 'Down')
        while grid_pos[1] > self.ent_dict[w].loc[1]:
            self.move_curs(dir = 'Up')
        
    def animate(self):
        # Prepare for attack animations, do them while showing hit/damage labels in do_attack
        # when do_attack, add ent to 'atk list', here in animate if ent is in atk list, use alternate animation logic, 
        # ent will need a func like rotate_image that cycles it through attack images, so for 2 seconds in tohit/damage 'afters' (currently 1.8 secs), object will be animated through atk animations instead
        for ent in self.ent_dict.keys():
            if ent != selected:
                self.ent_dict[ent].rotate_image()
                self.canvas.delete(ent)
                self.canvas.create_image(self.ent_dict[ent].loc[0]*100+50-self.moved_right, self.ent_dict[ent].loc[1]*100+50-self.moved_down, image = self.ent_dict[ent].img, tags = ent)
        for sqr in self.sqr_dict.keys():
            self.sqr_dict[sqr].rotate_image()
            self.canvas.delete(sqr)
            self.canvas.create_image(self.sqr_dict[sqr].loc[0]*100+50-self.moved_right, self.sqr_dict[sqr].loc[1]*100+50-self.moved_down, image = self.sqr_dict[sqr].img, tags = sqr)
#             elif ent in self.attacking:
#                 self.ent_dict[ent].rotate_attack_image()
#                 self.canvas.delete(ent)
#                 self.canvas.create_image(self.ent_dict[ent].loc[0]*100+50-self.moved_right, self.ent_dict[ent].loc[1]*100+50-self.moved_down, image = self.ent_dict[ent].img, tags = ent)
        root.after(300, self.animate)
    
    def populate_context(self, event):
        e = self.current_pos()
        if e == '':
            return
        if self.context_buttons != []:
            print('error here app.context_buttons not empty')
            return
        expanded_name = e.replace('_',' ')
        # if generic summon (name ends with number), show class name instead of proper Noun
        try:
            num = int(e[-1])
            expanded_name = self.ent_dict[e].__class__.__name__
        except:
            pass
        if self.ent_dict[e].owner != self.active_player:
            b = tk.Button(self.context_menu, text = expanded_name, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = self.ent_dict[e].info)
            b.pack(side = 'left')
            self.context_buttons.append(b)
            return
        act_dict = self.ent_dict[e].actions
        b = tk.Button(self.context_menu, text = expanded_name, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = self.ent_dict[e].info)
        b.pack(side = 'left')
        self.context_buttons.append(b)
        for act, call in act_dict.items():
            b = tk.Button(self.context_menu, text = act, font = ('chalkduster', 24), fg = 'tan3', highlightbackground = 'tan3', command = call)
            b.pack(side = 'left')
            self.context_buttons.append(b)
        
    def depopulate_context(self, event):
        for b in self.context_buttons:
            b.destroy()
        self.context_buttons = []
    
    def cancel_pickup(self, event):
        root.bind('<a>', self.populate_context)
        global is_object_selected, selected
        if is_object_selected == True:
            for sqr in self.sqr_dict.keys():
                self.canvas.delete(sqr)
            self.sqr_dict = {}
            self.grid[self.ent_dict[selected].origin[0]][self.ent_dict[selected].origin[1]] = selected
            # return selected entity to sqr of origin
            self.canvas.delete(selected)
            self.canvas.create_image(self.ent_dict[selected].origin[0]*100+50-self.moved_right, self.ent_dict[selected].origin[1]*100+50-self.moved_down, image = self.ent_dict[selected].img, tags = selected)
            self.ent_dict[selected].loc = self.ent_dict[selected].origin[:]
            w = selected
            is_object_selected = False
            selected = ''
            self.get_focus(w)
    
    def pickup_putdown(self, event):
        # unbind 'a' until returns or is 'putdown'
        root.unbind('<a>')
        global is_object_selected, selected, curs_pos
        # PICK UP
        if is_object_selected == False and self.current_pos() != '':
            unit = self.current_pos()
            print('unit ', unit)
            if self.ent_dict[unit].owner == self.active_player and self.ent_dict[unit].move_used == False:
                is_object_selected = True
                # SQUARES / MOVEMENT
                if self.ent_dict[unit].move_used == False:
                    sqrs = self.ent_dict[unit].legal_moves()
                else:
                    sqrs = []
                self.animate_squares(sqrs)
                self.ent_dict[unit].origin = self.ent_dict[unit].loc[:]
                self.ent_dict[unit].loc = [None, None]
                selected = unit
                # REMOVE UNIT FROM GRID
                self.grid[grid_pos[0]][grid_pos[1]] = ''
            # ELSE SHOW INFO DEBUG finish this
            elif self.ent_dict[unit].owner != self.active_player:
                # rebind 'a', exits naturally
                root.bind('<a>', self.populate_context)
                print('not yours')
        # PUT DOWN
        elif is_object_selected == True and self.current_pos() == '':
            # Restrict movement, if grid_pos is within highlighted sqrs
            sqrs = [self.sqr_dict[s].loc for s in self.sqr_dict.keys()]
            if grid_pos not in sqrs:
                return
            self.ent_dict[selected].move_used = True
            # erase old sqrs
            for sqr in self.sqr_dict.keys():
                self.canvas.delete(sqr)
            self.sqr_dict = {}
            is_object_selected = False
            unit = selected
            selected = ''
            self.ent_dict[unit].loc = grid_pos[:]
            self.ent_dict[unit].origin = grid_pos[:]
            self.grid[grid_pos[0]][grid_pos[1]] = unit
            root.bind('<a>', self.populate_context)
    
    def move_curs(self, event = None, dir = None):
        if event == None:
            event = Dummy()
            event.keysym = None
        frame_width = self.canvas.winfo_width()
        frame_height = self.canvas.winfo_height()
        if event.keysym == 'Left' or dir == 'Left':
            if curs_pos[0] > 0: # leftmost possible cursor position, always zero
                self.canvas.move('curs', -100, 0)
                self.canvas.move(selected, -100, 0)
                curs_pos[0] -= 1
                grid_pos[0] -= 1
            elif map_pos[0] > 0: # leftmost possible map position, always zero
                map_pos[0] -= 1
                self.move_map('Left')
                grid_pos[0] -= 1
        elif event.keysym == 'Right' or dir == 'Right':
            if grid_pos[0] == ((self.map_width//100) - 1):
                return
            if curs_pos[0] < ((frame_width//100)-1):
                self.canvas.move('curs', 100, 0)
                self.canvas.move(selected, 100, 0)
                curs_pos[0] += 1
                grid_pos[0] += 1
            elif map_pos[0] < ((self.map_width//100)-(frame_width//100)):
                self.move_map('Right')
                map_pos[0] += 1
                grid_pos[0] += 1
        elif event.keysym == 'Up' or dir == 'Up':
            if curs_pos[1] > 0: # topmost, always zero
                self.canvas.move('curs', 0, -100)
                self.canvas.move(selected, 0, -100)
                curs_pos[1] -= 1
                grid_pos[1] -= 1
            elif map_pos[1] > 0: # topmost, always zero
                self.move_map('Down')
                map_pos[1] -= 1
                grid_pos[1] -= 1
        elif event.keysym == 'Down' or dir == 'Down':
            if grid_pos[1] == ((self.map_height//100)-1):
                return
            if curs_pos[1] < ((frame_height//100)-1):
                self.canvas.move('curs', 0, 100)
                self.canvas.move(selected, 0, 100)
                curs_pos[1] += 1
                grid_pos[1] += 1
            elif map_pos[1] < ((self.map_height//100)-(frame_height//100)):
                self.move_map('Up')
                map_pos[1] += 1
                grid_pos[1] += 1


    def move_map(self, direction):
        tmp = self.ent_dict.keys()
        ents = [x for x in tmp if x != selected]
        if direction == 'Left':
            self.canvas.move('map', 100, 0)
            self.moved_right -= 100
            for ent in ents:
                self.canvas.move(ent, 100, 0)
            for sqr in self.sqr_dict.keys():
                self.canvas.move(sqr, 100, 0)
        elif direction == 'Right':
            self.canvas.move('map', -100, 0)
            self.moved_right += 100
            for ent in ents:
                self.canvas.move(ent, -100, 0)
            for sqr in self.sqr_dict.keys():
                self.canvas.move(sqr, -100, 0)
        elif direction == 'Up':
            self.canvas.move('map', 0, -100)
            self.moved_down += 100
            for ent in ents:
                self.canvas.move(ent, 0, -100)
            for sqr in self.sqr_dict.keys():
                self.canvas.move(sqr, 0, -100)
        elif direction == 'Down':
            self.canvas.move('map', 0, 100)
            self.moved_down -= 100
            for ent in ents:
                self.canvas.move(ent, 0, 100)
            for sqr in self.sqr_dict.keys():
                self.canvas.move(sqr, 0, 100)

    # Helper functions
    def animate_squares(self, sqrs):
        for i, sqr in enumerate(sqrs):
            img = ImageTk.PhotoImage(Image.open('animations/move/0.png'))
            self.sqr_dict['sqr'+str(i)] = Sqr(img, sqr)
            self.canvas.create_image(sqr[0]*100+50-self.moved_right, sqr[1]*100+50-self.moved_down, image = self.sqr_dict['sqr'+str(i)].img, tags = 'sqr'+str(i))
    
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
        
    def kill(self, id):
        # DEBUG handle if killing witch
        # If witch is dead, show popup with victory/defeat
        self.canvas.delete(id)
        self.grid[self.ent_dict[id].loc[0]][self.ent_dict[id].loc[1]] = ''
        del self.ent_dict[id]
        # if id begins with 'a' belongs to protag_witch, else belongs to antag_witch
        if id[0] == 'a':
            del self.ent_dict[self.protag_witch].summon_dict[id]
        elif id[0] == 'b':
            del self.ent_dict[self.antag_witch].summon_dict[id]
            
    def unbind_all(self):
        root.unbind('<Right>')
        root.unbind('<Left>')
        root.unbind('<Up>')
        root.unbind('<Down>')
        root.unbind('<space>')
        root.unbind('<z>')
        root.unbind('<a>')
        root.unbind('<q>')
        root.unbind('<Escape>')

    def rebind_all(self):
        root.bind('<Right>', app.move_curs)
        root.bind('<Left>', app.move_curs)
        root.bind('<Up>', app.move_curs)
        root.bind('<Down>', app.move_curs)
        root.bind('<space>', app.pickup_putdown)
        root.bind('<z>', app.cancel_pickup)
        root.bind('<a>', app.populate_context)
        root.bind('<q>', app.depopulate_context)
        root.bind('<Escape>', app.exit_fullscreen)

    def confirm_quit(self):
        pass

root = tk.Tk()
app = App(master=root)

root.bind('<Right>', app.move_curs)
root.bind('<Left>', app.move_curs)
root.bind('<Up>', app.move_curs)
root.bind('<Down>', app.move_curs)
root.bind('<space>', app.pickup_putdown)
root.bind('<z>', app.cancel_pickup)
root.bind('<a>', app.populate_context)
root.bind('<q>', app.depopulate_context)
root.bind('<Escape>', app.exit_fullscreen)

root.configure(background = 'black')

root.attributes('-transparent', True)
root.attributes("-fullscreen", True)

width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry('%sx%s' % (width, height))

app.mainloop()