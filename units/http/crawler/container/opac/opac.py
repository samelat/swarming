
import re
import string
import random

from units.http.crawler.container.opac.opac_tree import PathNode


''' ################################
        PUBLIC - OPAC CLASS
    ################################
'''
class OPaC:
    def __init__(self):
        self.paths = {}
        self.trees = {}
        self.current_depth = 0
        
        self.muzzle = False

    def __iter__(self):
        return self

    def __next__(self):
        for depth in self.paths:
            if len(self.paths[depth]):
                return self.paths[depth].pop()
        raise StopIteration

    def __len__(self):
        return sum([len(paths) for paths in self.paths.values()])


    def add_path(self, complete_path):
        clean_path = complete_path.strip('/')
        if clean_path:
            splitted_path = clean_path.split('/')

            self.current_depth = len(splitted_path)
            if self.current_depth not in self.trees:
                self.paths[self.current_depth] = []
                self.trees[self.current_depth] = PathNode(name='', callback=self.refresh_callback)

            if self.trees[self.current_depth].add_path(splitted_path):
                self.paths[self.current_depth].append(complete_path)
                return True

        return False

    ''' Refresh routines
    '''
    def refresh_callback(self, opac_node):
        if not self.muzzle:
            return

        root_path = opac_node.get_root()

        paths = []
        for path in self.paths[self.current_depth]:
            if re.match('^' + root_path, path):
                subpath = path.replace(root_path, '')
                splitted_path = subpath.strip('/').split('/')
                if splitted_path[0] in opac_node.children:
                    paths.append(path)
                continue

            paths.append(path)
        self.paths[self.current_depth] = paths
