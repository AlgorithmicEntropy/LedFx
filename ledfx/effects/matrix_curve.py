from ledfx.color import COLORS
from ledfx.effects.audio import AudioReactiveEffect
from ledfx.effects.matrix_effect import ORIENTATION, MatrixEffect
import numpy as np
import voluptuous as vol
import math

class MatrixCurve(AudioReactiveEffect, MatrixEffect):
    NAME = "Matrix Curve"
    CATEGORY = "Matrix"

    _amplitude_buffer = None
    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "decay",
                description="Column Decay",
                default="0.1",
            ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=0.99)),
            vol.Optional(
                "gain",
                description="Column Gain",
                default="0.5",
            ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=0.99)),
            vol.Optional(
                "color_start",
                description="Gradient start",
                default="red",
            ): vol.In(list(COLORS.keys())),
            vol.Optional(
                "color_end",
                description="Gradient end",
                default="green",
            ): vol.In(list(COLORS.keys())),
            vol.Optional(
                "color_background",
                description="Background color",
                default="black",
            ): vol.In(list(COLORS.keys())),
        }
    )

    def on_activate(self, pixel_count):
        self.r = np.zeros(self._width)

    def config_updated(self, config):
        # Create the filters used for the effect
        decay = self._config["decay"]
        gain = self._config["gain"]
        self._r_filter = self.create_filter(alpha_decay=decay, alpha_rise=gain)
        self._height = self._config["matrix_height"]
        self._width = self._config["matrix_width"]
        self._amplitude_buffer = np.zeros(self._width)
        self._start_color = self._config["color_start"]
        self._end_color = self._config["color_end"]
        self._bg_color = COLORS[self._config["color_background"]]

        self.gen_gradient(self._start_color, self._end_color);


    def audio_data_updated(self, data):
        self.r = self.melbank(filtered=True, size=self._width)

    def render(self):
        #y_filtered = data.interpolated_melbank(self._width, filtered=True)
        #r = self._r_filter.update(y - y_filtered)
        r = self._r_filter.update(self.r)
        r_clipped = np.clip(r, 0, 1)
        
        new_amplitudes = np.array([np.interp(x, (0, 1), (0, self._height)) for x in np.nditer(r_clipped)])
        #new_amplitudes * 2
        #amplitudes = self._update_amplitudes(new_amplitudes)
        amplitudes = new_amplitudes

        # Construct the array
        p = np.zeros(np.shape(self.pixels))

        for row in range(0, self._height):
            start = self._width * row
            end = start + self._width
            #print(np.fromfunction(lambda i, j: color if amplitudes[i] >= row else bg, (self._width, 1), dtype=int).flatten())
            array = np.array([self._gradient[row] if amplitudes[i] >= row+1 else self._bg_color for i in range(0, self._width)])
            if row % 2 == 0:
                p[start:end] = array
            else:
                p[start:end] = np.flip(array, 0)

        # Update the pixel values
        self.pixels = p
        return p

    
    def _update_amplitudes(self, new_amplitudes):
        amplitudes = np.zeros(len(new_amplitudes))
        for i in range(0, len(new_amplitudes)):
            amplitudes[i] = max(new_amplitudes[i], self._amplitude_buffer[i])
            self._amplitude_buffer[i] = amplitudes[i] - 1
        return amplitudes

    def gen_gradient(self, start_color, end_color):
        start_color = COLORS[start_color]
        end_color = COLORS[end_color]

        r = [np.interp(i, (0, self._height), (start_color[0], end_color[0])) for i in range(0, self._height)]
        g = [np.interp(i, (0, self._height), (start_color[1], end_color[1])) for i in range(0, self._height)]
        b = [np.interp(i, (0, self._height), (start_color[2], end_color[2])) for i in range(0, self._height)]

        r = np.array(r).astype(int)
        g = np.array(g).astype(int)
        b = np.array(b).astype(int)

        self._gradient = np.array([[re, ge, be] for re, ge, be in zip(r,g,b)])
        #print(self._gradient)

