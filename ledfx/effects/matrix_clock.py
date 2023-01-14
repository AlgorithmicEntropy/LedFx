from ledfx.color import parse_color, validate_color
from ledfx.effects.audio import AudioReactiveEffect
from ledfx.effects.matrix_effect import Orientation
from ledfx.effects.matrix_text import MatrixText
import numpy as np
import voluptuous as vol
import time


class MatrixClock(MatrixText):
    NAME = "Matrix Clock"
    CATEGORY = "Matrix"

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "bass_strobe",
                description="Enable bass strobe",
                default=False
            ): bool
        }
    )

    def on_activate(self, pixel_count):
        self._text = ''

    def config_updated(self, config):
        super().config_updated(config)
        self._recalc_position()


    def audio_data_updated(self, data):
        pass

    def render(self):
        p = np.zeros(np.shape(self.pixels))
        p = np.reshape(p, (self._height, self._width, 3))

        cur_time = time.strftime('%H:%M')
        if cur_time != self._text:
            self._text = cur_time
            self._recalc_position()
        
        self.color_stack_arr(p,  self._text_buff, self._x_start, self._y_ofsett)

        # flip rows
        for i in range(0, self._height):
            if i % 2 == 1:
                p[i] = np.flip(p[i], 0)

        self.pixels = np.reshape(p, (len(self.pixels), 3))   

    
    def _recalc_position(self):
        self._build_text_buf()
        self._x_start = (self._width - self.rendered_len) // 2


    def _build_text_buf(self):
        # create text buffer
        self._x_start = self._width
        text_len = len(self._text)
        rendered_len = text_len * self._font_size + text_len - 1
        self.rendered_len = rendered_len

        text_arr = np.zeros((self._font_size, rendered_len))
        word_idx = rendered_len - self._font_size
        for char in self._text.upper():
            if char in self._font.chars:
                self._add_color_mask(text_arr, self._font.chars[char], word_idx)
            else:
                # for now display empty
                self._add_color_mask(text_arr, self._font.chars[' '], word_idx)
            word_idx -= self._font_size + 1
        self._text_buff = text_arr
