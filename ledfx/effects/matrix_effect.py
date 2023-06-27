from ledfx.effects import Effect
import voluptuous as vol
import numpy as np
from enum import Enum

class Orientation(str, Enum):
    VERTICAL = "vertical",
    HORIZONTAL = "horizontal"

@Effect.no_registration
class MatrixEffect(Effect):
    """
    Base class for all matrix effects
    """
    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Required(
                "matrix_width",
                description="Width of the matrix",
                default=25,
            ): vol.All(vol.Coerce(int)),
            vol.Required(
                "matrix_height",
                description="Height of the matrix",
                default=12,
            ): vol.All(vol.Coerce(int)),
            vol.Required(
                "matrix_orientation",
                description="Matrix orientation",
                default=Orientation.HORIZONTAL,
            ): vol.In([i.value for i in Orientation]),
        }
    )

    def config_updated(self, config):
        self._height = self._config["matrix_height"]
        self._width = self._config["matrix_width"]