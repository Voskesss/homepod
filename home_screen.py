import pygame
import math
import sys
import os
import assist
import time
import tools
from RealtimeSTT import AudioToTextRecorder
import threading

class AppCircle:
    def __init__(self, center, app_index, screen_size):
        self.center = center
        self.radius = min(screen_size) // 10
        self.app_index = app_index
        self.image = self.load_image(app_index)
        self.text = f'App {app_index}'

    def load_image(self, app_index):
        path = f'./apps/app_{app_index}/app_{app_index}.png'
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (2 * self.radius, 2 * self.radius))
            return img
        except FileNotFoundError:
            print(f"Image file not found: {path}")
            return None

    def draw(self, screen):
        if self.image:
            top_left = (self.center[0] - self.radius, self.center[1] - self.radius)
            screen.blit(self.image, top_left)
        else:
            pygame.draw.circle(screen, (255, 255, 255), self.center, self.radius)
            font = pygame.font.Font(None, 32)
            text_surface = font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.center)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return math.hypot(pos[0] - self.center[0], pos[1] - self.center[1]) <= self.radius

def create_circles(screen_size):
    circles = []
    num_circles = 8
    angle_step = 360 / num_circles
    center_x, center_y = screen_size[0] // 2, screen_size[1] // 2
    radius = min(screen_size) // 2.6

    for i in range(num_circles):
        angle = math.radians(angle_step * i)
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        circles.append(AppCircle((x, y), i + 1, screen_size))
    return circles


def create_text_surfaces(response, font, screen_width, margin):
    words = response.split()
    lines = []
    current_line = []
    for word in words:
        test_line = current_line + [word]
        test_surface = font.render(' '.join(test_line), True, (255, 255, 255))
        if test_surface.get_width() <= screen_width - 2 * margin:
            current_line = test_line
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))

    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in lines]
    total_height = sum(surface.get_height() for surface in text_surfaces)
    start_y = (screen.get_height() - total_height) // 2

    text_rects = [surface.get_rect(center=(screen_width // 2, start_y + i * surface.get_height())) for i, surface in enumerate(text_surfaces)]

    return text_surfaces, text_rects

def apply_blur_ring_and_text(screen, text, blue_ring_thickness=100):
    # Maak een kopie van het scherm om te blurren
    blurred = screen.copy()
    
    # Schaal naar beneden en weer terug om een blur-effect te creëren
    small_surface = pygame.transform.smoothscale(blurred, (screen.get_width()//4, screen.get_height()//4))
    blurred = pygame.transform.smoothscale(small_surface, (screen.get_width(), screen.get_height()))
    
    # Teken het geblurde oppervlak op het scherm
    screen.blit(blurred, (0, 0))
    
    # Teken een blauwe ring
    pygame.draw.circle(screen, (0, 0, 255, 128), (screen.get_width()//2, screen.get_height()//2), 
                       min(screen.get_width(), screen.get_height())//2 - blue_ring_thickness//2, blue_ring_thickness)
    
    # Render de tekst
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(text_surface, text_rect)
    
    pygame.display.flip()

def run_voice_assistant(circles, screen, background, draw_event, idle_event):
    recorder = AudioToTextRecorder(spinner=False, model="tiny.en", language="en", post_speech_silence_duration=0.1, silero_sensitivity=0.4)
    hot_words = ["happy", "alexa"]
    stop_words = ["stop", "end", "goodbye"]
    print("Zeg iets...")
    
    while True:
        current_text = recorder.text()
        if current_text:
            print(f"Huidige tekst: {current_text}")
        
        if any(hot_word in current_text.lower() for hot_word in hot_words):
            print(f"Hot word gedetecteerd: {current_text}")
            
            conversation_active = True
            while conversation_active:
                print("Assistent luistert... Zeg 'stop' om te beëindigen.")
                
                recorder.stop()
                recorder.start()
                user_question = wait_for_input(recorder, timeout=15)
                
                if not user_question:
                    print("Geen input gedetecteerd. Einde van de conversatie.")
                    assist.TTS("Ik heb een tijdje niets gehoord. Als je nog vragen hebt, zeg dan 'Happy' om me opnieuw te activeren.")
                    break
                
                print(f"Gebruikersvraag: {user_question}")
                
                if any(stop_word in user_question.lower() for stop_word in stop_words):
                    print("Assistent gestopt.")
                    assist.TTS("Tot ziens!")
                    conversation_active = False
                    break
                
                # Indicate that voice assistant is drawing
                draw_event.set()
                idle_event.clear()

                # Start the blur effect and display the query
                apply_blur_ring_and_text(screen, user_question, blue_ring_thickness=100)
                
                # Verwerk de vraag met tools.parse_command
                response = tools.parse_command(user_question)
                print(f"Ruwe response van parse_command: {repr(response)}")

                if response and isinstance(response, str) and response.strip():
                    print(f"Antwoord van assistent: {response}")
                    assist.TTS(response)
                else:
                    error_message = "Excuses, ik kon geen antwoord vinden op je vraag."
                    print(f"Antwoord van assistent: {error_message}")
                    assist.TTS(error_message)
                
                # Indicate that the voice assistant is done drawing
                idle_event.set()
                draw_event.clear()
                
                # Pauze na het antwoord
                time.sleep(2)
                assist.TTS("Heb je nog een vraag?")
                
                # Reset voor de volgende vraag
                recorder.stop()
                recorder.start()
        
        # Kort wachten om CPU-gebruik te verminderen
        time.sleep(0.1)

def wait_for_input(recorder, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        user_input = recorder.text()
        if user_input and len(user_input) > 3:  # Negeer zeer korte inputs
            return user_input
        time.sleep(0.1)
    return None

def run_home_screen(screen):
    screen_size = screen.get_size()
    background = pygame.image.load('./resources/background.jpg')
    background = pygame.transform.scale(background, screen_size)
    
    circles = create_circles(screen_size)
    
    running = True
    draw_event = threading.Event()
    idle_event = threading.Event()
    idle_event.set()  # Initially set the idle event to allow drawing

    print("Here")
    voice_thread = threading.Thread(target=run_voice_assistant, args=(circles, screen, background, draw_event, idle_event))
    voice_thread.daemon = True
    voice_thread.start()
    print("Here2")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for circle in circles:
                    if circle.is_clicked(event.pos):
                        app_index = circles.index(circle) + 1
                        app_module_name = f'apps.app_{app_index}.app_{app_index}'
                        mod = __import__(app_module_name, fromlist=[''])
                        mod.run(screen)

        # Draw home screen only if the voice assistant is idle
        if idle_event.is_set():
            screen.blit(background, (0, 0))  # Draw background first
            for circle in circles:  # Then draw apps (circles)
                circle.draw(screen)

        pygame.display.flip()
        pygame.time.delay(1)






if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1080, 1080))

    # Run the home screen
    run_home_screen(screen)
