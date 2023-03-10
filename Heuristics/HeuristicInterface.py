import abc
from git import Repo, Commit
import re


class HeuristicInterface(metaclass=abc.ABCMeta):
    '''Interface for all heuristic implementations'''

    __slots__ = ["repo", "file_endings"]
    '''Slots define abstract class attributes. No instance
    '''

    def __new__(cls, *args, **kwargs):
        '''Factory method for base/subtype creation. Simply creates an
        (new-style class) object instance and sets a base property. '''
        instance = object.__new__(cls)

        if len(args) < 1 and not type(args[0]) == Repo:
            raise Exception("Heuristic not implemented correctly! Constructor requires first argument of type Repo")
        instance.repo = args[0]

        if 'java' not in kwargs or not type(kwargs['java']) == bool:
            raise Exception("Heuristic not implemented correctly! Constructor requires named argument java")

        java = kwargs['java']
        if java:
            instance.file_endings = '^.*\.(java)$'
        else:
            instance.file_endings = '^.*\.(c|c\+\+|cpp|h|hpp|cc)$'

        return instance

    @abc.abstractmethod
    def use_heuristic(self, commit: Commit, cve: dict):
        pass

    def is_code_file(self, file):
        if file:
            return re.match(self.file_endings, file) and "test" not in file.lower()
        return False
