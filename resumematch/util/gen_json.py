from random import gauss, random, randint

def gen_json(obj, feature_gen, num_things, obj_pct=0.3, lst_pct=0.3):
   for i in range(num_things):
      feat = feature_gen(i)
      r = random()
      if r < obj_pct:
         obj[feat] = gen_json_obj(obj_pct=obj_pct/1.5, lst_pct=lst_pct/1.5)
      elif r < obj_pct + lst_pct:
         obj[feat] = gen_json_lst(obj_pct=obj_pct/1.25, lst_pct=lst_pct/5)
      else:
         obj[feat] = gen_json_lit()
   return obj

def rand_feat_num(mean, std):
   num = int(gauss(mean, std))
   if num < 1:
      num = 1
   return num

def gen_json_obj(mean_features=5, std_dev=1, **kwargs):
   oa = ord('a')
   return gen_json({}, lambda i: chr(oa+i), rand_feat_num(mean_features, std_dev), **kwargs)

def gen_json_lst(mean_items=5, std_dev=1, num_items=None, **kwargs):
   if num_items is None:
      num_items = rand_feat_num(mean_items, std_dev)
   obj_pct = 0.3
   if 'obj_pct' in kwargs:
      obj_pct = kwargs['obj_pct']
   lst_pct = 0.3
   if 'lst_pct' in kwargs:
      lst_pct = kwargs['lst_pct']
   template = gen_json_obj(obj_pct=obj_pct/1.5, lst_pct=lst_pct/1.5)
   lst = [template,]
   for _ in range(num_items-1):
      lst.append(randomize_template_lits(lst[0]))
   return lst

def gen_json_lit(lo=1, hi=10):
   return randint(1, 10)

def randomize_template_lits(template):
   template = template.copy()
   if isinstance(template, dict):
      it = template.items()
   if isinstance(template, list):
      it = enumerate(template)
   for k, v in it:
      if isinstance(v, (dict, list)):
         template[k] = randomize_template_lits(v)
      else:
         template[k] = gen_json_lit()
   return template


