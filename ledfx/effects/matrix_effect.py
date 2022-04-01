from ledfx.effects import Effect
import voluptuous as vol

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
        }
    )

ORIENTATION = {
    "vertical": 0,
    "horizontal": 1
}