import hashlib

def string_to_binary(text):
    """Mengubah teks menjadi representasi biner (8-bit per karakter)"""
    return ' '.join(format(ord(c), '08b') for c in text)

def sha256_hash_bin(text):
    """Menghasilkan hash SHA-256 dalam bentuk Hex dan Biner (256-bit)"""
    hex_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    bin_hash = bin(int(hex_hash, 16))[2:].zfill(256)
    return hex_hash, bin_hash

def format_bin_spaced(bin_str, step=8):
    """Memecah string biner panjang dengan spasi setiap 'step' karakter"""
    return ' '.join(bin_str[i:i+step] for i in range(0, len(bin_str), step))

def generate_y_1bit_diff(text):
    """Membuat teks Y yang berbeda tepat 1 bit dari teks X"""
    if not text:
        return text
    char_list = list(text)
    char_list[0] = chr(ord(char_list[0]) ^ 1)
    return "".join(char_list)

def print_difference_map(bin_A, bin_B):
    """Mencetak peta perbandingan bit baris demi baris (64 bit per baris)"""
    print("\n[ PETA PERBEDAAN BIT ]")
    print("Keterangan: Tanda '^' di baris 'Beda' menunjukkan posisi bit yang berubah.")
    chunk_size = 64
    
    for i in range(0, 256, chunk_size):
        chunk_A = bin_A[i:i+chunk_size]
        chunk_B = bin_B[i:i+chunk_size]
        
        spaced_A = format_bin_spaced(chunk_A)
        spaced_B = format_bin_spaced(chunk_B)
        
        # Membuat string indikator perbedaan ('^')
        diff_str = ""
        for a, b in zip(spaced_A, spaced_B):
            if a == ' ':
                diff_str += ' ' # Pertahankan spasi pemisah
            elif a != b:
                diff_str += '^' # Beri tanda jika bit berbeda
            else:
                diff_str += ' ' # Kosongkan jika bit sama
                
        print(f"\n>> Bit ke-{i+1:03d} sampai {i+chunk_size:03d}:")
        print(f"h(X) : {spaced_A}")
        print(f"h(Y) : {spaced_B}")
        print(f"Beda : {diff_str}")

def execute_avalanche_test(x):
    """Fungsi utama eksekusi"""
    print("=" * 85)
    y = generate_y_1bit_diff(x)
    
    print(f"Input X = '{x}' -> Biner: {string_to_binary(x)}")
    print(f"Input Y = '{y}' -> Biner: {string_to_binary(y)}")
    print("-" * 85)
    
    hex_A, bin_A = sha256_hash_bin(x)
    hex_B, bin_B = sha256_hash_bin(y)
    
    print(f"h(X) [Hex] = {hex_A}")
    print(f"h(Y) [Hex] = {hex_B}")
    
    # Panggil fungsi pencetak peta
    print_difference_map(bin_A, bin_B)
    print("-" * 85)
    
    # Hitung total perbedaan
    jBeda = sum(1 for i in range(256) if bin_A[i] != bin_B[i])
    persentase = (jBeda / 256) * 100
    
    print(f"Total bit yang berbeda (jBeda) = {jBeda} bit dari 256 bit")
    print(f"Persentase Perubahan Output    = {persentase:.2f}%")
    print("=" * 85)

# ==========================================
# MAIN PROGRAM (MODE INTERAKTIF)
# ==========================================
if __name__ == "__main__":
    print("PROGRAM PETA AVALANCHE EFFECT SHA-256")
    while True:
        user_input = input("\nMasukkan Input X (ketik 'exit' untuk keluar): ")
        if user_input.lower() == 'exit':
            break
        if len(user_input) > 0:
            execute_avalanche_test(user_input)