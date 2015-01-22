#!/usr/bin/env python

import lirc, sys
import subprocess
import re

BUS_SPOTIFY="qdbus org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player."
HOST="skane@192.168.1.9"
sessionkey=""
SHOW_ERRORS=False

def main():
    sockid = lirc.init("lircremote", blocking = True)
    retrieve_session_key()
    while True:
        codeIR = lirc.nextcode()

        if codeIR:
            exec(codeIR[0] + '()')


# *************************************** #
#             SSH
# *************************************** #
def simple_ssh(command, handler):
    return my_ssh(command, handler, ["ssh", "%s" % HOST, command])

def session_ssh(command, handler):
    return my_ssh(command, handler, ["ssh", "%s" % HOST, "DBUS_SESSION_BUS_ADDRESS=\""+sessionkey+"\"", command])

def my_ssh(command, handler, popen_arg):
    ssh = subprocess.Popen(popen_arg, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    result = ssh.stdout.readlines()
    if result == []:
        if SHOW_ERRORS:
            error = ssh.stderr.readlines()
            print >>sys.stderr, "ERROR: %s" % error
    else:
        if handler:
            return handler(result)
        return result


# *************************************** #
#             BUS SESSION
# *************************************** #
def retrieve_session_key():
    global sessionkey
    sessionkey = simple_ssh("cat ~/spotifySessionFile", False)[0].strip()


# *************************************** #
#               VOLUME
# *************************************** #
def volume_change_handler(result):
    print re.search('\[\d*%\]', result[5].strip()).group(0)
def volume_up():
    simple_ssh("amixer -D pulse sset Master 5%+", volume_change_handler)
def volume_down():
    simple_ssh("amixer -D pulse sset Master 5%-", volume_change_handler)


# *************************************** #
#               SPOTIFY
# *************************************** #
def spotify_callback_handler(result):
    print result

def spotify_playpause():
    session_ssh(BUS_SPOTIFY + "PlayPause", spotify_callback_handler)
def spotify_next():
    session_ssh(BUS_SPOTIFY + "Next", spotify_callback_handler)
def spotify_previous():
    session_ssh(BUS_SPOTIFY + "Previous", spotify_callback_handler)
def spotify_status():
    session_ssh(BUS_SPOTIFY + "PlaybackStatus", spotify_callback_handler)


# *************************************** #
#               COMMANDS
# *************************************** #
def close_remote():
    session_ssh("notify-send 'closing remote'",False)
    print "Shutting down remote."
    sys.exit()

def check_it():
    exec('close_remote()')

def not_supported():
    print "Not supported."
    #session_ssh("notify-send 'invalid entry'",False)

main()
