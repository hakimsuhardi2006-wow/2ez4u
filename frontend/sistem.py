"""Lapisan penghubung antara UI dan backend M1-M3.
Tanpa Tkinter supaya mudah diuji. Tanpa dict/set/sorted/.sort().
Setiap metode m*_ mengembalikan teks hasil untuk ditampilkan di UI.
"""
import time

from backend.csv_loader import (muat_pesanan, jam, OID, PELANGGAN, RESTO, MENU,
                                HARGA, PRIORITAS, T_MASUK, T_SELESAI, STATUS)
from backend.m1_pesanan import Array, LinkList
from backend.m2_antrean import ke_postfix, hitung, AntreanNaif, AntreanMelingkar, Riwayat
from backend.m3_laporan import (insertion_sort, merge_sort, linear_search,
                                binary_search, BATAS_INSERTION)


def rupiah(n):
    s = str(int(n))
    hasil = ""
    hitung_digit = 0
    for i in range(len(s) - 1, -1, -1):
        hasil = s[i] + hasil
        hitung_digit += 1
        if hitung_digit % 3 == 0 and i != 0:
            hasil = "." + hasil
    return "Rp " + hasil


def angka(n):
    return rupiah(n)[3:]


def detail(r):
    return ("oid       : %s\npelanggan : %s\nresto     : %s\nmenu      : %s\n"
            "harga     : %s\nprioritas : %d\nmasuk     : %s\nselesai   : %s\nstatus    : %s") % (
        r[OID], r[PELANGGAN], r[RESTO], r[MENU], angka(r[HARGA]), r[PRIORITAS],
        jam(r[T_MASUK]), jam(r[T_SELESAI]), r[STATUS])


def tabel(rows, maks=10):
    baris = ["%-4s %-10s %-24s %-8s %-9s %-9s" % ("#", "oid", "pelanggan", "harga", "masuk", "selesai")]
    n = len(rows)
    if n > maks:
        n = maks
    for i in range(n):
        r = rows[i]
        baris.append("%-4d %-10s %-24s %-8s %-9s %-9s" % (
            i + 1, r[OID], r[PELANGGAN][:24], angka(r[HARGA]), jam(r[T_MASUK]), jam(r[T_SELESAI])))
    if len(rows) > maks:
        baris.append("... dan %d baris lainnya" % (len(rows) - maks))
    return "\n".join(baris)


def kunci_fn(nama):
    if nama == "oid":
        return lambda r: r[OID]
    if nama == "harga":
        return lambda r: r[HARGA]
    return lambda r: r[T_SELESAI] if r[T_SELESAI] is not None else 10 ** 9


class Sistem:
    def __init__(self, path):
        self.path = path
        self.data = None
        self.oid_terurut = None

    def _perlu(self):
        if self.data is None:
            raise RuntimeError("Data belum dimuat. Pilih menu Load dulu.")

    # ---------------- DATA ----------------
    def muat(self):
        data, t = muat_pesanan(self.path)
        self.data = data
        self.arr = Array()
        self.ll = LinkList()
        self.naif = AntreanNaif()
        self.circ = AntreanMelingkar(1024)
        self.riwayat = Riwayat(self.circ)
        for r in data:
            self.arr.append(r)
            self.ll.append(r)
            if r[STATUS] == "ANTRE":
                self.naif.enqueue(r)
                self.circ.enqueue(r)
        self.next_id = len(data) + 1
        self.oid_terurut = None
        return ("%s baris dibaca dalam %.2f detik.\nArray: %s | LinkedList: %s\n"
                "Antrean (status ANTRE): naif %s, circular %s") % (
            angka(len(data)), t, angka(len(self.arr)), angka(len(self.ll)),
            angka(len(self.naif)), angka(len(self.circ)))

    def _baru(self, nama, prioritas):
        oid = "O-%06d" % self.next_id
        self.next_id += 1
        t = time.localtime()
        detik = t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec
        return (oid, nama, "kafe-teknik", "roti-bakar", 12000, prioritas, detik, None, "ANTRE")

    # ---------------- M1 ----------------
    def _struktur(self, st):
        if st == "array":
            return self.arr, "geser", "elemen digeser/disalin"
        return self.ll, "telusur", "simpul ditelusuri"

    def m1_lihat(self, st, idx):
        self._perlu()
        s, attr, ket = self._struktur(st)
        i = int(idx)
        sebelum = getattr(s, attr)
        r = s.get(i)
        d = getattr(s, attr) - sebelum
        return "Pesanan indeks %d dari %s (%s)\n%d %s\n\n%s" % (
            i, angka(len(s)), st, d, ket, detail(r))

    def m1_tambah(self, st, jenis, nama):
        self._perlu()
        nama = nama.strip()
        if nama == "":
            raise ValueError("Nama pelanggan tidak boleh kosong")
        s, attr, ket = self._struktur(st)
        sebelum = getattr(s, attr)
        n = len(s)
        if jenis == "reguler":
            r = self._baru(nama, 3)
            s.tambah_reguler(r)
            pos = n
        elif jenis == "prioritas":
            r = self._baru(nama, 2)
            s.tambah_prioritas(r)
            pos = n // 2
        else:
            r = self._baru(nama, 1)
            s.tambah_vip(r)
            pos = 0
        d = getattr(s, attr) - sebelum
        return "%s masuk di indeks %d. Panjang sekarang %s.\n%s %s\n\n%s" % (
            r[OID], pos, angka(len(s)), angka(d), ket, detail(r))

    def m1_hapus(self, st, idx):
        self._perlu()
        s, attr, ket = self._struktur(st)
        i = int(idx)
        sebelum = getattr(s, attr)
        r = s.hapus(i)
        d = getattr(s, attr) - sebelum
        return "Pesanan indeks %d dihapus. Panjang sekarang %s.\n%s %s\n\n%s" % (
            i, angka(len(s)), angka(d), ket, detail(r))

    # ---------------- M2 ----------------
    def m2_postfix(self, ekspresi):
        postfix = ke_postfix(ekspresi)
        total = hitung(postfix)
        if total is not None and total == int(total):
            total = int(total)
        return "Struk  : %s\nPostfix: %s\nTOTAL  : %s" % (
            ekspresi, " ".join(postfix), rupiah(total))

    def _status_riwayat(self):
        return "Antrean: naif %s, circular %s. Tumpukan undo %d, redo %d." % (
            angka(len(self.naif)), angka(len(self.circ)),
            len(self.riwayat.undo), len(self.riwayat.redo))

    def m2_undo(self):
        self._perlu()
        aksi = self.riwayat.undo_last()
        if aksi is None:
            return "Tumpukan undo kosong, tidak ada yang dibatalkan.\n" + self._status_riwayat()
        jenis, daftar = aksi
        if jenis == "ENQUEUE":
            ket = "%s dikeluarkan lagi dari belakang." % daftar[0][OID]
        else:
            ket = "%d pesanan dikembalikan ke DEPAN antrean circular." % len(daftar)
        return "Pembatalan %s: %s\n%s" % (jenis.lower(), ket, self._status_riwayat())

    def m2_redo(self):
        self._perlu()
        aksi = self.riwayat.redo_last()
        if aksi is None:
            return "Tumpukan redo kosong, tidak ada yang diulang.\n" + self._status_riwayat()
        jenis, daftar = aksi
        return "%s dikerjakan ulang (%d pesanan).\n%s" % (jenis.lower(), len(daftar), self._status_riwayat())

    def m2_enqueue(self, nama):
        self._perlu()
        nama = nama.strip()
        if nama == "":
            raise ValueError("Nama pelanggan tidak boleh kosong")
        r = self._baru(nama, 3)
        self.naif.enqueue(r)
        self.riwayat.enqueue(r)  # circular + catat undo, kosongkan redo
        return "%s masuk paling belakang pada KEDUA antrean.\n%s\n\n%s" % (
            r[OID], self._status_riwayat(), detail(r))

    def m2_dequeue_naif(self, k):
        self._perlu()
        k = int(k)
        sebelum = self.naif.geser
        keluar = []
        for _ in range(k):
            x = self.naif.dequeue()
            if x is None:
                break
            keluar.append(x)
        geser = self.naif.geser - sebelum
        return "%d pesanan keluar | %s elemen digeser\nSisa antrean naif %s.\n\n%s" % (
            len(keluar), angka(geser), angka(len(self.naif)), tabel(keluar, 5))

    def m2_dequeue_circ(self, k):
        self._perlu()
        k = int(k)
        keluar = self.riwayat.dequeue(k)
        return "%d pesanan keluar | 0 elemen digeser\nSisa antrean circular %s. Tumpukan undo %d.\n\n%s" % (
            len(keluar), angka(len(self.circ)), len(self.riwayat.undo), tabel(keluar, 5))

    # ---------------- M3 ----------------
    def m3_sort(self, jenis, jumlah, kunci):
        self._perlu()
        n = int(jumlah)
        if n < 1 or n > len(self.data):
            raise ValueError("Jumlah harus 1 sampai %d" % len(self.data))
        if jenis == "insertion" and n > BATAS_INSERTION:
            return "DITOLAK: batas insertion sort %s baris. Pakai merge sort untuk data besar." % angka(BATAS_INSERTION)
        A = self.data[:n]
        k = kunci_fn(kunci)
        if jenis == "insertion":
            A, c = insertion_sort(A, k)
        else:
            A, c = merge_sort(A, k)
        return "%s pesanan terurut menurut %s\n%s perbandingan, %s pemindahan\n\n%s" % (
            angka(n), kunci, angka(c.bandingan), angka(c.pindah), tabel(A, 10))

    def m3_linear(self, oid):
        self._perlu()
        oid = oid.strip().upper()
        i, c = linear_search(self.data, oid, lambda r: r[OID])
        if i < 0:
            return "%s tidak ditemukan.\n%s perbandingan (seluruh data diperiksa)." % (oid, angka(c.bandingan))
        return "Ditemukan pada indeks %s.\n%s perbandingan.\n\n%s" % (
            angka(i), angka(c.bandingan), detail(self.data[i]))

    def m3_binary(self, oid):
        self._perlu()
        oid = oid.strip().upper()
        catatan = ""
        if self.oid_terurut is None:
            t0 = time.perf_counter()
            self.oid_terurut, cs = merge_sort(self.data, lambda r: r[OID])
            catatan = "Daftar terurut oid dibangun sekali dengan merge sort: %.2f ms (%s perbandingan).\n" % (
                (time.perf_counter() - t0) * 1000, angka(cs.bandingan))
        i, c = binary_search(self.oid_terurut, oid, lambda r: r[OID])
        if i < 0:
            return "%s%s tidak ditemukan.\n%d perbandingan." % (catatan, oid, c.bandingan)
        return "%sDitemukan pada baris ke-%s dari %s.\n%d perbandingan, bandingkan dengan linear search.\n\n%s" % (
            catatan, angka(i + 1), angka(len(self.oid_terurut)), c.bandingan, detail(self.oid_terurut[i]))
