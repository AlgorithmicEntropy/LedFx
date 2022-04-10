from ledfx.color import parse_color, validate_color
from ledfx.effects.audio import AudioReactiveEffect
from ledfx.effects.matrix_effect import ORIENTATION, MatrixEffect
import numpy as np
import voluptuous as vol
from ledfx.effects.fonts.font_3x3 import Font3x3
from .fonts.font_3x3 import Font3x3
import time

class MatrixText(AudioReactiveEffect, MatrixEffect):
    NAME = "Matrix Text"
    CATEGORY = "Matrix"

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "font_color",
                description="Font Color",
                default="red",
            ): validate_color,
            vol.Optional(
                "bass_strobe_color",
                description="Bass strobe Color",
                default="white",
            ): validate_color,
            vol.Optional(
                "text",
                description="Text",
                default="lol",
            ): str,
            vol.Optional(
                "scroll_speed",
                description="Scroll speed",
                default = 1,
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
            vol.Optional(
                "y_ofsett",
                description="Y Ofsett",
                default = 5,
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=10)),
            vol.Optional(
                "bass_strobe",
                description="Enable bass strobe",
                default=False
            ): bool,
        }
    )

    def on_activate(self, pixel_count):
        self._frame_counter = 0
        self._is_beat = False

    def config_updated(self, config):
        # TODO maybe move to ctor (font needs to exist to calc buffer)
        self._font = Font3x3()
        self._height = config["matrix_height"]
        self._width = config["matrix_width"]
        self._text = config['text']
        self._font_color = parse_color(config['font_color'])
        self._scroll_speed = config['scroll_speed']
        self._y_ofsett = config['y_ofsett']

        self.bass_strobe_enabled = config['bass_strobe']
        self.bass_strobe_color = parse_color(config['bass_strobe_color'])
        self.last_bass_strobe_time = 0
        self.bass_strobe_wait_time = 0.2

        # create text buffer
        self._x_start = self._width - 1
        text_len = len(self._text)
        rendered_len = text_len * 3 + text_len - 1
        self.text_pos = rendered_len

        text_arr = np.zeros((3, rendered_len))
        word_idx = rendered_len - 3
        for char in self._text.upper():
            if char in self._font.chars:
                self._add_color_mask(text_arr, self._font.chars[char], word_idx)
            else:
                # for now display empty
                self._add_color_mask(text_arr, self._font.chars[' '], word_idx)
            word_idx -= 4
        self._text_buff = text_arr

    def audio_data_updated(self, data):
        currentTime = time.time()
        if (
            data.volume_beat_now()
            and currentTime - self.last_bass_strobe_time
            > self.bass_strobe_wait_time
        ):
            self._is_beat = True
            self.last_bass_strobe_time = currentTime
        else:
            self._is_beat = False

    def render(self):
        p = np.zeros(np.shape(self.pixels))
        p = np.reshape(p, (self._height, self._width, 3))

        # frame counter
        if self._frame_counter > 20 - self._scroll_speed:
            self._frame_counter = 0

            if self.text_pos != 0:
                self.text_pos -= 1

            self._x_start -= 1
            if self._x_start <= 0:
                self._x_start = self._width - 1
                #self.text_pos = len(self._text) * 3 + len(self._text) - 1

        #self._render_text(p, self._text, self._x_start, self._y_ofsett)
        self._stack_arrays(p, self._text_buff[:,self.text_pos:], self._x_start, self._y_ofsett)

        # flip rows
        for i in range(0, self._height):
            if i % 2 == 1:
                p[i] = np.flip(p[i], 0)

        self.pixels = np.reshape(p, (len(self.pixels), 3))
        self._frame_counter += 1     

    def _stack_arrays(self, m, mask, x_0, y_0):
        y = y_0
        while y - y_0 < len(mask) and y < self._height:
            x = x_0
            while x_0 - x < len(mask[0]):
                if mask[y - y_0, x_0 - x] == 1:
                    if self._is_beat and self.bass_strobe_enabled:
                        m[y, x] = self.bass_strobe_color
                    else:
                        m[y, x] = self._font_color
                x -= 1
            y += 1 


    def _add_color_mask(self, m, mask, x_0):
        m[:, x_0:x_0+len(mask[0])] = mask
    

