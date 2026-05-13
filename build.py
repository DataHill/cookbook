import os
import re
import shutil
import pandas as pd
from  jinja2 import Environment, FileSystemLoader




#import google sheets data
#  # remove edit?gid=0#gid=0 and use export?format=csv&gid=0 #  #
recipes_url       = 'https://docs.google.com/spreadsheets/d/19EdezjfCuFwYmWSd4SKlamLAJeOOR2Yn7b2QFPCBN0s/export?format=csv&gid=0'
ingredients_url   = 'https://docs.google.com/spreadsheets/d/19EdezjfCuFwYmWSd4SKlamLAJeOOR2Yn7b2QFPCBN0s/export?format=csv&gid=0' 
instructions_url  = 'https://docs.google.com/spreadsheets/d/19EdezjfCuFwYmWSd4SKlamLAJeOOR2Yn7b2QFPCBN0s/export?format=csv&gid=0' 



recipes_df      = pd.read_csv(recipes_url)
ingredients_df  = pd.read_csv(ingredients_url)
instructions_df = pd.read_csv(instructions_url)



