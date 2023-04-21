# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Solution to CS 410P/510 Sound HW2: Tone

import argparse, math, sys, time
from scipy.io import wavfile
import numpy as np
import sounddevice as sd

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

# Read from a 16-bit WAV file. Returns 
def read_wav(filename):
    rate, data = wavfile.read(filename)
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

# Get tone generator.
rate, data = read_wav(sys.argv[1])
play(rate, data)
