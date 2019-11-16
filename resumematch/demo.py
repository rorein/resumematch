from resumematch.matching import Matcher

match = Matcher()

@match.add_handler
def match_default(pat, obj, **kwargs):
   if pat == obj or pat is obj:
      return 1
   return 0

@match.add_handler
def match_dict(pat: dict, obj: dict, **kwargs):
   score = 0.0
   num_items = 0
   for k, v in pat.items():
      if isinstance(k, str) and k.startswith('_'):
         continue
      num_items += 1
      if k in obj:
         score += match(v, obj[k])
   return score/num_items

#@match.add_handler
#def match_lit(pat: (int, float, str, bool), obj, **kwargs):
#   if pat == obj or pat is obj:
#      return 1
#   return 0

@match.add_handler
def match_bool(pat: bool, obj: bool, **kwargs):
   return obj if pat else True

@match.add_handler
def match_num(pat: (int, float), obj: (int, float), **kwargs):
   return obj/pat

@match.add_handler
def match_list_lit(pat: list, obj, **kwargs):
   return (obj in pat)

@match.add_handler
def match_list(pat: list, obj: list, **kwargs):
   score = 0.0
   for e1 in pat:
      best_score = 0
      for e2 in obj:
         try:
            mscore = match(e1, e2)
         except NoHandlerError:
            continue
         if mscore > best_score:
            best_score = mscore
      score += best_score
   return score/len(pat)


pattern = {
   '_title': 'Senior Data Analyist',
   '_approximate_salary': 100000,
   'skill_level': 4,
   'travelling': False,
   'degree': {
      'level': ['Master', 'PhD'],
      'domain': 'Statistics',
   },
   'prog_langs': [
      'Python',
      'R'
   ],
   'frameworks': [
      ['Tensorflow', 'Keras'],
   ],
   'libraries': [
      'pandas',
      'scikit-learn'
   ]
}

objct = {
   'name': {
      'first': 'John',
      'last': 'Doe'
   },
   'skill_level': 3,
   'age': 42,
   'gender': 'male',
   'travelling': True,
   'degree': {
      'level': 'Master',
      'domain': 'Statistics'
   },
   'prog_langs': [
      'java',
      'Python'
   ],
   'frameworks': [
      'Keras',
   ],
   'libraries': [
      'pandas',
      'statsmodels'
   ]
}

print(match(pattern, objct)**0.5)
