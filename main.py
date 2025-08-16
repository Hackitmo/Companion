import sys
import random
import os
import pygame
import time
import requests
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout)
from PyQt5.QtCore import (Qt, QTimer, QSize, QBuffer, QIODevice)
from PyQt5.QtGui import (QMovie, QFont)

class TextWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Компаньон - Сообщения")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.chat_bubble = QLabel()
        self.chat_bubble.setStyleSheet("""
            background-color: rgba(255, 255, 255, 220);
            border-radius: 15px;
            padding: 10px;
            border: 2px solid #ffb6c1;
            color: #333;
            font-weight: bold;
        """)
        self.chat_bubble.setFont(QFont('Arial', 10))
        self.chat_bubble.setWordWrap(True)
        self.chat_bubble.setAlignment(Qt.AlignCenter)
        self.chat_bubble.setMinimumWidth(300)
        self.chat_bubble.setMaximumWidth(400)
        self.chat_bubble.hide()
        
        self.layout.addWidget(self.chat_bubble)
        self.setFixedSize(400, 150)
        
        self.bubble_timer = QTimer(self)
        self.bubble_timer.timeout.connect(self.hide_bubble)
        self.bubble_timer.setSingleShot(True)
        
        self.current_message = ""
    
    def show_message(self, text):
        if self.bubble_timer.isActive():
            self.bubble_timer.stop()
        self.current_message = text
        self.chat_bubble.setText(text)
        self.chat_bubble.adjustSize()
        self.chat_bubble.show()
        
        if text not in ["До встречи! Буду скучать!", "Ой, ты уже уходишь? До скорой встречи!"]:
            self.bubble_timer.start(5000)
    
    def hide_bubble(self):
        if self.current_message not in ["До встречи! Буду скучать!", "Ой, ты уже уходишь? До скорой встречи!"]:
            self.chat_bubble.hide()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPos() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start)

class GifWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Компаньон - Анимация")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.animation_label = QLabel()
        self.animation_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.animation_label)
        
        self.setFixedSize(300, 300)
        
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_animation)
        self.check_timer.start(100)
        
        self.current_movie = None
        self.buffer = None
    
    def set_gif(self, movie_data):
        if self.current_movie:
            self.current_movie.stop()
            self.current_movie = None
        
        self.buffer = QBuffer()
        self.buffer.open(QIODevice.ReadWrite)
        self.buffer.write(movie_data)
        self.buffer.seek(0)
        
        self.current_movie = QMovie()
        self.current_movie.setDevice(self.buffer)
        self.current_movie.setCacheMode(QMovie.CacheAll)
        
        if self.current_movie.isValid():
            self.animation_label.setMovie(self.current_movie)
            self.current_movie.start()
            
            if self.current_movie.frameCount() > 0:
                self.current_movie.jumpToFrame(0)
                size = self.current_movie.currentImage().size()
                if not size.isEmpty():
                    self.setFixedSize(size)
        else:
            print("Ошибка: Не удалось загрузить гифку")
            self.animation_label.setText("Аниме-девушка")
            self.animation_label.setStyleSheet("background: rgba(255, 255, 255, 200); color: black;")
            self.setFixedSize(300, 300)
    
    def check_animation(self):
        if self.current_movie and self.current_movie.state() != QMovie.Running:
            self.current_movie.start()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPos() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start)

class AnimeGirl:
    def __init__(self):
        self.movies = {}
        self.current_animation = None
        self._load_tenor_gifs()
        
        if "idle" in self.movies:
            self.set_emotion("idle")

    def _load_tenor_gifs(self):
        try:
            API_KEY = "LIVDSRZULELA"
            emotions = {
                "idle": "anime girl smile",
                "happy": "anime girl happy",
                "sad": "anime girl sad",
                "flirty": "anime girl blush",
                "thinking": "anime girl thinking",
                "tired": "anime girl tired"
            }
            
            for emotion, query in emotions.items():
                url = f"https://g.tenor.com/v1/search?q={query}&key={API_KEY}&limit=1"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                gif_url = response.json()["results"][0]["media"][0]["gif"]["url"]
                gif_data = requests.get(gif_url, timeout=15).content
                
                self.movies[emotion] = {
                    'data': gif_data,
                    'size': QSize(300, 300)
                }
            
            print("GIF успешно загружены с Tenor")
            return True
                
        except Exception as e:
            print(f"Ошибка загрузки GIF: {e}")
            self.movies = {
                "idle": {'data': b'', 'size': QSize(300, 300)},
                "happy": {'data': b'', 'size': QSize(300, 300)},
                "sad": {'data': b'', 'size': QSize(300, 300)},
                "flirty": {'data': b'', 'size': QSize(300, 300)},
                "thinking": {'data': b'', 'size': QSize(300, 300)},
                "tired": {'data': b'', 'size': QSize(300, 300)}
            }
            return False

    def set_emotion(self, emotion):
        if emotion in self.movies:
            self.current_animation = self.movies[emotion]
            return True
        return False

class SimpleChatAI:
    def __init__(self):
        self.ngrams = defaultdict(lambda: defaultdict(int))
        self.context_size = 2
        self.last_action_time = time.time()
        self.action_cooldown = 1
        
        self.responses = {
            "greeting": ["Привет-привет! Как твои дела?", "О-о, кто это тут у нас? ^_^", "Здравствуй! Как прошел твой день?"],
            "question": ["Хм... {user_question}... Дай-ка подумать...", "Интересный вопрос... {user_question}... Я думаю...", "Ох, {user_question}... Давай обсудим это!"],
            "flirty": ["*смущенно краснеет* Ты сегодня такой милый!", "Ой, ну что ты такое говоришь~ *прикрывает лицо руками*", "Ты меня смущаешь! *улыбается*"],
            "sad": ["Мне грустно это слышать... Хочешь об этом поговорить?", "*вздыхает* Я понимаю тебя... Что тебя беспокоит?", "Давай поговорим о чем-то приятном? Или расскажи мне больше..."],
            "tired": ["Похоже, тебе нужен отдых... Хочешь, я расскажу что-нибудь приятное?", "*кивает* Я понимаю... Усталость - это нормально. Как я могу помочь?", "Может, сделаем перерыв? Я могу просто посидеть с тобой в тишине..."],
            "default": ["Расскажи мне больше!", "Я слушаю тебя очень внимательно!", "Интересно! Что еще ты хочешь рассказать?"]
        }
        
        self._init_simple_model()
    
    def _init_simple_model(self):
        training_data = [
            "привет как дела", "как тебя зовут", "что ты умеешь",
            "ты кто такая", "пока дорогая", "ты мне нравишься",
            "какой твой любимый аниме", "мне грустно сегодня",
            "я устал на работе", "как твое настроение"
        ]
        
        for sentence in training_data:
            words = sentence.split()
            for i in range(len(words) - self.context_size):
                context = tuple(words[i:i+self.context_size])
                next_word = words[i+self.context_size]
                self.ngrams[context][next_word] += 1
    
    def generate_response(self, prompt):
        current_time = time.time()
        if current_time - self.last_action_time < self.action_cooldown:
            return None
            
        try:
            prompt = prompt.lower()
            words = prompt.split()
            
            if any(w in prompt for w in ["привет", "здравствуй", "хай"]):
                return random.choice(self.responses["greeting"])
            elif any(w in prompt for w in ["люблю", "нравишься", "красив", "мила"]):
                return random.choice(self.responses["flirty"])
            elif any(w in prompt for w in ["грустно", "печаль", "плохо"]):
                return random.choice(self.responses["sad"])
            elif any(w in prompt for w in ["устал", "усталость", "утомился"]):
                return random.choice(self.responses["tired"])
            elif "?" in prompt:
                question = prompt.split("?")[0].strip()
                template = random.choice(self.responses["question"])
                return template.format(user_question=question)
            
            if len(words) >= self.context_size:
                context = tuple(words[-self.context_size:])
                if context in self.ngrams:
                    next_words = self.ngrams[context]
                    total = sum(next_words.values())
                    probs = {word: count/total for word, count in next_words.items()}
                    next_word = max(probs.items(), key=lambda x: x[1])[0]
                    return f"Ты упомянул {next_word}... Это интересно! Расскажи подробнее."
            
            return random.choice(self.responses["default"])
            
        except Exception as e:
            print(f"Ошибка генерации ответа: {e}")
            return random.choice(self.responses["default"])
    
    def should_show_action(self):
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            self.last_action_time = current_time
            return True
        return False

class VoiceEngine:
    def __init__(self):
        pygame.mixer.init()
        self.audio_files = {
            "greeting": "audio/greeting.wav",
            "farewell": "audio/farewell.wav",
            "thinking": "audio/thinking.wav",
            "happy": "audio/happy.wav",
            "idle": "audio/idle.wav",
            "flirty": "audio/flirty.wav",
            "sad": "audio/sad.wav",
            "tired": "audio/tired.wav"
        }
        
        for emotion in self.audio_files.keys():
            path = self.audio_files[emotion]
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path):
                print(f"Создан фиктивный файл: {path}")
                open(path, 'wb').close()
    
    def speak(self, emotion):
        if emotion in self.audio_files and os.path.exists(self.audio_files[emotion]):
            try:
                pygame.mixer.music.load(self.audio_files[emotion])
                pygame.mixer.music.play()
            except Exception as e:
                print()

class AnimeCompanion:
    def __init__(self):
        self.chat_ai = SimpleChatAI()
        self.ai = AnimeGirl()
        self.voice = VoiceEngine()
        
        self.text_window = TextWindow()
        self.gif_window = GifWindow()
        
        if self.ai.current_animation:
            self.update_gif()
        
        self.position_windows()
        
        self.text_window.show()
        self.gif_window.show()
        
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.random_action)
        self.idle_timer.start(5000)
    
    def update_gif(self):
        if self.ai.current_animation:
            self.gif_window.set_gif(self.ai.current_animation['data'])
    
    def position_windows(self):
        screen = QApplication.primaryScreen().geometry()
        
        gif_x = 100
        gif_y = (screen.height() - 300) // 2
        self.gif_window.move(gif_x, gif_y)
        
        text_x = gif_x + 350
        text_y = (screen.height() - 150) // 2
        self.text_window.move(text_x, text_y)
    
    def show_message(self, text, emotion=None):
        self.text_window.show_message(text)
        
        if emotion and self.ai.set_emotion(emotion):
            self.update_gif()
            self.voice.speak(emotion)
    
    def random_action(self):
        if self.chat_ai.should_show_action() and random.random() < 0.3:
            actions = [
                ("*потягивается*", "idle"),
                ("*осматривается*", "thinking"),
                ("*улыбается*", "happy")
            ]
            action_text, emotion = random.choice(actions)
            self.show_message(action_text, emotion)
    
    def determine_emotion(self, text):
        text = text.lower()
        if any(w in text for w in ["привет", "здравствуй", "хай"]):
            return "happy"
        elif any(w in text for w in ["люблю", "нравишься", "красив", "мила"]):
            return "flirty"
        elif any(w in text for w in ["грустно", "плохо", "печаль"]):
            return "sad"
        elif any(w in text for w in ["устал", "усталость", "утомился"]):
            return "tired"
        elif "?" in text:
            return "thinking"
        return "idle"

if __name__ == "__main__":
    if not os.path.exists("audio"):
        os.makedirs("audio", exist_ok=True)
        print("Создана папка 'audio'. Добавьте туда аудиофайлы для озвучки.")
    
    internet_available = True
    try:
        requests.get("https://www.google.com", timeout=5)
        print("Интернет-соединение доступно. Загрузка GIF...")
    except:
        internet_available = False
    
    app = QApplication(sys.argv)
    companion = AnimeCompanion()
    
    print("Привет! Я твоя компаньонка ^_^")
    print("Поговори со мной - спрашивай о чем угодно!")
    
    companion.show_message("Привет! ^_^", "happy")
    
    while True:
        try:
            user_input = input("\nТы: ").strip()
            
            if user_input.lower() in ["пока", "выход", "до свидания"]:
                print("\nАниме: До встречи! Буду скучать!")
                companion.show_message("До встречи! Буду скучать!", "sad")
                time.sleep(2)
                break
            else:
                emotion = companion.determine_emotion(user_input)
                response = companion.chat_ai.generate_response(user_input)
                
                if response:
                    print("\nАниме:", response)
                    companion.show_message(response, emotion)
                else:
                    companion.show_message("Дай-ка подумаю...", "thinking")
                
        except (KeyboardInterrupt, EOFError):
            print("\nАниме: Ой, ты уже уходишь? До скорой встречи!")
            companion.show_message("Ой, ты уже уходишь? До скорой встречи!", "sad")
            time.sleep(2)
            break
    
    sys.exit(app.exec_())
