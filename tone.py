# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Solution to CS 410P/510 Sound HW2: Tone

import argparse, math, sys, time
from scipy import io, signal
import numpy as np
import sounddevice as sd

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

# Read from a 16-bit WAV file. Returns 
def read_wav(filename):
    rate, data = io.wavfile.read(filename)
    assert data.dtype == np.int16
    data = data.astype(np.float32)
    data /= 32768
    return rate, data

# Play a tone on the computer.
def play(rate, wav):
    # Deal with stereo.
    channels = 1
    if wav.ndim == 2:
        channels = 2

    # Set up and start the stream.
    stream = sd.RawOutputStream(
        samplerate = rate,
        blocksize = BUFFER_SIZE,
        channels = channels,
        dtype = 'float32',
    )

    # Write the samples.
    stream.start()
    done = False
    for buffer in np.array_split(wav, BUFFER_SIZE):
        stream.write(buffer)

    # Tear down the stream.
    stream.stop()
    stream.close()

# Parse command-line arguments.
argp = argparse.ArgumentParser()
argp.add_argument("--bass", help="bass emphasis", type=np.float32, default=0.5)
argp.add_argument("--midrange", help="midrange emphasis", type=np.float32, default=0.5)
argp.add_argument("--treble", help="treble emphasis", type=np.float32, default=0.5)
argp.add_argument("wav", help="audio file")
args = argp.parse_args()

rate, data = read_wav(args.wav)

# Build filters.
def make_filter(freqs, btype):
    global rate
    freqs = 2.0 * np.array(freqs, dtype=np.float32) / rate
    return signal.firwin(1023, freqs, pass_zero=btype)

filter_bass = make_filter(200, 'lowpass')
filter_mid = make_filter((200, 2500), 'bandpass')
filter_treble = make_filter(2500, 'highpass')

play(rate, data)
