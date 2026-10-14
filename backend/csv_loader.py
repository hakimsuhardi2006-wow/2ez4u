"""Pembaca CSV buatan sendiri. Tanpa dict/set/csv module.
Tiap baris pesanan menjadi TUPLE:
  (oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status)
t_selesai bernilai None bila kosong (CANCEL/ANTRE).
Nama seperti "Dr. Raina Firmansyah, S.I.Kom" mengandung koma, jadi
baris yang memuat tanda kutip diurai karakter per karakter.
"""
import time

OID, PELANGGAN, RESTO, MENU, HARGA, PRIORITAS, T_MASUK, T_SELESAI, STATUS = range(9)


def pecah_baris(baris):
    """Pecah satu baris CSV menjadi list kolom, menghormati tanda kutip."""
    if '"' not in baris:
        return baris.split(",")  # jalur cepat: sebagian besar baris
    kolom = []
    saat_ini = ""
    dalam_kutip = False
    i = 0
    n = len(baris)
    while i < n:
        ch = baris[i]
        if dalam_kutip:
            if ch == '"':
                if i + 1 < n and baris[i + 1] == '"':  # "" = kutip literal
                    saat_ini += '"'
                    i += 1
                else:
                    dalam_kutip = False
            else:
                saat_ini += ch
        else:
            if ch == '"':
                dalam_kutip = True
            elif ch == ",":
                kolom.append(saat_ini)
                saat_ini = ""
            else:
                saat_ini += ch
        i += 1
    kolom.append(saat_ini)
    return kolom


def _int_atau_none(s):
    s = s.strip()
    if s == "":
        return None
    return int(s)


def muat_pesanan(path):
    """Baca CSV pesanan -> (list of tuple, waktu_detik). Header dilewati."""
    mulai = time.perf_counter()
    hasil = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        header = True
        for baris in f:
            baris = baris.rstrip("\r\n")
            if header:
                header = False
                continue
            if baris == "":
                continue
            k = pecah_baris(baris)
            if len(k) < 9:
                continue  # baris rusak dilewati
            hasil.append((
                k[0].strip(),
                k[1].strip(),
                k[2].strip(),
                k[3].strip(),
                int(k[4]),
                int(k[5]),
                int(k[6]),
                _int_atau_none(k[7]),
                k[8].strip(),
            ))
    return hasil, time.perf_counter() - mulai


def jam(detik):
    """Detik -> 'HH:MM:SS'. None -> '-'."""
    if detik is None:
        return "-"
    h = detik // 3600
    m = (detik % 3600) // 60
    s = detik % 60
    return "%02d:%02d:%02d" % (h, m, s)


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "data/pesanan.csv"
    data, t = muat_pesanan(path)
    print("Terbaca %d baris dalam %.2f detik" % (len(data), t))
    print("Baris pertama :", data[0])
    print("Baris terakhir:", data[len(data) - 1])
    antre = 0
    for r in data:
        if r[STATUS] == "ANTRE":
            antre += 1
    print("Berstatus ANTRE:", antre)
