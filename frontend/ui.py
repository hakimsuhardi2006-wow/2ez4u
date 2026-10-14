"""Antarmuka Tkinter 2EZ4U: menu di kiri, form + hasil di kanan, COMMAND di bawah.
Tanpa dict/set. Menu disimpan sebagai list of tuple.
"""
import os
import time
import tkinter as tk
from tkinter import ttk

from frontend.sistem import Sistem

BIRU = "#2c3e5a"
FONT_MONO = ("Consolas", 10)


def susun_menu(s):
    """Daftar menu: ("H", teks) = judul bagian, ("M", label, modul, judul, deskripsi, params, fungsi)."""
    m = []
    m.append(("H", "DATA"))
    m.append(("M", "Load", "data", "Muat data pesanan",
              "Membaca data/pesanan.csv lalu mengisi array, linked list, dan kedua antrean.",
              [], lambda v: s.muat()))

    m.append(("H", "M1 - DATA PESANAN"))
    for st, nama in (("array", "ARRAY"), ("ll", "LINKEDLIST")):
        modul = "M1 - " + ("array" if st == "array" else "linkedlist")
        m.append(("M", nama + " - LIHAT PESANAN", modul, nama + ": lihat pesanan ke-i",
                  "Membuka detail satu pesanan. Array O(1), linked list O(n).",
                  [("Indeks (mulai 0)", "0", None)],
                  lambda v, st=st: s.m1_lihat(st, v[0])))
        for jenis, label, ket in (("reguler", "REGULER", "paling belakang"),
                                  ("prioritas", "PRIORITAS", "tengah barisan"),
                                  ("vip", "VIP", "paling depan")):
            m.append(("M", nama + " - TAMBAH PESANAN " + label, modul,
                      nama + ": tambah pesanan " + label,
                      "Pesanan " + label + " disisipkan di " + ket + ".",
                      [("Nama pelanggan", "Pelanggan Baru", None)],
                      lambda v, st=st, jenis=jenis: s.m1_tambah(st, jenis, v[0])))
        m.append(("M", nama + " - HAPUS PESANAN", modul, nama + ": hapus pesanan ke-i",
                  "Mencabut satu pesanan dari barisan.",
                  [("Indeks (mulai 0)", "0", None)],
                  lambda v, st=st: s.m1_hapus(st, v[0])))

    m.append(("H", "M2 - STACK DAN QUEUE"))
    m.append(("M", "STACK - POSTFIX (MESIN KASIR)", "M2 - stack", "Stack: hitung struk lewat postfix",
              "Struk infix diubah ke postfix memakai stack operator, lalu dihitung memakai stack angka.",
              [("Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000", None)],
              lambda v: s.m2_postfix(v[0])))
    m.append(("M", "STACK - UNDO", "M2 - stack", "Stack: batalkan aksi antrean terakhir",
              "Mengambil catatan teratas tumpukan undo lalu menjalankan kebalikannya.",
              [], lambda v: s.m2_undo()))
    m.append(("M", "STACK - REDO", "M2 - stack", "Stack: kerjakan lagi aksi yang dibatalkan",
              "Mengambil catatan teratas tumpukan redo lalu mengerjakan ulang aksi aslinya.",
              [], lambda v: s.m2_redo()))
    m.append(("M", "QUEUE - ENQUEUE", "M2 - queue", "Queue: pesanan baru masuk ke belakang",
              "Menambah pesanan di ujung belakang kedua antrean sekaligus.",
              [("Nama pelanggan", "Pelanggan Baru", None)],
              lambda v: s.m2_enqueue(v[0])))
    m.append(("M", "QUEUE - DEQUEUE NAIF", "M2 - queue naif", "Queue naif: ambil dari depan dengan menggeser isi",
              "Setiap dequeue menggeser seluruh sisa elemen satu langkah ke kiri: O(n).",
              [("Berapa kali dequeue", "1", None)],
              lambda v: s.m2_dequeue_naif(v[0])))
    m.append(("M", "QUEUE - DEQUEUE CIRCULAR", "M2 - queue circular", "Queue circular: ambil dengan memajukan penunjuk",
              "Hanya penunjuk front yang maju, tidak ada elemen yang digeser: O(1).",
              [("Berapa kali dequeue", "1", None)],
              lambda v: s.m2_dequeue_circ(v[0])))

    m.append(("H", "M3 - SORT DAN SEARCH"))
    kunci = ["oid", "harga", "selesai"]
    m.append(("M", "SORT - INSERTION SORT", "M3 - insertion sort", "Sort: insertion sort, O(n^2)",
              "Stabil dan di tempat. Ditolak bila lebih dari 20.000 baris.",
              [("Jumlah baris diurutkan", "2000", None), ("Diurutkan menurut", "harga", kunci)],
              lambda v: s.m3_sort("insertion", v[0], v[1])))
    m.append(("M", "SORT - MERGE SORT", "M3 - merge sort", "Sort: merge sort, O(n log n)",
              "Stabil, mengurutkan seluruh data. Perhatikan jumlah perbandingannya.",
              [("Jumlah baris diurutkan", "2000", None), ("Diurutkan menurut", "harga", kunci)],
              lambda v: s.m3_sort("merge", v[0], v[1])))
    m.append(("M", "SEARCH - LINEAR SEARCH", "M3 - linear", "Search: linear search, O(n)",
              "Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut.",
              [("Nomor pesanan (oid)", "O-137442", None)],
              lambda v: s.m3_linear(v[0])))
    m.append(("M", "SEARCH - BINARY SEARCH", "M3 - binary", "Search: binary search, O(log n)",
              "Membuang separuh sisa daftar tiap perbandingan. Daftar terurut oid dibangun sekali.",
              [("Nomor pesanan (oid)", "O-137442", None)],
              lambda v: s.m3_binary(v[0])))
    return m


def format_waktu(detik):
    ms = detik * 1000.0
    if ms >= 1000:
        return "%.2f s" % (ms / 1000.0)
    return "%.2f ms" % ms


class App:
    def __init__(self, root, path_csv):
        self.root = root
        self.sistem = Sistem(path_csv)
        self.entri = susun_menu(self.sistem)
        self.menu_aktif = None
        self.widgets = []

        root.title("2EZ4U Food Delivery")
        root.geometry("1150x720")
        root.minsize(900, 600)

        tk.Label(root, text="2EZ4U Food Delivery", bg=BIRU, fg="white",
                 font=("Segoe UI", 13, "bold"), anchor="w", padx=12, pady=8).pack(fill="x")

        tengah = tk.Frame(root)
        tengah.pack(fill="both", expand=True)

        # ---- kiri: daftar menu ----
        kiri = tk.Frame(tengah)
        kiri.pack(side="left", fill="y")
        self.daftar = tk.Listbox(kiri, width=38, exportselection=False,
                                 activestyle="none", font=("Segoe UI", 9))
        sb = tk.Scrollbar(kiri, command=self.daftar.yview)
        self.daftar.config(yscrollcommand=sb.set)
        self.daftar.pack(side="left", fill="y")
        sb.pack(side="left", fill="y")
        for i in range(len(self.entri)):
            e = self.entri[i]
            if e[0] == "H":
                self.daftar.insert("end", e[1])
                self.daftar.itemconfig(i, foreground="#667", background="#eef")
            else:
                self.daftar.insert("end", "  " + e[1])
        self.daftar.bind("<<ListboxSelect>>", self.saat_pilih)

        # ---- kanan: judul, form, hasil ----
        kanan = tk.Frame(tengah, padx=10, pady=6)
        kanan.pack(side="left", fill="both", expand=True)
        self.judul = tk.Label(kanan, text="Pilih menu di kiri", font=("Segoe UI", 12, "bold"), anchor="w")
        self.judul.pack(fill="x")
        self.deskripsi = tk.Label(kanan, text="Mulai dengan menu Load.", fg="#555",
                                  anchor="w", justify="left", wraplength=750)
        self.deskripsi.pack(fill="x")
        self.form = tk.Frame(kanan)
        self.form.pack(fill="x", pady=6)
        hasil_frame = tk.Frame(kanan)
        hasil_frame.pack(fill="both", expand=True)
        self.hasil = tk.Text(hasil_frame, font=FONT_MONO, wrap="none", state="disabled", bg="#fafafa")
        sy = tk.Scrollbar(hasil_frame, command=self.hasil.yview)
        sx = tk.Scrollbar(hasil_frame, orient="horizontal", command=self.hasil.xview)
        self.hasil.config(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.hasil.pack(side="left", fill="both", expand=True)

        # ---- bawah: COMMAND ----
        tk.Label(root, text="COMMAND", font=("Segoe UI", 8, "bold"), anchor="w", padx=10).pack(fill="x")
        self.log = tk.Text(root, height=6, font=("Consolas", 9), state="disabled", bg="#f4f4f4")
        self.log.pack(fill="x", padx=10)
        self.status = tk.Label(root, text="Siap.", bg=BIRU, fg="white", anchor="w", padx=10)
        self.status.pack(fill="x", pady=(6, 0))

    def saat_pilih(self, event):
        pilih = self.daftar.curselection()
        if len(pilih) == 0:
            return
        e = self.entri[pilih[0]]
        if e[0] == "H":
            return
        self.tampil_menu(e)

    def tampil_menu(self, e):
        self.menu_aktif = e
        self.judul.config(text=e[3])
        self.deskripsi.config(text=e[4])
        for w in self.form.winfo_children():
            w.destroy()
        self.widgets = []
        params = e[5]
        for i in range(len(params)):
            label, default, pilihan = params[i]
            tk.Label(self.form, text=label, anchor="w", font=("Segoe UI", 9, "bold")).grid(row=0, column=i, sticky="w", padx=4)
            if pilihan is None:
                w = tk.Entry(self.form, width=38 if len(params) == 1 else 20)
                w.insert(0, default)
            else:
                w = ttk.Combobox(self.form, values=pilihan, state="readonly", width=12)
                w.set(default)
            w.grid(row=1, column=i, sticky="w", padx=4)
            w.bind("<Return>", lambda ev: self.jalankan())
            self.widgets.append(w)
        tk.Button(self.form, text="JALANKAN", bg=BIRU, fg="white", padx=16, pady=2,
                  command=self.jalankan).grid(row=1, column=len(params), padx=10)

    def jalankan(self):
        e = self.menu_aktif
        if e is None:
            return
        nilai = []
        for w in self.widgets:
            nilai.append(w.get())
        t0 = time.perf_counter()
        try:
            teks = e[6](nilai)
        except Exception as ex:
            teks = "ERROR: %s" % ex
        dt = time.perf_counter() - t0
        self.tulis(self.hasil, teks, ganti=True)
        waktu = format_waktu(dt)
        self.tulis(self.log, "%-26s -> %-20s %s" % (e[1][:26], e[2], waktu), ganti=False)
        self.status.config(text="[%s] %s" % (e[2], waktu))

    def tulis(self, widget, teks, ganti):
        widget.config(state="normal")
        if ganti:
            widget.delete("1.0", "end")
            widget.insert("1.0", teks)
        else:
            widget.insert("1.0", teks + "\n")  # terbaru di atas
        widget.config(state="disabled")


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_csv = os.path.join(root_dir, "data", "pesanan.csv")
    root = tk.Tk()
    App(root, path_csv)
    root.mainloop()
