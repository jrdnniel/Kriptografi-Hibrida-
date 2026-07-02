import hashlib

def sha256_hex(text):
    """Menghitung SHA-256 dari string input dan mengembalikan hex."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def hex_to_binary_256(hex_str):
    """Konversi hex SHA-256 (64 karakter) ke string biner 256 bit."""
    return bin(int(hex_str, 16))[2:].zfill(256)

def hitung_bit_berbeda(bin_a, bin_b):
    """Hitung jumlah posisi bit yang berbeda antara dua string biner."""
    return sum(1 for a, b in zip(bin_a, bin_b) if a != b)

def tampilkan_biner(label, bin_str, bin_other, tampilkan_beda=True):
    """Tampilkan 256 bit dengan penanda perbedaan."""
    result = f"{label}: "
    for i, (b, bo) in enumerate(zip(bin_str, bin_other)):
        result += b
        if (i + 1) % 8 == 0 and i < 255:
            result += " "
    return result

def run_eksperimen(x, y):
    print("=" * 70)
    print(f"  INPUT X : '{x}'")
    print(f"  INPUT Y : '{y}'")
    print("=" * 70)

    # Hitung hash
    hx = sha256_hex(x)
    hy = sha256_hex(y)
    print(f"\n[SHA-256 HEX]")
    print(f"  h(X) = {hx}")
    print(f"  h(Y) = {hy}")

    # Konversi ke biner 256-bit
    bx = hex_to_binary_256(hx)
    by = hex_to_binary_256(hy)

    print(f"\n[REPRESENTASI BINER 256-BIT]")
    print(f"  A = h(X) dalam biner:")
    # Tampilkan per 32 bit per baris
    for i in range(0, 256, 32):
        print(f"       Bit {i+1:3d}-{i+32:3d}: {bx[i:i+32]}")
    print(f"  B = h(Y) dalam biner:")
    for i in range(0, 256, 32):
        print(f"       Bit {i+1:3d}-{i+32:3d}: {by[i:i+32]}")

    # Hitung perbedaan bit
    j_beda = 0
    posisi_beda = []
    print(f"\n[PENGECEKAN BIT KE-1 SAMPAI KE-256]")
    for i in range(256):
        if bx[i] != by[i]:
            j_beda += 1
            posisi_beda.append(i + 1)

    persentase = (j_beda / 256) * 100
    print(f"  Jumlah bit berbeda  : {j_beda} dari 256")
    print(f"  Persentase perbedaan: {persentase:.2f}%")
    print(f"  Batas minimal teori : 128 bit (50%)")

    if j_beda >= 128:
        print(f"\n  ✓ AVALANCHE EFFECT TERBUKTI! ({j_beda} bit ≥ 128 bit)")
    else:
        print(f"\n  ✗ Kurang dari 50% bit berbeda ({j_beda} bit < 128 bit)")

    print(f"\n  Posisi bit berbeda (10 pertama):")
    print(f"  {posisi_beda[:10]} ...")
    print()
    return hx, hy, bx, by, j_beda, persentase, posisi_beda

def main():
    print("\n" + "=" * 70)
    print("       DEMONSTRASI AVALANCHE EFFECT — SHA-256")
    print("       Prinsip: 1 bit input berbeda → ≥50% output berbeda")
    print("=" * 70)

    print("\n[MODE 1: EKSPERIMEN OTOMATIS]")
    eksperimen = [
        ("b", "c"),
        ("hello", "Hello"),
        ("abc", "abd"),
        ("password", "password1"),
        ("0", "1"),
    ]
    for x, y in eksperimen:
        run_eksperimen(x, y)

    print("\n" + "=" * 70)
    print("[MODE 2: INPUT KUSTOM]")
    print("=" * 70)
    while True:
        print("\nMasukkan dua teks untuk dibandingkan (atau 'q' untuk keluar):")
        x = input("  Input X: ").strip()
        if x.lower() == 'q':
            break
        y = input("  Input Y: ").strip()
        if y.lower() == 'q':
            break
        run_eksperimen(x, y)

if __name__ == "__main__":
    main()