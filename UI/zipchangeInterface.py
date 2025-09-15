import customtkinter as ctk
import zipfile
import pyzipper
import threading
import time
import os
import re
from queue import Queue
from tkinter import filedialog
from CTkListbox import CTkListbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

class ZIPPasswordCrackerGUI:
    def __init__(self):
        # Configuração do tema
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Janela principal
        self.window = ctk.CTk()
        self.window.title("ZIP Password Cracker Pro")
        self.window.geometry("1000x700")
        self.window.minsize(900, 650)
        
        # Variáveis de estado
        self.running = False
        self.stop_event = threading.Event()
        self.password_history = deque(maxlen=100)
        self.speed_history = deque(maxlen=50)
        
        # Layout principal
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho
        self.header = ctk.CTkFrame(self.window, height=60)
        self.header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.header.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.header, 
            text="🔓 ZIP Password Cracker Pro", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Painel de configuração
        self.config_frame = ctk.CTkFrame(self.main_frame)
        self.config_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.config_frame.grid_columnconfigure(1, weight=1)
        
        # Arquivo ZIP
        ctk.CTkLabel(self.config_frame, text="Arquivo ZIP:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.zip_entry = ctk.CTkEntry(self.config_frame, placeholder_text="Selecione o arquivo ZIP...")
        self.zip_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)
        self.zip_browse = ctk.CTkButton(self.config_frame, text="Procurar", width=100, command=self.browse_zip)
        self.zip_browse.grid(row=0, column=2, padx=(0, 10), pady=5)
        
        # Wordlist
        ctk.CTkLabel(self.config_frame, text="Wordlist:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.wordlist_entry = ctk.CTkEntry(self.config_frame, placeholder_text="Selecione a wordlist...")
        self.wordlist_entry.grid(row=1, column=1, sticky="ew", padx=(0, 5), pady=5)
        self.wordlist_browse = ctk.CTkButton(self.config_frame, text="Procurar", width=100, command=self.browse_wordlist)
        self.wordlist_browse.grid(row=1, column=2, padx=(0, 10), pady=5)
        
        # Threads
        ctk.CTkLabel(self.config_frame, text="Threads:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.threads_slider = ctk.CTkSlider(self.config_frame, from_=1, to=16, number_of_steps=15)
        self.threads_slider.set(4)
        self.threads_slider.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=5)
        self.threads_label = ctk.CTkLabel(self.config_frame, text="4")
        self.threads_label.grid(row=2, column=2, padx=(0, 10), pady=5)
        self.threads_slider.configure(command=self.update_threads_label)
        
        # Botões de controle
        self.button_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.start_btn = ctk.CTkButton(
            self.button_frame, 
            text="▶ Iniciar", 
            command=self.start_cracking,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ctk.CTkButton(
            self.button_frame, 
            text="⏹ Parar", 
            command=self.stop_cracking,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.clear_btn = ctk.CTkButton(
            self.button_frame, 
            text="🗑 Limpar", 
            command=self.clear_output
        )
        self.clear_btn.grid(row=0, column=2, padx=5)
        
        # Painel de conteúdo
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Abas
        self.tabview = ctk.CTkTabview(self.content_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew")
        
        # Aba de output
        self.output_tab = self.tabview.add("Output")
        self.output_tab.grid_columnconfigure(0, weight=1)
        self.output_tab.grid_rowconfigure(0, weight=1)
        
        self.output_text = ctk.CTkTextbox(
            self.output_tab, 
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="word"
        )
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Aba de estatísticas
        self.stats_tab = self.tabview.add("Estatísticas")
        self.stats_tab.grid_columnconfigure(0, weight=1)
        self.stats_tab.grid_rowconfigure(1, weight=1)
        
        # Painel de métricas
        self.metrics_frame = ctk.CTkFrame(self.stats_tab)
        self.metrics_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.tested_label = ctk.CTkLabel(
            self.metrics_frame, 
            text="Senhas testadas: 0",
            font=ctk.CTkFont(weight="bold")
        )
        self.tested_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.speed_label = ctk.CTkLabel(
            self.metrics_frame, 
            text="Velocidade: 0/s",
            font=ctk.CTkFont(weight="bold")
        )
        self.speed_label.grid(row=0, column=1, padx=10, pady=10)
        
        self.time_label = ctk.CTkLabel(
            self.metrics_frame, 
            text="Tempo: 00:00:00",
            font=ctk.CTkFont(weight="bold")
        )
        self.time_label.grid(row=0, column=2, padx=10, pady=10)
        
        self.progress_label = ctk.CTkLabel(
            self.metrics_frame, 
            text="Progresso: 0%",
            font=ctk.CTkFont(weight="bold")
        )
        self.progress_label.grid(row=0, column=3, padx=10, pady=10)
        
        # Gráfico
        self.chart_frame = ctk.CTkFrame(self.stats_tab)
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_rowconfigure(0, weight=1)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.setup_chart()
        
        # Barra de progresso
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Status bar
        self.status_bar = ctk.CTkFrame(self.window, height=30)
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.status_bar.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Pronto")
        self.status_label.grid(row=0, column=0, sticky="w", padx=10)
        
        # Bind events
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_chart(self):
        """Configura o gráfico de velocidade"""
        self.ax.clear()
        self.ax.set_title('Velocidade de Teste (senhas/segundo)')
        self.ax.set_xlabel('Tempo')
        self.ax.set_ylabel('Velocidade')
        self.ax.grid(True, alpha=0.3)
        self.line, = self.ax.plot([], [], 'b-')
        self.canvas.draw()
    
    def update_chart(self):
        """Atualiza o gráfico de velocidade"""
        if len(self.speed_history) > 1:
            x_data = list(range(len(self.speed_history)))
            self.line.set_data(x_data, list(self.speed_history))
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
    
    def update_threads_label(self, value):
        """Atualiza o label de threads"""
        self.threads_label.configure(text=str(int(float(value))))
    
    def browse_zip(self):
        """Abre diálogo para selecionar arquivo ZIP"""
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo ZIP",
            filetypes=[("ZIP Files", "*.zip"), ("All Files", "*.*")]
        )
        if file_path:
            self.zip_entry.delete(0, "end")
            self.zip_entry.insert(0, file_path)
    
    def browse_wordlist(self):
        """Abre diálogo para selecionar wordlist"""
        file_path = filedialog.askopenfilename(
            title="Selecione a wordlist",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.wordlist_entry.delete(0, "end")
            self.wordlist_entry.insert(0, file_path)
    
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.password_history.append(message)
    
    def clean_password(self, password):
        """Remove tabs, espaços extras e caracteres não imprimíveis"""
        cleaned = password.strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = ''.join(char for char in cleaned if char.isprintable())
        return cleaned
        
    def read_and_clean_wordlist(self, wordlist_file):
        """Lê e limpa a wordlist"""
        cleaned_passwords = []
        try:
            with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    cleaned_line = self.clean_password(line)
                    if cleaned_line and cleaned_line not in cleaned_passwords:
                        cleaned_passwords.append(cleaned_line)
            return cleaned_passwords
        except Exception as e:
            self.log_message(f"Erro ao ler wordlist: {e}")
            return None
    
    def test_password(self, zip_ref, password):
        """Testa uma senha no arquivo ZIP"""
        try:
            file_to_test = zip_ref.namelist()[0]
            with zip_ref.open(file_to_test, pwd=password.encode('utf-8')) as f:
                f.read(1)
                return True
        except:
            return False
    
    def crack_password(self):
        """Método principal para quebrar a senha"""
        zip_file = self.zip_entry.get()
        wordlist_file = self.wordlist_entry.get()
        max_threads = int(self.threads_slider.get())
        
        self.running = True
        self.stop_event.clear()
        
        self.log_message(f"Iniciando quebra de senha para: {zip_file}")
        self.log_message(f"Usando wordlist: {wordlist_file}")
        self.log_message(f"Threads: {max_threads}")
        self.log_message("-" * 50)
        
        # Verifica se os arquivos existem
        if not os.path.exists(zip_file):
            self.log_message(f"Erro: Arquivo ZIP '{zip_file}' não encontrado!")
            self.running = False
            self.update_ui_state(False)
            return
            
        if not os.path.exists(wordlist_file):
            self.log_message(f"Erro: Wordlist '{wordlist_file}' não encontrada!")
            self.running = False
            self.update_ui_state(False)
            return
        
        # Lê e limpa a wordlist
        self.log_message("Limpando wordlist...")
        self.status_label.configure(text="Limpando wordlist...")
        passwords = self.read_and_clean_wordlist(wordlist_file)
        
        if passwords is None:
            self.running = False
            self.update_ui_state(False)
            return
        
        total_passwords = len(passwords)
        self.log_message(f"Total de senhas únicas: {total_passwords:,}")
        self.log_message(f"Primeiras 5 senhas: {passwords[:5]}")
        
        # Cria queue com todas as senhas
        password_queue = Queue()
        for password in passwords:
            if self.stop_event.is_set():
                break
            password_queue.put(password)
        
        # Variáveis para acompanhamento
        tested_passwords = 0
        found_password = None
        start_time = time.time()
        last_update_time = start_time
        
        # Função do worker
        def worker():
            nonlocal tested_passwords, found_password, last_update_time
            try:
                with pyzipper.AESZipFile(zip_file) as zip_ref:
                    while not self.stop_event.is_set() and not password_queue.empty():
                        try:
                            password = password_queue.get_nowait()
                            tested_passwords += 1
                            
                            # Atualiza interface periodicamente
                            current_time = time.time()
                            if current_time - last_update_time > 0.1:  # Atualiza a cada 100ms
                                elapsed = current_time - start_time
                                speed = tested_passwords / elapsed if elapsed > 0 else 0
                                
                                # Atualiza UI na thread principal
                                self.window.after(0, self.update_stats, tested_passwords, speed, elapsed, tested_passwords/total_passwords*100)
                                
                                # Atualiza histórico de velocidade
                                self.speed_history.append(speed)
                                if len(self.speed_history) % 5 == 0:
                                    self.window.after(0, self.update_chart)
                                
                                last_update_time = current_time
                            
                            # Testa a senha
                            if self.test_password(zip_ref, password):
                                found_password = password
                                self.stop_event.set()
                                self.window.after(0, lambda: self.log_message(f"\n🎉 SENHA ENCONTRADA: '{password}'"))
                                break
                                
                            password_queue.task_done()
                            
                        except:
                            break
            except Exception as e:
                self.window.after(0, lambda: self.log_message(f"Erro ao processar arquivo ZIP: {e}"))
        
        # Inicia as threads
        threads = []
        for i in range(max_threads):
            if self.stop_event.is_set():
                break
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda conclusão
        try:
            while not self.stop_event.is_set() and any(thread.is_alive() for thread in threads):
                time.sleep(0.1)
                
                if password_queue.empty():
                    self.stop_event.set()
                    
        except:
            pass
        
        # Resultado final
        elapsed = time.time() - start_time
        self.log_message("\n" + "=" * 50)
        self.log_message("RESULTADO DA BUSCA:")
        self.log_message(f"Tempo decorrido: {elapsed:.2f} segundos")
        self.log_message(f"Senhas testadas: {tested_passwords}")
        
        if elapsed > 0:
            self.log_message(f"Velocidade média: {tested_passwords/elapsed:.2f} senhas/segundo")
        
        if found_password:
            self.log_message(f"✅ SENHA ENCONTRADA: '{found_password}'")
            
            # Tenta extrair os arquivos
            try:
                with pyzipper.AESZipFile(zip_file) as zip_ref:
                    zip_ref.extractall(pwd=found_password.encode('utf-8'))
                    self.log_message(f"✅ Arquivos extraídos com sucesso!")
                    self.log_message(f"✅ Arquivos desbloqueados: {zip_ref.namelist()}")
            except Exception as e:
                self.log_message(f"⚠️  Erro na extração: {e}")
        else:
            self.log_message("❌ Senha não encontrada na wordlist")
            
            if tested_passwords < total_passwords:
                self.log_message(f"⚠️  Interrompido pelo usuário")
        
        self.running = False
        self.window.after(0, self.update_ui_state, False)
    
    def update_stats(self, tested, speed, elapsed, progress):
        """Atualiza as estatísticas na UI"""
        self.tested_label.configure(text=f"Senhas testadas: {tested}")
        self.speed_label.configure(text=f"Velocidade: {speed:.0f}/s")
        self.time_label.configure(text=f"Tempo: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
        self.progress_label.configure(text=f"Progresso: {progress:.1f}%")
        self.progress_bar.set(progress / 100)
        self.status_label.configure(text=f"Testando... {tested} senhas verificadas")
    
    def update_ui_state(self, running):
        """Atualiza o estado dos controles da UI"""
        if running:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_label.configure(text="Executando...")
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.status_label.configure(text="Pronto")
    
    def start_cracking(self):
        """Inicia o processo de quebra de senha"""
        if not self.zip_entry.get() or not self.wordlist_entry.get():
            self.log_message("Erro: Selecione o arquivo ZIP e a wordlist!")
            return
        
        self.update_ui_state(True)
        
        # Inicia a thread de quebra de senha
        thread = threading.Thread(target=self.crack_password, daemon=True)
        thread.start()
    
    def stop_cracking(self):
        """Para o processo de quebra de senha"""
        self.stop_event.set()
        self.log_message("⏹️  Interrompido pelo usuário")
        self.update_ui_state(False)
    
    def clear_output(self):
        """Limpa a saída"""
        self.output_text.delete("1.0", "end")
        self.progress_bar.set(0)
        self.tested_label.configure(text="Senhas testadas: 0")
        self.speed_label.configure(text="Velocidade: 0/s")
        self.time_label.configure(text="Tempo: 00:00:00")
        self.progress_label.configure(text="Progresso: 0%")
        self.status_label.configure(text="Pronto")
        self.speed_history.clear()
        self.setup_chart()
    
    def on_closing(self):
        """Lida com o fechamento da janela"""
        self.stop_event.set()
        self.window.quit()
        self.window.destroy()
    
    def run(self):
        """Inicia a aplicação"""
        self.window.mainloop()

# Instalação das dependências necessárias
def install_dependencies():
    try:
        import customtkinter
    except ImportError:
        import subprocess
        import sys
        print("Instalando CustomTkinter...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    
    try:
        import pyzipper
    except ImportError:
        import subprocess
        import sys
        print("Instalando pyzipper...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyzipper"])
    
    try:
        import matplotlib
    except ImportError:
        import subprocess
        import sys
        print("Instalando matplotlib...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    
    try:
        from CTkListbox import CTkListbox
    except ImportError:
        import subprocess
        import sys
        print("Instalando CTkListbox...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "CTkListbox"])

if __name__ == "__main__":
    # Instala dependências automaticamente
    install_dependencies()
    
    # Inicia a interface
    app = ZIPPasswordCrackerGUI()
    app.run()