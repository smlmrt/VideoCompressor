import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import subprocess
from PIL import Image, ImageTk
from tkinter import scrolledtext
import queue

class VideoCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Sıkıştırma Uygulaması")
        self.root.geometry("800x600")
        
        # Renk şeması
        self.bg_color = "#2E3440"
        self.frame_bg = "#3B4252"
        self.text_color = "#ECEFF4"
        self.accent_color = "#88C0D0"
        self.button_color = "#5E81AC"
        self.warning_color = "#EBCB8B"
        
        self.root.configure(bg=self.bg_color)
        
        # Font ayarları
        self.title_font = ("Helvetica", 18, "bold")
        self.heading_font = ("Helvetica", 12, "bold")
        self.normal_font = ("Helvetica", 10)
        self.button_font = ("Helvetica", 10, "bold")
        
        # Stil ayarları
        style = ttk.Style()
        style.configure("TCombobox", fieldbackground=self.frame_bg, background=self.frame_bg)
        style.configure("TProgressbar", thickness=10, background=self.accent_color)
        
        # FFmpeg kontrolü
        self.check_ffmpeg()
        
        # Ana frame
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = tk.Label(self.main_frame, text="Video Kalite Düşürme Uygulaması", 
                               font=self.title_font, bg=self.bg_color, fg=self.text_color)
        title_label.pack(pady=10)
        
        # Video seçme alanı
        self.select_frame = tk.LabelFrame(self.main_frame, text="Video Seçimi", 
                                         bg=self.frame_bg, fg=self.text_color, font=self.heading_font)
        self.select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        select_buttons_frame = tk.Frame(self.select_frame, bg=self.frame_bg)
        select_buttons_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=5)
        
        self.browse_btn = tk.Button(select_buttons_frame, text="Tek Video Seç", 
                                   command=self.browse_file, bg=self.button_color, fg=self.text_color,
                                   font=self.button_font, padx=10, relief=tk.FLAT)
        self.browse_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.browse_multiple_btn = tk.Button(select_buttons_frame, text="Çoklu Video Seç", 
                                          command=self.browse_multiple_files, bg=self.button_color, fg=self.text_color,
                                          font=self.button_font, padx=10, relief=tk.FLAT)
        self.browse_multiple_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Seçili videoları göster (liste olarak)
        self.video_listbox_frame = tk.Frame(self.select_frame, bg=self.frame_bg)
        self.video_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.video_listbox = tk.Listbox(self.video_listbox_frame, bg=self.frame_bg, fg=self.text_color,
                                      font=self.normal_font, selectbackground=self.accent_color, height=5)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        listbox_scrollbar = tk.Scrollbar(self.video_listbox_frame, orient="vertical", 
                                       command=self.video_listbox.yview)
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.video_listbox.config(yscrollcommand=listbox_scrollbar.set)
        
        # Video listesi işlemleri için butonlar
        video_list_buttons_frame = tk.Frame(self.select_frame, bg=self.frame_bg)
        video_list_buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.remove_btn = tk.Button(video_list_buttons_frame, text="Seçili Videoyu Kaldır", 
                                   command=self.remove_selected_video, bg=self.warning_color, fg=self.bg_color,
                                   font=self.button_font, padx=10, relief=tk.FLAT)
        self.remove_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.clear_btn = tk.Button(video_list_buttons_frame, text="Tüm Listeyi Temizle", 
                                  command=self.clear_video_list, bg=self.warning_color, fg=self.bg_color,
                                  font=self.button_font, padx=10, relief=tk.FLAT)
        self.clear_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Video dosyalarını saklayacak liste
        self.video_files = []
        
        # Ayarlar alanı
        self.settings_frame = tk.LabelFrame(self.main_frame, text="Kalite Ayarları", 
                                           bg=self.frame_bg, fg=self.text_color, font=self.heading_font)
        self.settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Kalite ayarı
        quality_frame = tk.Frame(self.settings_frame, bg=self.frame_bg)
        quality_frame.pack(fill=tk.X, padx=10, pady=15)
        
        tk.Label(quality_frame, text="Video Kalitesi:", 
                bg=self.frame_bg, fg=self.text_color, font=self.normal_font).pack(side=tk.LEFT, padx=5)
        
        self.quality_var = tk.StringVar(value="Orta")
        quality_options = ["Çok Yüksek", "Yüksek", "Orta", "Düşük", "Çok Düşük"]
        self.quality_menu = ttk.Combobox(quality_frame, textvariable=self.quality_var, 
                                       values=quality_options, state="readonly", width=15)
        self.quality_menu.pack(side=tk.LEFT, padx=5)
        self.quality_menu.current(2)  # Varsayılan olarak "Orta" seçeneğini seç
        
        # Hedef klasör seçimi
        output_frame = tk.Frame(self.settings_frame, bg=self.frame_bg)
        output_frame.pack(fill=tk.X, padx=10, pady=15)
        
        tk.Label(output_frame, text="Hedef Klasör:", 
                bg=self.frame_bg, fg=self.text_color, font=self.normal_font).pack(side=tk.LEFT, padx=5)
        
        self.output_entry = tk.Entry(output_frame, width=40, font=self.normal_font,
                                    bg=self.frame_bg, fg=self.text_color, insertbackground=self.text_color)
        self.output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.output_btn = tk.Button(output_frame, text="Gözat", 
                                  command=self.browse_output_dir, bg=self.button_color, fg=self.text_color,
                                  font=self.button_font, padx=10, relief=tk.FLAT)
        self.output_btn.pack(side=tk.RIGHT, padx=5)
        
        # İşlem başlatma düğmesi
        self.compress_btn = tk.Button(self.main_frame, text="Videoyu İşle", 
                                    command=self.start_compression, bg=self.accent_color, fg=self.bg_color,
                                    font=self.heading_font, padx=20, pady=8, relief=tk.FLAT)
        self.compress_btn.pack(pady=20)
        
        # İlerleme çubuğu
        self.progress_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                          length=100, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(self.progress_frame, text="Hazır", 
                                   bg=self.bg_color, fg=self.text_color, font=self.normal_font)
        self.status_label.pack(pady=5)
        
        # Sonuç bilgisi
        self.result_frame = tk.LabelFrame(self.main_frame, text="Sonuç Bilgisi", 
                                        bg=self.frame_bg, fg=self.text_color, font=self.heading_font)
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.result_text = scrolledtext.ScrolledText(self.result_frame, height=6, width=70, 
                                                  font=("Consolas", 10), bg="#2E3440", fg=self.text_color,
                                                  insertbackground=self.text_color)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def check_ffmpeg(self):
        """FFmpeg'in sistemde kurulu olup olmadığını kontrol eder"""
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            messagebox.showerror("Hata", 
                               "FFmpeg bulunamadı! Lütfen FFmpeg'i yükleyin ve PATH'e ekleyin.")
            self.root.after(1000, self.root.destroy)
    
    def browse_file(self):
        """Tek bir video dosyası seçme iletişim kutusunu açar"""
        filetypes = (
            ("Video dosyaları", "*.mp4 *.avi *.mkv *.mov *.wmv"),
            ("Tüm dosyalar", "*.*")
        )
        filename = filedialog.askopenfilename(title="Video dosyası seçin", 
                                            filetypes=filetypes)
        if filename:
            # Listeyi temizle ve bu dosyayı ekle
            self.video_files = [filename]
            self.update_video_listbox()
            
            # Varsayılan olarak orijinal dosyanın bulunduğu klasörü ayarla
            default_output = os.path.dirname(filename)
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, default_output)
    
    def browse_multiple_files(self):
        """Birden fazla video dosyası seçme iletişim kutusunu açar"""
        filetypes = (
            ("Video dosyaları", "*.mp4 *.avi *.mkv *.mov *.wmv"),
            ("Tüm dosyalar", "*.*")
        )
        filenames = filedialog.askopenfilenames(title="Birden fazla video dosyası seçin", 
                                              filetypes=filetypes)
        if filenames:
            # Listede mevcut videoları tutalım
            self.video_files.extend(filenames)
            self.update_video_listbox()
            
            # Eğer ilk dosya eklendiyse, varsayılan klasörü ayarla
            if len(self.video_files) == 1:
                default_output = os.path.dirname(self.video_files[0])
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, default_output)
    
    def update_video_listbox(self):
        """Video listbox'ını günceller"""
        self.video_listbox.delete(0, tk.END)
        for file in self.video_files:
            # Sadece dosya adını göster, tam yolu değil
            filename = os.path.basename(file)
            self.video_listbox.insert(tk.END, filename)
    
    def remove_selected_video(self):
        """Listeden seçili videoyu kaldırır"""
        try:
            selected_index = self.video_listbox.curselection()[0]
            del self.video_files[selected_index]
            self.update_video_listbox()
        except (IndexError, KeyError):
            messagebox.showinfo("Bilgi", "Lütfen önce listeden bir video seçin.")
    
    def clear_video_list(self):
        """Tüm video listesini temizler"""
        self.video_files = []
        self.update_video_listbox()
    
    def browse_output_dir(self):
        """Hedef klasör seçme iletişim kutusunu açar"""
        dirname = filedialog.askdirectory(title="Hedef klasörü seçin")
        if dirname:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dirname)
    
    def get_ffmpeg_params(self):
        """Seçilen ayarlara göre FFmpeg parametrelerini oluşturur"""
        # Kalite ayarları (CRF değeri - düşük değer daha yüksek kalite demektir)
        quality_map = {
            "Çok Yüksek": "17",
            "Yüksek": "20",
            "Orta": "23",
            "Düşük": "28",
            "Çok Düşük": "35"
        }
        
        # Seçilen kalite değerini doğrudan al
        selected_quality = self.quality_var.get()
        
        # Kalite değerini kontrol et ve debug çıktısı ver
        crf = quality_map.get(selected_quality, "23")
        print(f"Seçilen kalite: {selected_quality}, CRF değeri: {crf}")
        
        # FFmpeg parametreleri - sadece kalite
        params = ["-c:v", "libx264", "-crf", crf, "-preset", "medium"]
        
        # Ses kodlaması - orijinal ses kalitesini koru
        params.extend(["-c:a", "copy"])
        
        return params
    
    def start_compression(self):
        """Video kalite düşürme işlemini başlatır"""
        output_dir = self.output_entry.get().strip()
        
        if not self.video_files:
            messagebox.showerror("Hata", "Lütfen en az bir video dosyası seçin!")
            return
        
        if not output_dir:
            messagebox.showerror("Hata", "Lütfen bir hedef klasör seçin!")
            return
        
        if not os.path.isdir(output_dir):
            messagebox.showerror("Hata", "Seçilen hedef klasör bulunamadı!")
            return
        
        # Tüm dosyaların varlığını kontrol et
        missing_files = [f for f in self.video_files if not os.path.isfile(f)]
        if missing_files:
            missing_names = [os.path.basename(f) for f in missing_files]
            messagebox.showerror("Hata", f"Bazı video dosyaları bulunamadı:\n{', '.join(missing_names)}")
            return
        
        # Seçili kalite bilgisini göster (debug amaçlı)
        print(f"İşlem başlatılıyor. Seçilen kalite: {self.quality_var.get()}")
        print(f"İşlenecek video sayısı: {len(self.video_files)}")
        
        # Çıktı listbox'ını temizle
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Toplam {len(self.video_files)} video işleme alınıyor...\n")
        
        # İşlenecek dosya kuyruğu
        self.processing_queue = queue.Queue()
        for input_file in self.video_files:
            # Çıktı dosya adını oluştur
            filename = os.path.basename(input_file)
            name, ext = os.path.splitext(filename)
            # Seçilen kaliteyi dosya adına ekle
            kalite_eki = self.quality_var.get().lower().replace(" ", "_")
            output_file = os.path.join(output_dir, f"{name}_{kalite_eki}{ext}")
            
            # Dosya çiftini kuyruğa ekle
            self.processing_queue.put((input_file, output_file))
        
        # İlk dosyayı işlemeye başla
        self.process_next_video()
        
        # UI'ı güncelle
        self.progress_bar.start(10)
        self.status_label.config(text=f"Kalite düşürme işlemi devam ediyor... ({self.quality_var.get()} kalite)", fg=self.warning_color)
        self.compress_btn.config(state=tk.DISABLED)
    
    def process_next_video(self):
        """Kuyruktaki bir sonraki videoyu işler"""
        if self.processing_queue.empty():
            # Tüm dosyalar işlendi
            self.status_label.config(text="Tüm videolar işlendi!", fg=self.text_color)
            self.progress_bar.stop()
            self.compress_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Başarılı", f"Tüm videolar başarıyla işlendi!")
            return
        
        # Kuyruktaki bir sonraki dosyayı al
        input_file, output_file = self.processing_queue.get()
        
        # Durumu güncelle
        self.status_label.config(text=f"İşleniyor: {os.path.basename(input_file)}", fg=self.warning_color)
        self.result_text.insert(tk.END, f"\nİşleniyor: {os.path.basename(input_file)}\n")
        self.result_text.see(tk.END)
        
        # Thread olarak işlemi başlat
        self.compress_thread = threading.Thread(
            target=self.compress_video,
            args=(input_file, output_file, True)
        )
        self.compress_thread.daemon = True
        self.compress_thread.start()
        
    def compress_video(self, input_file, output_file, is_batch=False):
        """Video sıkıştırma işlemini gerçekleştirir"""
        try:
            # Orijinal dosya boyutunu al
            original_size = os.path.getsize(input_file) / (1024 * 1024)  # MB cinsinden
            
            # FFmpeg komutunu oluştur
            cmd = ["ffmpeg", "-i", input_file]
            cmd.extend(self.get_ffmpeg_params())
            cmd.append(output_file)
            
            # Debug için komutu yazdır
            print(f"Çalıştırılan komut: {' '.join(cmd)}")
            
            # Komutu çalıştır
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            _, stderr = process.communicate()
            
            # İşlem tamamlandı
            self.root.after(0, self.compression_finished, input_file, output_file, stderr, is_batch)
            
        except Exception as e:
            self.root.after(0, self.compression_error, str(e), is_batch)
    
    def compression_finished(self, input_file, output_file, log, is_batch=False):
        """Sıkıştırma işlemi tamamlandığında çağrılır"""
        if not is_batch:
            self.progress_bar.stop()
            self.compress_btn.config(state=tk.NORMAL)
        
        if os.path.exists(output_file):
            # Boyut bilgilerini hesapla
            original_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
            compressed_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            saved = original_size - compressed_size
            saved_percent = (saved / original_size) * 100 if original_size > 0 else 0
            
            # Sonuç bilgisini göster
            result_info = (
                f"Dosya: {os.path.basename(input_file)}\n"
                f"Kalite: {self.quality_var.get()}\n"
                f"Orijinal: {original_size:.2f} MB → Sıkıştırılmış: {compressed_size:.2f} MB\n"
                f"Kazanç: {saved:.2f} MB ({saved_percent:.1f}%)\n"
                f"Çıktı: {output_file}\n"
                f"{'-'*50}"
            )
            
            if not is_batch:
                self.status_label.config(text="Sıkıştırma tamamlandı!")
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, result_info)
                messagebox.showinfo("Başarılı", f"Video başarıyla sıkıştırıldı!\nSeçilen kalite: {self.quality_var.get()}\nKazanılan alan: {saved:.2f} MB ({saved_percent:.1f}%)")
            else:
                # Toplu işlem sonucunu ekle ve sonraki videoyu işle
                self.result_text.insert(tk.END, result_info + "\n")
                self.result_text.see(tk.END)
                self.process_next_video()
        else:
            error_msg = "Çıktı dosyası oluşturulamadı. FFmpeg hatası olabilir."
            if not is_batch:
                self.compression_error(error_msg, is_batch)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, log)
            else:
                # Hata bilgisini ekle ve sonraki videoyu işle
                self.result_text.insert(tk.END, f"HATA ({os.path.basename(input_file)}): {error_msg}\n{'-'*50}\n")
                self.result_text.see(tk.END)
                self.process_next_video()
    
    def compression_error(self, error_msg, is_batch=False):
        """Sıkıştırma sırasında hata oluştuğunda çağrılır"""
        if not is_batch:
            self.progress_bar.stop()
            self.compress_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Hata oluştu!")
            messagebox.showerror("Hata", f"Sıkıştırma sırasında bir hata oluştu:\n{error_msg}")
        else:
            # Hata mesajını göster ve sıradaki dosyaya geç
            self.result_text.insert(tk.END, f"HATA: {error_msg}\n{'-'*50}\n")
            self.result_text.see(tk.END)
            self.process_next_video()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCompressorApp(root)
    
    # Pencere simgesini değiştirme seçeneği (opsiyonel)
    try:
        root.iconbitmap("video_icon.ico")  # İsterseniz bir ikon dosyası ekleyebilirsiniz
    except:
        pass
        
    # Pencereyi ekranın ortasında göster
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    root.mainloop()