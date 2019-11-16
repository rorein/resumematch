from inspect import signature, Parameter

class ArgumentCountError(Exception):
   pass


class InvalidParameterError(Exception):
   pass


class MultiLDispatcher:
   def __init__(self, numparams):
      self.num_params = numparams
      self._handlers = {}

   def _extract_params(self, handler):
      sig = signature(handler)
      params = [p for p in sig.parameters.values() if p.kind == p.POSITIONAL_OR_KEYWORD]
      if len(params) != self.num_params: 
         raise ArgumentCountError('The given handler has ' + len(params) + ' parameters, however this MultipleLDispatcher requires ' + self.num_params + ' parameters.')
      return sig, params

   def add(self, handler):
      sig, params = self._extract_params(handler)
      scope = self._handlers
      for param in params[:-1]:
         if param.annotation is Parameter.empty:
            scope[None] = handler
            break
         if param.annotation not in scope:
            scope[param.annotation] = {}
         scope = scope[param.annotation]
      else:
         if params[-1].annotation is Parameter.empty:
            scope[None] = handler
         scope[params[-1].annotation] = handler
      
      return handler

   def addall(self, handlers):
      for handler in handlers:
         self.add(handler)

   def get_handler(self, scope, args):
      if len(args) == 0:
         return scope
      arg = args[0]
      for t in scope:
         if t is not None and isinstance(arg, t):
            handler = self.get_handler(scope[t], args[1:])
            if handler is not None:
               return handler
      if None in scope:
         return scope[None]
      return None

   def __call__(self, *args, **kwargs):
      if len(args) != self.num_params:
         raise ArgumentCountError('The number of arguments provided does not match the number of arguments specified in the MultipleLDispatcher')
      handler = self.get_handler(self._handlers, args)
      if handler is None:
         raise TypeError('This MultipleLDispatcher can not handle those parameters')
      return handler(*args, *kwargs)

     
