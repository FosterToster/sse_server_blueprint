import asyncio
from DACServer.exceptions import DACException
from DACServer.types import DACConnectionKind, DACEventStatus, EventBase
from .abc import DACUnit
from asyncio import Queue

class DACConnection(DACUnit):
    def __init__(self, uuid_: str, remote: str) -> None:
        super().__init__(uuid = uuid_, remote=remote)
        self.__pipe = Queue()

    @property
    def pipe(self) -> Queue:
        return self.__pipe

    async def send(self, event: EventBase):
        await self.pipe.put(event)
        return event

    @classmethod
    async def get_connection_class(class_, kind:DACConnectionKind):
        for connection_class in class_.__subclasses__():
            if connection_class._kind == kind:
                return connection_class

        raise DACException(f'Unknown connection kind: {kind}')

class Connections:

    '''
    dict-like object that can handle DAC Connection
    '''
    def __init__(self) -> None:
        self.__storage = dict()

    def __setitem__(self, key, item):
        self.__storage[key] = item

    def __getitem__(self, key):
        return self.__storage[key]

    def __repr__(self):
        return repr(self.__storage)

    def __len__(self):
        return len(self.__storage)

    def __delitem__(self, key):
        del self.__storage[key]

    def connect(self, connection:DACUnit):
        self[connection.uuid] = connection
    
    async def disconnect(self, connection:DACUnit):
        while not connection.pipe.empty():
            (await connection.pipe.pop()).set_status(DACEventStatus.CANCELLED)

        return self.__storage.pop(connection.uuid)

    def all_of_kind(self, kind: DACConnectionKind) -> DACConnection:
        return (conn for conn in self.values() if conn.kind == kind)

    def clear(self):
        return self.__storage.clear()

    def has_key(self, k):
        return k in self.__storage

    def keys(self):
        return self.__storage.keys()

    def values(self):
        return self.__storage.values()


class SSEConnection(DACConnection):
    _kind = DACConnectionKind.SSE
    