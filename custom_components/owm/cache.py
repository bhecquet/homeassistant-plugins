'''
Created on 4 mars 2019

@author: s047432
'''

import pickle
import os

class Cache:
    
    cache_path = None
    
    @classmethod
    def set_cache_path(cls, config_path):
        cls.cache_path = os.path.join(config_path, 'cache')
        os.makedirs(cls.cache_path, exist_ok=True)
    
    def __init__(self, object_name):
        self.cache_file = os.path.join(Cache.cache_path, object_name)
    
    def get(self):
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, 'rb') as c:
                try:
                    return pickle.load(c)
                except Exception as e:
                    print(e)
                    return None
    
    def update(self, object):
        with open(self.cache_file, 'wb') as c:
            try:
                pickle.dump(object, c)
            except Exception as e:
                print(e)
            finally:
                return object
        
        
    def exists(self):
        return os.path.isfile(self.cache_file)
