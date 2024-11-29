class GameError(Exception): pass
class GameConfigError(GameError): pass
class WordValidationError(GameError): pass
class GameInitializationError(GameError): pass
class GameExecutionError(GameError): pass