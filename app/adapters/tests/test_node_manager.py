from app.core.tools.linked_list import LinkedList
from app.adapters.services.node_manager import NodeManager

class TestClass:
    def __init__(self, name) -> None:
        self.max_count = 10
        self.name = name        
        self.count = 0
    
    def incr(self):
        self.count += 1

def test_get_node_with_number():
    linked_list = LinkedList[int]()
    linked_list.append(1)
    linked_list.append(2)
    linked_list.append(3)
    linked_list.append(4)

    def is_valid(data):
        if data < 3:
            return False
        return True

    manage = NodeManager(linked_list)
    data = manage.get(is_valid)
    assert data == 3

def test_get_node_with_counter():
    linked_list = LinkedList[TestClass]()
    linked_list.append(TestClass("list 1"))
    linked_list.append(TestClass("list 2"))
    linked_list.append(TestClass("list 3"))
    linked_list.append(TestClass("list 4"))
    
    def comparator(data: TestClass):
        if data.count < data.max_count:
            return True
        return False
    
    manager = NodeManager(linked_list)
    data =  manager.get(comparator)
    assert data.name == "list 1" # First node

    # Loop 20 times should reach to second node
    for _ in range(1, 21):
        data =  manager.get(comparator)
        data.incr()
    assert data.name == "list 2"
    
    # Next 20 loops times should reach to last node
    for _ in range(1, 20):
        data =  manager.get(comparator)
        data.incr()
    assert data.name == "list 4"
    
    # Any further should return None
    for _ in range(1, 5):
        data =  manager.get(comparator)
        if data is None:
            break
        data.incr()
    assert data is None