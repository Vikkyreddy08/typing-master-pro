import sys
import time
import random
import pygame
import json
import os
import numpy as np  # Add this import for proper sound generation
from pygame.locals import *

# File for high scores
HIGH_SCORES_FILE = "typing_master_highscores.json"

LEVELS = {
    1: {"sentence": "Hello Start typing to level up", "time_limit": 999, "req_acc": 70},
    2: {"sentence": "The quick brown fox jumps", "time_limit": 60, "req_acc": 75},
    3: {"sentence": "Python is great for coding", "time_limit": 50, "req_acc": 78},
    4: {"sentence": "Practice daily for tech interviews", "time_limit": 45, "req_acc": 80},
    5: {"sentence": "Django React fullstack projects rock", "time_limit": 40, "req_acc": 82},
    6: {"sentence": "BTech grads build amazing portfolios", "time_limit": 35, "req_acc": 84},
    7: {"sentence": "Mumbai coders type super fast now", "time_limit": 30, "req_acc": 86},
    8: {"sentence": "Level up your typing speed mastery", "time_limit": 27, "req_acc": 88},
    9: {"sentence": "You are almost a typing champion", "time_limit": 24, "req_acc": 90},
    10: {"sentence": "Congratulations Master Typist Achieved", "time_limit": 20, "req_acc": 92}
}

DIFFICULTY_MODES = {
    "Easy": {"time_mult": 1.5, "acc_mult": 0.8},
    "Medium": {"time_mult": 1.0, "acc_mult": 1.0},
    "Hard": {"time_mult": 0.7, "acc_mult": 1.2}
}

SUPER_MOTIVATIONS = [
    "🚀 YOU ARE A TYPING ROCKET!",
    "💥 EXPLOSIVE PROGRESS!",
    "⭐ YOU SHINE BRIGHTER!",
    "🔥 BURNING UP THE KEYBOARD!",
    "👑 LEVEL KING/QUEEN!",
    "⚡ LIGHTNING FAST FINGERS!",
    "🎯 PERFECT PRECISION!",
    "🏆 CHAMPION IN MAKING!"
]

class TypingTest:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.w, self.h = 1200, 800
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Typing Master Pro - Portfolio Edition')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 60)
        self.big_font = pygame.font.Font(None, 48)
        
        # Colors
        self.bg_color = (5, 5, 25)
        self.text_color = (255, 255, 255)
        self.correct_color = (0, 255, 150)
        self.error_color = (255, 100, 100)
        self.heading_color = (255, 215, 0)
        self.glow_color = (100, 255, 255)
        self.trophy_gold = (255, 215, 0)
        
        # Game states
        self.difficulty = "Medium"
        self.player_name = ""
        self.game_state = "menu"
        self.high_scores = self.load_high_scores()
        self.sounds_loaded = False
        
        # Load sounds safely
        self.load_sounds()
        
        # Game variables
        self.level = 1
        self.max_level = 10
        self.sentence = LEVELS[1]["sentence"]
        self.req_acc = LEVELS[1]["req_acc"]
        self.time_limit = LEVELS[1]["time_limit"]
        self.input_text = ""
        self.active = False
        self.show_results = False
        self.game_won = False
        self.start_time = 0
        self.time_used = 0.0
        self.accuracy = 0.0
        self.wpm = 0.0
        self.total_score = 0
        self.particles = []
        self.motivation_msg = ""
        self.stars_count = 0
        self.menu_selection = 0
        self.running = True

    def load_sounds(self):
        """Load sound effects safely with fallback"""
        try:
            self.click_sound = pygame.mixer.Sound("click.wav")
            self.success_sound = pygame.mixer.Sound("success.wav")
            self.level_up_sound = pygame.mixer.Sound("levelup.wav")
            self.game_win_sound = pygame.mixer.Sound("win.wav")
            self.sounds_loaded = True
        except:
            # Create simple beeps using numpy
            try:
                self.click_sound = self.create_beep(800, 0.05)
                self.success_sound = self.create_beep(1000, 0.15)
                self.level_up_sound = self.create_beep(1200, 0.25)
                self.game_win_sound = self.create_beep(1500, 0.4)
                self.sounds_loaded = True
            except:
                self.sounds_loaded = False
                print("Sound effects disabled - no numpy available")

    def create_beep(self, freq, duration):
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.sin(2 * np.pi * freq * np.linspace(0, duration, frames))
        arr = (arr * 32767).astype(np.int16)
        arr = np.column_stack((arr, arr))  # Stereo fix
        sound = pygame.sndarray.make_sound(arr)
        return sound


    def play_sound(self, sound):
        """Safely play sound"""
        if self.sounds_loaded:
            try:
                sound.play()
            except:
                pass

    def load_high_scores(self):
        if os.path.exists(HIGH_SCORES_FILE):
            try:
                with open(HIGH_SCORES_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_high_score(self):
        score_data = {
            "name": self.player_name,
            "difficulty": self.difficulty,
            "score": self.total_score,
            "stars": self.stars_count,
            "date": time.strftime("%Y-%m-%d %H:%M")
        }
        self.high_scores.append(score_data)
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:10]
        try:
            with open(HIGH_SCORES_FILE, 'w') as f:
                json.dump(self.high_scores, f, indent=2)
        except:
            print("Could not save high score")

    def draw_text(self, text, x, y, color, font=None):
        if font is None:
            font = self.font
        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))

    def draw_centered_text(self, text, y, color, font=None):
        if font is None:
            font = self.font
        surface = font.render(str(text), True, color)
        rect = surface.get_rect(center=(self.w//2, y))
        self.screen.blit(surface, rect)

    def draw_menu(self):
        overlay = pygame.Surface((self.w, self.h))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 60))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_centered_text("🎮 TYPING MASTER PRO 🎮", 120, self.heading_color, self.title_font)
        self.draw_centered_text("Choose Difficulty", 200, self.glow_color, self.big_font)
        
        modes = list(DIFFICULTY_MODES.keys())
        for i, mode in enumerate(modes):
            color = self.trophy_gold if i == self.menu_selection else self.glow_color
            self.draw_centered_text(f"[{'>' if i == self.menu_selection else ' '}] {mode}", 300 + i*60, color, self.big_font)
        
        self.draw_centered_text("ENTER = Select | ARROW KEYS = Navigate", 500, (0, 255, 255))
        self.draw_centered_text("L = Leaderboard | SPACE = Skip Sounds", 550, (255, 215, 0))

    def draw_leaderboard(self):
        overlay = pygame.Surface((self.w, self.h))
        overlay.set_alpha(240)
        overlay.fill((15, 25, 50))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_centered_text("🏆 GLOBAL LEADERBOARD 🏆", 100, self.trophy_gold, self.title_font)
        
        if not self.high_scores:
            self.draw_centered_text("No scores yet! Be the first!", 350, self.glow_color)
        else:
            y_offset = 250
            for i, score in enumerate(self.high_scores[:10]):
                rank_color = self.trophy_gold if i == 0 else self.glow_color if i < 3 else self.text_color
                line = f"{i+1}. {score['name']} - {score['score']}pts ({score['difficulty']}) ⭐{score['stars']}"
                self.draw_text(line, 100, y_offset + i*35, rank_color)
        
        self.draw_centered_text("ESC = Back", self.h - 100, (0, 255, 255))

    def draw_name_entry(self):
        overlay = pygame.Surface((self.w, self.h))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 60))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_centered_text(f"🎮 {self.difficulty} MODE 🎮", 150, self.heading_color, self.title_font)
        self.draw_centered_text("Enter your name:", 250, self.glow_color, self.big_font)
        
        pygame.draw.rect(self.screen, self.glow_color, (400, 350, 400, 60), 4)
        name_display = self.player_name if self.player_name else "Type your name here..."
        self.draw_centered_text(name_display, 385, self.text_color)
        
        self.draw_centered_text("Press ENTER to start!", 480, (0, 255, 255))

    def draw_sentence_highlighted(self, x, y):
        correct_chars = sum(1 for i, c in enumerate(self.sentence) if i < len(self.input_text) and self.input_text[i] == c)
        live_accuracy = (correct_chars / len(self.sentence)) * 100 if self.sentence else 0
        
        for i, char in enumerate(self.sentence):
            if i < len(self.input_text):
                color = self.correct_color if self.input_text[i] == char else self.error_color
            else:
                color = self.text_color
            self.draw_text(char, x + i * 20, y, color, self.small_font)
        
        self.draw_centered_text(f"{live_accuracy:.0f}%", 280, self.glow_color)

    def create_explosion(self, x, y):
        for _ in range(100):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-12, 12),
                'vy': random.uniform(-15, -3),
                'life': 90,
                'size': random.randint(3, 8)
            })
        self.play_sound(self.level_up_sound)

    def update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw_particles(self):
        for p in self.particles:
            alpha = int(255 * (p['life'] / 90))
            size = int(p['size'] * (p['life'] / 90))
            if size > 0:
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 215, 0, alpha), (size, size), size)
                self.screen.blit(s, (int(p['x']-size), int(p['y']-size)))

    def calculate_score(self):
        base_score = int(self.accuracy * 10)
        time_bonus = int((self.time_limit - self.time_used) * 5)
        difficulty_mult = {"Easy": 1, "Medium": 1.5, "Hard": 2}[self.difficulty]
        level_mult = self.level * 0.5
        return int((base_score + time_bonus) * difficulty_mult * level_mult)

    def check_level_complete(self):
        self.time_used = time.time() - self.start_time
        self.active = False
        
        correct_chars = sum(1 for i, c in enumerate(self.sentence) if i < len(self.input_text) and self.input_text[i] == c)
        self.accuracy = (correct_chars / len(self.sentence)) * 100
        self.wpm = (len(self.input_text) / 5) / (self.time_used / 60)
        
        level_score = self.calculate_score()
        self.total_score += level_score
        
        if self.accuracy >= self.req_acc:
            self.show_results = True
            self.play_sound(self.success_sound)
            self.create_explosion(self.w//2, self.h//2)
            self.motivation_msg = random.choice(SUPER_MOTIVATIONS)
            self.stars_count += 1
        else:
            self.input_text = ""

    def next_level(self):
        if self.level >= self.max_level:
            self.game_won = True
            self.play_sound(self.game_win_sound)
            self.save_high_score()
            self.create_explosion(self.w//2, self.h//2)
            return
        
        self.level += 1
        self.sentence = LEVELS[self.level]["sentence"]
        diff = DIFFICULTY_MODES[self.difficulty]
        self.req_acc = LEVELS[self.level]["req_acc"] * diff["acc_mult"]
        self.time_limit = LEVELS[self.level]["time_limit"] * diff["time_mult"]
        self.input_text = ""
        self.active = False
        self.show_results = False
        self.particles = []

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "playing":
                        if not self.active and not self.show_results and not self.game_won:
                            self.active = True
                            self.start_time = time.time()
                        elif self.show_results:
                            self.next_level()
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "menu":
                        if event.key == pygame.K_RETURN:
                            self.difficulty = list(DIFFICULTY_MODES.keys())[self.menu_selection]
                            self.game_state = "name_entry"
                        elif event.key == pygame.K_UP:
                            self.menu_selection = (self.menu_selection - 1) % len(DIFFICULTY_MODES)
                        elif event.key == pygame.K_DOWN:
                            self.menu_selection = (self.menu_selection + 1) % len(DIFFICULTY_MODES)
                        elif event.key == pygame.K_l:
                            self.game_state = "leaderboard"
                        elif event.key == pygame.K_SPACE:
                            self.sounds_loaded = False
                        self.play_sound(self.click_sound)
                        
                    elif self.game_state == "name_entry":
                        if event.key == pygame.K_RETURN and self.player_name.strip():
                            self.game_state = "playing"
                            self.level = 1
                            self.sentence = LEVELS[1]["sentence"]
                            diff = DIFFICULTY_MODES[self.difficulty]
                            self.req_acc = LEVELS[1]["req_acc"] * diff["acc_mult"]
                            self.time_limit = LEVELS[1]["time_limit"] * diff["time_mult"]
                            self.input_text = ""
                            self.active = False
                            self.show_results = False
                            self.game_won = False
                            self.total_score = 0
                            self.stars_count = 0
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif event.key != pygame.K_ESCAPE:
                            self.player_name += event.unicode
                            
                    elif self.game_state == "playing":
                        if self.active and not self.show_results:
                            if event.key == pygame.K_RETURN:
                                self.check_level_complete()
                            elif event.key == pygame.K_BACKSPACE:
                                self.input_text = self.input_text[:-1]
                                self.play_sound(self.click_sound)
                            else:
                                self.input_text += event.unicode
                                self.play_sound(self.click_sound)
                    elif event.key == pygame.K_ESCAPE:
                        if self.game_state in ["playing", "game_won", "leaderboard", "name_entry"]:
                            self.game_state = "menu"
                            self.menu_selection = 1

            self.screen.fill(self.bg_color)
            
            if self.player_name:
                self.draw_centered_text(f"Player: {self.player_name} | Score: {self.total_score}", 30, self.heading_color, self.small_font)
            
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "leaderboard":
                self.draw_leaderboard()
            elif self.game_state == "name_entry":
                self.draw_name_entry()
            elif self.game_state == "playing":
                self.draw_centered_text(f"Level {self.level}/{self.max_level} | {self.difficulty} ⭐{self.stars_count}", 60, self.heading_color, self.big_font)
                
                if self.active and not self.show_results:
                    time_elapsed = time.time() - self.start_time
                    time_left = max(0, self.time_limit - time_elapsed)
                    self.draw_centered_text(f"Time: {time_left:.1f}s | Goal: {self.req_acc:.0f}% | Score: {self.total_score}", 110, self.text_color)
                else:
                    self.draw_centered_text(f"Goal: {self.req_acc:.0f}% accuracy | Score: {self.total_score}", 110, self.text_color)
                
                self.draw_text("Type exactly:", 50, 170, self.text_color)
                self.draw_sentence_highlighted(50, 210)
                
                pygame.draw.rect(self.screen, self.glow_color, (50, 500, 1100, 60), 4)
                input_display = self.input_text if self.input_text else "Click to unleash your typing power..."
                self.draw_text(input_display, 70, 520, self.text_color)
                
                self.draw_text("ENTER=FINISH | Backspace OKAY | Click results to LEVEL UP! | ESC=Menu", 50, 700, (200, 255, 200), self.small_font)
                
                if self.show_results:
                    overlay = pygame.Surface((self.w, self.h))
                    overlay.set_alpha(220)
                    overlay.fill((15, 30, 70))
                    self.screen.blit(overlay, (0, 0))
                    
                    self.draw_centered_text(f"🎉 LEVEL {self.level} CRUSHED! 🎉", self.h//2 - 140, self.heading_color, self.title_font)
                    self.draw_centered_text(self.motivation_msg, self.h//2 - 80, self.glow_color, self.big_font)
                    self.draw_centered_text(f"Accuracy: {self.accuracy:.1f}%", self.h//2 - 20, self.correct_color)
                    self.draw_centered_text(f"WPM: {self.wpm:.1f}", self.h//2 + 30, self.correct_color)
                    self.draw_centered_text(f"Time: {self.time_used:.1f}s (+{self.calculate_score()}pts)", self.h//2 + 80, self.correct_color)
                    self.draw_centered_text("👆 CLICK TO DOMINATE NEXT LEVEL 👆", self.h//2 + 160, self.glow_color)
                
                elif self.game_won:
                    overlay = pygame.Surface((self.w, self.h))
                    overlay.set_alpha(240)
                    overlay.fill((20, 20, 60))
                    self.screen.blit(overlay, (0, 0))
                    
                    for i in range(5):
                        pygame.draw.circle(self.screen, self.trophy_gold, 
                                         (self.w//2 + i*30 - 120, self.h//2 - 150), 40 + i*5)
                    
                    self.draw_centered_text("🏆🏆🏆 TYPING LEGEND! 🏆🏆🏆", self.h//2 - 120, self.trophy_gold, self.title_font)
                    self.draw_centered_text(f"{self.player_name} - {self.total_score}pts", self.h//2 - 50, self.heading_color, self.big_font)
                    self.draw_centered_text(f"{self.difficulty} Mode ⭐{self.stars_count}", self.h//2 + 20, self.glow_color)
                    self.draw_centered_text("ESC = Main Menu", self.h//2 + 140, (0, 255, 255))
            
            self.update_particles()
            self.draw_particles()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    try:
        if 'np' not in globals():
            print("Install numpy for sound effects: pip install numpy")
        game = TypingTest()
        game.run()
    finally:
        pygame.quit()
        sys.exit()