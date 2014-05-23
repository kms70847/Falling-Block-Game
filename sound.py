import pygame
import os

sounds = {}
sound_dir = "sounds"

def init(**kargs):
    """
        preinitializes sounds.
        sounds not in the initial list may still be played, but this may cause some latency the first time they are loaded.
        kargs:
        music: the file name, with extension, of the background music that will play on loop.
        sounds: an iterable of strings, each of which is the name of a wav in the sound directory. (no file extensions)
        
    """
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512) #keep a small buffer size to reduce sfx latency
    pygame.init()

    if "music" in kargs:
        music_name = kargs["music"]
        pygame.mixer.music.load(os.path.join(sound_dir, music_name))
        pygame.mixer.music.play(-1)
        

    sound_names = kargs.get("sounds", [])
    for name in sound_names:
        _load_sound(name)

def _load_sound(name):
    full_name = os.path.join(sound_dir, name) + ".wav"
    assert os.path.exists(full_name), "couldn't find file {}".format(full_name)
    sounds[name] = pygame.mixer.Sound(full_name)
    

def pause_music():
    pygame.mixer.music.pause()

def resume_music():
    pygame.mixer.music.unpause()


def play(name):
    if name not in sounds:
        _load_sound(name)
    sounds[name].play()