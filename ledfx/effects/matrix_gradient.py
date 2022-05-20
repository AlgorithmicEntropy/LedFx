import logging

import numpy as np
import voluptuous as vol

from ledfx.color import RGB, parse_gradient, validate_gradient
from ledfx.effects import Effect
from .matrix_effect import MatrixEffect, Orientation

_LOGGER = logging.getLogger(__name__)


@Effect.no_registration
class MatrixGradientEffect(MatrixEffect):
    """
    Simple effect base class that supplies gradient functionality. This
    is intended for effect which instead of outputing exact colors output
    colors based upon some configured color pallet.
    """

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "gradient",
                description="Color gradient to display",
                default="linear-gradient(90deg, rgb(255, 0, 0) 0%, rgb(255, 120, 0) 14%, rgb(255, 200, 0) 28%, rgb(0, 255, 0) 42%, rgb(0, 199, 140) 56%, rgb(0, 0, 255) 70%, rgb(128, 0, 128) 84%, rgb(255, 0, 178) 98%)",
            ): validate_gradient,
            vol.Optional(
                "gradient_roll",
                description="Amount to shift the gradient",
                default=0,
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=10)),
            vol.Optional(
                "gradient_orientation",
                description="Gradient orientation",
                default=Orientation.HORIZONTAL,
            ): vol.In([i.value for i in Orientation]),
        }
    )

    _gradient_curve = None
    _gradient_roll_counter = 0

    def _comb(self, N, k):
        N = int(N)
        k = int(k)

        if k > N or N < 0 or k < 0:
            return 0

        M = N + 1
        nterms = min(k, N - k)
        numerator = 1
        denominator = 1

        for j in range(1, nterms + 1):
            numerator *= M - j
            denominator *= j

        return numerator // denominator

    def _bernstein_poly(self, i, n, t):
        """The Bernstein polynomial of n, i as a function of t"""
        return self._comb(n, i) * (t ** (n - i)) * (1 - t) ** i

    def _ease(self, chunk_len, start_val, end_val, slope=1.5):
        x = np.linspace(0, 1, chunk_len)
        diff = end_val - start_val
        pow_x = np.power(x, slope)
        return diff * pow_x / (pow_x + np.power(1 - x, slope)) + start_val

    def _generate_gradient_curve(self, gradient, gradient_length):
        _LOGGER.debug(f"Generating new gradient curve: {gradient}")

        try:
            gradient = parse_gradient(gradient)
        except ValueError:
            gradient = RGB(0, 0, 0)

        if isinstance(gradient, RGB):
            self._gradient_curve = (
                np.tile(gradient, gradient_length).astype(float).T
            )
            return

        gradient_colors = gradient.colors

        # fill in start and end colors if not explicitly given
        if gradient_colors[0][1] != 0.0:
            gradient_colors.insert(0, (gradient_colors[0][0], 0.0))

        if gradient_colors[-1][1] != 1.0:
            gradient_colors.insert(-1, (gradient_colors[-1][0], 1.0))

        # split colors and splits into two separate groups
        gradient_colors, gradient_splits = zip(*gradient_colors)

        # turn splits into real indexes to split array
        gradient_splits = [
            int(gradient_length * position)
            for position in gradient_splits
            if 0 < position < 1
        ]
        # pair colors (1,2), (2,3), (3,4) for color transition of each segment
        gradient_colors_paired = zip(gradient_colors, gradient_colors[1:])

        # create gradient array and split it up into the segments
        gradient = np.zeros((gradient_length, 3)).astype(float)
        gradient_segments = np.split(gradient, gradient_splits, axis=0)

        for (color_1, color_2), segment in zip(
            gradient_colors_paired, gradient_segments
        ):
            segment_len = len(segment)
            segment[:, 0] = self._ease(segment_len, color_1[0], color_2[0])
            segment[:, 1] = self._ease(segment_len, color_1[1], color_2[1])
            segment[:, 2] = self._ease(segment_len, color_1[2], color_2[2])

        self._gradient_curve = gradient.T

    def _assert_gradient(self):
        if (self._gradient_curve is None):  # Uninitialized gradient
            if self._config["gradient_orientation"] == Orientation.HORIZONTAL:
                gradient_len = self._config["matrix_width"]
            else:
                gradient_len = self._config["matrix_height"]
            self._generate_gradient_curve(
                self._config["gradient"],
                gradient_len,
            )

    def _roll_gradient(self):
        if self._config["gradient_roll"] == 0:
            return

        self._gradient_roll_counter += self._config["gradient_roll"]

        if self._gradient_roll_counter >= 1.0:
            pixels_to_roll = np.floor(self._gradient_roll_counter)
            self._gradient_roll_counter -= pixels_to_roll

            self._gradient_curve = np.roll(
                self._gradient_curve,
                int(pixels_to_roll),
                axis=0,
            )

    def get_gradient_color(self, point):
        self._assert_gradient()

        return self._gradient_curve[:, point]

    def config_updated(self, config):
        """Invalidate the gradient"""
        self._gradient_curve = None

    def apply_gradient(self, y):
        self._assert_gradient()

        output = self._gradient_curve.T * y
        # Apply and roll the gradient if necessary
        self._roll_gradient()

        return output
