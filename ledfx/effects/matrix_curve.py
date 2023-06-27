from ledfx.color import parse_color, validate_color
from ledfx.effects.audio import AudioReactiveEffect
from ledfx.effects.matrix_effect import Orientation
from .matrix_gradient import MatrixGradientEffect
import numpy as np
import voluptuous as vol
import math

class MatrixCurve(AudioReactiveEffect, MatrixGradientEffect):
    NAME = "Matrix Curve"
    CATEGORY = "Matrix"

    _amplitude_buffer = None
    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "decay",
                description="Column Decay",
                default="0.5",
            ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=0.99)),
            vol.Optional(
                "gain",
                description="Column Gain",
                default="0.7",
            ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=0.99)),
        }
    )

    def on_activate(self, pixel_count):
        self.r = np.zeros(self._width)

    def config_updated(self, config):
        super().config_updated(config)
        # Create the filters used for the effect
        decay = config["decay"]
        gain = config["gain"]
        self._r_filter = self.create_filter(alpha_decay=decay, alpha_rise=gain)
        self._amplitude_buffer = np.zeros(self._width)

    def audio_data_updated(self, data):
        self.r = self.melbank(filtered=True, size=self._width)

    def render(self):
        #y_filtered = data.interpolated_melbank(self._width, filtered=True)
        #r = self._r_filter.update(y - y_filtered)
        r = self._r_filter.update(self.r)
        r_clipped = np.clip(r, 0, 1)
        
        amplitudes = np.array([np.interp(x, (0, 1), (0, self._height)) for x in np.nditer(r_clipped)])

        if self._gradient_orientation == Orientation.VERTICAL:
            for row in range(0, self._height):
                start = self._width * row
                end = start + self._width
                array = np.array([self.get_gradient_color(row) if amplitudes[i] > row+1 else self._bg_color for i in range(0, self._width)])
                if row % 2 == 0:
                    self.pixels[start:end] = array
                else:
                    self.pixels[start:end] = np.flip(array, 0)
        else:
            # TODO optimize horizontal gradient
            p = np.zeros((self._width, self._height, 3))
            for col in range(0, self._width):
                array = np.array([self.get_gradient_color(col) if amplitudes[col] > i+1 else self._bg_color for i in range(0, self._height)])
                p[col] = array

            for row in range(0, self._height):
                start = self._width * row
                end = start + self._width
                if row % 2 == 0:
                    self.pixels[start:end] = p[:, row]
                else:
                    self.pixels[start:end] = np.flip(p[:, row], 0)
    
    def _update_amplitudes(self, new_amplitudes):
        amplitudes = np.zeros(len(new_amplitudes))
        for i in range(0, len(new_amplitudes)):
            amplitudes[i] = max(new_amplitudes[i], self._amplitude_buffer[i])
            self._amplitude_buffer[i] = amplitudes[i] - 1
        return amplitudes
