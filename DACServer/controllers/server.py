from uuid import uuid4
from .abc import DACUnit
from .connection import Connections, DACConnection
from quart.wrappers import Request
from quart import make_response
from ..types import DACConnectionKind, DACHeader, DACEventStatus, EventBase, SSEventBase
from ..exceptions import DACException
import asyncio
from loguru import logger as log
import copy
from typing import TypeVar




class ServerContoller(DACUnit):
    _kind = DACConnectionKind.INTERSERVER

    def __init__(self) -> None:
        super().__init__()
        self.connections = Connections()

    @staticmethod
    async def parse_request(request: Request, connection_kind: str) -> DACConnection:
        uuid = request.headers.get(DACHeader.UUID, uuid4())
        remote = request.headers.get(DACHeader.REMOTE)
        class_ = await DACConnection.get_connection_class(DACConnectionKind(connection_kind.upper()))

        return class_(uuid, remote)

        # if uuid is None:
        #     raise DACException(f'{DACHeaders.UUID} header not found')

        # return DACConnection(uuid, remote) 
        
        
    async def init_connection(self, connection: DACConnection):
        
        self.connections.connect(connection)

        log.success(f'{connection.uuid} connected')
        
        async def feed_pipe(connection):
            while True:
                try:
                    event = await connection.pipe.get()
                    log.info(f'{event.__class__.__name__}(id={event.id}) sent to {connection.uuid}')
                    yield await event.encode()
                except asyncio.CancelledError:
                    try:
                        if event:
                            await event.set_status(DACEventStatus.CANCELLED)
                    except:
                        pass

                    await self.connections.disconnect(connection)

                    log.error(f'{connection.uuid} disconnected')
                else:
                    await event.set_status(DACEventStatus.DONE)
        
        response = await make_response(
            feed_pipe(connection),
            connection.feed_response_headers
        )

        response.timeout = None
        return response

    async def broadcast(self, event_class: TypeVar('EventBase'), **event_kwargs):
        events_statuses = []
        for conn in self.connections.all_of_kind(event_class._kind):
            events_statuses.append((await conn.send(event_class(**event_kwargs))).new_status())
        
        events_results = []
        for evt in asyncio.as_completed(events_statuses):
            events_results.append((await evt).value)

        return events_results
        
        return await asyncio.gather(*events_statuses)

        return [evt.result for evt in events_statuses]
            


    async def send(self, data:str):
        evt = SSEventBase(data=f"{data}\n")

        for conn in  self.connections.values():
            await conn.pipe.put(evt)
            return 'sended' if await evt.new_status() == DACEventStatus.DONE else 'rejected'

        return 'no client' 

    async def request(self, connection: DACConnection):
        pass