import pygame
import widgets
import os
import random
import eyed3

"""Whole code for the music player, it uses self-made objects (buttons, sliders, frames, texts) in widgets.py. The idea was to use these objects the same
    way as tkinter's object but with more style options.
    The music player supports: play/pause, skip, previous, mixed mode, auto mode (plays automatically another song), a volume slider, a music time slider, 
    skip artist, previous artist. If you've listened to all available musics, the skip button stops working and it's intended (same thing if you're trying to go back
    while you haven't even skipped/listened to at least one music)"""

#Initialize pygame and its mixer
pygame.init()
pygame.mixer.init()

#Creates the different frames (which are Surfaces), it lays out the window which makes it easier for me to work with
width, height = 550, 720
res = (width, height)
DISPLAY = pygame.display.set_mode(res)
DISPLAY.fill((25, 25, 25))
CONTROLBUTTONS = widgets.Frame(DISPLAY, (width, 270), pos=(0, 450), color=(35, 35, 35))
CONTROLBUTTONS.fill((35, 35, 35))
ALBUMDISPLAY = widgets.Frame(DISPLAY, (width, height-270), pos=(0, 0), color=(25, 25, 25))
ALBUMDISPLAY.fill((25, 25, 25))

#Global variables
started, playing = False, False
mixedMode, autoMode = False, False
artistSelector, musicSelector = 0, 0
musicList = "MusicFolder/"
activeMusic = ""
totalMusic = 0
for music in os.listdir(musicList):
    totalMusic += len(os.listdir(musicList+music))-1
imgExtensions = [".jpg", ".gif", ".png", ".tng", ".webp"]
musicManager = {
    "Artists":os.listdir("MusicFolder"),
    "Musics":[],
    "prevMusics":[]
}

#Initialize the first music in "MusicFolder/"
musicManager["Musics"] = os.listdir(musicList+musicManager["Artists"][artistSelector])
currentArtist = musicManager["Artists"][artistSelector]
activeMusic = musicManager["Musics"][musicSelector]
musicPath = os.path.join((musicList+currentArtist), activeMusic)
musicData = eyed3.load(musicPath)
title = f"{musicData.tag.album_artist} - {musicData.tag.title}"
musicDuration = int(musicData.info.time_secs)
albumCover = ""
for file in os.listdir(musicList+currentArtist):
    extension = os.path.splitext(file)[1]
    if extension in imgExtensions:
        albumCover = os.path.join((musicList+currentArtist), file)
musicProgress = 0
print(musicDuration)
pygame.mixer.music.load(musicPath)


#Loads the next or previous music depending on which button we're clicking
def LoadMusic():
    global musicPath, musicDuration, albumCover, musicData, title
    
    pygame.mixer.music.stop() 
    pygame.mixer.music.unload()

    musicPath = os.path.join((musicList+currentArtist), activeMusic)
    print(musicPath)
    musicData = eyed3.load(musicPath)
    title = f"{musicData.tag.album_artist} - {musicData.tag.title}"
    for file in os.listdir(musicList+currentArtist):
        extension = os.path.splitext(file)[1]
        if extension in imgExtensions:
            albumCover = f"{musicList}{currentArtist}\{file}"
    musicTitle.NewText(title)
    musicDuration = int(musicData.info.time_secs)
    musicSlider.Update(musicDuration)
    pygame.mixer.music.load(musicPath)

#Play/pause button
def Play():
    global playing, started
    if playing == False and started == False:
        pygame.mixer.music.play(start=musicProgress)
        playing = True
        started = True
    elif playing == False and started:
        pygame.mixer.music.unpause()
        playing = True
    else:
        pygame.mixer.music.pause()
        playing = False

#Skips to the next artist or goes back to the first artist if we reached the last artist
def SkipArtists():
    global artistSelector, musicProgress, musicSelector
    musicProgress = 0
    musicSelector = 0
    artistSelector += 1
    if artistSelector > len(musicManager["Artists"])-1:
        artistSelector = 0
    UpdateMusicData()
    MusicChange()
    WasPlaying()

#Goes back to the previous artist, or goes to the last one if we're at the beginning
def PreviousArtists():
    global artistSelector, musicProgress, musicSelector
    musicProgress = 0
    musicSelector = 0
    artistSelector -= 1
    if artistSelector < 0:
        artistSelector = len(musicManager["Artists"])-1
    UpdateMusicData()
    MusicChange()
    WasPlaying()

#Defines skipping mode
def SkipMode():
    global mixedMode
    if mixedMode:
        mixedMode = False
    elif mixedMode == False: 
        mixedMode = True

#Defines if we're playing the next song automatically
def AutoMode():
    global autoMode
    if autoMode == False:
        autoMode = True
    elif autoMode:
        autoMode = False

#Skips depending on enabled modes and if we already went back to previously listened musics
def Skip():
    global activeMusic, musicManager, artistSelector, musicSelector, started, musicProgress, currentArtist
    if activeMusic not in musicManager["prevMusics"]:
        musicManager["prevMusics"].append(activeMusic)
    
    musicProgress = 0
    if mixedMode:
        if musicManager["Musics"] == musicManager["prevMusics"]:
            musicManager["prevMusics"] = musicManager["Musics"][:musicManager["Musics"].index(activeMusic)+1]
        RandomPick()
    elif mixedMode == False:
        if musicManager["Musics"] == musicManager["prevMusics"]:
            musicManager["prevMusics"] = musicManager["Musics"][:musicManager["Musics"].index(activeMusic)+1]
            for artist in os.listdir(musicList):
                if activeMusic in os.listdir(musicList+artist):
                    currentArtist = artist
            musicManager["Musics"] = os.listdir(musicList+currentArtist)
            artistSelector = musicManager["Artists"].index(currentArtist)
            musicSelector = musicManager["Musics"].index(activeMusic) + 1
            activeMusic = musicManager["Musics"][musicSelector]
        else:
            musicSelector += 1
            currentArtist = musicManager["Artists"][artistSelector]
            activeMusic = musicManager["Musics"][musicSelector]
        
        if len(musicManager["prevMusics"]) == len(musicManager["Musics"])-1:
            musicSelector = 0
            SkipArtists()
        elif len(musicManager["prevMusics"]) == totalMusic:
            return None
    else:
        return None
    
    LoadMusic()
    WasPlaying()

#Goes back to previously listened musics, previous musics are stored in a list that grows every time we skip/play the next music
def PreviousMusic():
    global musicManager, musicSelector, currentArtist, musicProgress, activeMusic, started
    musicProgress = 0
    if musicManager["Musics"] != musicManager["prevMusics"]:
        musicSelector = len(musicManager["prevMusics"])-1
        if musicSelector < 0:
            return None
        musicManager["Musics"] = musicManager["prevMusics"]
        activeMusic = musicManager["Musics"][musicSelector]
        for artist in os.listdir(musicList):
            if activeMusic in os.listdir(musicList+artist):
                currentArtist = artist
    else:
        musicSelector -= 1
        if musicSelector < 0:
            return None
        activeMusic = musicManager["Musics"][musicSelector]
        for artist in os.listdir(musicList):
            if activeMusic in os.listdir(musicList+artist):
                currentArtist = artist
    
    MusicChange()
    WasPlaying()

#Utility functions which shortens the skip function, defines how to choose a random song when mixed mode is enabled
def RandomPick():
    global activeMusic, musicManager, artistSelector, musicSelector, currentArtist
    while True:
            artistSelector = random.randint(0, len(musicManager["Artists"])-1)
            musicManager["Musics"] = os.listdir(musicList+musicManager["Artists"][artistSelector])
            musicSelector = random.randint(0, len(musicManager["Musics"])-1)
            currentArtist = musicManager["Artists"][artistSelector]
            activeMusic = musicManager["Musics"][musicSelector]
            if len(musicManager["prevMusics"]) == totalMusic:
                return None
            elif ".mp3" in activeMusic and activeMusic not in musicManager["prevMusics"]:
                MusicChange()
                break

#Utility function which updates the data when changing musics
def UpdateMusicData():
    global currentArtist, musicManager, activeMusic
    currentArtist = musicManager["Artists"][artistSelector]
    musicManager["Musics"] = os.listdir(musicList+currentArtist)
    activeMusic = musicManager["Musics"][musicSelector]

#Utility function that loads the music and change the cover
def MusicChange():
    LoadMusic()
    albumButton.ImgChange(albumCover)

#Defines how to handle music when changing if it was playing or not
def WasPlaying():
    global started
    if playing:
        pygame.mixer.music.play()
    else:
        started = False

#Enables the different elements, needed to make them usable since they need to be checked every frame, used in pygame's mainloop
def InitGUI():
    ALBUMDISPLAY.ActiveFrame()
    albumButton.ActiveButton()
    skipAlbButton.ActiveButton()
    prevAlbButton.ActiveButton()

    CONTROLBUTTONS.ActiveFrame()
    prevButton.ActiveButton()
    playButton.ActiveButton(buttonClicked="images-src/bouton-pause.png")
    nextButton.ActiveButton()
    modeButton.ActiveButton(buttonClicked="images-src/shuffleOn.png")
    autoButton.ActiveButton(buttonClicked="images-src/autoplayOn.png")

#Creates the different elements for the music player (buttons, sliders, texts) in their respective frames
albumButton = widgets.Button(ALBUMDISPLAY, 360, 360, centerX=True, centerY=True, imageButton=albumCover, type="OnClick", func=Play)
skipAlbButton = widgets.Button(ALBUMDISPLAY, 30, 60, color=(150, 150, 150), pourcentMode=True, posX=90, centerY=True, borderR=20, buttonLabel="images-src/right-arrow.png", type="OnClick", func=SkipArtists)
prevAlbButton = widgets.Button(ALBUMDISPLAY, 30, 60, color=(150, 150, 150), pourcentMode=True, posX=10, centerY=True, borderR=20, buttonLabel="images-src/left-arrow.png", type="OnClick", func=PreviousArtists)

musicTitle = widgets.TextLabel(CONTROLBUTTONS, title, 20, pourcentMode=True, centerX=True, posY=15)
musicSlider = widgets.Slider(CONTROLBUTTONS, 450, musicDuration, "x", thickness=4, pourcentMode=True, centerX=True, posY=31)
volumeSlider = widgets.Slider(CONTROLBUTTONS, 60, 10, "y", thickness=4, pourcentMode=True, posX=15, posY=60)
playButton = widgets.Button(CONTROLBUTTONS, 80, 80, color=(230, 230, 230), pourcentMode=True, centerX=True, posY=60, borderR=50, buttonLabel="images-src/play.png", func=Play)
prevButton = widgets.Button(CONTROLBUTTONS, 70, 70, color=(230, 230, 230), pourcentMode=True, posX=30, posY=60, borderR=50, buttonLabel="images-src/backward.png", type="OnClick", func=PreviousMusic)
nextButton = widgets.Button(CONTROLBUTTONS, 70, 70, color=(230, 230, 230), pourcentMode=True, posX=70, posY=60, borderR=50, buttonLabel="images-src/forward.png", type="OnClick", func=Skip)
modeButton = widgets.Button(CONTROLBUTTONS, 35, 35, color=(230, 230, 230), pourcentMode=True, posX=60, posY=85, borderR=50, buttonLabel="images-src/shuffleOff.png", func=SkipMode)
autoButton = widgets.Button(CONTROLBUTTONS, 35, 35, color=(230, 230, 230), pourcentMode=True, posX=40, posY=85, borderR=50, buttonLabel="images-src/autoplayOff.png", func=AutoMode)

pygame.display.flip()





#The program itself and Pygame's mainloop
if __name__ == "__main__":
    running = True
    while running: 
        setVolume = 10 * (volumeSlider.GetSlideValue()/100)
        InitGUI()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if autoMode and (musicProgress + int(pygame.mixer_music.get_pos()/1000)) >= musicDuration-1:
            Skip()
        elif (musicProgress + int(pygame.mixer_music.get_pos()/1000)) >= musicDuration-1:
            musicProgress = 0
        if musicSlider.GetChangingState():
            pygame.mixer.music.set_volume(0.0)
            musicProgress = int(musicDuration * (musicSlider.GetSlideValue()/100))
            pygame.mixer_music.play(start=musicProgress)
            if playing == False:
                pygame.mixer.music.pause()
        else:
            pygame.mixer.music.set_volume(setVolume / 10)
        
        musicSlider.ActiveSlider(musicProgress + int(pygame.mixer_music.get_pos()/1000))
        volumeSlider.ActiveSlider()

        