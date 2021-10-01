from ledfx.effects.audio import AudioReactiveEffect
from ledfx.effects.matrix_effect import ORIENTATION, MatrixEffect
import numpy as np

class MatrixCurve(AudioReactiveEffect, MatrixEffect):
    NAME = "Matrix Curve"

    def config_updated(self, config):
        # Create the filters used for the effect
        self._r_filter = self.create_filter(alpha_decay=0.5, alpha_rise=0.1)
        self._height = self._config["matrix_height"]
        self._width = self._config["matrix_width"]

    def audio_data_updated(self, data):
        y = data.interpolated_melbank(self._width, filtered=False)
        y_filtered = data.interpolated_melbank(self._width, filtered=True)
        #r = self._r_filter.update(y - y_filtered)
        r = self._r_filter.update(y)
        r_clipped = np.clip(r, 0, 1)
        
        amplitudes = np.array([np.interp(x, (0, 1), (0, self._height)) for x in np.nditer(r_clipped)])

        color = (255,0,0)
        bg = (0,0,0)

        # Construct the array
        p = np.zeros(np.shape(self.pixels))

        for row in range(0, self._height):
            start = self._width * row
            end = start + self._width
            #print(np.fromfunction(lambda i, j: color if amplitudes[i] >= row else bg, (self._width, 1), dtype=int).flatten())
            array = np.array([(255, row*20,0) if amplitudes[i] >= row+1 else bg for i in range(0, self._width)])
            if row % 2 == 0:
                p[start:end] = array
            else:
                p[start:end] = np.flip(array, 0)

        # Update the pixel values
        self.pixels = p
