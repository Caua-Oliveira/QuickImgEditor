from collections import deque
from PIL import Image


class ChangesHistory():
    def __init__(self):
        self.queue = deque(maxlen=10)
        self.current_index = -1

    def add(self, image: Image.Image):
        # Remove the oldest image if the queue is full
        if len(self.queue) == self.queue.maxlen:
            self.queue.popleft()
            self.current_index -= 1

        # If the current index is at the end of the queue, append the new image
        if self.current_index == len(self.queue) - 1:
            self.queue.append(image)
            self.current_index += 1
        else:
            # Remove all images after the current index
            self.queue = deque(list(self.queue)[:self.current_index + 1], maxlen=10)
            # Add the new image
            self.queue.append(image)
            self.current_index += 1

    def undo(self) -> None | Image.Image:
        if self.current_index == -1:
            return None
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = 0
            return None
        return self.queue[self.current_index]

    def redo(self) -> None | Image.Image:
        if self.current_index == len(self.queue) - 1:
            return None
        self.current_index += 1
        if self.current_index >= len(self.queue):
            self.current_index = len(self.queue) - 1
            return None
        return self.queue[self.current_index]

