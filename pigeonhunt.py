# Copyright (c) 2001-2011 WorldViz LLC. 
# All rights reserved. 
import viz
import vizact
import vizcam
import vizinfo
import viztask
import vizproximity
import vizfx.postprocess
from vizfx.postprocess.color import GrayscaleEffect
from vizfx.postprocess.composite import BlendEffect

import math
import random

# Script settings
TRIAL_COUNT = 5             # Number of trials per game
TRIAL_DURATION = 20         # Amount of time allowed for finding each pigeon (in seconds)
TRIAL_DELAY = 4             # Delay time between trials
PROXIMITY_RADIUS = 3.0      # Radius for proximity sensor around pigeon
FLASH_TIME = 3.0            # Time to flash screen at beginning of each trial

# List of hiding spots for pigeons
HIDING_SPOTS = [
    [13, 0, 19]
    ,[0, 0, 15]
    ,[14, 0, -14]
    ,[-12, 0, -15]
    ,[-6, 0, -12]
    ,[11, 0, 14]
    ,[6, 0, -12]
    ,[-12.5, 0, 22]
    ,[6.8, 0, -1.4]
    ,[-7, 0, 7]
]

INSTRUCTIONS = """
Help find the escaped pigeons before they fly away!
{} pigeons flew the coop and are hiding out in the piazza.
You have {} seconds to catch each one before it flys away.
Listen carefully and you might be able to hear where they are hiding.
Use the mouse and WASD keys to move around.
Press spacebar to begin the hunt!""".format(TRIAL_COUNT,TRIAL_DURATION)

RESULTS = """You found {} of {} pigeons.
Press spacebar to start over or escape to exit."""

TRIAL_SUCCESS = 'You caught the pigeon!'
TRIAL_FAIL = 'The pigeon flew away!'

viz.setMultiSample(4)
viz.fov(60)
viz.go(viz.FULLSCREEN)

# Setup directional light
viz.MainView.getHeadLight().disable()
sky_light = viz.addDirectionalLight(euler=(0,20,0))
sky_light.color(viz.WHITE)
sky_light.ambient([0.8]*3)
viz.setOption('viz.lightModel.ambient',[0]*3)

# Setup keyboard/mouse tracker
tracker = vizcam.addWalkNavigate(moveScale=2.0)
tracker.setPosition([0,1.8,0])
viz.link(tracker,viz.MainView)
viz.mouse.setVisible(False)

# Load piazza environment
piazza = viz.addChild('piazza.osgb')

# Loop fountain sound
piazza.playsound('fountain.wav',viz.LOOP,node='fountain-sound')

# Swap out sky with animated sky dome
piazza.getChild('pz_skydome').remove()
day = viz.add('sky_day.osgb')

# Add avatar sitting on a bench
male = viz.addAvatar('vcc_male2.cfg',pos=(-6.5,0,13.5),euler=(90,0,0))
male.state(6)

# Create pigeon
pigeon_root = viz.addGroup()
pigeon_root.visible(False)
pigeon = viz.addAvatar('pigeon.cfg',parent=pigeon_root)

# Add idle animation
random_walk = vizact.walkTo(pos=[vizact.randfloat(-0.5,0.5),0,vizact.randfloat(-0.5,0.5)])
random_animation = vizact.method.state(vizact.choice([1,3],vizact.RANDOM))
random_wait = vizact.waittime(vizact.randfloat(4.0,8.0))
pigeon_idle = vizact.sequence( random_walk, random_animation, random_wait, viz.FOREVER)
pigeon.runAction(pigeon_idle)

# Adding sound to pigeon
hooting = pigeon.playsound('birds.wav',viz.LOOP)
hooting.pause()

# Create flash screen quad
flash_quad = viz.addTexQuad(parent=viz.ORTHO)
flash_quad.color(viz.WHITE)
flash_quad.alignment(viz.ALIGN_LEFT_BOTTOM)
flash_quad.drawOrder(-10)
flash_quad.blendFunc(viz.GL_ONE,viz.GL_ONE)
flash_quad.visible(False)
viz.link(viz.MainWindow.WindowSize,flash_quad,mask=viz.LINK_SCALE)

# Create status bar background
status_bar = viz.addTexQuad(parent=viz.ORTHO)
status_bar.color(viz.BLACK)
status_bar.alpha(0.5)
status_bar.alignment(viz.ALIGN_LEFT_BOTTOM)
status_bar.drawOrder(-1)
viz.link(viz.MainWindow.LeftTop,status_bar,offset=[0,-80,0])
viz.link(viz.MainWindow.WindowSize,status_bar,mask=viz.LINK_SCALE)

# Create time limit text
time_text = viz.addText('',parent=viz.ORTHO,fontSize=40)
time_text.alignment(viz.ALIGN_CENTER_TOP)
time_text.setBackdrop(viz.BACKDROP_OUTLINE)
viz.link(viz.MainWindow.CenterTop,time_text,offset=[0,-20,0])

# Create score text
score_text = viz.addText('',parent=viz.ORTHO,fontSize=40)
score_text.alignment(viz.ALIGN_LEFT_TOP)
score_text.setBackdrop(viz.BACKDROP_OUTLINE)
viz.link(viz.MainWindow.LeftTop,score_text,offset=[20,-20,0])

# Create post process effect for blending to gray scale
gray_effect = BlendEffect(None,GrayscaleEffect(),blend=0.0)
gray_effect.setEnabled(False)
vizfx.postprocess.addEffect(gray_effect)

def DisplayInstructionsTask():
    """Task that display instructions and waits for keypress to continue"""
    panel = vizinfo.InfoPanel(INSTRUCTIONS,align=viz.ALIGN_CENTER,fontSize=22,icon=False,key=None)
    pigeonClone = pigeon.clone(scale=[200]*3)
    pigeonClone.addAction(vizact.spin(0,1,0,45))
    pigeonClone.enable(viz.DEPTH_TEST,op=viz.OP_ROOT)
    panel.addItem(pigeonClone,align=viz.ALIGN_CENTER)
    yield viztask.waitKeyDown(' ')
    panel.remove()

def TrialCountDownTask():
    """Task that count downs to time limit for trial"""

    # Action for text fading out
    text_fade = vizact.parallel(
        vizact.fadeTo(0,time=0.8,interpolate=vizact.easeOut)
        ,vizact.sizeTo([1.5,1.5,1.0],time=0.8,interpolate=vizact.easeOut)
    )

    # Reset time text
    time_text.clearActions()
    time_text.alpha(1.0)
    time_text.color(viz.WHITE)
    time_text.setScale([1,1,1])
    time_text.message(str(int(TRIAL_DURATION)))

    # Countdown from time limit
    start_time = viz.getFrameTime()
    last_remain = int(TRIAL_DURATION)
    while (viz.getFrameTime() - start_time) < TRIAL_DURATION:

        # Compute remaining whole seconds
        remain = int(math.ceil(TRIAL_DURATION - (viz.getFrameTime() - start_time)))

        # Update text if time remaining changed
        if remain != last_remain:
            if remain <= 5:
                time_text.alpha(1.0)
                time_text.color(viz.RED)
                time_text.setScale([1]*3)
                time_text.runAction(text_fade)
                viz.playSound('sounds/beep.wav')
            time_text.message(str(remain))
            last_remain = remain

        # Wait tenth of second
        yield viztask.waitTime(0.1)

def FlashScreen():
    """Flash screen and fade out"""
    flash_quad.visible(True)
    flash_quad.color(viz.WHITE)
    fade_out = vizact.fadeTo(viz.BLACK,time=FLASH_TIME,interpolate=vizact.easeOutStrong)
    flash_quad.runAction(vizact.sequence(fade_out,vizact.method.visible(False)))

def FadeToGrayTask():
    gray_effect.setBlend(0.0)
    gray_effect.setEnabled(True)
    yield viztask.waitCall(gray_effect.setBlend,vizact.mix(0.0,1.0,time=1.0))

def UpdateScore(score):
    """Update score text"""
    score_text.message('Found: {} / {}'.format(score,TRIAL_COUNT))

def TrialTask(pos):
    """Task for individual trial. Returns whether pigeon was found."""

    #Reset tracker to origin
    tracker.setPosition([0,1.8,0])
    tracker.setEuler([0,0,0])

    # Flash screen
    FlashScreen()

    # Place pigeon at new location
    pigeon_root.setPosition(pos)
    pigeon_root.visible(True)
    hooting.play(loop=True)

    # Create proximity sensor for pigeon using main view as target
    manager = vizproximity.Manager()
    #manager.setDebug(True)
    manager.addTarget( vizproximity.Target(viz.MainView) )
    sensor = vizproximity.Sensor(vizproximity.Sphere(PROXIMITY_RADIUS),pigeon_root)
    manager.addSensor(sensor)

    # Wait until pigeon is found or time runs out
    wait_time = viztask.waitTask( TrialCountDownTask() )
    wait_find = vizproximity.waitEnter(sensor)
    data = yield viztask.waitAny([wait_time,wait_find])

    # Hide pigeon and remove proximity sensor
    pigeon_root.visible(False)
    hooting.pause()
    manager.remove()

    # Return whether pigeon was found
    viztask.returnValue(data.condition is wait_find)

def MainTask():
    """Top level task that controls the game"""

    # Display instructions and wait for key press to continue
    yield DisplayInstructionsTask()

    # Create panel to display trial results
    resultPanel = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER,fontSize=25,icon=False,key=None)
    resultPanel.visible(False)

    while True:

        # Randomly choose hiding spots from list
        locations = random.sample(HIDING_SPOTS,TRIAL_COUNT)

        # Reset score
        score = 0
        UpdateScore(score)

        # Go through each position
        for pos in locations:

            # Perform a trial
            found = yield TrialTask(pos)

            # Update score and display status text
            if found:
                viz.playSound('sounds/pigeon_catch.wav')
                score += 1
                UpdateScore(score)
                tracker.runAction(vizact.spinTo(point=pos,time=0.8,interpolate=vizact.easeOutStrong))
                resultPanel.setText(TRIAL_SUCCESS)
            else:
                viz.playSound('sounds/pigeon_fly.wav')
                viztask.schedule(FadeToGrayTask())
                resultPanel.setText(TRIAL_FAIL)

            #Display success/failure message
            resultPanel.visible(True)

            # Add delay before starting next trial
            yield viztask.waitTime(TRIAL_DELAY)
            resultPanel.visible(False)

            # Disable gray effect
            gray_effect.setEnabled(False)

        #Display results and ask to quit or play again
        resultPanel.setText(RESULTS.format(score,TRIAL_COUNT))
        resultPanel.visible(True)
        yield viztask.waitKeyDown(' ')
        resultPanel.visible(False)

viztask.schedule( MainTask() )

# Pre-load sounds
viz.playSound('sounds/beep.wav',viz.SOUND_PRELOAD)
viz.playSound('sounds/pigeon_fly.wav',viz.SOUND_PRELOAD)
viz.playSound('sounds/pigeon_catch.wav',viz.SOUND_PRELOAD)