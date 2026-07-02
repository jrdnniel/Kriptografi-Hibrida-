import os
import hashlib
from io import BytesIO
from PIL import Image
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util import Padding

# ==========================================
# 1. PERTUKARAN KUNCI (DIFFIE-HELLMAN SIMULATION)
# ==========================================
class DiffieHellman:
    def __init__(self):
        # Menggunakan grup prima standar (RFC 3526 - 1536-bit MODP Group)
        self.p = int("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
                     "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
                     "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
                     "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
                     "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
                     "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
                     "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
                     "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
                     "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
                     "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
                     "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16)
        self.g = 2
        
    def generate_private_key(self):
        # Mengembalikan integer acak yang berfungsi sebagai private key
        return int.from_bytes(os.urandom(32), byteorder='big') % (self.p - 2) + 2

    def generate_public_key(self, private_key):
        # Formula: Public = (g ^ private) % p
        return pow(self.g, private_key, self.p)

    def compute_shared_secret(self, private_key, remote_public_key):
        # Formula: Shared = (remote_public ^ private) % p
        shared_secret_int = pow(remote_public_key, private_key, self.p)
        # Turunkan menjadi kunci 256-bit menggunakan SHA256 untuk digunakan di AES
        return hashlib.sha256(str(shared_secret_int).encode()).digest()


# ==========================================
# 2. DIGITAL SIGNATURE & ASYMMETRIC ENCRYPTION (RSA)
# ==========================================
class RSAManager:
    @staticmethod
    def generate_keypair():
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    @staticmethod
    def sign_message(message_bytes, private_key_pem):
        key = RSA.import_key(private_key_pem)
        # Hashing pesan dengan SHA256 sesuai instruksi soal
        hashed_msg = SHA256.new(message_bytes)
        signature = pkcs1_15.new(key).sign(hashed_msg)
        return signature

    @staticmethod
    def verify_signature(message_bytes, signature, public_key_pem):
        key = RSA.import_key(public_key_pem)
        hashed_msg = SHA256.new(message_bytes)
        try:
            pkcs1_15.new(key).verify(hashed_msg, signature)
            return True
        except (ValueError, TypeError):
            return False


# ==========================================
# 3. SYMMETRIC ENCRYPTION (AES-256 CBC)
# ==========================================
class AESManager:
    @staticmethod
    def encrypt(plain_bytes, key_bytes):
        # Menggunakan mode CBC dengan Initialization Vector (IV) acak 16 byte
        iv = os.urandom(16)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # Menambahkan padding PKCS7 agar panjang data kelipatan 16 byte
        padded_data = Padding.pad(plain_bytes, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        # Kembalikan IV diletakkan di depan ciphertext agar mudah dipisahkan saat dekripsi
        return iv + ciphertext

    @staticmethod
    def decrypt(encrypted_bytes, key_bytes):
        iv = encrypted_bytes[:16]
        actual_ciphertext = encrypted_bytes[16:]
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(actual_ciphertext)
        return Padding.unpad(decrypted_padded, AES.block_size)


# ==========================================
# 4. STEGANOGRAFI (MODIFIKASI LSB)
# ==========================================
class LSBSteganography:
    @staticmethod
    def encode(image_path, data_bytes, output_path):
        img = Image.open(image_path).convert('RGB')
        pixels = list(img.getdata())
        
        # Tambahkan marker panjang data di 4 byte pertama agar penerima tahu kapan harus berhenti membaca
        data_len = len(data_bytes)
        header = data_len.to_bytes(4, byteorder='big')
        full_payload = header + data_bytes
        
        # Ubah payload byte menjadi deretan bit string
        bit_string = "".join(f"{b:08b}" for b in full_payload)
        
        if len(bit_string) > len(pixels) * 3:
            raise ValueError(f"Ukuran payload terlalu besar ({len(bit_string)} bits) untuk gambar ini.")
            
        new_pixels = []
        bit_idx = 0
        payload_len = len(bit_string)
        
        for pixel in pixels:
            r, g, b = pixel
            channels = [r, g, b]
            
            for i in range(3):
                if bit_idx < payload_len:
                    # Modifikasi Bit Terendah (LSB) dengan bit payload
                    channels[i] = (channels[i] & ~1) | int(bit_string[bit_idx])
                    bit_idx += 1
            
            new_pixels.append(tuple(channels))
            
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(new_pixels)
        new_img.save(output_path, "PNG") # Harus disimpan dalam format lossless (PNG)
        print(f"[Stegano] Berhasil menyisipkan {data_len} byte ke dalam {output_path}")

    @staticmethod
    def decode(stego_image_path):
        img = Image.open(stego_image_path)
        pixels = list(img.getdata())
        
        # Ekstrak semua bit dari LSB gambar
        extracted_bits = []
        for pixel in pixels:
            for channel in pixel[:3]:
                extracted_bits.append(str(channel & 1))
                
        full_bit_string = "".join(extracted_bits)
        
        # Baca 4 byte pertama (32 bit) untuk mendapatkan panjang payload asli
        header_bits = full_bit_string[:32]
        header_bytes = int(header_bits, 2).to_bytes(4, byteorder='big')
        payload_len = int.from_bytes(header_bytes, byteorder='big')
        
        # Ekstrak data utama berdasarkan panjang payload tersebut
        start_bit = 32
        end_bit = start_bit + (payload_len * 8)
        payload_bits = full_bit_string[start_bit:end_bit]
        
        # Konversi kembali bit string menjadi bytes
        payload_bytes = bytearray()
        for i in range(0, len(payload_bits), 8):
            payload_bytes.append(int(payload_bits[i:i+8], 2))
            
        return bytes(payload_bytes)


# ==========================================
# 5. INTEGRASI MAIN WORKFLOW (SIMULASI ALICE & BOB)
# ==========================================
if __name__ == "__main__":
    print("=== MEMULAI SIMULASI SISTEM KRIPTOGRAFI HIBRIDA + STEGANOGRAFI ===\n")
    
    # 0. Pembuatan Dummy Gambar Cover untuk Keperluan Steganografi
    cover_img_path = "cover_input.png"
    stego_img_path = "stego_output.png"
    img = Image.new('RGB', (300, 300), color = (73, 109, 137))
    img.save(cover_img_path)
    
    # Inisialisasi Data Rahasia
    pesan_rahasia = "Nilai A untuk Mata Kuliah Kriptografi Terapan - Mikroskil 2026!".encode('utf-8')
    print(f"[Pesan Asli]: {pesan_rahasia.decode('utf-8')}\n")
    
    # --- PROSES GENERASI KUNCI ---
    # Generate Keypair RSA Alice (Untuk Tanda Tangan Digital)
    alice_private_rsa, alice_public_rsa = RSAManager.generate_keypair()
    
    # Inisialisasi Diffie-Hellman untuk Alice & Bob
    dh_alice = DiffieHellman()
    dh_bob = DiffieHellman()
    
    # Generate Kunci Privat & Publik DH masing-masing
    priv_a = dh_alice.generate_private_key()
    pub_a = dh_alice.generate_public_key(priv_a)
    
    priv_b = dh_bob.generate_private_key()
    pub_b = dh_bob.generate_public_key(priv_b)
    
    # Hitung Shared Secret (Kunci Simetris AES)
    aes_key_alice = dh_alice.compute_shared_secret(priv_a, pub_b)
    aes_key_bob = dh_bob.compute_shared_secret(priv_b, pub_a)
    
    assert aes_key_alice == aes_key_bob, "Gagal! Shared Secret Key tidak sinkron."
    print(f"[Diffie-Hellman] Berhasil melakukan pertukaran kunci.")
    print(f"-> Shared Key (AES): {aes_key_alice.hex()}\n")
    
    # ==========================================
    # SISI PENGIRIM (ALICE)
    # ==========================================
    print("--- SISI PENGIRIM (ALICE) ---")
    
    # 1. Buat Digital Signature menggunakan SHA256 + RSA Private Key
    signature = RSAManager.sign_message(pesan_rahasia, alice_private_rsa)
    print(f"[RSA] Digital Signature berhasil dibuat (SHA256).")
    print(f"-> Signature (16 byte pertama): {signature[:16].hex()}...")
    
    # 2. Gabungkan Pesan Asli dengan Signature agar terenkripsi bersama
    # Format: [Panjang Signature (4 byte)] + [Signature] + [Pesan Asli]
    payload_to_encrypt = len(signature).to_bytes(4, byteorder='big') + signature + pesan_rahasia
    
    # 3. Enkripsi Gabungan Data menggunakan AES-256 CBC
    ciphertext_aes = AESManager.encrypt(payload_to_encrypt, aes_key_alice)
    print(f"[AES] Data + Signature berhasil dienkripsi.")
    print(f"-> Ciphertext AES (16 byte pertama): {ciphertext_aes[:16].hex()}...")
    
    # 4. Sisipkan Ciphertext ke dalam Gambar Menggunakan LSB Steganografi
    LSBSteganography.encode(cover_img_path, ciphertext_aes, stego_img_path)
    print("\n" + "="*50 + "\n")
    
    # ==========================================
    # SISI PENERIMA (BOB)
    # ==========================================
    print("--- SISI PENERIMA (BOB) ---")
    
    # 1. Ekstrak data dari Gambar Stego (Mendapatkan Ciphertext AES)
    extracted_ciphertext = LSBSteganography.decode(stego_img_path)
    print(f"[Stegano] Berhasil mengekstrak ciphertext dari gambar.")
    
    # 2. Dekripsi Ciphertext menggunakan Kunci AES dari hasil Diffie-Hellman
    decrypted_payload = AESManager.decrypt(extracted_ciphertext, aes_key_bob)
    print(f"[AES] Proses Dekripsi sukses.")
    
    # 3. Parsing Data (Pisahkan kembali Tanda Tangan dan Pesan Asli)
    sig_len = int.from_bytes(decrypted_payload[:4], byteorder='big')
    extracted_signature = decrypted_payload[4:4+sig_len]
    extracted_message = decrypted_payload[4+sig_len:]
    
    print(f"[Parsing] Pesan yang diekstrak: {extracted_message.decode('utf-8')}")
    
    # 4. Verifikasi Keaslian Pesan Menggunakan Kunci Publik RSA Alice
    is_valid = RSAManager.verify_signature(extracted_message, extracted_signature, alice_public_rsa)
    
    print("\n--- HASIL VERIFIKASI AKHIR ---")
    if is_valid:
        print(" STATUS: INTEGRITAS TERJAMIN & SAH (VALID)")
        print(" Kesimpulan: Pesan tidak dimodifikasi dan benar-benar dikirim oleh Alice.")
    else:
        print(" STATUS: DATA CORRUPTED ATAU UNVERIFIED (INVALID)")
        
    # Membersihkan dummy file yang terbuat otomatis oleh script
    if os.path.exists(cover_img_path): os.remove(cover_img_path)
    if os.path.exists(stego_img_path): os.remove(stego_img_path)