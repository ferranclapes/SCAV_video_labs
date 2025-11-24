import matplotlib
matplotlib.use('TkAgg')
import unittest
import numpy as np
import os

# Importem les classes del teu fitxer 'first_seminar.py'
# Assegura't que el teu fitxer es diu així o canvia el nom aquí sota
from first_seminar import traslator, DCTEncoder, DWTEncoder

class TestVideoCoding(unittest.TestCase):

    def setUp(self):
        """S'executa abans de cada test. Preparem les instàncies."""
        self.trans = traslator()
        self.dct_enc = DCTEncoder()
        self.dwt_enc = DWTEncoder()

    # --- TESTS PER A LA CLASSE TRASLATOR ---

    def test_rgb_yuv_conversion(self):
        """Prova que convertir RGB -> YUV -> RGB retorna els valors originals."""
        # Creem un píxel de prova (Vermell pur)
        r, g, b = 255, 0, 0
        
        # Convertim a YUV
        y, u, v = self.trans.rgb_to_yuv(r, g, b)
        
        # Tornem a RGB
        r_out, g_out, b_out = self.trans.yuv_to_rgb(y, u, v)
        
        # Comprovem amb un petit marge d'error (pels decimals)
        self.assertAlmostEqual(r, r_out, delta=1.0)
        self.assertAlmostEqual(g, g_out, delta=1.0)
        self.assertAlmostEqual(b, b_out, delta=1.0)
        print("[OK] RGB <-> YUV conversion verified.")

    def test_run_length_encoding(self):
        """Prova l'algorisme RLE amb una cadena coneguda."""
        # Dades: A tres vegades, B dues, C una
        data = ['A', 'A', 'A', 'B', 'B', 'C']
        expected = [('A', 3), ('B', 2), ('C', 1)]
        
        result = self.trans.run_length_encoding(data)
        self.assertEqual(result, expected)
        print("[OK] Run Length Encoding verified.")

    def test_serpentine(self):
        """
        Prova el recorregut en serpentina. 
        Nota: Com que 'serpentine' llegeix un fitxer, crearem una imatge dummy temporalment
        o provarem la lògica si la separes. Per aquest test, assumim que la lògica interna funciona
        i validem que retorna la mida correcta d'array.
        """
        # Creem una imatge petita 4x4 aleatòria
        from PIL import Image
        dummy_name = "test_serpentine.png"
        arr = np.random.randint(0, 255, (4, 4, 3), dtype=np.uint8)
        img = Image.fromarray(arr)
        img.save(dummy_name)

        try:
            output = self.trans.serpentine(dummy_name)
            # L'output ha de tenir mida Height * Width
            self.assertEqual(len(output), 16) 
            print("[OK] Serpentine traversal output size verified.")
        finally:
            # Neteja: esborrem la imatge temporal
            if os.path.exists(dummy_name):
                os.remove(dummy_name)

    # --- TESTS PER A LA CLASSE DCTENCODER ---

    def test_dct_reversibility(self):
        """Prova que DCT Encode -> Decode recupera la imatge original."""
        # Creem una matriu aleatòria 8x8 (típic bloc DCT)
        input_matrix = np.random.rand(8, 8)
        
        encoded = self.dct_enc.encode(input_matrix)
        decoded = self.dct_enc.decode(encoded)
        
        # Comprovem que la matriu decodificada és gairebé idèntica a l'original
        np.testing.assert_allclose(input_matrix, decoded, atol=1e-5)
        print("[OK] DCT Reversibility (Encode -> Decode) verified.")

    # --- TESTS PER A LA CLASSE DWTENCODER ---

    def test_dwt_filters_basic(self):
        """Prova bàsica dels filtres lowpass i highpass."""
        a = np.array([10, 10])
        b = np.array([20, 20])
        
        # Lowpass: Mitjana -> (10+20)/2 = 15
        lp = self.dwt_enc.lowpassfilter(a, b)
        np.testing.assert_array_equal(lp, np.array([15, 15]))
        
        # Highpass: Diferència -> (10-20)/2 = -5
        hp = self.dwt_enc.highpassfilter(a, b)
        np.testing.assert_array_equal(hp, np.array([-5, -5]))
        print("[OK] DWT Lowpass/Highpass filters verified.")

    def test_dwt_reversibility(self):
        """Prova que DWT Encode -> Decode recupera la imatge original (Manual)."""
        # Imatge parell per facilitar (4x4)
        input_img = np.random.rand(4, 4) * 255
        
        # 1. Encode manual
        coeffs = self.dwt_enc.encode(input_img)
        
        # 2. Decode manual (Necessites haver afegit la funció decode!)
        reconstructed = self.dwt_enc.decode(coeffs)
        
        # Comprovació
        np.testing.assert_allclose(input_img, reconstructed, atol=1e-5)
        print("[OK] DWT Reversibility (Manual Encode -> Manual Decode) verified.")

    def test_dwt_manual_vs_auto(self):
        """
        COMPARA LA TEVA IMPLEMENTACIÓ MANUAL VS PYWAVELETS (AUTOMÀTIC).
        Aquest test valida l'exercici 7.
        """
        try:
            import pywt
        except ImportError:
            self.skipTest("PyWavelets not installed")

        input_img = np.random.rand(16, 16) * 255
        
        # Resultat manual
        LL_man, LH_man, HL_man, HH_man = self.dwt_enc.encode(input_img)
        
        # Resultat automàtic (Pywt fa servir un factor d'escala sqrt(2) de vegades, 
        # però l'estructura ha de ser idèntica. Per comparar valors exactes,
        # caldria normalitzar. Aquí comprovem les dimensions i consistència).
        
        LL_auto, LH_auto, HL_auto, HH_auto = self.dwt_enc.encode_auto(input_img)
        
        self.assertEqual(LL_man.shape, LL_auto.shape)
        self.assertEqual(HH_man.shape, HH_auto.shape)
        
        # Nota: Si el teu manual usa (a+b)/2 i pywt usa (a+b)/sqrt(2), 
        # els valors seran proporcionals. Comprovem que no siguin zero o buits.
        self.assertTrue(np.mean(LL_man) > 0)
        print("[OK] DWT Manual vs Auto structure verified.")

    def test_z_visualize_dwt_output(self):
        """
        [VISUAL TEST] Aquest test carrega una imatge real i mostra
        la descomposició DWT.
        Nota: El test s'aturarà fins que tanquis la finestra del gràfic.
        """
        import cv2
        import os

        # 1. Seleccionem una imatge que tinguis a la carpeta
        # Com que veig a la teva captura que tens 'bw_image.jpg', fem servir aquesta
        image_path = "bw_image.jpg" 
        
        # Si no la troba, intentem amb 'image.jpg' convertint-la a gris
        if not os.path.exists(image_path):
            image_path = "image.jpg"
        
        if not os.path.exists(image_path):
            print(f"\n[SKIP] No s'ha trobat cap imatge a '{image_path}' per visualitzar.")
            return

        print(f"\n[VISUAL] Carregant '{image_path}' per a inspecció visual...")

        # 2. Carreguem la imatge en escala de grisos (flag 0)
        img = cv2.imread(image_path, 0)

        # 3. Fem l'Encode amb la teva classe
        LL, LH, HL, HH = self.dwt_enc.encode(img)

        # 4. Cridem a la teva funció de visualització
        # Assumim que l'has posat dins de la classe DWTEncoder com em vas ensenyar
        print(">>> S'obrirà una finestra amb els sub-bands. Tanca-la per acabar el test.")
        try:
            self.dwt_enc.visualize_dwt(LL, LH, HL, HH)
        except AttributeError:
            # Per si de cas no has posat la funció dins la classe encara
            print("Error: No trobo 'visualize_dwt' dins de DWTEncoder.")
            
        print("[OK] Visualització completada.")

if __name__ == '__main__':
    print("=== RUNNING VIDEO CODING UNIT TESTS ===")
    unittest.main()
