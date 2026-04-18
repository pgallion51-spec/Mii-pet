import pygame
from pygame.locals import *
import random
import json
import os
from datetime import datetime
import requests
from game_state import Mii

class DesktopCompanion:
    """Mii companion on your desktop"""
    def __init__(self, mii, screen_width=1920, screen_height=1080):
        self.mii = mii
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Window position (bottom right corner)
        self.window_width = 300
        self.window_height = 400
        self.x = screen_width - self.window_width - 20
        self.y = screen_height - self.window_height - 20
        
        # State
        self.is_visible = True
        self.is_minimized = False
        self.current_state = 'idle'  # idle, talking, searching, joking, fact
        self.message = ""
        self.animation_frame = 0
        self.message_timer = 0
        
        # Load resources
        self.jokes = self._load_jokes()
        self.facts = self._load_facts()
        self.search_history = []
    
    def _load_jokes(self):
        """Load jokes from file or API"""
        jokes_file = 'data/jokes.json'
        if os.path.exists(jokes_file):
            with open(jokes_file, 'r') as f:
                return json.load(f)
        else:
            # Default jokes
            return [
                {"setup": "Why did the Mii go to school?", "punchline": "To get a little brighter!"},
                {"setup": "What do Miis eat for breakfast?", "punchline": "Mii-uesli!"},
                {"setup": "Why don't Miis ever get lost?", "punchline": "They always know which way to face!"},
                {"setup": "What's a Mii's favorite music?", "punchline": "Wii-d music!"},
                {"setup": "How do Miis stay in shape?", "punchline": "With Wii-robics!"},
                {"setup": "What did the Mii say to the computer?", "punchline": "You've got a great interface!"},
                {"setup": "Why do Miis make terrible chefs?", "punchline": "They always Wii-peat the same recipes!"},
            ]
    
    def _load_facts(self):
        """Load fun facts from file or API"""
        facts_file = 'data/facts.json'
        if os.path.exists(facts_file):
            with open(facts_file, 'r') as f:
                return json.load(f)
        else:
            # Default facts
            return [
                "Did you know? Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs that was still edible!",
                "Did you know? A group of flamingos is called a 'flamboyance'!",
                "Did you know? Octopuses have three hearts!",
                "Did you know? Bananas are berries, but strawberries aren't!",
                "Did you know? A day on Venus is longer than its year!",
                "Did you know? Cats have over 20 different vocal sounds!",
                "Did you know? Dolphins have names for each other!",
                "Did you know? A cockroach can live for a week without its head!",
                "Did you know? Carrots were originally purple, not orange!",
                "Did you know? The smell of petrichor (after rain) comes from bacteria!",
                "Did you know? Miis were first introduced on the Nintendo Wii in 2006!",
                "Did you know? You can create over 60 million different Miis on the Wii!",
            ]
    
    def tell_joke(self):
        """Tell a random joke"""
        joke = random.choice(self.jokes)
        self.message = joke['setup']
        self.current_state = 'joking'
        self.message_timer = 3.0
        self.mii.happiness = min(100, self.mii.happiness + 5)
        
        # Queue up punchline
        return joke
    
    def tell_fact(self):
        """Tell a random fun fact"""
        fact = random.choice(self.facts)
        self.message = fact
        self.current_state = 'fact'
        self.message_timer = 4.0
        return fact
    
    def search(self, query):
        """Search the web"""
        self.message = f"Searching for '{query}'..."
        self.current_state = 'searching'
        self.message_timer = 2.0
        self.search_history.append({'query': query, 'timestamp': datetime.now().isoformat()})
        
        try:
            # Use simple search API
            results = self._web_search(query)
            return results
        except Exception as e:
            self.message = f"Search failed: {str(e)}"
            return None
    
    def _web_search(self, query):
        """Perform web search (using free API)"""
        # Using DuckDuckGo API (no key required)
        try:
            import urllib.parse
            import urllib.request
            
            url = f"https://api.duckduckgo.com/?q={{urllib.parse.quote(query)}}&format=json"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read())
                
                results = {
                    'query': query,
                    'results': []
                }
                
                # Extract results
                if data.get('AbstractText'):
                    results['results'].append({
                        'title': data.get('AbstractTitle', 'Result'),
                        'snippet': data['AbstractText'],
                        'url': data.get('AbstractURL', '')
                    })
                
                return results
        except Exception as e:
            print(f"Search error: {e}")
            return None
    
    def update(self, dt):
        """Update companion state"""
        self.animation_frame += 1
        
        if self.message_timer > 0:
            self.message_timer -= dt
        else:
            self.message = ""
            self.current_state = 'idle'
        
        # Update Mii stats
        self.mii.hunger = max(0, self.mii.hunger - 0.05 * dt)
    
    def render(self, screen):
        """Render companion window on screen"""
        if not self.is_visible or self.is_minimized:
            return
        
        # Create companion window surface
        window_surface = pygame.Surface((self.window_width, self.window_height))
        window_surface.fill((230, 200, 220))  # Light purple
        
        # Draw border
        pygame.draw.rect(window_surface, (150, 100, 150), 
                        (0, 0, self.window_width, self.window_height), 3)
        
        # Draw Mii name and status
        font_small = pygame.font.Font(None, 24)
        font_large = pygame.font.Font(None, 32)
        
        name_text = font_large.render(self.mii.name, True, (0, 0, 0))
        window_surface.blit(name_text, (10, 10))
        
        # Draw Mii simple animation
        self._draw_mii_animation(window_surface, 150, 100)
        
        # Draw stats
        self._draw_stats(window_surface, font_small)
        
        # Draw message/speech bubble
        if self.message:
            self._draw_speech_bubble(window_surface, font_small)
        
        # Draw buttons
        self._draw_buttons(window_surface, font_small)
        
        # Blit to main screen
        screen.blit(window_surface, (self.x, self.y))
    
    def _draw_mii_animation(self, surface, x, y):
        """Draw animated Mii"""
        color = self.mii.color
        
        # Body (circle)
        pygame.draw.circle(surface, color, (x, y), 30)
        
        # Eyes
        eye_offset = 5 + int(3 * abs(self.animation_frame % 60 - 30) / 30)
        pygame.draw.circle(surface, (0, 0, 0), (x - 10, y - 8), 3)
        pygame.draw.circle(surface, (0, 0, 0), (x + 10, y - 8), 3)
        
        # Mouth (changes based on state)
        if self.current_state == 'idle':
            pygame.draw.arc(surface, (0, 0, 0), (x - 8, y, 16, 8), 0, 3.14, 2)
        elif self.current_state in ['talking', 'joking', 'fact']:
            # Open mouth
            pygame.draw.circle(surface, (200, 100, 100), (x, y + 10), 4)
    
    def _draw_stats(self, surface, font):
        """Draw Mii stats"""
        stats_y = 160
        
        # Hunger bar
        hunger_text = font.render(f"Hunger: {{int(self.mii.hunger)}}%", True, (0, 0, 0))
        surface.blit(hunger_text, (10, stats_y))
        self._draw_bar(surface, 10, stats_y + 20, 280, 10, 
                      self.mii.hunger / 100, (255, 100, 100))
        
        # Happiness bar
        happy_text = font.render(f"Happy: {{int(self.mii.happiness)}}%", True, (0, 0, 0))
        surface.blit(happy_text, (10, stats_y + 40))
        self._draw_bar(surface, 10, stats_y + 60, 280, 10, 
                      self.mii.happiness / 100, (255, 200, 100))
    
    def _draw_bar(self, surface, x, y, width, height, percentage, color):
        """Draw a progress bar"""
        # Background
        pygame.draw.rect(surface, (200, 200, 200), (x, y, width, height))
        # Filled
        pygame.draw.rect(surface, color, (x, y, width * percentage, height))
        # Border
        pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 1)
    
    def _draw_speech_bubble(self, surface, font):
        """Draw speech bubble with message"""
        bubble_y = 210
        bubble_width = 280
        bubble_height = 60
        
        # Draw bubble
        pygame.draw.rect(surface, (255, 255, 200), 
                        (10, bubble_y, bubble_width, bubble_height))
        pygame.draw.rect(surface, (0, 0, 0), 
                        (10, bubble_y, bubble_width, bubble_height), 2)
        
        # Draw text (wrapped)
        words = self.message.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] < 260:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines[:2]):  # Max 2 lines
            text_render = font.render(line, True, (0, 0, 0))
            surface.blit(text_render, (20, bubble_y + 10 + i * 20))
    
    def _draw_buttons(self, surface, font):
        """Draw interactive buttons"""
        button_y = 280
        button_height = 25
        button_width = 85
        
        buttons = [
            {'label': 'Joke', 'action': 'joke', 'x': 10},
            {'label': 'Fact', 'action': 'fact', 'x': 105},
            {'label': 'Search', 'action': 'search', 'x': 200},
        ]
        
        for btn in buttons:
            # Draw button
            pygame.draw.rect(surface, (200, 150, 200), 
                           (btn['x'], button_y, button_width, button_height))
            pygame.draw.rect(surface, (100, 50, 100), 
                           (btn['x'], button_y, button_width, button_height), 2)
            
            # Draw label
            label = font.render(btn['label'], True, (0, 0, 0))
            surface.blit(label, (btn['x'] + 5, button_y + 3))
    
    def handle_click(self, mouse_pos):
        """Handle mouse clicks on buttons"""
        rel_x = mouse_pos[0] - self.x
        rel_y = mouse_pos[1] - self.y
        
        button_y = 280
        button_height = 25
        button_width = 85
        
        # Joke button
        if 10 <= rel_x <= 10 + button_width and button_y <= rel_y <= button_y + button_height:
            joke = self.tell_joke()
            print(f"Joke: {{joke['setup']}}\n{{joke['punchline']}}")
        
        # Fact button
        elif 105 <= rel_x <= 105 + button_width and button_y <= rel_y <= button_y + button_height:
            self.tell_fact()
        
        # Search button
        elif 200 <= rel_x <= 200 + button_width and button_y <= rel_y <= button_y + button_height:
            print("Opening search dialog...")
            self.open_search_dialog()
    
    def open_search_dialog(self):
        """Open search input dialog"""
        # This would open a simple input window
        self.message = "What do you want to search for?"
        self.current_state = 'searching'
    
    def save_companion_state(self):
        """Save companion state to file"""
        state = {
            'mii': self.mii.to_dict(),
            'search_history': self.search_history,
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs('data', exist_ok=True)
        with open('data/companion_state.json', 'w') as f:
            json.dump(state, f, indent=2)