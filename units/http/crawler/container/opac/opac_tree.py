import re
import math
from units.http.crawler.container.opac.opac_regex import OPaCRegex

''' ################################
        PRIVATE - PATHNODE CLASS
    ################################
'''
class PathNode:

    increment = 10

    def __init__(self, name, callback=None, parent=None):
        self.name = name
        self.regexes = {}
        self.children = {}
        self.trigger = self.increment
        self.parent = parent

        self.refresh_callback = callback

    '''
        tree to String. Just for debugging uses
    '''
    def stringify(self, depth=0):

        string = '----|'*depth + self.name + '(# of childs: {0})\n'.format(len(self.children))
        
        for child in self.children:
            string += self.children[child].stringify(depth+1)

        for child in self.regexes:
            string += self.regexes[child].stringify(depth+1)

        return string


    def get_root(self):
        if not self.parent:
            return ''
        return self.parent.get_root() + '/' + self.name


    ''' Adds a new path into the tree.
    '''
    def add_path(self, path):

        child_node = None
        child_name = path[0]

        child_added = False
        localy_added = False

        if child_name in self.children:
            child_node = self.children[child_name]
 
        else:
            for regex, child in self.regexes.items():
                if re.match(regex, child_name):
                    child_node = child
                    break
                    
        if not child_node:
            localy_added = True
            child_node = PathNode(name=child_name, callback=self.refresh_callback, parent=self)
            self.children[child_name] = child_node

        if len(path) > 1:
            child_added = child_node.add_path(path[1:])

        if localy_added and self.compress() and self.refresh_callback:
            self.refresh_callback(self)

        return (localy_added or child_added)


    def compress(self):
        if len(self.children) < self.trigger:
            return False

        children_names = list(self.children.keys())

        opac_regex = OPaCRegex()
        regex = opac_regex.digest(children_names)

        matching_children = [child_name for child_name in children_names if re.match(regex, child_name)]

        if len(matching_children) > int(self.increment * 0.8):

            regex_node = PathNode(regex)
            self.regexes[regex] = regex_node

            for child_name in matching_children:
                regex_node.merge(self.children[child_name])
                del(self.children[child_name])

            regex_node.compress()
        else:
            self.trigger = len(self.children) + self.increment
            return False

        return True


    def merge(self, node):
        for child_name, child_node in node.children.items():
            if child_name in self.children:
                self.children[child_name].merge(child_node)
                continue

            for regex in self.regexes:
                if re.match(regex, child_name):
                    self.regexes[regex].merge(child_node)
                    break

            self.children[child_name] = child_node


