import asyncio
from enum import Enum
import uuid
from typing import Any
import json

class DACHeader(Enum):
    UUID = 'DAC-UUID'
    REMOTE = 'DAC-REMOTE'
    EVENT_ID = 'DAC-EVENT-ID'
    KIND = 'DAC-KIND'

class DACConnectionKind(Enum):
    BASE = 'BASE'
    SSE = 'SSE'
    INTERSERVER = 'INTERSERVER'

class DACEventStatus(Enum):
    NEW = 'NEW'
    AWAITING = 'AWAITING'
    DONE = 'DONE'
    CANCELLED = 'CANCELLED'

# event base class
class EventBase:
    _id: str
    _kind: DACConnectionKind = DACConnectionKind.BASE
    _status: DACEventStatus
    _status_change_condition: asyncio.Condition
    _args = None

    def __init__(self,*, id = None, **kwargs ) -> None:
        self._id = id if not id is None else str(uuid.uuid4())
        self.__dict__.update(kwargs)
        self._status = DACEventStatus.NEW
        self._status_change_condition = asyncio.Condition()
        # self._status_change_condition.acquire()

    async def new_status(self, from_status: DACEventStatus = DACEventStatus.NEW):
        async with self._status_change_condition:
            await self._status_change_condition.wait_for(lambda: self.status != from_status)
            return self.status

    async def set_status(self, status: DACEventStatus):
        self._status = status
        async with self._status_change_condition:
            self._status_change_condition.notify()

    @property
    def status(self):
        return self._status

    @property
    def kind(self):
        return self._kind

    @property
    def id(self):
        return self._id

    def __eq__(self, o: object) -> bool:
        result = False
        if issubclass(self, EventBase) and issubclass(o, EventBase):
            if self.id == o.id:
                if self.kind == o.kind:
                    result = True
        
        return result

    async def encode(self) -> bytearray:
        raise Exception(f'{self.__class__.__name__} must override "encode" method.')

    
class SSEventBase(EventBase):
    _kind: DACConnectionKind = DACConnectionKind.SSE
    _name: str = None
    _data: Any

    def __init__(self, *, data:str, **kwargs) -> None:
        self._data = data
        self._name = kwargs.get('name')
        super().__init__(**kwargs)

    async def encode(self) -> bytearray:
        return \
            (f'id: {self.id}\n' +
            (f'event: {self._name}\n' if self._name else '') +  
            f'data: {self._data}\n\n').encode()


class JSONSSEvent(SSEventBase):
    def __init__(self, *, data: dict, **kwargs) -> None:
        super().__init__(data=json.dumps(data), name=self.__class__.__name__, **kwargs)

            



