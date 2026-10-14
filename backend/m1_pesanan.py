"""M1: Array (kapasitas 2x) vs LinkList (head + tail).
Tanpa dict/set/sorted/.sort()/collections. Hanya list sebagai larik primitif.
Posisi tengah (PRIORITAS) = n // 2.
"""


class Array:
    def __init__(self, kapasitas=4):
        self.kapasitas = kapasitas
        self.data = [None] * kapasitas
        self.n = 0
        self.geser = 0  # jumlah salin/geser, untuk ditampilkan di UI

    def _tumbuh(self):
        baru = [None] * (self.kapasitas * 2)
        for i in range(self.n):
            baru[i] = self.data[i]
            self.geser += 1
        self.data = baru
        self.kapasitas *= 2

    def append(self, v):  # REGULER: O(1) amortized
        if self.n == self.kapasitas:
            self._tumbuh()
        self.data[self.n] = v
        self.n += 1

    def insert(self, i, v):  # PRIORITAS (tengah) / VIP (i=0): O(n)
        if i < 0 or i > self.n:
            raise IndexError("indeks di luar rentang")
        if self.n == self.kapasitas:
            self._tumbuh()
        j = self.n
        while j > i:
            self.data[j] = self.data[j - 1]
            self.geser += 1
            j -= 1
        self.data[i] = v
        self.n += 1

    def get(self, i):  # O(1)
        if i < 0 or i >= self.n:
            raise IndexError("indeks di luar rentang")
        return self.data[i]

    def hapus(self, i):  # O(n)
        if i < 0 or i >= self.n:
            raise IndexError("indeks di luar rentang")
        v = self.data[i]
        for j in range(i, self.n - 1):
            self.data[j] = self.data[j + 1]
            self.geser += 1
        self.data[self.n - 1] = None
        self.n -= 1
        return v

    def tambah_reguler(self, v):
        self.append(v)

    def tambah_prioritas(self, v):
        self.insert(self.n // 2, v)

    def tambah_vip(self, v):
        self.insert(0, v)

    def __len__(self):
        return self.n


class Node:
    def __init__(self, nilai):
        self.nilai = nilai
        self.next = None


class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.n = 0
        self.telusur = 0  # jumlah simpul yang dilewati

    def append(self, v):  # REGULER: O(1) berkat tail
        node = Node(v)
        if self.head is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.n += 1

    def prepend(self, v):  # VIP: O(1)
        node = Node(v)
        node.next = self.head
        self.head = node
        if self.tail is None:
            self.tail = node
        self.n += 1

    def insert(self, i, v):  # PRIORITAS: O(n) telusur
        if i < 0 or i > self.n:
            raise IndexError("indeks di luar rentang")
        if i == 0:
            self.prepend(v)
            return
        if i == self.n:
            self.append(v)
            return
        cur = self.head
        for _ in range(i - 1):
            cur = cur.next
            self.telusur += 1
        node = Node(v)
        node.next = cur.next
        cur.next = node
        self.n += 1

    def get(self, i):  # O(n)
        if i < 0 or i >= self.n:
            raise IndexError("indeks di luar rentang")
        cur = self.head
        for _ in range(i):
            cur = cur.next
            self.telusur += 1
        return cur.nilai

    def hapus(self, i):  # O(n) telusur
        if i < 0 or i >= self.n:
            raise IndexError("indeks di luar rentang")
        if i == 0:
            v = self.head.nilai
            self.head = self.head.next
            if self.head is None:
                self.tail = None
        else:
            cur = self.head
            for _ in range(i - 1):
                cur = cur.next
                self.telusur += 1
            target = cur.next
            v = target.nilai
            cur.next = target.next
            if target is self.tail:  # jangan lupa update tail
                self.tail = cur
        self.n -= 1
        return v

    def tambah_reguler(self, v):
        self.append(v)

    def tambah_prioritas(self, v):
        self.insert(self.n // 2, v)

    def tambah_vip(self, v):
        self.prepend(v)

    def __len__(self):
        return self.n


if __name__ == "__main__":
    for S in (Array, LinkList):
        s = S()
        for x in ("R1", "R2", "R3", "R4", "R5"):
            s.tambah_reguler(x)
        s.tambah_vip("VIP")
        s.tambah_prioritas("PRI")
        urut = [s.get(i) for i in range(len(s))]
        assert urut == ["VIP", "R1", "R2", "PRI", "R3", "R4", "R5"], urut
        assert s.hapus(3) == "PRI"
        assert s.hapus(len(s) - 1) == "R5"
        s.tambah_reguler("R6")
        assert s.get(len(s) - 1) == "R6"
        print(S.__name__, "OK")
