import pygame
import sys
import math

pygame.init()
pygame.display.set_caption("Combinatorial + Sequential Circuit Simulator")
screen = pygame.display.set_mode((1500, 900)) #screen size
clock = pygame.time.Clock() # control frame rate

FONT = pygame.font.SysFont(None, 24) # default font for text rendering
GRID_SIZE = 20 # size of grid squares for snapping blocks 

# GLOBAL STATE
typed_target = None # reference to input block
clock_tick = False # triggered by space bar to run a clock cycle

########################################################################
# TOOLBAR BUTTON 
########################################################################
class Button:
    def __init__(self, label, x, y): # takes text label and xy position
        self.label = label
        self.rect = pygame.Rect(x, y, 110, 40) # rectangle button

    def draw(self, surf, mouse_pos):
        color = (164, 176, 190) if self.rect.collidepoint(mouse_pos) else (116, 125, 140) # button color to lighter grey when collide 
        pygame.draw.rect(surf, color, self.rect, border_radius=4) # draw button
        text = FONT.render(self.label, True, (0,0,0)) # text label in black
        surf.blit(text, (self.rect.x + 20, self.rect.y + 10)) # blit onto screen


########################################################################
# PORTS 
########################################################################
class InputPort:
    def __init__(self, parent, ox, oy): 
        self.parent = parent # reference logic block the port belongs to 
        self.ox = ox # port offsets based on parent's top left corner
        self.oy = oy
        self.signal = 0 # boolean recieved by the port 
        self.connected_wires = [] # should be only 1

    @property # calculates and returns the absolute screen position of the port based on the parent block's position and the port's offset
    def pos(self):
        return (self.parent.x + self.ox, self.parent.y + self.oy)


class OutputPort:
    def __init__(self, parent, ox, oy):
        self.parent = parent
        self.ox = ox
        self.oy = oy
        self.signal = 0
        self.connected_wires = [] # can be multiple 

    @property
    def pos(self):
        return (self.parent.x + self.ox, self.parent.y + self.oy)


########################################################################
# WIRE OBJECT
########################################################################
class Wire:
    def __init__(self, start_port):
        self.start = start_port
        self.end = None # while user is dragging 

    def contains_point(self, pt): # checks if mouse (pt) is close enough to wire (knows which to delete with right click)
        if self.end is None:
            return False

        x1, y1 = self.start.pos
        x2, y2 = self.end.pos
        px, py = pt # mouse position

        A = px - x1 # vector from start to mouse
        B = py - y1
        C = x2 - x1 # vector from start to end
        D = y2 - y1

        dot = A*C + B*D # dot product of the two vectors (reflect how much the two vectors point in the same direction)
        len_sq = C*C + D*D # squared length from start to end
        if len_sq == 0: # if distance is non, no wire drawn
            return False

        t = max(0, min(1, dot / len_sq)) # indicate where the closest point on the line containing the wire is located
        cx = x1 + t*C # actual coordinates of the closest point
        cy = y1 + t*D
        dist = math.hypot(px - cx, py - cy) # Euclidean distance between the mouse and the closest point on the wire 

        return dist < 6 # click tolerance (consider hit within 6 pixels)

    def draw(self, surface, mouse_pos=None):
        start_pos = self.start.pos
        end_pos = self.end.pos if self.end else mouse_pos # use input port pos if self.end is not none, otherwise use mouse pos
        color = (46, 213, 115) if self.start.signal else (255, 71, 87) # set wire green for 1 and red for 0 
        pygame.draw.line(surface, color, start_pos, end_pos, 4) # thickness of 4 pixels


########################################################################
# BLOCK BASE
########################################################################
class Block: # parent for all logic gate components 
    def __init__(self, type, x, y):
        self.type = type # type of logic gate
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 110, 70)

    def snap_to_grid(self):
        self.x = GRID_SIZE * round(self.x / GRID_SIZE)
        self.y = GRID_SIZE * round(self.y / GRID_SIZE)
        self.rect.topleft = (self.x, self.y)


########################################################################
# INPUT BLOCK  (LSB-FIRST READING)
########################################################################
class InputBlock(Block):
    def __init__(self, x, y):
        super().__init__("INPUT", x, y)
        self.stream = "" # store input
        self.index = 0 # counter for number of bits input
        self.output = OutputPort(self, 110, 35) # create output port

    def set_stream(self, s):
        clean = "".join(c for c in s if c in "01") # allow only boolean input
        self.stream = clean 
        self.index = 0 # when starting to type/ delete, the index reset to 0

    def next_bit(self):
        if self.index < len(self.stream):
            bit = int(self.stream[-1 - self.index]) # LSB first reading 
            self.index += 1 # increment counter to read next bit to the left 
        else:
            bit = 0   # if all input bit used, send 0 as output
        self.output.signal = bit # send bit to output port

    def compute(self): 
        pass # no computation needed for input block (kept to avoid future attribut errors)

    def draw(self, surf):
        pygame.draw.rect(surf, (112, 161, 255), self.rect, border_radius=8)
        
        display_text = self.stream if self.stream else "[TYPE]" # Handle empty display
        surf.blit(FONT.render(f"IN: {display_text}", True, (0,0,0)), (self.x+10, self.y+10)) # draws inputed text MSB first

        surf.blit(FONT.render(f"idx={self.index}", True, (0,0,0)), (self.x+10, self.y+40)) # shows how many bits are sent
        
        pygame.draw.circle(surf, (255, 255, 255), self.output.pos, 7) # draw output port


########################################################################
# OUTPUT BLOCK (MSB-FIRST DISPLAY)
########################################################################
class OutputBlock(Block):
    def __init__(self, x, y):
        super().__init__("OUTPUT", x, y)
        self.input = InputPort(self, 0, 35) # create input port 
        self.history = "" # store output

    def record_bit(self):
        self.history = str(self.input.signal) + self.history # LSB displayed first, more significant bits appended to the left

    def compute(self):
        pass 

    def draw(self, surf):
        pygame.draw.rect(surf, (112, 161, 255), self.rect, border_radius=8)
        surf.blit(FONT.render("OUT:", True, (0,0,0)), (self.x+10, self.y+10))
        surf.blit(FONT.render(self.history, True, (0,0,0)), (self.x+10, self.y+35))
        pygame.draw.circle(surf, (255, 255, 255), self.input.pos, 7)


########################################################################
# LOGIC GATES
########################################################################
class LogicGate(Block): # inherit form Block class
    def __init__(self, type, x, y):
        super().__init__(type, x, y) # calls parent block cosntructor
        if type in ("AND","OR","XOR"): 
            self.inputs = [InputPort(self,0,20), InputPort(self,0,50)] # offset input port position for 2 input logic gates
        else:
            self.inputs = [InputPort(self,0,35)]
        self.output = OutputPort(self,110,35)

    def compute(self):
        vals = [inp.signal for inp in self.inputs] # create list of all inputs (min = 1, max = 2)
        if self.type == "AND":
            self.output.signal = int(all(vals)) # True if all 1
        elif self.type == "OR":
            self.output.signal = int(any(vals)) # True if any 1
        elif self.type == "NOT":
            self.output.signal = int(not vals[0]) # True if first (and only val) = 0
        elif self.type == "XOR": 
            if len(vals) == 2:
                 self.output.signal = int(vals[0] != vals[1]) # True if two vals are difference 
            else:
                 self.output.signal = 0 
            

    def draw(self, surf):
        pygame.draw.rect(surf,(236, 204, 104),self.rect,border_radius=8)
        surf.blit(FONT.render(self.type,True,(0,0,0)),(self.x+30,self.y+25))
        for inp in self.inputs:
            pygame.draw.circle(surf,(255, 255, 255),inp.pos,7)
        pygame.draw.circle(surf,(255, 255, 255),self.output.pos,7)


########################################################################
# MEMORY (1 bit flip flop)
########################################################################
class M(Block):# inherit form parent Block class
    def __init__(self, x, y):
        super().__init__("M", x, y)
        self.input = InputPort(self, 0, 35) # M-in
        self.output = OutputPort(self, 110, 35) # M-out
        self.stored = 0 # Starts at 0 bit
        self.next_stored = None # Captured M in

    def compute(self):
        self.output.signal = self.stored # output M-out

    def capture(self):
        self.next_stored = self.input.signal # capture next M-in

    def commit(self):
        self.stored = self.next_stored # store next M-in 

    def draw(self, surf):
        pygame.draw.rect(surf,(255, 127, 80),self.rect,border_radius=8) 
        surf.blit(FONT.render("M",True,(0,0,0)),(self.x+10,self.y+10))
        surf.blit(FONT.render(f"Stored={self.stored}",True,(0,0,0)),(self.x+10,self.y+40))
        pygame.draw.circle(surf,(255, 255, 255),self.input.pos,7)
        pygame.draw.circle(surf,(255, 255, 255),self.output.pos,7)


########################################################################
# GLOBALS
########################################################################
blocks = []
wires = []

dragging_gate = None
dragging_wire = None

offset_x = 0 # store distance between the mouse and the block's top-left corner at the moment the drag started
offset_y = 0 # prevents block from snapping to mouse center

toolbar_buttons = [
    Button("INPUT",20,10),
    Button("OUTPUT",140,10),
    Button("AND",260,10),
    Button("OR",380,10),
    Button("XOR", 500, 10),
    Button("NOT",620,10),
    Button("M",740,10)]
########################################################################
# Helper (Compute untill no changes )
########################################################################
def settle_combinational(blocks, wires, max_iters=256):
    for _ in range(max_iters):
        changed = False

        # propagate wires
        for w in wires:
            if not w.end:
                continue
            new_sig = w.start.signal
            if w.end.signal != new_sig:
                w.end.signal = new_sig
                changed = True

        # compute non-memory blocks
        for bl in blocks:
            if isinstance(bl, M):
                continue
            prev = getattr(getattr(bl, "output", None), "signal", None) # get previous output signal
            bl.compute()
            curr = getattr(getattr(bl, "output", None), "signal", None) # get current output signal
            if prev != curr:
                changed = True

        if not changed:
            break
########################################################################
# MAIN LOOP
########################################################################
while True:
    mouse = pygame.mouse.get_pos() # retrieve current mouse postition

    for event in pygame.event.get():

        if event.type == pygame.QUIT: # handle quit
            pygame.quit()
            sys.exit()

        # ----------------------------------------------------------
        # SPACEBAR CLOCK
        # ----------------------------------------------------------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                clock_tick = True

        # ----------------------------------------------------------
        # Typing input
        # ----------------------------------------------------------
        if event.type == pygame.TEXTINPUT: # Handle character input (1,0)
            if typed_target:
                typed_target.set_stream(typed_target.stream + event.text)

        if event.type == pygame.KEYDOWN:
            if typed_target:
                if event.key == pygame.K_BACKSPACE: # handle backspace (delete last input)
                    typed_target.set_stream(typed_target.stream[:-1])
                elif event.key == pygame.K_RETURN: # exit typing mode
                    typed_target = None

        # ----------------------------------------------------------
        # Spawn blocks + Enter Typing Mode
        # ----------------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # primary mouse click
            for b in toolbar_buttons:
                if b.rect.collidepoint(mouse):
                    if b.label == "INPUT":
                        blocks.append(InputBlock(500,300))
                    elif b.label == "OUTPUT":
                        blocks.append(OutputBlock(500,300))
                    elif b.label == "M":
                        blocks.append(M(500,300))
                    else: # Handles AND, OR, NOT, and XOR
                        blocks.append(LogicGate(b.label,500,300)) 
                        
            for bl in blocks:
                if isinstance(bl, InputBlock) and bl.rect.collidepoint(mouse): # if left click on input block
                    typed_target = bl # enter typing mode by setting that block as typed target
                    break

        # ----------------------------------------------------------
        # Delete wires and blocks
        # ----------------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # secondary mouse click
            removed = False
            for w in wires: # wire deletion
                if w.end and w.contains_point(mouse): # if mouse close enougth to wire, remove start and end point
                    if w in w.start.connected_wires: w.start.connected_wires.remove(w) 
                    if w in w.end.connected_wires: w.end.connected_wires.remove(w)
                    wires.remove(w)
                    removed = True
                    break
            if removed:
                continue

            for bl in blocks: # block deletion
                if bl.rect.collidepoint(mouse):
                    ports = [] # store all associated ports related to block being deleted
                    if hasattr(bl,"inputs"): # if have attribute of multi-inputs 
                        ports += bl.inputs # store in port list
                    if hasattr(bl,"input"): # if have single input
                        ports.append(bl.input)# store in port list
                    if hasattr(bl,"output"): # if have output
                        ports.append(bl.output)# store in port list
                    
                    for p in ports:
                        for w in p.connected_wires[:]: 
                            wires.remove(w) # remove all connected input an output wires connected to port
                            if w.start and w in w.start.connected_wires: w.start.connected_wires.remove(w)
                            if w.end and w in w.end.connected_wires: w.end.connected_wires.remove(w)
                            # ensures that any other block connected to the deleted wire doesn't hold a reference to a deleted object
                    blocks.remove(bl) # delete block itself
                    break

        # ----------------------------------------------------------
        # Start wire drag
        # ----------------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # primary mouse button pressed and hold
            for bl in blocks:
                output_port = getattr(bl, 'output', None) # get output port and return non if block does not have it
                if output_port:
                    ox,oy = output_port.pos
                    if (mouse[0]-ox)**2 + (mouse[1]-oy)**2 < 10**2: # if mouse distance within 10 pixel radius, consider port clicked
                        dragging_wire = Wire(output_port) # new Wire object created, starting at the clicked output port
                        wires.append(dragging_wire) # added to global wires list to be drawn on next frame
                        break

            if dragging_wire is None: # if no dragging wire is made (output port not clicked on)
                for bl in blocks:
                    if bl.rect.collidepoint(mouse): # check if main block is clicked 
                        dragging_gate = bl # block being moved
                        offset_x = bl.x - mouse[0] # offset to ensure the block moves smoothly relative to user's mouse clicking point
                        offset_y = bl.y - mouse[1]
                        break

        # ----------------------------------------------------------
        # Finish wire drag
        # ----------------------------------------------------------
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:# primary mouse button lifted
            if dragging_wire:
                connected = False # flag to check if wire connected
                for bl in blocks:
                    ports = [] # stor all input ports
                    if hasattr(bl,"inputs"):
                        ports += bl.inputs
                    if hasattr(bl,"input"):
                        ports.append(bl.input)

                    for inp in ports:
                        if inp.parent == dragging_wire.start.parent: # Prevent connecting output to its own block's input
                            continue
                        
                        ix,iy = inp.pos
                        if (mouse[0]-ix)**2 + (mouse[1]-iy)**2 < 10**2: # if mouse distance within 10 pixel radius, consider port clicked
                            dragging_wire.end = inp
                            inp.connected_wires.append(dragging_wire) # updates connected_wires lists of both the start and end ports
                            dragging_wire.start.connected_wires.append(dragging_wire)
                            connected = True 
                            break
                    if connected:
                        break

                if not connected:
                    wires.remove(dragging_wire)

                dragging_wire = None # reset wire drag

            if dragging_gate:
                dragging_gate.snap_to_grid() # align block to grid for neat placement
                dragging_gate = None # reset block drag

        # ----------------------------------------------------------
        # Drag block
        # ----------------------------------------------------------
        if event.type == pygame.MOUSEMOTION and dragging_gate: # mouse moving and block is selected
            dragging_gate.x = mouse[0] + offset_x # update position of block with drag (in regards to mouse position)
            dragging_gate.y = mouse[1] + offset_y
            dragging_gate.rect.topleft = (dragging_gate.x, dragging_gate.y) # update the drawn rectangle to new x and y


    # ==================================================================
    # LOGIC COMPUTATION (CLOCK-CONTROLLED)
    # ==================================================================
    
    if clock_tick:
        # input blocks emit next bit
        for bl in blocks:
            if isinstance(bl, InputBlock):
                bl.next_bit()
                
        for bl in blocks:
            bl.compute()
            
        settle_combinational(blocks, wires)
    
        # output block records bit (from settled inputs)
        for bl in blocks:
            if isinstance(bl, OutputBlock):
                bl.record_bit()
    
        # M captures and commits 
        for bl in blocks:
            if isinstance(bl, M):
                bl.capture()
                
        for bl in blocks:
            if isinstance(bl, M):
                bl.commit()
    
        clock_tick = False
        

    # ==================================================================
    # DRAW EVERYTHING
    # ==================================================================
    screen.fill((0,0,0)) # window background 
    pygame.draw.rect(screen, (47, 53, 66), pygame.Rect(0,0,1500,60)) # tool bar background

    for b in toolbar_buttons:
        b.draw(screen, mouse) # draw buttons and handle hover effect

    for gx in range(0,1500,GRID_SIZE): # draw grid, skipping my GRID_SIZE (20 pixels)
        pygame.draw.line(screen,(47, 53, 66),(gx,60),(gx,900)) # vertial lines
    for gy in range(60,900,GRID_SIZE):
        pygame.draw.line(screen,(47, 53, 66),(0,gy),(1500,gy)) # horizontal lines

    for bl in blocks:
        bl.draw(screen)

    for w in wires:
        w.draw(screen, mouse)

    pygame.display.flip() # update changes
    clock.tick(60)