In this homework you will build code to play a WAV file with
its tone and volume adjusted.

## Background

"Tone" controls — controls that change the level of various
frequency bands within an audio signal — are almost as old
as electronic audio. Audio recording and reproduction
equipment is bad at maintaing flat frequency response; also,
listeners may have preferences about frequency response.

One classic tone control option seen on a lot of audio equipment
is a "bass", "midrange", "treble" scheme. Audio controls
tend to range from 0..10 (or sometimes, famously, 11); what
these numbers mean, as well as what frequencies are "bass",
"midrange" or "treble", is left to the listener.

These tone controls also interact with signal volume: a
volume control will be desirable.

With digital filtering, we can very selectively filter bands
of frequencies and emphasize or de-emphasize them.

## The Assignment

In this assignment, you will write a command-line volume and
tone control application that will read a WAV file and
either play it with adjusted tone and volume or write a WAV
file with adjusted tone and volume.

### Command-Line Program Requirements

Your program must accept the following optional command-line
arguments:

* `--volume`: Volume setting, a non-negative float normally
  in the range 0.0..10.0 (but may be larger). Each full
  volume step is 3 dB, with 0dB at the default volume
  setting of 9.0. A volume setting of less than 0.1 is
  treated as "0 volume": no sound at all is produced.

* `--bass`, `--mid`, `--treble`: Volume setting, a
  non-negative float normally in the range 0.0..10.0 (but
  may be larger). Each full volume step is 3 dB, with 0dB at
  the default volume setting of 5.0. A tone setting of less
  than 0.1 is treated as "0 tone": no sound at all is
  produced for that band.

* `--out`: Name of an output WAV file. This will suppress
  playback and instead write the output into the given WAV
  file in the same format as the input.
  
The program must also take a positional argument naming
the input WAV file.

For example, for my Python program an invocation as

    python3 tone.py --out test-out.wav --volume 7 --mid 11.01 test.wav

should produce an output file named `test-out.wav`
containing the audio from the input file `test.wav`, but
with the volume reduced 6dB and the midrange tone increased
a little more than 18dB.

### Program Audio Requirements.

Your tone program must successfully process 16-bit mono and
stereo WAV files with sample rates of 44100 or 48000 samples
per second. The output file should have the same format,
channels and sample rate as the input file. Stereo channels
must be processed independently.

The output will be computed by filtering for the bass,
mid-range and treble frequencies using a lowpass filter, a
bandpass filter, and a high-pass filter. The split between
bass and midrange will be at 300 Hz (independent of sample
rate), and the split between midrange and treble will be at
4000 Hz.

The three filter outputs will be multiplied by their tone
control gains to get weighted bands, which will then be
summed to get the final output audio. That output audio will
then be scaled according to the volume control.

    y[n] = gain(volume) *
      (gain(bass) * lp(x[n])
        + gain(mid) * bp(x[n])
        + gain(treble) * hp(x[n]))

It is acceptable (and encouraged) to read the whole input
WAV into memory, do all of the processing on the entire WAV,
and then output after that.

The inputs need to be converted from "knob values" to gain
coefficients. This can be done roughly like this:

    To compute the gain coefficient for a knob setting of s
    with a knob offset of m:

        if s < 0.1
            return 0
        db ← 3.0 * (s - m)
        return pow(10.0, db / 20.0)

Again, for the tone controls the knob offset will be 5,
while for the volume control it will be 9. This offset is
the 0dB gain point (gain of 1).

### Resources

https://github.com/pdx-cs-sound/hw-tone-resources contains
resources provided for this assignment. There is Python code
for some of the functionality, and filter coefficients for
the non-Python user. There are also a few WAV files to play
with.

### Special Python Requirements

If you are using Python for this assignment:

* You must use Python 3.9 or later.

* You must have the `numpy`, `scipy` and `sounddevice` libraries
  available to your program.

* You must use the library routines I supply in the
  `hw-tone-resources` repository to read and write WAV
  files, to play WAV files on your computer, and to process
  command-line arguments.

* You must make your own custom lowpass, midrange bandpass,
  and highpass filters using `scipy.signal` or similar. You
  should apply these filters using `scipy.signal` or similar
  rather than writing your own custom dot-product or
  convolution code. If you use an FIR filter, use 255
  coefficients; if you use an IIR filter, use filter
  order 32. These should give you a good filter.

### Special Non-Python Requirements

* You must process command-line arguments consistently with
  the description in this assignment. Your language probably
  has a nice library for processing arguments. Please use it.

* You may generate filter coefficients, if you can find a
  good library for this, or you may use the filter
  coefficients in `hw-tone-resources` to do FIR filtering.

## Hints

* If you are using Python, you will probably want to explore
  `numpy` and `scipy` pretty carefully. Check out
  `numpy.transpose` for converting between an array of
  frames and a pair of channels. Checkout out
  `signal.firwin` and `signal.lfilter` for one possible way
  to do the filtering.

* Check the sample rate, amplitude, channels and spectrum of
  your WAV files in Audacity. On Linux the `file` command
  will also tell you the sample rate, number of channels,
  and bits per sample.  You can also use the
  [`wavfile`](http://github.com/pdx-cs-sound/wavfile) Python
  utility I built for the course to check these things. Lots
  of options.

## Turn-in

Please submit your work on Canvas as a single ZIP
archive. Your archive should contain:

* A
  [Markdown](https://guides.github.com/features/mastering-markdown/)
  file named `README.md` with your name near the top. It
  should start with the project name and your name. Then
  briefly describe what you did, how it went, and what is
  still to be done.

* The source code and build files for your program. Please
  include anything you wrote: all source code, etc. If you
  wrote in a compiled language, provide a build tool script
  that can build your program if needed. For C/C++
  specifically, provide a working `Makefile`. For Rust, a
  working `Cargo.toml`. Java and Go are fine without
  tools. For all programming languages, please include
  detailed build instructions in the `README.md`.

* Please *do not* include executables, WAV files other than
  the ones asked for, `.git`, those horrible `MacOS`
  resource fork files, binaries, etc.

tl;dr: Your submission should be a ZIP file containing the
following

    ./README.md
    ./mysourcecode.myprogramminglanguage
