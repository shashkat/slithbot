import sys
import yaml
from pathlib import Path
import pygame
sys.path.append("/Users/shashankkatiyar/Documents/github_repos/slithbot/src")  # For dev; use pip install -e . for prod

# Initialize Pygame
pygame.init()

from game import SlitherGame

# from a supplied path, reads the config yaml, and returns a dict
def load_config(config_path: str) -> dict:
    with open(Path(config_path)) as f:
        return yaml.safe_load(f)

def main(config_path: str):
    config = load_config(config_path)
    game = SlitherGame(config)
    
    running = True
    while running:
        running = game.handle_events()

        if game.game_running:  
            action = game.get_action_from_keys()
            game.step(action)

        game.render()
        game.clock.tick(config['fps'])
    game.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_simulation.py <config.yaml>")
        sys.exit(1)
    main(sys.argv[1])
    # main(config_path='/Users/shashankkatiyar/Documents/github_repos/slithbot/config/base.yaml')
