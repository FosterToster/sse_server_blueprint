from .controllers.server import ServerContoller
from .blueprint import DAC as DACBlueprint

DACBlueprint.controller = ServerContoller()    
from .blueprint import DAC as DACBlueprint
from .controllers.server import ServerContoller

DACBlueprint.controller = ServerContoller()