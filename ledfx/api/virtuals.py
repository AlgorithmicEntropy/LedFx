import logging
from json import JSONDecodeError

from aiohttp import web

from ledfx.api import RestEndpoint
from ledfx.api.virtual import make_virtual_response
from ledfx.config import save_config
from ledfx.utils import generate_id

_LOGGER = logging.getLogger(__name__)


class VirtualsEndpoint(RestEndpoint):
    """REST end-point for querying and managing virtuals"""

    ENDPOINT_PATH = "/api/virtuals"

    async def get(self) -> web.Response:
        """
        Get info of all virtuals

        Returns:
            web.Response: The response containing the info of all virtuals
        """
        response = {"status": "success", "virtuals": {}}
        response["paused"] = self._ledfx.virtuals._paused
        for virtual in self._ledfx.virtuals.values():
            response["virtuals"][virtual.id] = make_virtual_response(virtual)

        return web.json_response(data=response, status=200)

    async def put(self) -> web.Response:
        """
        Toggles a global pause on all virtuals

        Returns:
            web.Response: The response containing the paused virtuals.
        """
        self._ledfx.virtuals.pause_all()

        response = {
            "status": "success",
            "paused": self._ledfx.virtuals._paused,
        }
        return await self.bare_request_success(response)

    async def post(self, request: web.Request) -> web.Response:
        """
        Create a new virtual or update config of an existing one

        Args:
            request (web.Request): The request object containing the virtual `config` dict.

        Returns:
            web.Response: The response indicating the success or failure of the creation.
        """
        try:
            data = await request.json()
        except JSONDecodeError:
            return await self.json_decode_error()

        virtual_config = data.get("config")
        if virtual_config is None:
            return await self.invalid_request(
                'Required attribute "config" was not provided'
            )
        # TODO: Validate the config schema against the virtuals config schema.
        virtual_id = data.get("id")

        # Update virtual config if id exists
        if virtual_id is not None:
            virtual = self._ledfx.virtuals.get(virtual_id)
            if virtual is None:
                return await self.invalid_request(
                    f"Virtual with ID {virtual_id} not found"
                )
            # Update the virtual's configuration
            virtual.config = virtual_config
            _LOGGER.info(
                f"Updated virtual {virtual.id} config to {virtual_config}"
            )

            virtual.virtual_cfg["config"] = virtual.config

            response = {
                "status": "success",
                "payload": {
                    "type": "success",
                    "reason": f"Updated Virtual {virtual.name}",
                },
                "virtual": {
                    "config": virtual.config,
                    "id": virtual.id,
                    "is_device": virtual.is_device,
                    "auto_generated": virtual.auto_generated,
                },
            }
        # Or, create new virtual if id does not exist
        else:
            virtual_id = generate_id(virtual_config.get("name"))

            # Create the virtual
            _LOGGER.info(f"Creating virtual with config {virtual_config}")

            virtual = self._ledfx.virtuals.create(
                id=virtual_id,
                is_device=False,
                config=virtual_config,
                ledfx=self._ledfx,
            )

            # Update the configuration
            self._ledfx.config["virtuals"].append(
                {
                    "id": virtual.id,
                    "config": virtual.config,
                    "is_device": virtual.is_device,
                    "auto_generated": virtual.auto_generated,
                }
            )

            virtual.virtual_cfg = self._ledfx.config["virtuals"][-1]

            response = {
                "status": "success",
                "payload": {
                    "type": "success",
                    "reason": f"Created Virtual {virtual.id}",
                },
                "virtual": {
                    "config": virtual.config,
                    "id": virtual.id,
                    "is_device": virtual.is_device,
                    "auto_generated": virtual.auto_generated,
                },
            }

        # Save config
        save_config(
            config=self._ledfx.config,
            config_dir=self._ledfx.config_dir,
        )
        return await self.bare_request_success(response)
