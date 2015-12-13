"""
Module defining a first order allpass filter with modulating coefficients.
"""

import matplotlib.pyplot as plt
import numpy as np

from scipy import signal
from wavetable.oscillators import StandardOscillator, RealTimeResamplingOscillator
from wavetable.wavetable import WaveType

class AllpassFilter:
    """
    First-order allpass filter class with an additional constraint that the
    b0 coefficient always equals the a1 coefficient.

    Parameters
    a1 : The initial value for the a1 coefficient.
    """

    def __init__(self, a1):
        self.a0 = 1.0
        self.a1 = a1
        self.b0 = self.a1
        self.b1 = 1.0

        # Zero pad the initial input and output buffers. The filter will be in
        # its transient state for 1 sample before reaching steady state.
        self._x = 0.0
        self._y = 0.0

    def process_block(self, input_buffer, output_buffer):
        _len = input_buffer.size
        _x = np.insert(input_buffer, 0, self._x)
        _y = np.insert(output_buffer, 0, self._y)

        for i in range(2, _len):
            sample = (self.b0 / self.a0) * _x[i]     \
                   + (self.b1 / self.a0) * _x[i - 1] \
                   - (self.a1 / self.a0) * _y[i - 1] \

            _y[i] = sample

        np.copyto(output_buffer, _y[1:])
        self._x = input_buffer[-1]
        self._y = output_buffer[-1]

    def plot(self, ax1, ax2, color='c', alpha=1.0):
        w, h = signal.freqz([self.b0, self.b1], [self.a0, self.a1])

        # Scale x-axis to Hz.
        x = w * 44100 / (2 * np.pi)

        # Plot amplitude response on the dB scale.
        ax1.plot(x,  20 * np.log10(abs(h)), color=color, alpha=alpha)

        # Plot phase response in radians.
        ax2.plot(x, np.unwrap(np.angle(h)), color=color, alpha=alpha)

        ax1.set_title('Amplitude Response (dB)')
        ax2.set_title('Phase Response (radians)')

        ax2.set_yticks(np.linspace(-2.0, 0.0, 9) * np.pi)
        ax2.set_yticklabels([
            r'$-2\pi$',
            r'',
            r'$-\frac{3\pi}{2}$',
            r'',
            r'$-\pi$',
            r'',
            r'$-\frac{\pi}{2}$',
            r'',
            r'$0$'])

        ax1.axis('tight')
        ax2.axis('tight')

        ax1.grid()
        ax2.grid()


if __name__ == '__main__':
    # Show the frequency response as we move the cutoff frequency.
    _, (ax1, ax2) = plt.subplots(2, sharex=True)

    for i in np.linspace(0.0, 0.8, 4):
        apf = AllpassFilter(i)
        apf.plot(ax1, ax2, 'c', i / 0.8)

    plt.show()

    # Now we'll take a look at how this allpass filter affects the waveform
    # of an input signal so we can compare it with how the drop-sample
    # interpolation filter of the ResamplingOscillator.
    fs = 44100
    duration = 1
    size = fs * duration

    x = np.linspace(0, size, size)

    ss = np.zeros(size, dtype='d')
    StandardOscillator(WaveType.SAWTOOTH, 43.65, 3.0, 1.0).render(ss)

    rs = np.zeros(size, dtype='d')
    RealTimeResamplingOscillator(WaveType.SAWTOOTH, 43.65, 3.0, 1.0).render(rs)

    ap = np.zeros(size, dtype='d')
    apf = AllpassFilter(0.68)
    apf.process_block(ss, ap)

    plt.figure()
    plt.subplot(211)
    plt.plot(x, rs - ss)

    plt.subplot(212)
    plt.plot(x, ap - ss)

    plt.show()
