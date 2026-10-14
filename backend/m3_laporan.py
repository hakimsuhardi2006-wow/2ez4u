"""M3: Sort & Search, semua melaporkan jumlah perbandingan.
Tanpa dict/set/sorted/.sort()/bisect/collections.
kunci = fungsi yang mengambil nilai pembanding dari satu elemen, mis. lambda r: r[4]
"""

BATAS_INSERTION = 20000


class Pencacah:
    def __init__(self):
        self.bandingan = 0
        self.pindah = 0


def insertion_sort(A, kunci, c=None):
    """Di tempat, stabil (geser hanya bila LEBIH BESAR, bukan >=). O(n^2)."""
    if c is None:
        c = Pencacah()
    if len(A) > BATAS_INSERTION:
        raise ValueError("DITOLAK: batasnya %d baris, pakai merge sort" % BATAS_INSERTION)
    for i in range(1, len(A)):
        x = A[i]
        kx = kunci(x)
        j = i - 1
        while j >= 0:
            c.bandingan += 1
            if kunci(A[j]) > kx:
                A[j + 1] = A[j]
                c.pindah += 1
                j -= 1
            else:
                break
        A[j + 1] = x
        c.pindah += 1
    return A, c


def _gabung(A, tmp, lo, mid, hi, kunci, c):
    i = lo
    j = mid + 1
    k = lo
    while i <= mid and j <= hi:
        c.bandingan += 1
        if kunci(A[i]) <= kunci(A[j]):  # <= agar stabil (kiri didahulukan)
            tmp[k] = A[i]
            i += 1
        else:
            tmp[k] = A[j]
            j += 1
        k += 1
        c.pindah += 1
    while i <= mid:  # sisa kiri jangan lupa
        tmp[k] = A[i]
        i += 1
        k += 1
        c.pindah += 1
    while j <= hi:  # sisa kanan jangan lupa
        tmp[k] = A[j]
        j += 1
        k += 1
        c.pindah += 1
    for p in range(lo, hi + 1):
        A[p] = tmp[p]


def _ms(A, tmp, lo, hi, kunci, c):
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    _ms(A, tmp, lo, mid, kunci, c)
    _ms(A, tmp, mid + 1, hi, kunci, c)
    _gabung(A, tmp, lo, mid, hi, kunci, c)


def merge_sort(A, kunci, c=None):
    """Stabil, O(n log n). Mengembalikan larik BARU; A asli tidak berubah."""
    if c is None:
        c = Pencacah()
    hasil = [None] * len(A)
    for i in range(len(A)):
        hasil[i] = A[i]
    tmp = [None] * len(A)
    _ms(hasil, tmp, 0, len(hasil) - 1, kunci, c)
    return hasil, c


def linear_search(A, target, kunci=None, c=None):
    """O(n). Tidak butuh data terurut. Return (indeks atau -1, pencacah)."""
    if c is None:
        c = Pencacah()
    for i in range(len(A)):
        c.bandingan += 1
        v = A[i] if kunci is None else kunci(A[i])
        if v == target:
            return i, c
    return -1, c


def binary_search(A, target, kunci=None, c=None):
    """O(log n). A HARUS terurut menurut kunci yang dicari. Return (indeks atau -1, pencacah)."""
    if c is None:
        c = Pencacah()
    lo = 0
    hi = len(A) - 1
    while lo <= hi:  # <=, bukan <
        mid = (lo + hi) // 2
        v = A[mid] if kunci is None else kunci(A[mid])
        c.bandingan += 1
        if v == target:
            return mid, c
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, c


# Catatan untuk UI/laporan harian: kolom t_selesai_detik bisa kosong (CANCEL/ANTRE).
# Pakai kunci mis. lambda r: r[7] if r[7] != "" else 10**9 atau saring hanya DONE.

if __name__ == "__main__":
    def acak(n, seed=12345):
        out = [None] * n
        x = seed
        for i in range(n):
            x = (x * 1103515245 + 12345) % 2147483648
            out[i] = x % 1000
        return out

    def urut_ok(A, kunci):
        for i in range(len(A) - 1):
            if kunci(A[i]) > kunci(A[i + 1]):
                return False
        return True

    k = lambda r: r[0]
    kasus = []
    kasus.append(("acak", acak(500)))
    kasus.append(("terurut", list(range(300))))
    kasus.append(("terbalik", list(range(300, 0, -1))))
    kasus.append(("duplikat", [5, 3, 5, 3, 5, 1, 1, 1, 9, 9]))
    kasus.append(("kosong", []))
    kasus.append(("satu", [7]))
    for nama, data in kasus:
        baris = [(v, i) for i, v in enumerate(data)]  # (kunci, urutan asli)
        a, _ = insertion_sort(list(baris), k)
        m, _ = merge_sort(baris, k)
        assert urut_ok(a, k) and urut_ok(m, k), nama
        assert a == m, "hasil kedua sort harus identik: " + nama  # identik = sama-sama stabil
        for i in range(len(m) - 1):  # stabil: kunci sama -> urutan asli naik
            if m[i][0] == m[i + 1][0]:
                assert m[i][1] < m[i + 1][1], "tidak stabil: " + nama

    # binary search: tengah, kiri, kanan, tidak ada, kosong
    A = [2, 4, 6, 8, 10, 12, 14]
    assert binary_search(A, 8)[0] == 3
    assert binary_search(A, 2)[0] == 0
    assert binary_search(A, 14)[0] == 6
    assert binary_search(A, 7)[0] == -1
    assert binary_search([], 1)[0] == -1
    assert linear_search(A, 12)[0] == 5 and linear_search(A, 99)[0] == -1

    # pola: n dilipatduakan -> insertion ~4x, merge ~2x perbandingan
    print("n      insertion      merge")
    for n in (1000, 2000, 4000):
        d = [(v, i) for i, v in enumerate(acak(n))]
        _, ci = insertion_sort(list(d), k)
        _, cm = merge_sort(d, k)
        print(n, ci.bandingan, cm.bandingan)

    try:
        insertion_sort([0] * 20001, lambda r: r)
        assert False
    except ValueError:
        pass
    print("M3 OK")
