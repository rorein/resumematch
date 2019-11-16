from inspect import signature, Parameter


class NoHandlerError(Exception):
   pass


class MissingParameterError(Exception):
   pass

 
class ObjectHandler:

   FAST_SINGLE_OPTION = False

   def __init__(self, pat, obj_handler, multipat=False):
      self.get_handler = self.get_handler_from_list
      if multipat:
         self.get_handler = self.get_handler_from_list_mp
      if isinstance(obj_handler, list) and len(obj_handler) == 1:
         obj_handler = obj_handler[0]
         if multipat:
            pat = pat[0]
      if isinstance(obj_handler, dict):
         if ObjectHandler.FAST_SINGLE_OPTION and len(obj_handler) == 1:
            k = next(iter(obj_handler))
            obj_handler = obj_handler[k]
            self.get_handler = self.get_handler_from_fso
         else:
            self.get_handler = self.get_handler_from_dict
      self.pat = pat
      self.obj_handler = obj_handler

   def get_handler_from_list_mp(self, obj):
      for pat, obj_handle_dict in zip(self.pat, self.obj_handler):
         for t, handler in obj_handle_dict.items():
            if t is not None and isinstance(obj, t):
               return pat, handler
      for pat, obj_handle_dict in zip(self.pat, self.obj_handler):
         if None in obj_handle_dict:
            return pat, obj_handle_dict[None]
      raise NoHandlerError('No handler matching type of "obj" found')

   def get_handler_from_list(self, obj):
      for obj_handle_dict in self.obj_handler:
         for t, handler in obj_handle_dict.items():
            if t is not None and isinstance(obj, t):
               return self.pat, handler
      for obj_handle_dict in self.obj_handler:
         if None in obj_handle_dict:
            return self.pat, obj_handle_dict[None]
      raise NoHandlerError('No handler matching type of "obj" found')

   def get_handler_from_dict(self, obj):
      for t, handler in self.obj_handler.items():
         if t is not None and isinstance(obj, t):
            return self.pat, handler
      if None in self.obj_handler:
         return self.pat, self.obj_handler[None]
      raise NoHandlerError('No handler matching type of "obj" found')
   
   def get_handler_from_fso(self, obj):
      return self.pat, self.obj_handler

   def __call__(self, obj):
      pat, handler = self.get_handler(obj)
      return handler(pat, obj)


class Matcher:
 
   def __init__(self):
      self.pat_handlers = {}

   def add_handler(self, handler):
      params = signature(handler).parameters
      if 'pat' not in params:
         raise MissingParameterError('The handler must contain an argument named "pat", the pattern parameter for the type handler')
      if 'obj' not in params:
         raise MissingParameterError('The handler must contian an argument named "obj", the object to be compared against the pattern for the type handler')

      pat_type = params['pat'].annotation
      if pat_type is Parameter.empty:
         pat_type = None
      
      obj_type = params['obj'].annotation
      if obj_type is Parameter.empty:
         obj_type = None

      obj_handlers = {}
      if pat_type in self.pat_handlers:
         obj_handlers = self.pat_handlers[pat_type]
      else:
         self.pat_handlers[pat_type] = obj_handlers
      obj_handlers[obj_type] = handler
      return handler
   
   def get_obj_handler(self, pat):
      obj_handlers = []
      for t, obj_handler in self.pat_handlers.items():
         if t is not None and isinstance(pat, t):
            obj_handlers.append(obj_handler)
      if None in self.pat_handlers:
         obj_handlers.append(self.pat_handlers[None])
      if len(obj_handlers) == 0:
         raise NoHandlerError('No handler matching type of "pat" found')
      return ObjectHandler(pat, obj_handlers)

   def match(self, pat, obj=None):
      obj_handler = self.get_obj_handler(pat)
      if obj is None:
         return obj_handler
      return obj_handler(obj)

   def __call__(self, pat, obj=None):
      return self.match(pat, obj)


class DefaultMatcher(Matcher):

   def __init__(self):
      super().__init__()
      
      @self.add_handler
      def match_dict(pat: dict, obj: dict):
         score = 0.0
         num_items = 0
         for k, v in pat.items():
            if isinstance(k, str) and k.startswith('_'):
               continue
            num_items += 1
            if k in obj:
               score += self.match(v, obj[k])
         return score/num_items

      @self.add_handler
      def match_list(pat: list, obj: list):
         score = 0.0
         num_items = len(pat)
         for e1 in pat:
            best_score = 0
            for e2 in obj:
               try:
                  mscore = self.match(e1, e2)
               except NoHandlerError:
                  continue
               if mscore > best_score:
                  best_score = mscore
            score += best_score
         return score/num_items

      @self.add_handler
      def match_def(pat: (int, float, str, bool), obj):
         if pat is obj or pat == obj:
            return 1
         return 0

match = DefaultMatcher()


class CompilingMatcher:

   def __init__(self):
      self.cpat_handlers = {}
      self.compilers = {}

   def add_chandler(self, chandler):
      params = signature(chandler).parameters
      if 'cpat' not in params:
         raise MissingParameterError('The handler must contain an argument named "cpat", the compiled pattern parameter for the type handler')
      if 'obj' not in params:
         raise MissingParameterError('The handler must contian an argument named "obj", the object to be compared against the compiled pattern for the type handler')

      cpat_type = params['cpat'].annotation
      if cpat_type is Parameter.empty:
         cpat_type = None
      
      obj_type = params['obj'].annotation
      if obj_type is Parameter.empty:
         obj_type = None

      obj_handlers = {}
      if cpat_type in self.cpat_handlers:
         obj_handlers = self.cpat_handlers[cpat_type]
      else:
         self.cpat_handlers[cpat_type] = obj_handlers
      obj_handlers[obj_type] = chandler
      return chandler

   def add_compiler(self, compiler):
      params = signature(compiler).parameters
      if 'pat' not in params:
         raise MissingPatameterError('The compiler must contain an argument named "pat", the pattern to compile')

      pat_type = params['pat'].annotation
      if pat_type is Parameter.empty:
         pat_type = None

      self.compilers[pat_type] = compiler
      return compiler

   def compile(self, pat):
      cpats = []
      collapsable = True
      obj_handlers = []
      for t, obj_handler in self.cpat_handlers.items():
         if t is not None and isinstance(pat, t):
            if t in self.compilers:
               cpats.append(self.compilers[t](pat))
            else:
               cpats.append(pat)
            if collapsable and len(cpats) > 0 and cpats[-1] != cpats[0]:
               collapsable = False
            obj_handlers.append(obj_handler)
      if None in self.cpat_handlers:
         if None in self.compilers:
            cpats.append(self.compilers[None](pat))
         else:
            cpats.append(pat)
         if collapsable and len(cpats) > 0 and cpats[-1] != cpats[0]:
            collapsable = False
         obj_handlers.append(self.pat_handlers[None])
      if len(obj_handlers) == 0:
         raise NoHandlerError('No handler matching type of "pat" found')
      if collapsable:
         cpats = cpats[0]
      return ObjectHandler(cpats, obj_handlers, multipat=not collapsable)

   def __call__(self, pat, obj=None):
      obj_handler = self.compile(pat)
      if obj is None:
         return obj_handler
      return obj_handler(obj)


class DefaultCompilingMatcher(CompilingMatcher):
   
   def __init__(self):
      super().__init__()

      @self.add_compiler
      def compile_dict(pat: dict):
         cpat = []
         for k, v in pat.items():
            if isinstance(k, str) and k.startswith('_'):
               continue
            cv = self.compile(v)
            cpat.append((k, cv))
         return cpat

      @self.add_chandler
      def match_dict(cpat: dict, obj: dict):
         score = 0
         for k, cv in cpat:
            if k in obj:
               score += cv(obj[k])
         return score / len(cpat)

      @self.add_compiler
      def compile_list(pat: list):
         return [self.compile(e) for e in pat]

      @self.add_chandler
      def match_list(cpat: list, obj: list):
         score = 0
         for ce in cpat:
            best_score = 0
            for e in obj:
               try:
                  s = ce(e)
               except NoHandlerError:
                  continue
               if s > best_score:
                  best_score = s
            score += best_score
         return score / len(cpat)

      @self.add_chandler
      def match_lit(cpat: (int, float, str, bool), obj):
         if cpat is obj or cpat == obj:
            return 1
         return 0

cmatch = DefaultCompilingMatcher()
