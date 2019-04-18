import speech_recognition as sr
import pyaudio
import wave
import audioop
from collections import deque
import os
import time
import math
import re

"""
This script is adapted from the original by Jeyson Molina.
https://github.com/jeysonmc/python-google-speech-scripts
This version does not utilise Google speech API due to the
requirement for an API key and subscription to Google Cloud
services. Instead it uses SpeechRecognition library which 
supports Google's speech API, along with other free ones.
https://pypi.org/project/SpeechRecognition/

"""

LANG_CODE = 'en-US'  # Language to use

# Microphone stream config.
CHUNK = 1024  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 8500  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 0.5  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.


def audio_int(num_samples=50):
    """ Gets average audio intensity of your mic sound. You can use it to get
        average intensities while you're talking and/or silent. The average
        is the avg of the 20% largest intensities recorded.
    """

    print("Getting intensity values from mic.")
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    values = [math.sqrt(abs(audioop.avg(stream.read(CHUNK), 4))) 
              for x in range(num_samples)] 
    values = sorted(values, reverse=True)
    r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
    print(" Finished ")
    print(" Average audio intensity is ", r)
    stream.close()
    p.terminate()
    return r


def listen_for_speech(threshold=THRESHOLD, num_phrases=-1,
        trigwords=None):
    """
    Listens to Microphone, extracts phrases from it and sends it to 
    Google's TTS service and returns response. a "phrase" is sound 
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process 
    (-1 for infinite).
    trigwords is an optional argument containing list of one or more
    trigger words which will break the function and return the
    trigger as response.
    """

    #Open stream
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* Listening mic. ")
    audio2send = []
    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK
    slid_win = deque(maxlen=math.ceil(SILENCE_LIMIT * rel))
    #Prepend audio from 0.5 seconds before noise was detected
    prev_audio = deque(maxlen=math.ceil(PREV_AUDIO * rel)) 
    started = False
    n = num_phrases
    response = []

    while (num_phrases == -1 or n > 0):
        cur_data = stream.read(CHUNK)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        #print(slid_win[-1])
        if sum([x > THRESHOLD for x in slid_win]) > 0:
            if not started:
                print("Starting record of phrase")
                started = True
            audio2send.append(cur_data)
        elif started is True:
            print("Finished")
            # The limit was reached, finish capture and deliver.
            filename = save_speech(list(prev_audio) + audio2send, p)
            # Send file to Google and get response
            r = stt_google_wav(filename) 

            # check if response contains a trig word
            if trigwords is not None:
                for word in trigwords:
                    if word in r:#find_whole_word(word)(r):
                        print("* Trig word detected: ", r, word)
                        stream.close()
                        p.terminate()
                        os.remove(filename)
                        num_phrases = 1
                        return word

            if num_phrases == -1:
                print("Response", r)
            else:
                response.append(r)
            # Remove temp file. Comment line to review.
            os.remove(filename)
            # Reset all
            started = False
            slid_win = deque(maxlen=math.ceil(SILENCE_LIMIT * rel))
            prev_audio = deque(maxlen=math.ceil(0.5 * rel)) 
            audio2send = []
            n -= 1
            print("Listening ...")
        else:
            prev_audio.append(cur_data)

    print("* Done recording")
    stream.close()
    p.terminate()

    return response


def save_speech(data, p):
    """ Saves mic data to temporary WAV file. Returns filename of saved 
        file """
    filename = 'output_'+str(int(time.time()))+'.wav'
    # writes data to WAV file
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(p.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(data))
    waveFile.close()
    return filename


def stt_google_wav(audio_fname):
    """ Sends audio file (audio_fname) to Google's text to speech 
        service and returns service's response. """

    print("Sending ", audio_fname)
    r = sr.Recognizer()
    try:
        with sr.WavFile(audio_fname) as source:
            audio = r.record(source)
            res = r.recognize_google(audio, language="en-US")
    except:
        res = ""
    return res

def find_whole_word(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

#if(__name__ == '__main__'):
    #listen_for_speech()  # listen to mic.
    #print(stt_google_wav('hello.flac'))  # translate audio file
    #audio_int()  # To measure your mic levels
