from app.core.tools.linked_list import LinkedList

class NodeManager:
    
    def __init__(self, node_list: LinkedList) -> None:
        self.node_list = node_list
        self.current = node_list.head
        
    def get(self, comparator_func):
        while self.current is not None and comparator_func(self.current.data) == False:
            self.current = self.current.next
            
        if self.current is not None:    
            return self.current.data
        return None