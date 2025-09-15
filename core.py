import secrets
from collections import deque

class Cell:
    __slots__ = ("bomb", "revealed", "flag", "adj")
    def __init__(self):
        self.bomb = False
        self.revealed = False
        self.flag = False
        self.adj = 0

class Board:
    def __init__(self, size, bombs):
        self.size = size
        self.total_bombs = bombs
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        self.first_click_done = False
        self.open_count = 0
        self.lost = False

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def neighbors(self, r, c):
        for i in range(r-1, r+2):
            for j in range(c-1, c+2):
                if (i != r or j != c) and self.in_bounds(i, j):
                    yield i, j

    def place_bombs(self, safe_rc):
        r0, c0 = safe_rc
        placed = 0
        while placed < self.total_bombs:
            r = secrets.randbelow(self.size)
            c = secrets.randbelow(self.size)
            if (r, c) == (r0, c0): 
                continue
            cell = self.grid[r][c]
            if not cell.bomb:
                cell.bomb = True
                placed += 1
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c].adj = sum(1 for i, j in self.neighbors(r, c) if self.grid[i][j].bomb)

    def toggle_flag(self, r, c):
        cell = self.grid[r][c]
        if cell.revealed:
            return
        cell.flag = not cell.flag

    def reveal(self, r, c):
        if not self.in_bounds(r, c) or self.grid[r][c].flag:
            return set()
        if not self.first_click_done:
            self.place_bombs((r, c))
            self.first_click_done = True
            cell = self.grid[r][c]
            if not cell.revealed and not cell.bomb:
                cell.revealed = True
                self.open_count += 1
            return {(r, c)}
        cell = self.grid[r][c]
        if cell.revealed:
            return set()
        if cell.bomb:
            self.lost = True
            for i in range(self.size):
                for j in range(self.size):
                    if self.grid[i][j].bomb:
                        self.grid[i][j].revealed = True
            return {(r, c)}
        opened = set()
        q = deque()
        q.append((r, c))
        while q:
            i, j = q.popleft()
            cur = self.grid[i][j]
            if cur.revealed or cur.flag:
                continue
            cur.revealed = True
            opened.add((i, j))
            self.open_count += 1
            if cur.adj == 0 and not cur.bomb:
                for ni, nj in self.neighbors(i, j):
                    if not self.grid[ni][nj].revealed and not self.grid[ni][nj].flag and not self.grid[ni][nj].bomb:
                        q.append((ni, nj))
        return opened

    def victory(self):
        total_cells = self.size * self.size
        return self.first_click_done and not self.lost and self.open_count == total_cells - self.total_bombs
