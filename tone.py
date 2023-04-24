# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Solution to CS 410P/510 Sound HW2: Tone

import argparse
from scipy import io, signal
import numpy as np
import sounddevice as sd

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

# Read from a 16-bit WAV file. Returns the sample rate in
# samples per second, and the samples as a numpy array of
# IEEE 64-bit floats. The array will be 1D for mono data,
# and will be a 2D array of 2-element frames for stereo
# data.
def read_wav(filename):
    rate, data = io.wavfile.read(filename)
    assert data.dtype == np.int16
    data = data.astype(np.float64)
    data /= 32768
    return rate, data

# Write to a 16-bit WAV file. Data is in the same
# format produced by read_wav().
def write_wav(filename, rate, data):
    assert data.dtype == np.float64
    data *= 32767
    data = data.astype(np.int16)
    io.wavfile.write(filename, rate, data)

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
    # https://stackoverflow.com/a/73368196
    indices = np.arange(BUFFER_SIZE, wav.shape[0], BUFFER_SIZE)
    samples = np.ascontiguousarray(wav, dtype=np.float32)
    for buffer in np.array_split(samples, indices):
        stream.write(buffer)

    # Tear down the stream.
    stream.stop()
    stream.close()

# Parse command-line arguments.
argp = argparse.ArgumentParser()
argp.add_argument(
    "--volume",
    help="volume in 3dB units (default 9 = 0dB, 0 = 0 output)",
    type=np.float64,
    default=9,
)
argp.add_argument(
    "--bass",
    help="bass emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)",
    type=np.float64,
    default=5,
)
argp.add_argument(
    "--midrange",
    help="midrange emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)",
    type=np.float64,
    default=5,
)
argp.add_argument(
    "--treble",
    help="treble emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)",
    type=np.float64,
    default=5,
)
argp.add_argument(
    "--split1",
    help="bass/mid split frequency in Hz (default 150)",
    type=np.float64,
    default=150,
)
argp.add_argument(
    "--split2",
    help="mid/treble split frequency in Hz (default 2500)",
    type=np.float64,
    default=2500,
)
argp.add_argument(
    "--fir",
    help="FIR filter width (must be odd; default 255, suggest 127..1023)",
    type=int,
    default=255,
)
argp.add_argument(
    "--iir",
    help="IIR filter width (must be even; suggest 32 / 16..64)",
    type=int,
    default=0,
)
argp.add_argument(
    "--out",
    help="write to WAV file instead of playing",
)
argp.add_argument("wav", help="audio file")
args = argp.parse_args()

# Given a knob setting s (0.0..), return 3 * (s - offset) dB as
# a gain factor. Exception: knob setting < 0.1 gives gain
# factor 0, not -3 * offset dB.
def knob(s, offset=5.0):
    if s < 0.1:
        return 0
    db = 3.0 * (s - offset)
    a = 10.0 ** (db / 20.0)
    return a

# Read WAV.
rate, in_data = read_wav(args.wav)

# Build filters.
def make_filter(freqs, btype):
    global rate
    freqs = 2.0 * np.array(freqs, dtype=np.float64) / rate

    if args.iir > 0:
        assert args.iir % 2 == 0
        return 'sos', signal.iirfilter(
            args.iir,
            freqs,
            btype=btype,
            rp=1.0,
            rs=3.0,
            ftype='ellip',
            output = 'sos',
        )
    else:
        assert args.fir > 0
        assert args.fir % 2 == 1
        return 'ba', signal.firwin(
            args.fir,
            freqs,
            pass_zero=btype,
        )

def do_filter(ft, f, channels):
    if ft == 'sos':
        return signal.sosfilt(f, channels)
    elif ft == 'ba':
        return signal.lfilter(f, [1.], channels)
    else:
        raise Exception('bad filter type')

ft, filter_bass = make_filter(args.split1, 'lowpass')
ft, filter_mid = make_filter((args.split1, args.split2), 'bandpass')
ft, filter_treble = make_filter(args.split2, 'highpass')

# Apply filters.
emphasis = (knob(args.bass), knob(args.midrange), knob(args.treble))
filters = (filter_bass, filter_mid, filter_treble)
channels = np.transpose(in_data)
filtered = np.array(tuple(e * do_filter(ft, f, channels)
            for e, f in zip(emphasis, filters)))
gain = knob(args.volume, offset=9.0)
result = gain * np.sum(filtered, axis=0)
out_data = np.transpose(result)

# Render or play result.
if args.out:
    write_wav(args.out, rate, out_data)
else:
    play(rate, out_data)
