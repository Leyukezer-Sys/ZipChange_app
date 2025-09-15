import PySimpleGUI as sg
import zipfile
import pyzipper
import threading
import time
import os
import re
from queue import Queue

class ZIPPasswordCrackerGUI:
    def __init__(self):
        self.theme = sg.theme('DarkBlue3')
        self.cracker = None
        self.running = False
        self.stop_event = threading.Event()
        
        # Layout da interface
        self.layout = [
            [sg.Text('Quebrador de Senhas ZIP', font=('Helvetica', 16, 'bold'))],
            [sg.HorizontalSeparator()],
            [
                sg.Text('Arquivo ZIP:', size=(12, 1)),
                sg.Input(key='-ZIP_FILE-', enable_events=True),
                sg.FileBrowse('Procurar', file_types=(('ZIP Files', '*.zip'),))
            ],
            [
                sg.Text('Wordlist:', size=(12, 1)),
                sg.Input(key='-WORDLIST_FILE-', enable_events=True),
                sg.FileBrowse('Procurar', file_types=(('Text Files', '*.txt'),))
            ],
            [
                sg.Text('Threads:', size=(12, 1)),
                sg.Slider(range=(1, 16), default_value=4, orientation='h', key='-THREADS-', size=(20, 15))
            ],
            [
                sg.Button('Iniciar', key='-START-', size=(10, 1), button_color=('white', 'green')),
                sg.Button('Parar', key='-STOP-', size=(10, 1), button_color=('white', 'red'), disabled=True),
                sg.Button('Limpar', key='-CLEAR-', size=(10, 1))
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Multiline(
                    key='-OUTPUT-', 
                    size=(70, 20), 
                    autoscroll=True, 
                    reroute_stdout=True, 
                    write_only=True,
                    font=('Courier New', 10)
                )
            ],
            [
                sg.ProgressBar(100, orientation='h', size=(50, 20), key='-PROGRESS-', expand_x=True),
                sg.Text('0%', key='-PROGRESS_TEXT-', size=(5, 1))
            ],
            [
                sg.Text('Senhas testadas: 0', key='-TESTED-', size=20),
                sg.Text('Velocidade: 0/s', key='-SPEED-', size=20),
                sg.Text('Tempo: 00:00:00', key='-TIME-', size=15)
            ]
        ]
        
        self.window = sg.Window('ZIP Password Cracker', self.layout, finalize=True)
        
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
            print(f"Erro ao ler wordlist: {e}")
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
    
    def crack_password(self, zip_file, wordlist_file, max_threads):
        """Método principal para quebrar a senha"""
        self.running = True
        self.stop_event.clear()
        
        print(f"Iniciando quebra de senha para: {zip_file}")
        print(f"Usando wordlist: {wordlist_file}")
        print(f"Threads: {max_threads}")
        print("-" * 50)
        
        # Verifica se os arquivos existem
        if not os.path.exists(zip_file):
            print(f"Erro: Arquivo ZIP '{zip_file}' não encontrado!")
            self.running = False
            return
            
        if not os.path.exists(wordlist_file):
            print(f"Erro: Wordlist '{wordlist_file}' não encontrada!")
            self.running = False
            return
        
        # Lê e limpa a wordlist
        print("Limpando wordlist...")
        passwords = self.read_and_clean_wordlist(wordlist_file)
        
        if passwords is None:
            self.running = False
            return
        
        total_passwords = len(passwords)
        print(f"Total de senhas únicas: {total_passwords:,}")
        print(f"Primeiras 5 senhas: {passwords[:5]}")
        
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
        
        # Função do worker
        def worker():
            nonlocal tested_passwords, found_password
            try:
                with pyzipper.AESZipFile(zip_file) as zip_ref:
                    while not self.stop_event.is_set() and not password_queue.empty():
                        try:
                            password = password_queue.get_nowait()
                            tested_passwords += 1
                            
                            # Atualiza interface a cada 10 senhas
                            if tested_passwords % 10 == 0:
                                elapsed = time.time() - start_time
                                self.window['-TESTED-'].update(f'Senhas testadas: {tested_passwords}')
                                self.window['-SPEED-'].update(f'Velocidade: {tested_passwords/elapsed:.0f}/s')
                                self.window['-TIME-'].update(f'Tempo: {time.strftime("%H:%M:%S", time.gmtime(elapsed))}')
                                progress = min(100, (tested_passwords / total_passwords) * 100)
                                self.window['-PROGRESS-'].update(progress)
                                self.window['-PROGRESS_TEXT-'].update(f'{progress:.1f}%')
                            
                            # Testa a senha
                            if self.test_password(zip_ref, password):
                                found_password = password
                                self.stop_event.set()
                                print(f"\n🎉 SENHA ENCONTRADA: '{password}'")
                                break
                                
                            password_queue.task_done()
                            
                        except:
                            break
            except Exception as e:
                print(f"Erro ao processar arquivo ZIP: {e}")
        
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
        print("\n" + "=" * 50)
        print("RESULTADO DA BUSCA:")
        print(f"Tempo decorrido: {elapsed:.2f} segundos")
        print(f"Senhas testadas: {tested_passwords}")
        
        if elapsed > 0:
            print(f"Velocidade média: {tested_passwords/elapsed:.2f} senhas/segundo")
        
        if found_password:
            print(f"✅ SENHA ENCONTRADA: '{found_password}'")
            
            # Tenta extrair os arquivos
            try:
                with pyzipper.AESZipFile(zip_file) as zip_ref:
                    zip_ref.extractall(pwd=found_password.encode('utf-8'))
                    print(f"✅ Arquivos extraídos com sucesso!")
                    print(f"✅ Arquivos desbloqueados: {zip_ref.namelist()}")
            except Exception as e:
                print(f"⚠️  Erro na extração: {e}")
        else:
            print("❌ Senha não encontrada na wordlist")
            
            if tested_passwords < total_passwords:
                print(f"⚠️  Interrompido pelo usuário")
        
        self.running = False
        self.window['-START-'].update(disabled=False)
        self.window['-STOP-'].update(disabled=True)
    
    def run(self):
        """Loop principal da interface"""
        while True:
            event, values = self.window.read(timeout=100)
            
            if event == sg.WINDOW_CLOSED:
                self.stop_event.set()
                break
                
            elif event == '-START-':
                if not values['-ZIP_FILE-'] or not values['-WORDLIST_FILE-']:
                    sg.popup_error('Selecione o arquivo ZIP e a wordlist!')
                    continue
                
                self.window['-START-'].update(disabled=True)
                self.window['-STOP-'].update(disabled=False)
                self.window['-OUTPUT-'].update('')
                
                # Inicia a thread de quebra de senha
                thread = threading.Thread(
                    target=self.crack_password,
                    args=(
                        values['-ZIP_FILE-'],
                        values['-WORDLIST_FILE-'],
                        int(values['-THREADS-'])
                    ),
                    daemon=True
                )
                thread.start()
                
            elif event == '-STOP-':
                self.stop_event.set()
                print("⏹️  Interrompido pelo usuário")
                self.window['-START-'].update(disabled=False)
                self.window['-STOP-'].update(disabled=True)
                
            elif event == '-CLEAR-':
                self.window['-OUTPUT-'].update('')
                self.window['-PROGRESS-'].update(0)
                self.window['-PROGRESS_TEXT-'].update('0%')
                self.window['-TESTED-'].update('Senhas testadas: 0')
                self.window['-SPEED-'].update('Velocidade: 0/s')
                self.window['-TIME-'].update('Tempo: 00:00:00')
        
        self.window.close()

# Instalação das dependências necessárias
def install_dependencies():
    try:
        import PySimpleGUI
    except ImportError:
        import subprocess
        import sys
        print("Instalando PySimpleGUI...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PySimpleGUI"])
    
    try:
        import pyzipper
    except ImportError:
        import subprocess
        import sys
        print("Instalando pyzipper...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyzipper"])

if __name__ == "__main__":
    # Instala dependências automaticamente
    install_dependencies()
    
    # Inicia a interface
    app = ZIPPasswordCrackerGUI()
    app.run()