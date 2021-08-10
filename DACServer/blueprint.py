from DACServer.types import DACConnectionKind, JSONSSEvent, SSEventBase
import asyncio
from loguru import logger as log
from jinja2.utils import consume
from quart import Blueprint, request
from .controllers.server import ServerContoller
from typing import Optional


from quart import Blueprint
from typing import Optional


class DacBlueprint(Blueprint):
    def __init__(self, name: str, import_name: str, static_folder: Optional[str] = None, static_url_path: Optional[str] = None, template_folder: Optional[str] = None, url_prefix: Optional[str] = None, subdomain: Optional[str] = None, url_defaults: Optional[dict] = None, root_path: Optional[str] = None, cli_group: Optional[str] = None) -> None:
        super().__init__(name, import_name, static_folder=static_folder, static_url_path=static_url_path, template_folder=template_folder, url_prefix=url_prefix, subdomain=subdomain, url_defaults=url_defaults, root_path=root_path, cli_group=cli_group)
        self.controller:ServerContoller = ServerContoller()

DAC = DacBlueprint('default', 'default')

@DAC.route('/dac/v1/dashboard')
async def index():
    return f'current client count: {len(DAC.controller.connections)}'


@DAC.route('/dac/v1/pipe/<string:connection_kind>', methods=['GET'])
async def out_pipe(connection_kind):
    return await DAC.controller.init_connection(await ServerContoller.parse_request(request, connection_kind))

@DAC.route('/dac/v1/pipe', methods=['POST'])
async def in_pipe():
    DAC.controller.request(request)

@DAC.route('/dac/v1/r')
async def r():
    return str( await DAC.controller.broadcast(JSONSSEvent, data={'buenos': 'dias'}))

