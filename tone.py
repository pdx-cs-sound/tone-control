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

    # Set up and start the stream.
    stream = sd.RawOutputStream(
        samplerate = rate,
        blocksize = BUFFER_SIZE,
        channels = 1,
        dtype = 'float32',
    )

    # Write the samples.
    stream.start()
    w = np.nditer(wav)
    done = False
    while not done:
        buffer = np.zeros(BUFFER_SIZE, dtype=np.float32)
        for i in range(BUFFER_SIZE):
            try:
                sample = next(w)
            except StopIteration:
                done = True
                break
            buffer[i] = sample
        stream.write(buffer)

    # Tear down the stream.
    stream.stop()
    stream.close()

# Get tone generator.
rate, data = read_wav(sys.argv[1])
play(rate, data)
