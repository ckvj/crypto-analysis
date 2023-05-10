from typing import List
from abc import ABC, abstractclassmethod
from cryptotax.trade import Trade

# Strategy Pattern Implementation for Analysis Type
class AnalysisStrategy(ABC):
    @abstractclassmethod
    def sort(self, txn_list: List[Trade]) -> List[Trade]:
        pass

class FifoStrategy(AnalysisStrategy):
    """First In First Out"""
    def sort(self, txn_list: List[Trade]) -> List[Trade]:
        return sorted(txn_list, key = lambda x : x.epoch_time)

class LifoStrategy(AnalysisStrategy):
    """Last In First Out"""
    def sort(self, txn_list: List[Trade]) -> List[Trade]:
        return sorted(txn_list, key = lambda x : x.epoch_time, reverse=True)
    
class HifoStrategy(AnalysisStrategy):
    """Highest In First Out"""
    def sort(self, txn_list: List[Trade]) -> List[Trade]:
        return sorted(txn_list, key = lambda x : x.price, reverse=True)
