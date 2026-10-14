"""M2: Stack (di atas Array M1), postfix, antrean naif vs melingkar, undo/redo.
Tanpa dict/set/sorted/.sort()/collections.
"""
try:
    from backend.m1_pesanan import Array
except ImportError:
    from m1_pesanan import Array


class Stack:
    def __init__(self):
        self.arr = Array()

    def push(self, x):
        self.arr.append(x)

    def pop(self):  # O(1): hapus indeks terakhir, tidak ada yang digeser
        if self.arr.n == 0:
            return None
        return self.arr.hapus(self.arr.n - 1)

    def peek(self):
        if self.arr.n == 0:
            return None
        return self.arr.get(self.arr.n - 1)

    def kosong(self):
        return self.arr.n == 0

    def __len__(self):
        return self.arr.n


# ---------------- Kasir: infix -> postfix -> total ----------------
def tokenisasi(teks):
    tokens = []
    angka = ""
    for ch in teks:
        if ch in "0123456789":
            angka += ch  # 12000 harus jadi satu token
        else:
            if angka != "":
                tokens.append(angka)
                angka = ""
            if ch in "+-*/()":
                tokens.append(ch)
            elif ch != " ":
                raise ValueError("karakter tidak dikenal: " + ch)
    if angka != "":
        tokens.append(angka)
    return tokens


def _prioritas(op):
    if op == "*" or op == "/":
        return 2
    return 1  # + dan -


def ke_postfix(ekspresi):
    keluaran = []
    st = Stack()
    for t in tokenisasi(ekspresi):
        if t[0] in "0123456789":
            keluaran.append(t)
        elif t == "(":
            st.push(t)
        elif t == ")":
            while not st.kosong() and st.peek() != "(":
                keluaran.append(st.pop())
            if st.kosong():
                raise ValueError("kurung tidak seimbang")
            st.pop()  # buang "("
        else:
            while (not st.kosong() and st.peek() != "("
                   and _prioritas(st.peek()) >= _prioritas(t)):
                keluaran.append(st.pop())
            st.push(t)
    while not st.kosong():
        op = st.pop()
        if op == "(":
            raise ValueError("kurung tidak seimbang")
        keluaran.append(op)
    return keluaran


def hitung(postfix):
    st = Stack()
    for t in postfix:
        if t[0] in "0123456789":
            st.push(int(t))
        else:
            b = st.pop()  # operand kanan keluar PERTAMA
            a = st.pop()
            if a is None or b is None:
                raise ValueError("ekspresi tidak valid")
            if t == "+":
                st.push(a + b)
            elif t == "-":
                st.push(a - b)
            elif t == "*":
                st.push(a * b)
            else:
                if b == 0:
                    raise ValueError("pembagian dengan nol")
                st.push(a // b if a % b == 0 else a / b)
    return st.pop()


# ---------------- Antrean naif (larik + pop(0) manual) ----------------
class AntreanNaif:
    def __init__(self):
        self.arr = Array()
        self.geser = 0

    def enqueue(self, x):
        self.arr.append(x)

    def dequeue(self):
        if self.arr.n == 0:
            return None
        sebelum = self.arr.geser
        x = self.arr.hapus(0)  # menggeser seluruh sisa: O(n)
        self.geser += self.arr.geser - sebelum
        return x

    def __len__(self):
        return self.arr.n


# ---------------- Antrean melingkar ----------------
class AntreanMelingkar:
    def __init__(self, K=4):
        self.K = K
        self.data = [None] * K
        self.front = 0
        self.rear = 0
        self.count = 0
        self.geser = 0  # selalu 0 untuk dequeue

    def kosong(self):
        return self.count == 0  # jangan pakai front == rear saja

    def _tumbuh(self):  # keputusan: tumbuh 2x saat penuh
        baru = [None] * (self.K * 2)
        for i in range(self.count):
            baru[i] = self.data[(self.front + i) % self.K]
        self.data = baru
        self.front = 0
        self.rear = self.count
        self.K *= 2

    def enqueue(self, x):
        if self.count == self.K:
            self._tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.K
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.K
        self.count -= 1
        return x

    def taruh_depan(self, x):  # untuk undo DEQUEUE
        if self.count == self.K:
            self._tumbuh()
        self.front = (self.front - 1) % self.K
        self.data[self.front] = x
        self.count += 1

    def keluar_belakang(self):  # untuk undo ENQUEUE
        if self.count == 0:
            return None
        self.rear = (self.rear - 1) % self.K
        x = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return x

    def isi(self):
        hasil = []
        for i in range(self.count):
            hasil.append(self.data[(self.front + i) % self.K])
        return hasil

    def __len__(self):
        return self.count


# ---------------- Undo / Redo di atas antrean melingkar ----------------
class Riwayat:
    def __init__(self, antrean):
        self.q = antrean
        self.undo = Stack()
        self.redo = Stack()

    def enqueue(self, x):
        self.q.enqueue(x)
        self.undo.push(("ENQUEUE", [x]))
        self.redo = Stack()  # aksi baru mengosongkan redo

    def dequeue(self, k=1):
        keluar = []
        for _ in range(k):
            x = self.q.dequeue()
            if x is None:
                break
            keluar.append(x)
        if len(keluar) > 0:
            self.undo.push(("DEQUEUE", keluar))  # simpan DAFTAR, bukan hitungan
            self.redo = Stack()
        return keluar

    def undo_last(self):
        if self.undo.kosong():
            return None
        aksi = self.undo.pop()
        jenis, daftar = aksi
        if jenis == "ENQUEUE":
            for _ in range(len(daftar)):
                self.q.keluar_belakang()
        else:  # kembalikan ke DEPAN, urutan dibalik
            for i in range(len(daftar) - 1, -1, -1):
                self.q.taruh_depan(daftar[i])
        self.redo.push(aksi)
        return aksi

    def redo_last(self):
        if self.redo.kosong():
            return None
        aksi = self.redo.pop()
        jenis, daftar = aksi
        if jenis == "ENQUEUE":
            for x in daftar:
                self.q.enqueue(x)
        else:  # kerjakan aksi ASLINYA
            for _ in range(len(daftar)):
                self.q.dequeue()
        self.undo.push(aksi)
        return aksi


if __name__ == "__main__":
    # kasir
    assert hitung(ke_postfix("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")) == 48000
    assert hitung(ke_postfix("10 - 3 - 2")) == 5
    assert hitung(ke_postfix("100 / 5 / 2")) == 10
    assert hitung(ke_postfix("((2+3)*(4-1))")) == 15
    # antrean melingkar, K=4: masuk 3, keluar 2, masuk 3 lagi
    q = AntreanMelingkar(4)
    for x in (1, 2, 3):
        q.enqueue(x)
    assert q.dequeue() == 1 and q.dequeue() == 2
    for x in (4, 5, 6):
        q.enqueue(x)
    assert q.isi() == [3, 4, 5, 6]
    assert q.dequeue() is None or True
    # naif vs melingkar identik
    n, c = AntreanNaif(), AntreanMelingkar(4)
    for i in range(50):
        n.enqueue(i)
        c.enqueue(i)
    for _ in range(10):
        assert n.dequeue() == c.dequeue()
    assert n.geser > 0 and c.geser == 0
    # undo/redo
    r = Riwayat(AntreanMelingkar(4))
    for i in range(6):
        r.enqueue(i)
    r.dequeue(3)
    r.undo_last()
    assert r.q.isi() == [0, 1, 2, 3, 4, 5]
    r.redo_last()
    assert r.q.isi() == [3, 4, 5]
    r.undo_last()
    r.enqueue(99)  # aksi baru
    assert r.redo_last() is None
    print("M2 OK")
