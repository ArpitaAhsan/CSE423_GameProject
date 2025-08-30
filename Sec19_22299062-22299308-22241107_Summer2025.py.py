from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

# Game state
current_state = "menu"  # "menu", "game", "level2", "level3"

# Game state variables
plyr_lif, gm_scr, bulets_mised, gm_ovr =10, 0, 0, False
plyr_pos, gun_angl, plyr_radus = [0, 0, 0], 0, 20
is_jumping, jump_start_time = False, 0
jump_duration = 2.0  # 2 seconds in air
jump_height = 100    # Height of jump
cmra_pos = (0, 500, 500) 

# Enemy variables
enmys = []
enmy_cnt = 2  # 2 moving enemies
static_enemy = None  # Static enemy at bottom
enmy_radus = 30
enmy_spd = 0.1
fireball_cooldown = 0
fireball_rate = 5.0  # Fireballs every 3 seconds

# Bullet variables
bulets = []
fireballs = []  # Enemy fireballs
bulet_spd = 10
fireball_spd = 4
bulet_siz = 10
fireball_siz = 15

# Grid variables
GRID_LENGTH = 600
tile_siz = GRID_LENGTH / 4
brdr_thic = 100
outr = GRID_LENGTH + brdr_thic

# Lava variables
lava_patches = []
lava_cooldown = 0
lava_spawn_rate = 10.0  # Spawn every 10 seconds
lava_duration = 5.0     # Stay for 2 seconds
lava_radius = enmy_radus  # Same size as enemy

quadric = None 
# Invisibility variables
is_invisible = False
invisible_start_time = 0
invisible_duration = 5.0  # 5 seconds of invisibility
invisible_count = 3  # Player can use invisibility 3 times

def activate_invisibility1():
    global is_invisible, invisible_start_time, invisible_count
    
    if not is_invisible and invisible_count > 0:
        is_invisible = True
        invisible_start_time = time.time()
        invisible_count -= 1

def update_invisibility1():
    global is_invisible
    
    if is_invisible:
        current_time = time.time()
        if current_time - invisible_start_time >= invisible_duration:
            is_invisible = False

def init_enmys1():
    global enmys, static_enemy
    enmys = []
    static_enemy_move_cooldown = 0
    # Create 2 moving enemies
    for _ in range(enmy_cnt):
        angl = random.uniform(0, 2*math.pi)
        distnc = random.uniform(GRID_LENGTH/2, GRID_LENGTH)
        x = distnc * math.cos(angl)
        y = distnc * math.sin(angl)
        enmys.append({
            'pos': [x, y, 0],
            'siz': enmy_radus
        })
    
    # Create static enemy at bottom center
    # static_enemy = {
    #     'pos': [0, GRID_LENGTH +50, 0],
    #     'siz': enmy_radus
    # }
    static_enemy = {
        'pos': [random.uniform(-GRID_LENGTH/2 + 50, GRID_LENGTH/2 - 50), GRID_LENGTH + 50, 0],
        'siz': enmy_radus
    }

def move_static_enemy():
    global static_enemy, static_enemy_move_cooldown
    
    # Update move cooldown
    static_enemy_move_cooldown -= 0.016  # Assuming ~60 FPS
    
    # If cooldown is up, move the enemy to a new random position
    if static_enemy_move_cooldown <= 0:
        static_enemy['pos'][0] = random.uniform(-GRID_LENGTH/2 + 50, GRID_LENGTH/2 - 50)
        # Reset cooldown with some randomness (2-4 seconds)
        static_enemy_move_cooldown = random.uniform(2.0, 4.0)

def init_gm1():
    global plyr_lif, gm_scr, bulets_mised, gm_ovr, fireball_cooldown, lava_patches, lava_cooldown
    global plyr_pos, gun_angl, cmra_pos, is_jumping, jump_start_time,static_enemy_move_cooldown
    global is_invisible, invisible_start_time, invisible_count
    
    plyr_lif, gm_scr, bulets_mised, gm_ovr = 10, 0, 0, False
    plyr_pos, gun_angl = [0, 0, 0], 0
    is_jumping, jump_start_time = False, 0
    fireball_cooldown = 0
    lava_cooldown = 0
    static_enemy_move_cooldown = 0
    lava_patches = []
    
    # Reset invisibility variables
    is_invisible = False
    invisible_start_time = 0
    invisible_count = 3  # Reset to 3 uses
    
    cmra_pos = (0, -500, 300)
    
    bulets.clear()
    fireballs.clear()
    init_enmys1()

def draw_text1(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_menu():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw menu background
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.2, 0.4)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()
    
    # Draw menu text
    draw_text1(400, 600, "Hero of Worlds", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text1(420, 500, "Select Level:", GLUT_BITMAP_HELVETICA_18)
    draw_text1(450, 400, "1 - Fire Level", GLUT_BITMAP_HELVETICA_18)
    draw_text1(450, 350, "2 - Ice Level (Coming Soon)", GLUT_BITMAP_HELVETICA_18)
    draw_text1(450, 300, "3 - Earth Level (Coming Soon)", GLUT_BITMAP_HELVETICA_18)
    draw_text1(400, 200, "Press '1, 2, or 3' to start your mission", GLUT_BITMAP_HELVETICA_18)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glutSwapBuffers()

def draw_plyr1():
    glPushMatrix()
    glTranslatef(plyr_pos[0], plyr_pos[1], plyr_pos[2])
    if gm_ovr:
        glRotatef(90, 1, 0, 0)
    
    # Change color/opacity when invisible
    if is_invisible:
        glColor3f(0.5, 0.4, 0.0)  # Lighter color with transparency
    else:
        glColor3f(1.0, 0.9, 0.2)
        
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glScalef(20, 20, 25)
    glutSolidCube(1)
    glPopMatrix()
    
    if is_invisible:
        glColor3f(0.5, 0.0, 0.0)  # Lighter color with transparency
    else:
        glColor3f(1.0, 0.0, 0.0)
        
    glPushMatrix()
    glTranslatef(0, 0, 45)
    glutSolidSphere(12, 12, 12)
    glPopMatrix()
    
    glPushMatrix()
    glRotatef(gun_angl, 0, 0, 1)
    
    if is_invisible:
        glColor4f(0.3, 0.3, 0.3, 0.5)  # Lighter color with transparency
    else:
        glColor3f(0.3, 0.3, 0.3)
        
    glPushMatrix()
    glTranslatef(15, 0, 25)  
    glScalef(10, 6, 6)  
    glutSolidCube(1)
    glPopMatrix()
    
    if is_invisible:
        glColor4f(0, 1, 0.5, 0.5)  # Lighter color with transparency
    else:
        glColor3f(0, 1, 0.5)
        
    glPushMatrix()
    glTranslatef(30, 0, 25)  
    glScalef(18, 4, 4)  
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()

def draw_enmys1():
    # Draw moving enemies
    for enmy in enmys:
        glPushMatrix()
        glTranslatef(enmy['pos'][0], enmy['pos'][1], enmy['pos'][2])
        glColor3f(1.0, 0.3, 0.0)
        glutSolidSphere(enmy_radus, 20, 20)
        glColor3f(1.0, 0.6, 0.0)
        for i in range(8):
            glPushMatrix()
            glRotatef(i * 45, 0, 0, 1)
            glTranslatef(enmy_radus, 0, 0)
            glScalef(0.5, 0.5, 1.5)
            glutSolidCone(5, 15, 8, 8)
            glPopMatrix()
        glPopMatrix()
    
    # Draw static enemy at bottom
    if static_enemy:
        glPushMatrix()
        glTranslatef(static_enemy['pos'][0], static_enemy['pos'][1], static_enemy['pos'][2])
        glColor3f(1.0, 0.0, 0.0)  # Red color for static enemy
        glutSolidSphere(enmy_radus, 20, 20)
        glColor3f(1.0, 0.8, 0.0)  # Bright yellow flames
        for i in range(8):
            glPushMatrix()
            glRotatef(i * 45, 0, 0, 1)
            glTranslatef(enmy_radus, 0, 0)
            glScalef(0.5, 0.5, 2.0)  # Taller flames for static enemy
            glutSolidCone(6, 20, 10, 10)  # Larger cones
            glPopMatrix()
        glPopMatrix()

def draw_bulets1():
    # Draw player water bullets
    for bulet in bulets:
        glPushMatrix()
        glTranslatef(bulet['pos'][0], bulet['pos'][1], bulet['pos'][2])
        glColor3f(0.0, 0.5, 1.0)
        glutSolidSphere(bulet_siz/2, 10, 10)
        glPopMatrix()
    
    # Draw enemy fireballs
    for fireball in fireballs:
        glPushMatrix()
        glTranslatef(fireball['pos'][0], fireball['pos'][1], fireball['pos'][2])
        glColor3f(1.0, 0.5, 0.0)  # Orange fireballs
        glutSolidSphere(fireball_siz/2, 12, 12)
        glPopMatrix()

def draw_lava1():
    for lava in lava_patches:
        glPushMatrix()
        glTranslatef(lava['pos'][0], lava['pos'][1], 1)  # Slightly above the ground
        glColor4f(1.0, 0.2, 0.0, 0.7)  # Red with transparency
        glutSolidSphere(lava_radius, 20, 20)
        glPopMatrix()

def draw_grid1():
    glBegin(GL_QUADS)
    glColor3f(0.9, 0.7, 0.5)
    for i in range(-4, 4):
        for j in range(-4, 4):
            glVertex3f(i * tile_siz, j * tile_siz, 0)
            glVertex3f((i+1) * tile_siz, j * tile_siz, 0)
            glVertex3f((i+1) * tile_siz, (j+1) * tile_siz, 0)
            glVertex3f(i * tile_siz, (j+1) * tile_siz, 0)
    glEnd()

def shoot_fireball1():
    global fireball_cooldown
    if static_enemy:
        # Fireballs shoot straight up from static enemy
        fireballs.append({
            'pos': static_enemy['pos'][:],
            'dir': [0, -1, 0],  # Straight up direction
            'speed': fireball_spd
        })
        fireball_cooldown = fireball_rate

def spawn_lava1():
    global lava_cooldown
    # Random position within the grid
    x = random.uniform(-GRID_LENGTH/2, GRID_LENGTH/2)
    y = random.uniform(-GRID_LENGTH/2, GRID_LENGTH/2)
    
    lava_patches.append({
        'pos': [x, y, 0],
        'spawn_time': time.time()
    })
    lava_cooldown = lava_spawn_rate

def updt_lava1():
    global lava_patches, lava_cooldown, plyr_lif, gm_ovr
    
    # Update cooldown
    lava_cooldown -= 0.016  # Assuming ~60 FPS
    
    # Spawn new lava if cooldown is up
    if lava_cooldown <= 0:
        spawn_lava1()
    
    # Remove expired lava patches
    current_time = time.time()
    lava_patches[:] = [lava for lava in lava_patches 
                      if current_time - lava['spawn_time'] < lava_duration]
    
    if is_invisible:
        return
    # Check collision with player (only if player is on ground)
    if plyr_pos[2] <= 0:  # Only hit if player is on ground
        lava_to_remove = []
        
        for i, lava in enumerate(lava_patches):
            dx = lava['pos'][0] - plyr_pos[0]
            dy = lava['pos'][1] - plyr_pos[1]
            distnc = math.sqrt(dx*dx + dy*dy)
            
            if distnc < plyr_radus + lava_radius:
                plyr_lif -= 1
                lava_to_remove.append(i)  # Mark this lava patch for removal
                if plyr_lif <= 0:
                    gm_ovr = True
        
        # Remove lava patches that hit the player
        for i in sorted(lava_to_remove, reverse=True):
            if i < len(lava_patches):
                lava_patches.pop(i)

def updt_fireballs1():
    global fireballs, plyr_lif, gm_ovr
    
    fireballs_to_remove = []
    
    for i, fireball in enumerate(fireballs):
        # Move fireball
        fireball['pos'][0] += fireball['dir'][0] * fireball['speed']
        fireball['pos'][1] += fireball['dir'][1] * fireball['speed']
        
        # Remove if out of bounds
        if (abs(fireball['pos'][0]) > outr or 
            abs(fireball['pos'][1]) > outr or 
            fireball['pos'][2] > 500):
            fireballs_to_remove.append(i)
            continue
        if is_invisible:
            continue
        # Check collision with player (only if player is on ground)
        if plyr_pos[2] <= 0:  # Only hit if player is on ground
            dx = fireball['pos'][0] - plyr_pos[0]
            dy = fireball['pos'][1] - plyr_pos[1]
            dz = fireball['pos'][2] - plyr_pos[2]
            distnc = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if distnc < plyr_radus + fireball_siz/2:
                fireballs_to_remove.append(i)
                plyr_lif -= 1
                if plyr_lif <= 0:
                    gm_ovr = True
    
    # Remove fireballs that hit or went out of bounds
    for i in sorted(fireballs_to_remove, reverse=True):
        if i < len(fireballs):
            fireballs.pop(i)

def updt_bulets1():
    global bulets, bulets_mised, gm_scr, gm_ovr
    
    bulets_to_remove = []
    enmys_to_respawn = []
    
    for i, bulet in enumerate(bulets):
        bulet['pos'][0] += bulet['dir'][0] * bulet_spd
        bulet['pos'][1] += bulet['dir'][1] * bulet_spd
        bulet['pos'][2] += bulet['dir'][2] * bulet_spd
        
        if abs(bulet['pos'][0]) > outr or abs(bulet['pos'][1]) > outr or bulet['pos'][2] > 500:
            bulets_to_remove.append(i)
            bulets_mised += 1
            if bulets_mised >= 30:
                gm_ovr = True
            continue
        
        # Check collision with moving enemies only (not static enemy)
        for j, enmy in enumerate(enmys):
            dx = bulet['pos'][0] - enmy['pos'][0]
            dy = bulet['pos'][1] - enmy['pos'][1]
            dz = bulet['pos'][2] - enmy['pos'][2]
            distnc = math.sqrt(dx*dx + dy*dy + dz*dz)

            if distnc < enmy_radus + bulet_siz/2:
                bulets_to_remove.append(i)
                enmys_to_respawn.append(j)
                gm_scr += 1
                break
    
    for i in sorted(set(bulets_to_remove), reverse=True):
        if i < len(bulets):
            bulets.pop(i)
    
    for j in set(enmys_to_respawn):
        if j < len(enmys):
            angl = random.uniform(0, 2*math.pi)
            distnc = random.uniform(GRID_LENGTH/2, GRID_LENGTH)
            enmys[j]['pos'][0] = distnc * math.cos(angl)
            enmys[j]['pos'][1] = distnc * math.sin(angl)
            enmys[j]['pos'][2] = 0

def updt_enmys1():
    global plyr_lif, gm_ovr, fireball_cooldown
    
    if gm_ovr:
        return
    move_static_enemy()
    # Update moving enemies
    for enmy in enmys:
        dx = plyr_pos[0] - enmy['pos'][0]
        dy = plyr_pos[1] - enmy['pos'][1]
        dist_squared = dx*dx + dy*dy
        
        if dist_squared > 0:
            inv_dist = 1.0 / (dist_squared ** 0.5)
            enmy['pos'][0] += (dx * inv_dist) * enmy_spd
            enmy['pos'][1] += (dy * inv_dist) * enmy_spd
        
        if is_invisible:  # Skip collision if player is invisible
            continue
            
        # Only check collision if player is on ground (z=0)
        if plyr_pos[2] <= 0 and dist_squared < (plyr_radus + enmy_radus) ** 2:
            plyr_lif -= 1
            enmy['pos'][0] = random.uniform(-GRID_LENGTH/2, GRID_LENGTH/2)
            enmy['pos'][1] = random.uniform(-GRID_LENGTH/2, GRID_LENGTH/2)
            enmy['pos'][2] = 0
            
            if plyr_lif <= 0:
                gm_ovr = True
    
    # Update fireball cooldown and shooting
    fireball_cooldown -= 0.016  # Assuming ~60 FPS
    if fireball_cooldown <= 0:
        shoot_fireball1()

def updt_jump1():
    global plyr_pos, is_jumping, jump_start_time
    
    if is_jumping:
        current_time = time.time()
        elapsed = current_time - jump_start_time
        
        if elapsed < jump_duration:
            progress = elapsed / jump_duration
            height = jump_height * math.sin(progress * math.pi)
            plyr_pos[2] = height
        else:
            plyr_pos[2] = 0
            is_jumping = False

def jump1():
    global is_jumping, jump_start_time
    
    if not is_jumping and plyr_pos[2] <= 0:
        is_jumping = True
        jump_start_time = time.time()

def fire_bulet1():
    if gm_ovr:
        return
    angl_rad = math.radians(gun_angl)
    bulets.append({
        'pos': [plyr_pos[0] + 40 * math.cos(angl_rad), 
                plyr_pos[1] + 40 * math.sin(angl_rad), 
                plyr_pos[2] + 20],
        'dir': [math.cos(angl_rad), math.sin(angl_rad), 0]
    })

def setup_cmra1():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(120, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cam_x, cam_y, cam_z = cmra_pos
    gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)
                        
def keyboardListener1(key, x, y):
    global plyr_pos, gun_angl, current_state
    
    key = key.decode('utf-8').lower()
    
    if current_state == "menu":
        if key == '1':
            current_state = "lvl1"
            init_gm1()
        elif key == '2':
            draw_text1(400, 200, "Ice Level Coming Soon!", GLUT_BITMAP_HELVETICA_18)
        elif key == '3':
            draw_text1(400, 200, "Earth Level Coming Soon!", GLUT_BITMAP_HELVETICA_18)
        return
    
    # Game controls
    if key == 'w':
        plyr_pos[0] += 10 * math.cos(math.radians(gun_angl))
        plyr_pos[1] += 10 * math.sin(math.radians(gun_angl))
    elif key == 's':
        plyr_pos[0] -= 10 * math.cos(math.radians(gun_angl))
        plyr_pos[1] -= 10 * math.sin(math.radians(gun_angl))
    elif key == 'a':  
        gun_angl = (gun_angl - 5) % 360
    elif key == 'd':
        gun_angl = (gun_angl + 5) % 360
    elif key == ' ':
        jump1()
    elif key == 'r':
        current_state = "menu"
    elif key == 'i':  # Activate invisibility
        activate_invisibility1()

def specialKeyListener1(key, x, y):
    global cmra_pos
    x, y, z = cmra_pos
    move_spd = 10
    if key == GLUT_KEY_UP:
        y -= move_spd
    elif key == GLUT_KEY_DOWN:
        y += move_spd
    elif key == GLUT_KEY_LEFT:
        x -= move_spd
    elif key == GLUT_KEY_RIGHT:
        x += move_spd
    cmra_pos = (x, y, z)

def mouseListener1(button, state, x, y):
    if state == GLUT_DOWN and button == GLUT_LEFT_BUTTON:
        fire_bulet1()

def idle():
    if current_state == "lvl1":
        updt_bulets1()
        updt_fireballs1()
        updt_enmys1()
        updt_jump1()
        updt_lava1()  # Update lava patches
        update_invisibility1()
    glutPostRedisplay()

def showScreen():
    if current_state == "menu":
        draw_menu()
    elif current_state == "lvl1":
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glViewport(0, 0, 1000, 800)
        setup_cmra1()
        draw_grid1()
        draw_plyr1()
        draw_enmys1()
        draw_bulets1()
        draw_lava1()  # Draw lava patches
        draw_text1(10, 680, f"Life: {plyr_lif}")
        draw_text1(10, 650, f"Score: {gm_scr}")
        draw_text1(10, 620, f"Missed: {bulets_mised}")
        draw_text1(10, 590, f"Jump: SPACE to dodge fireballs and lava!")
        draw_text1(10, 560, f"Invisibility: {invisible_count} left (Press I)")
        glutSwapBuffers()

def main():
    global quadric  
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Fire Fighter Frenzy")
    quadric = gluNewQuadric()
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener1)
    glutSpecialFunc(specialKeyListener1)
    glutMouseFunc(mouseListener1)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()