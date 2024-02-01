import speech_recognition as sr
from gtts import gTTS
import pygame
import os
from fuzzywuzzy import fuzz
from xgolib import XGO
import time
import spidev as SPI
import xgoscreen.LCD_2inch as LCD_2inch
from PIL import Image,ImageDraw,ImageFont
from key import Button


# to display on dog's display
button=Button()
dog=XGO("xgolite")
#define colors
btn_selected = (24,47,223)
btn_unselected = (20,30,53)
txt_selected = (255,255,255)
txt_unselected = (76,86,127)
splash_theme_color = (15,21,46)
color_black=(0,0,0)
color_white=(255,255,255)
color_red=(238,55,59)
#display init
display = LCD_2inch.LCD_2inch()
display.Init()
display.clear()

#font
font1 = ImageFont.truetype("/home/pi/model/msyh.ttc",15)
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc",16)
font3 = ImageFont.truetype("/home/pi/model/msyh.ttc",24)
splash = Image.new("RGB", (display.height, display.width ),splash_theme_color)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)

def lcd_draw_string(splash,x, y, text, color=(255,255,255), font_size=1, scale=1, mono_space=False, auto_wrap=True, background_color=(0,0,0)):
    splash.text((x,y),text,fill =color,font = scale) 

def lcd_rect(x,y,w,h,color,thickness):
    draw.rectangle([(x,y),(w,h)],fill=color,width=thickness)

import requests
net=False
try:
    html = requests.get("http://www.baidu.com",timeout=2)
    net=True
except:
    net=False

if net:
    dog = XGO(port='/dev/ttyAMA0',version="xgolite")
    #draw.line((2,98,318,98), fill=(255,255,255), width=2)
    draw.rectangle((20,30,300,100), splash_theme_color, 'white',width=3)
    lcd_draw_string(draw,5,100, "Say:'activate voice command to activate':", color=(255,255,255), scale=font2, mono_space=False)
    lcd_draw_string(draw,10,130, "Go forward|Go back|Turn left|Turn right", color=(0,255,255), scale=font2, mono_space=False)
    lcd_draw_string(draw,10,150, "Left translation|Right translation|Dance", color=(0,255,255), scale=font2, mono_space=False)
    lcd_draw_string(draw,10,170, "Push up|Take a pee|Sit dow|Wave hand", color=(0,255,255), scale=font2, mono_space=False)
    lcd_draw_string(draw,10,190, "Stretch|Hand shake|Pray", color=(0,255,255), scale=font2, mono_space=False)
    lcd_draw_string(draw,35,48, "Recording Audio", color=(255,0,0), scale=font3, mono_space=False)
    lcd_draw_string(draw,10,210, "Looking for food|Chicken head", color=(0,255,255), scale=font2, mono_space=False)
    display.ShowImage(splash)
        
    #time.sleep(2)
    while 1:


        def recognize_speech_with_noise_reduction(recognizer, source, timeout=None):
            try:
                print("Listening...")
                audio = recognizer.listen(source, timeout=timeout)
                command = recognizer.recognize_google(audio).lower()
                return command
            except sr.UnknownValueError:
                print("Sorry, could not understand audio.")
                return None
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return None
            except sr.WaitTimeoutError:
                print("Listening timed out, please speak louder or move closer to the microphone.")
                return None

        def say_text(text):
            tts = gTTS(text=text, lang='en')
            tts.save("command.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("command.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
            os.remove("command.mp3")

        COMMAND_LIST = ['go forward', 'go back', 'turn left', 'turn right', 'left translation', 'right translation', 
                        'dance', 'push up', 'take a pee', 'sit down', 'wave hand', 'stretch', 'hand shake', 'pray', 
                        'looking for food', 'chicken head','hath milau', 'what is your name', 'who are you',]

        def get_best_matching_command(input_text):
            best_match = None
            highest_similarity = 0
            for command in COMMAND_LIST:
                similarity = fuzz.partial_ratio(input_text, command)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = command
            return best_match

        def listen_for_activation_command(recognizer, source):
            print("Say 'activate voice command' to start listening for commands...")
            while True:
                recognized_phrase = recognize_speech_with_noise_reduction(recognizer, source)
                if recognized_phrase and "activate voice command" in recognized_phrase:
                    print("Voice command activated. You can now give commands.")
                    say_text("Voice command activated."+ 
                            "Bosss I am ready for your command")
                    listen_for_commands(recognizer, source)  # Start listening for commands
                    break

        def listen_for_deactivation_command(recognizer, source):
            print("Say 'deactivate voice command' to stop listening for commands...")
            while True:
                recognized_phrase = recognize_speech_with_noise_reduction(recognizer, source)
                if recognized_phrase and "deactivate voice command" in recognized_phrase:
                    print("Voice command deactivated.")
                    say_text("Voice command deactivated.")
                    listen_for_activation_command(recognizer, source)  # Return to the activation state
                    break

        def listen_for_commands(recognizer, source):
            while True:
                recognized_phrase = recognize_speech_with_noise_reduction(recognizer, source, timeout=None)
                if recognized_phrase:
                    print(f"You said: {recognized_phrase}")
                    if "deactivate voice command" in recognized_phrase:
                        print("Voice command deactivated.")
                        say_text("Voice command deactivated.")
                        listen_for_activation_command(recognizer, source)  # Return to the activation state
                        break
                    best_match = get_best_matching_command(recognized_phrase)
                    print(f"Best match: {best_match}")
                    # Define a dictionary to map commands to actions
                    command_actions = {
                        'hath milau': ("Shaking hand", 13),
                        'go forward': ("Going forward", 12),
                        'go back': ("Going back", -12),
                        'turn left': ("Turning left", 60),
                        'turn right': ("Turning right", -60),
                        'left translation': ("Left translation", 6),
                        'right translation': ("Right translation", -6),
                        'dance': ("Dancing", 23),
                        'push up': ("Pushing up", 9),
                        'take a pee': ("Taking a pee", 11),
                        'sit down': ("Sitting down", 12),
                        'wave hand': ("Waving hand", 13),
                        'stretch': ("Stretching", 6),
                        'hand shake': ("Shaking hand", 13),
                        'pray': ("Praying", 7),
                        'looking for food': ("Looking for food", 15),
                        'chicken head': ("Chicken head", 16)
                    }
                    
                    if best_match in command_actions:
                        action_text, action_code = command_actions[best_match]
                        print(f"Executing command: {best_match}")
                        say_text(action_text)
                        dog.action(action_code)
                        time.sleep(3)
                    else:
                        print(f"Executing command: {best_match}")
                        # say_text(f"Executing command: {best_match}")
                else:
                    print("No valid command recognized. Try again.")


        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            listen_for_activation_command(recognizer, source)  # Listen for the activation command
        if button.press_b():
            break
