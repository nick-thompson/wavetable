import numpy as np

from math import floor
from wavetable.oscillators import StandardOscillator, ResamplingOscillator, RealTimeResamplingOscillator
from scipy.io import wavfile
from utils import normalize, trim

# Render a single sawtooth waveform generated by the StandardOscillator.
s = np.zeros(44100 * 4, dtype='d')
StandardOscillator(43.65, 0.0, 1.0).render(s)
wavfile.write('sounds/single.wav', 44100, s)

# Render a detuned pair generated by StandardOscillator.
sdp = np.zeros(44100 * 4, dtype='d')
StandardOscillator(43.65, 0.0, 0.5).render(sdp)
StandardOscillator(43.65, 3.0, 0.5).render(sdp)
wavfile.write('sounds/standard_detuned_pair.wav', 44100, sdp)

# Now a detuned pair using the ResamplingOscillator.
rdp = np.zeros(44100 * 4, dtype='d')
StandardOscillator(43.65, 0.0, 0.5).render(rdp)
ResamplingOscillator(43.65, 3.0, 0.5).render(rdp)
wavfile.write('sounds/resampling_detuned_pair.wav', 44100, rdp)

# Next, to isolate the phase artifacts introduced by using the resampling
# approach, we'll render the difference between the two previous approaches.
wavfile.write('sounds/standard_resampling_diff.wav', 44100,
    normalize(trim(rdp - sdp, pow(2, 3 / 1200.0))))

# And to show that the RealTimeResamplingOscillator produces the same sound
# as the classic ResamplingOscillator, we'll render another detuned pair here.
rtdp = np.zeros(44100 * 4, dtype='d')
StandardOscillator(43.65, 0.0, 0.5).render(rtdp)
RealTimeResamplingOscillator(43.65, 3.0, 0.5).render(rtdp)
wavfile.write('sounds/realtime_detuned_pair.wav', 44100, rtdp)
