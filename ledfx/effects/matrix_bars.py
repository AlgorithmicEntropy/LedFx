from ledfx.color import COLORS
from ledfx.effects.audio import AudioReactiveEffect
from ledfx.effects.matrix_effect import ORIENTATION, MatrixEffect
import voluptuous as vol
import numpy as np
import math

class MatrixBars(AudioReactiveEffect, MatrixEffect):
    NAME = "Matrix Bars"
    _old_intensity = [0,0,0]

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "decay",
                description="Column Decay",
                default="0.4",
            ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1)),
            vol.Optional(
                "color_lows",
                description="Color of low, bassy sounds",
                default="red",
            ): vol.In(list(COLORS.keys())),
            vol.Optional(
                "color_mids",
                description="Color of mids",
                default="green",
            ): vol.In(list(COLORS.keys())),
            vol.Optional(
                "color_highs",
                description="Color of highs",
                default="blue",
            ): vol.In(list(COLORS.keys())),
            vol.Optional(
                "orientation",
                description="Orientation of the effect",
                default="horizontal",
            ): vol.In(list(ORIENTATION.keys())),
        }
    )

    def config_updated(self, config):
        # TODO handle orientations
        self._height = math.floor(config["matrix_height"] / 3)
        self._decay = config["decay"]
        self._color_lows = COLORS[config["color_lows"]]
        self._color_mids = COLORS[config["color_mids"]]
        self._color_highs = COLORS[config["color_highs"]]


    def audio_data_updated(self, data):
        intensity_low = np.mean(data.melbank_lows())
        intensity_mid = np.mean(data.melbank_mids())
        intensity_highs = np.mean(data.melbank_highs())

        factor = 2

        intensity_low *= factor
        intensity_mid *= factor
        intensity_highs *= factor

        width = self._config["matrix_width"]

        intensity = []
        intensity.append(math.floor(np.interp(intensity_low, (0, 1), (0, width))))
        intensity.append(math.floor(np.interp(intensity_mid, (0, 1), (0, width))))
        intensity.append(math.floor(np.interp(intensity_highs, (0, 1), (0, width))))

        # temporal smoothing
        # make shure to only reduce intensity by the decay value each update
        for i in range(0, len(intensity)):
            if intensity[i] < self._old_intensity[i]:
                intensity[i] = self._old_intensity[i] - self._decay
            self._old_intensity[i] = intensity[i]   
            intensity[i] = math.ceil(intensity[i])

        # Construct the array
        p = np.zeros(np.shape(self.pixels))

        for i in range(0, self._height):
            start = i*width
            if i % 2 == 0:
                p[start : start+intensity[0]] = self._color_lows
            else:
                start = start+width
                p[start - intensity[0] : start] = self._color_lows

        for i in range(self._height, self._height*2):
            start = i*width
            if i % 2 == 0:
                p[start : start+intensity[1]] = self._color_mids
            else:
                start = start+width
                p[start - intensity[1] : start] = self._color_mids
    
        for i in range(self._height*2, self._height*3):
            start = i*width
            if i % 2 == 0:
                p[start : start+intensity[2]] = self._color_highs
            else:
                start = start+width
                p[start - intensity[2] : start] = self._color_highs
        # Update the pixel values
        self.pixels = p
