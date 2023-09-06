from typing import TypeVar, Generic

T = TypeVar('T')  # Create a generic type variable

class Node(Generic[T]):
    def __init__(self, data: T):
        self.data: T = data
        self.next: T = None

class LinkedList(Generic[T]):
    def __init__(self):
        self.head: Node[T] = None
        self.size: int = 0
        
    def is_empty(self) -> bool:
        return self.head is None

    def append(self, data: T):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def prepend(self, data: T):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def delete(self, data: T):
        if self.head is None:
            return

        if self.head.data == data:
            self.head = self.head.next
            return

        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return
            current = current.next
        self.size -= 1
        
    def size(self) -> int:
        return self.size

    def display(self):
        current = self.head
        while current:
            print(current.data, end=" -> ")
            current = current.next
        print("None")
