import zipfile
import time
import os
import threading
from queue import Queue
import PySimpleGUI as sg

class ZIPPasswordCrackerGUI:
    def __init__(self):
        self.theme = sg.theme('DarkGrey5')
        self.found_password = None
        self.stop_event = threading.Event()
        self.tested_passwords = 0
        self.start_time = 0
        self.running = False
        
        # Layout da interface
        self.layout = [
            [sg.Text('Quebrador de Senhas ZIP', font=('Helvetica', 16), justification='center')],
            [sg.HorizontalSeparator()],
            [
                sg.Text('Arquivo ZIP:'), 
                sg.Input(key='-ZIPFILE-', enable_events=True), 
                sg.FileBrowse('Procurar', file_types=(('ZIP Files', '*.zip'),))
            ],
            [
                sg.Text('Wordlist:'), 
                sg.Input(key='-WORDLIST-', enable_events=True), 
                sg.FileBrowse('Procurar', file_types=(('Text Files', '*.txt'),))
            ],
            [
                sg.Text('Threads:'),
                sg.Slider(range=(1, 16), default_value=4, orientation='h', key='-THREADS-')
            ],
            [
                sg.Button('Iniciar', key='-START-', size=(10, 1)), 
                sg.Button('Parar', key='-STOP-', size=(10, 1), disabled=True),
                sg.Button('Sair', key='-EXIT-', size=(10, 1))
            ],
            [sg.HorizontalSeparator()],
            [sg.Text('Progresso:', font=('Helvetica', 12))],
            [sg.ProgressBar(100, orientation='h', size=(50, 20), key='-PROGRESS-')],
            [sg.Text('Senhas testadas: 0', key='-TESTED-')],
            [sg.Text('Velocidade: 0 senhas/segundo', key='-SPEED-')],
            [sg.Text('Tempo decorrido: 0 segundos', key='-TIME-')],
            [sg.Multiline('', size=(65, 10), key='-OUTPUT-', autoscroll=True, disabled=True)]
        ]
        
        self.window = sg.Window('ZIP Password Cracker', self.layout, finalize=True)
        
    def test_password(self, zip_ref, password):
        """Tenta abrir o arquivo ZIP com uma senha"""
        try:
            # Tenta extrair um arquivo com a senha
            with zip_ref.open(zip_ref.namelist()[0], pwd=password.encode()) as f:
                # Se não der erro, a senha está correta
                return True
        except:
            return False
    
    def worker(self, password_queue, zip_file, window):
        """Thread worker que testa senhas"""
        with zipfile.ZipFile(zip_file) as zip_ref:
            while not self.stop_event.is_set():
                try:
                    password = password_queue.get_nowait()
                    self.tested_passwords += 1
                    
                    # Atualiza a interface a cada 100 senhas
                    if self.tested_passwords % 100 == 0:
                        elapsed = time.time() - self.start_time
                        window.write_event_value('-UPDATE-', {
                            'tested': self.tested_passwords,
                            'speed': self.tested_passwords / elapsed,
                            'time': elapsed
                        })
                    
                    # Testa a senha
                    if self.test_password(zip_ref, password):
                        self.found_password = password
                        self.stop_event.set()
                        window.write_event_value('-FOUND-', password)
                        break
                        
                    password_queue.task_done()
                    
                except:
                    break
        
        # Se a fila estiver vazia e não encontrou senha
        if not self.found_password and password_queue.empty():
            window.write_event_value('-NOTFOUND-', None)
    
    def crack(self, zip_file, wordlist_file, max_threads, window):
        """Método principal para quebrar a senha"""
        self.start_time = time.time()
        self.tested_passwords = 0
        self.found_password = None
        self.stop_event.clear()
        
        # Lê a wordlist
        try:
            with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except Exception as e:
            window.write_event_value('-ERROR-', f"Erro ao ler wordlist: {e}")
            return
        
        total_passwords = len(passwords)
        window.write_event_value('-STATUS-', f"Total de senhas na wordlist: {total_passwords}")
        
        # Cria queue com todas as senhas
        password_queue = Queue()
        for password in passwords:
            password_queue.put(password)
        
        # Inicia as threads
        threads = []
        for i in range(max_threads):
            thread = threading.Thread(target=self.worker, args=(password_queue, zip_file, window))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda conclusão ou senha encontrada
        while not self.stop_event.is_set() and any(thread.is_alive() for thread in threads):
            time.sleep(0.1)
            
            if password_queue.empty():
                self.stop_event.set()
    
    def run(self):
        """Loop principal da interface"""
        while True:
            event, values = self.window.read(timeout=100)
            
            if event in (sg.WIN_CLOSED, '-EXIT-'):
                break
                
            elif event == '-START-':
                zip_file = values['-ZIPFILE-']
                wordlist = values['-WORDLIST-']
                threads = int(values['-THREADS-'])
                
                if not zip_file or not wordlist:
                    sg.popup_error('Selecione o arquivo ZIP e a wordlist!')
                    continue
                
                if not os.path.exists(zip_file):
                    sg.popup_error('Arquivo ZIP não encontrado!')
                    continue
                    
                if not os.path.exists(wordlist):
                    sg.popup_error('Wordlist não encontrada!')
                    continue
                
                self.running = True
                self.window['-START-'].update(disabled=True)
                self.window['-STOP-'].update(disabled=False)
                self.window['-OUTPUT-'].update('')
                
                # Inicia a thread de quebra de senha
                threading.Thread(
                    target=self.crack, 
                    args=(zip_file, wordlist, threads, self.window),
                    daemon=True
                ).start()
                
            elif event == '-STOP-':
                self.stop_event.set()
                self.running = False
                self.window['-START-'].update(disabled=False)
                self.window['-STOP-'].update(disabled=True)
                self.window['-OUTPUT-'].print("⏹️ Processo interrompido pelo usuário")
                
            elif event == '-UPDATE-':
                tested = values[event]['tested']
                speed = values[event]['speed']
                elapsed = values[event]['time']
                
                self.window['-TESTED-'].update(f'Senhas testadas: {tested}')
                self.window['-SPEED-'].update(f'Velocidade: {speed:.2f} senhas/segundo')
                self.window['-TIME-'].update(f'Tempo decorrido: {elapsed:.2f} segundos')
                
                # Atualiza a barra de progresso (assumindo 100000 como máximo para exemplo)
                progress = min(100, (tested / 100000) * 100)
                self.window['-PROGRESS-'].update(progress)
                
            elif event == '-FOUND-':
                password = values[event]
                elapsed = time.time() - self.start_time
                
                self.window['-OUTPUT-'].print(f"✅ SENHA ENCONTRADA: {password}")
                self.window['-OUTPUT-'].print(f"✅ Tempo total: {elapsed:.2f} segundos")
                self.window['-OUTPUT-'].print(f"✅ Senhas testadas: {self.tested_passwords}")
                
                # Tenta extrair o arquivo
                try:
                    with zipfile.ZipFile(values['-ZIPFILE-']) as zip_ref:
                        zip_ref.extractall(pwd=password.encode())
                    self.window['-OUTPUT-'].print("✅ Arquivo extraído com sucesso!")
                except Exception as e:
                    self.window['-OUTPUT-'].print(f"⚠️ Erro na extração: {e}")
                
                self.running = False
                self.window['-START-'].update(disabled=False)
                self.window['-STOP-'].update(disabled=True)
                
            elif event == '-NOTFOUND-':
                elapsed = time.time() - self.start_time
                
                self.window['-OUTPUT-'].print("❌ Senha não encontrada na wordlist")
                self.window['-OUTPUT-'].print(f"⏱️ Tempo total: {elapsed:.2f} segundos")
                self.window['-OUTPUT-'].print(f"🔢 Senhas testadas: {self.tested_passwords}")
                
                self.running = False
                self.window['-START-'].update(disabled=False)
                self.window['-STOP-'].update(disabled=True)
                
            elif event == '-STATUS-':
                self.window['-OUTPUT-'].print(values[event])
                
            elif event == '-ERROR-':
                self.window['-OUTPUT-'].print(values[event])
                self.running = False
                self.window['-START-'].update(disabled=False)
                self.window['-STOP-'].update(disabled=True)
        
        self.window.close()

if __name__ == "__main__":
    # Verifica se o PySimpleGUI está instalado, se não, instala
    try:
        import PySimpleGUI
    except ImportError:
        import os
        os.system('pip install pysimplegui')
        import PySimpleGUI as sg
        
    app = ZIPPasswordCrackerGUI()
    app.run()