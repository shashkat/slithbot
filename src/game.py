import pygame
import math
import random
import numpy as np
from typing import List, Tuple, Dict, Optional

# Initialize Pygame
pygame.init()

# Game settings
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800
WORLD_WIDTH = 2400
WORLD_HEIGHT = 1600
SEGMENT_RADIUS = 8
FOOD_RADIUS = 4
INITIAL_LENGTH = 10
SPEED = 3
TURN_SPEED = 0.08
NUM_BOTS = 20
FOOD_COUNT = 300
FPS = 60

# Colors
BACKGROUND = (45, 52, 54)
GRID_COLOR = (60, 67, 69)
FOOD_COLOR = (255, 217, 61)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SNAKE_COLORS = [
    [(255, 107, 107), (238, 90, 82)],
    [(78, 205, 196), (69, 183, 170)],
    [(255, 230, 109), (247, 220, 111)],
    [(149, 225, 211), (126, 207, 192)],
    [(255, 159, 243), (243, 104, 224)],
    [(116, 185, 255), (9, 132, 227)]
]


class Snake:
    def __init__(self, x: float, y: float, is_player: bool = False):
        self.segments = []
        self.is_player = is_player
        self.alive = True
        self.angle = random.random() * math.pi * 2
        self.target_angle = self.angle
        self.color_index = random.randint(0, len(SNAKE_COLORS) - 1)
        
        # Initialize segments
        for i in range(INITIAL_LENGTH):
            self.segments.append({
                'x': x - i * SEGMENT_RADIUS,
                'y': y,
                'radius': SEGMENT_RADIUS
            })
        
        # AI properties
        if not is_player:
            self.ai_target = None
            self.ai_timer = 0
    
    @property
    def head(self):
        return self.segments[0]
    
    @property
    def length(self):
        return len(self.segments)
    
    # update the snake's segments according to target_angle value.
    # needs to have the information of all snakes because if it is non-player snake, it needs to consider 
    # other snakes' positions to make a decision about where to move.
    def update(self, snakes, food):
        if not self.alive:
            return
        
        # if not player, then use update_ai method to update the target angle appropriately
        if not self.is_player:
            self.update_ai(snakes, food)
        
        # Smooth angle transition
        angle_diff = self.target_angle - self.angle
        # get angle in range (-pi,+pi)
        while angle_diff > math.pi:
            angle_diff -= math.pi * 2
        while angle_diff < -math.pi:
            angle_diff += math.pi * 2
        self.angle += angle_diff * 0.1
        
        # Move head
        new_head = {
            'x': self.head['x'] + math.cos(self.angle) * SPEED,
            'y': self.head['y'] + math.sin(self.angle) * SPEED,
            'radius': SEGMENT_RADIUS
        }
        
        # THIS PART OF CODE NEEDS REWORK. I DON'T WANNA WRAP AROUND THE WORLD, BUT INSTEAD HAVE A WALL, 
        # UPON HITTING WHICH, THE SNAKE WILL DIE.
        # Wrap around world
        if new_head['x'] < 0:
            new_head['x'] = WORLD_WIDTH
        if new_head['x'] > WORLD_WIDTH:
            new_head['x'] = 0
        if new_head['y'] < 0:
            new_head['y'] = WORLD_HEIGHT
        if new_head['y'] > WORLD_HEIGHT:
            new_head['y'] = 0
        
        self.segments.insert(0, new_head)
        self.segments.pop()
    
    # update the bot snake's target angle according to if it should prioritize running away or gather food.
    # If running away, target angle becomes towards opposite direction of nearby snake/s. 
    # If gathering food, target angle is towards the direction of nearest food particle.
    # needs to have the information of all snakes because it has to avoid other snakes
    # Just updates target_angle, but not the actual segments list.
    def update_ai(self, snakes: List['Snake'], food: List[Dict]):
        self.ai_timer += 1
        
        # Find nearest food
        if self.ai_timer % 30 == 0 or self.ai_target is None:
            nearest_food = None
            min_dist = float('inf')
            
            # out of all foods find the one nearest to current snake's head
            for f in food:
                dist = math.hypot(f['x'] - self.head['x'], f['y'] - self.head['y'])
                if dist < min_dist:
                    min_dist = dist
                    nearest_food = f
            
            if nearest_food:
                self.ai_target = nearest_food
        
        # Avoid other snakes
        avoidance_vector = {'x': 0, 'y': 0}
        danger_level = 0
        
        for snake in snakes:
            if snake is self or not snake.alive:
                continue
            
            # for each segment of the other snake, compute the distance from self.head. If for any segment, 
            # distance<100, then compute a weight value, which is between 0 and 1, indicating how close that 
            # segment is, to the current snake, and increase the value of the avoidance vector with the weighted
            # distance from that segment. Also increment the danger_level with weight.
            for seg in snake.segments:
                dist = math.hypot(seg['x'] - self.head['x'], seg['y'] - self.head['y'])
                if dist < 100:
                    weight = (100 - dist) / 100
                    avoidance_vector['x'] += (self.head['x'] - seg['x']) * weight
                    avoidance_vector['y'] += (self.head['y'] - seg['y']) * weight
                    danger_level += weight
        
        # Calculate target angle
        if danger_level > 0.5:
            # Prioritize avoidance
            target_angle = math.atan2(avoidance_vector['y'], avoidance_vector['x'])
        elif self.ai_target:
            # Go towards food
            dx = self.ai_target['x'] - self.head['x']
            dy = self.ai_target['y'] - self.head['y']
            target_angle = math.atan2(dy, dx)
            
            # THIS SEEMS NOT REQUIRED.
            # Add some avoidance influence
            if danger_level > 0:
                avoid_angle = math.atan2(avoidance_vector['y'], avoidance_vector['x'])
                target_angle = target_angle * (1 - danger_level) + avoid_angle * danger_level
        else:
            # Random movement
            if self.ai_timer % 120 == 0:
                target_angle = self.angle + (random.random() - 0.5) * math.pi
            else:
                target_angle = self.angle
        
        # finally, trim the target angle to (-TURN_SPEED, +TURN_SPEED), as that is the range for the 
        # player snake.
        # target_angle = max(-TURN_SPEED, min(target_angle, TURN_SPEED))
        self.target_angle = target_angle
    
    # loops through all food particles, and if anyone is closer than SEGMENT_RADIUS + FOOD_RADIUS from 
    # self.head, then that food particle is removed from the env, and self.grow() is called.
    def check_food_collision(self, food: List[Dict]) -> int:
        """Returns number of food eaten"""
        food_eaten = 0
        i = len(food) - 1
        while i >= 0:
            f = food[i]
            dist = math.hypot(f['x'] - self.head['x'], f['y'] - self.head['y'])
            
            if dist < SEGMENT_RADIUS + FOOD_RADIUS:
                food.pop(i)
                self.grow()
                food_eaten += 1
            i -= 1
        
        return food_eaten
    
    # checks if any of the segments of of all objects in snakes are closer than SEGMENT_RADIUS * 1.5 to 
    # self's head
    def check_snake_collision(self, snakes: List['Snake']) -> bool:
        """Returns True if collision occurred"""
        for snake in snakes:
            if not snake.alive:
                continue
            
            # don't wanna count collision with self as collision
            if snake is self:
                continue

            for i in range(0, len(snake.segments)):
                seg = snake.segments[i]
                dist = math.hypot(seg['x'] - self.head['x'], seg['y'] - self.head['y'])
                
                if dist < SEGMENT_RADIUS * 1.5:
                    return True
        
        return False
    
    # append to self.segments, 3 copies of the last element in self.segments.
    def grow(self):
        tail = self.segments[-1].copy()
        for _ in range(3):
            self.segments.append(tail.copy())
    
    def die(self, food: List[Dict]):
        self.alive = False
        
        # Spawn food at death location
        for seg in self.segments:
            food.append({
                'x': seg['x'] + (random.random() - 0.5) * 20,
                'y': seg['y'] + (random.random() - 0.5) * 20
            })
    
    # update the target using the direction and TURN_SPEED variable
    def turn(self, direction: int):
        """Direction: -1 for left, 1 for right"""
        self.target_angle += direction * TURN_SPEED
    
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        if not self.alive:
            return
        
        colors = SNAKE_COLORS[self.color_index]
        
        # Draw segments. Draw in reverse order so that the head appears on front.
        for i in range(len(self.segments) - 1, -1, -1):
            seg = self.segments[i]
            screen_x = int(seg['x'] - camera_x + CANVAS_WIDTH / 2)
            screen_y = int(seg['y'] - camera_y + CANVAS_HEIGHT / 2)
            
            if screen_x < -50 or screen_x > CANVAS_WIDTH + 50 or \
               screen_y < -50 or screen_y > CANVAS_HEIGHT + 50:
                continue
            
            # Draw body
            pygame.draw.circle(screen, colors[0], (screen_x, screen_y), int(seg['radius']))
            
            # Outline for player
            if self.is_player:
                pygame.draw.circle(screen, WHITE, (screen_x, screen_y), int(seg['radius']), 2) # when the last, width parameter is supplied, the circle isn't filled
        
        # Draw eyes on head
        head_screen_x = int(self.head['x'] - camera_x + CANVAS_WIDTH / 2)
        head_screen_y = int(self.head['y'] - camera_y + CANVAS_HEIGHT / 2)
        eye_offset = 5
        
        for side in [-1, 1]:
            eye_x = int(head_screen_x + math.cos(self.angle + side * 0.5) * eye_offset)
            eye_y = int(head_screen_y + math.sin(self.angle + side * 0.5) * eye_offset)
            
            pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 3)
            pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 2)


class SlitherGame:
    
    # initialize. Assigns values to .screen and .clock attributes. And if render=True, then also assigns 
    # values to fonts. Also calls the reset method.
    def __init__(self, render: bool = True):
        self.render_enabled = render
        
        if self.render_enabled:
            self.screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
            pygame.display.set_caption("Slither.io - RL Training Environment")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        else:
            self.screen = None
            self.clock = None
        
        self.reset()
    
    # assigns values to various attributes like snakes, food, game_running. Returns state of the game.
    def reset(self):
        """Reset the game to initial state"""
        self.snakes = []
        self.food = []
        self.score = 0
        self.game_running = True
        self.camera = {'x': WORLD_WIDTH / 2, 'y': WORLD_HEIGHT / 2}
        
        # Create player
        self.player = Snake(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, is_player=True)
        self.snakes.append(self.player)
        
        # Create bots. Bots have two extra attributes: ai_timer, and ai_target
        for _ in range(NUM_BOTS):
            x = random.random() * WORLD_WIDTH
            y = random.random() * WORLD_HEIGHT
            self.snakes.append(Snake(x, y, is_player=False))
        
        # Spawn food. Just appends dicts like {x, y} to self.food
        self.spawn_food(FOOD_COUNT)
        
        return self.get_state()
    
    # Spawn food. Just appends dicts like {x, y} to self.food
    def spawn_food(self, count: int):
        for _ in range(count):
            self.food.append({
                'x': random.random() * WORLD_WIDTH,
                'y': random.random() * WORLD_HEIGHT
            })
    
    # execute one game step, which involves moving all snakes (player snake acc to input, and bot snakes 
    # according to update_ai method), checking food collision and growing the snakes if food collision 
    # happened checking snakes' collision and according declaring snakes dead, respawning the dead bots, 
    # and updating self.camera with self.player.head information
    def step(self, action: Optional[int] = None) -> Tuple[Dict, float, bool, Dict]:
        """
        Execute one game step
        
        Args:
            action: -1 (turn left), 0 (straight), 1 (turn right), None (no action)
        
        Returns:
            state: Current game state
            reward: Reward for this step
            done: Whether game is over
            info: Additional information
        """
        if action is not None and self.player.alive:
            if action == -1:
                self.player.turn(-1)
            elif action == 1:
                self.player.turn(1)
        
        # Update all snakes
        for snake in self.snakes:
            snake.update(self.snakes, self.food)
        
        # old_length = self.player.length # NOT REQUIRED

        # Check food collisions
        # loop through all the snakes and update their segments (and food locations) acc to food collision.
        for snake in self.snakes:
            food_eaten = snake.check_food_collision(self.food)
            
            # if player, then update score using food_eaten value
            if snake.is_player:
                self.score += food_eaten
            
            # Spawn new food. Randomly spawn #food_eaten food particles in the world. This means that with time, 
            # as more and more food is eaten by snakes, the overall food in the world will increase. 
            if food_eaten > 0:
                self.spawn_food(food_eaten)
        
        # Check snake collisions
        for snake in self.snakes:
            if snake.check_snake_collision(self.snakes):
                snake.die(self.food)
                if snake is self.player:
                    self.game_running = False
        
        # Respawn dead bots
        for i in range(1, len(self.snakes)):
            if not self.snakes[i].alive:
                x = random.random() * WORLD_WIDTH
                y = random.random() * WORLD_HEIGHT
                self.snakes[i] = Snake(x, y, is_player=False)
        
        # Update camera to follow player
        if self.player.alive:
            self.camera['x'] = self.player.head['x']
            self.camera['y'] = self.player.head['y']
        
        # Calculate reward. 
        # THIS PART SEEMS TO BE FOR THE RL, AND NOT NECESSARY FOR THE RAW GAME RUNNING.
        reward = food_eaten * 10  # Reward for eating food
        if not self.player.alive:
            reward -= 100  # Penalty for dying
        
        state = self.get_state()
        done = not self.game_running
        info = {
            'score': self.score,
            'length': self.player.length,
            'food_eaten': food_eaten
        }
        
        return state, reward, done, info
    
    # return a big dict, with keys ['player', 'snakes', 'food', 'score', 'world_size'], with information 
    # about these respective things.
    def get_state(self) -> Dict:
        """Get current game state for RL agent"""
        return {
            'player': {
                'alive': self.player.alive,
                'x': self.player.head['x'],
                'y': self.player.head['y'],
                'angle': self.player.angle,
                'length': self.player.length,
                'segments': [{'x': s['x'], 'y': s['y']} for s in self.player.segments]
            },
            'snakes': [
                {
                    'x': s.head['x'],
                    'y': s.head['y'],
                    'angle': s.angle,
                    'length': s.length,
                    'segments': [{'x': seg['x'], 'y': seg['y']} for seg in s.segments]
                }
                for s in self.snakes if s is not self.player and s.alive
            ],
            'food': [{'x': f['x'], 'y': f['y']} for f in self.food],
            'score': self.score,
            'world_size': {'width': WORLD_WIDTH, 'height': WORLD_HEIGHT}
        }
    
    # renders the grid, food, snakes, and text 
    def render(self):
        """Render the game"""
        if not self.render_enabled:
            return
        
        # Clear screen
        self.screen.fill(BACKGROUND)
        
        # Draw grid
        grid_size = 50
        camera_x = self.camera['x']
        camera_y = self.camera['y']
        
        start_x = int((camera_x - CANVAS_WIDTH / 2) / grid_size) * grid_size
        start_y = int((camera_y - CANVAS_HEIGHT / 2) / grid_size) * grid_size
        
        for x in range(start_x, int(camera_x + CANVAS_WIDTH / 2) + grid_size, grid_size):
            screen_x = int(x - camera_x + CANVAS_WIDTH / 2)
            pygame.draw.line(self.screen, GRID_COLOR, (screen_x, 0), (screen_x, CANVAS_HEIGHT))
        
        for y in range(start_y, int(camera_y + CANVAS_HEIGHT / 2) + grid_size, grid_size):
            screen_y = int(y - camera_y + CANVAS_HEIGHT / 2)
            pygame.draw.line(self.screen, GRID_COLOR, (0, screen_y), (CANVAS_WIDTH, screen_y))
        
        # Draw food
        for f in self.food:
            screen_x = int(f['x'] - camera_x + CANVAS_WIDTH / 2)
            screen_y = int(f['y'] - camera_y + CANVAS_HEIGHT / 2)
            
            if -50 < screen_x < CANVAS_WIDTH + 50 and -50 < screen_y < CANVAS_HEIGHT + 50:
                pygame.draw.circle(self.screen, FOOD_COLOR, (screen_x, screen_y), FOOD_RADIUS)
        
        # Draw snakes
        for snake in self.snakes:
            snake.draw(self.screen, camera_x, camera_y)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        length_text = self.small_font.render(f"Length: {self.player.length}", True, WHITE)
        
        # Calculate rank
        living_snakes = [s for s in self.snakes if s.alive]
        living_snakes.sort(key=lambda s: s.length, reverse=True)
        rank = living_snakes.index(self.player) + 1 if self.player in living_snakes else len(living_snakes)
        rank_text = self.small_font.render(f"Rank: {rank}/{len(living_snakes)}", True, WHITE)
        
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(length_text, (20, 60))
        self.screen.blit(rank_text, (20, 90))
        
        # Game over
        if not self.game_running:
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            final_score_text = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, (CANVAS_WIDTH // 2 - 100, CANVAS_HEIGHT // 2 - 50))
            self.screen.blit(final_score_text, (CANVAS_WIDTH // 2 - 80, CANVAS_HEIGHT // 2))
            self.screen.blit(restart_text, (CANVAS_WIDTH // 2 - 100, CANVAS_HEIGHT // 2 + 30))
        
        pygame.display.flip()
    
    # handle inputs (except arrow keys, as that is handled separately) that might have been given by the user
    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if should quit"""
        # if render_enabled is False, then basically the game is not interactive. Hence, there won't be any 
        # events to begin with to handle.
        if not self.render_enabled:
            return True
        
        for event in pygame.event.get():
            # if something caused the pygame.QUIT event to be present in current iteration's events list 
            # (like alt+f4), then return False, indicating that game should be quitted.
            if event.type == pygame.QUIT:
                return False
            # If some key was pressed
            if event.type == pygame.KEYDOWN:
                # If the game wasn't running, and the key pressed was r, then do game.reset()
                if event.key == pygame.K_r and not self.game_running:
                    self.reset()
                # if the escape key was pressed, then return False, indicating that game should be quitted.
                if event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    # Returns None if self.render_enabled=F. If render_enabled=T, returns -1 if left was pressed, 1 if right 
    # was pressed and 0 otherwise.
    def get_action_from_keys(self) -> Optional[int]:
        """Get action from keyboard input"""
        if not self.render_enabled:
            return None
        
        # pygame.key.get_pressed() returns a list of 512 boolean values, indicating if any of the possible 
        # keys are pressed or not
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            return -1
        elif keys[pygame.K_RIGHT]:
            return 1
        return 0
    
    def close(self):
        """Close the game"""
        if self.render_enabled:
            pygame.quit()


def main():
    """Main game loop for human play"""
    game = SlitherGame(render=True)
    
    running = True
    while running:
        running = game.handle_events()
        
        if game.game_running:
            action = game.get_action_from_keys()
            game.step(action)
        
        game.render()
        game.clock.tick(FPS)
    
    game.close()


if __name__ == "__main__":
    main()
