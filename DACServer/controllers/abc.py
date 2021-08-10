from uuid import uuid4
from ..types import DACConnectionKind
from ..exceptions import DACException

class DACUnit():
    _kind: DACConnectionKind = None

    @property
    def feed_response_headers(self):
        return {
            DACConnectionKind.BASE: {},
            DACConnectionKind.SSE: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Transfer-Encoding': 'chunked',
            },
            DACConnectionKind.INTERSERVER: {},
        }.get(self.kind)

    @property
    def kind(self):
        return self._kind

    def __init__(self,*, uuid:str = None, remote:str = None) -> None:
        if self._kind is None:
            raise DACException(f'{self.__class__.__name__} must specify connection kind')

        if uuid is None:
            self.uuid = str(uuid4())
        else:
            self.uuid = uuid
        
        self.remote = remote