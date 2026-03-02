"""
Task 2 - Preliminary code: Max Heap + Heap Sort (OOP style)
"""

class MaxHeap:
    def __init__(self):
        self._data: list[int] = []

    def __len__(self) -> int:
        return len(self._data)

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left(self, i: int) -> int:
        return 2 * i + 1

    def _right(self, i: int) -> int:
        return 2 * i + 2

    def peek_max(self) -> int:
        if not self._data:
            raise IndexError("peek from empty heap")
        return self._data[0]

    def insert(self, value: int) -> None:
        self._data.append(value)
        self._sift_up(len(self._data) - 1)

    def extract_max(self) -> int:
        if not self._data:
            raise IndexError("extract from empty heap")

        maximum = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return maximum

    def _sift_up(self, i: int) -> None:
        while i > 0:
            p = self._parent(i)
            if self._data[p] >= self._data[i]:
                break
            self._data[p], self._data[i] = self._data[i], self._data[p]
            i = p

    def _sift_down(self, i: int) -> None:
        n = len(self._data)
        while True:
            l = self._left(i)
            r = self._right(i)
            largest = i

            if l < n and self._data[l] > self._data[largest]:
                largest = l
            if r < n and self._data[r] > self._data[largest]:
                largest = r

            if largest == i:
                break

            self._data[i], self._data[largest] = self._data[largest], self._data[i]
            i = largest


def heap_sort(arr: list[int]) -> list[int]:
    heap = MaxHeap()
    for x in arr:
        heap.insert(x)

    out: list[int] = []
    while len(heap) > 0:
        out.append(heap.extract_max())

    out.reverse()
    return out


if __name__ == "__main__":
    sample = [10, 3, 25, 7, 1, 18]
    print("Original:", sample)
    print("Sorted:", heap_sort(sample))
