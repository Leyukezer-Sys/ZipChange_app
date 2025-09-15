import zipfile
import argparse
import time
from threading import Thread, Event
from queue import Queue
import os

class ZIPPasswordCracker:
    def __init__(self, zip_file, wordlist_file, max_threads=4):
        self.zip_file = zip_file
        self.wordlist_file = wordlist_file
        self.max_threads = max_threads
        self.found_password = None
        self.stop_event = Event()
        self.tested_passwords = 0
        self.start_time = time.time()
        
    def test_password(self, zip_ref, password):
        """Tenta abrir o arquivo ZIP com uma senha"""
        try:
            zip_ref.extractall(pwd=password.encode())
            return True
        except (RuntimeError, zipfile.BadZipFile):
            return False
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return False
    
    def worker(self, password_queue):
        """Thread worker que testa senhas"""
        with zipfile.ZipFile(self.zip_file) as zip_ref:
            # Pega o primeiro arquivo para teste
            file_to_test = zip_ref.namelist()[0]
            
            while not self.stop_event.is_set() and not password_queue.empty():
                try:
                    password = password_queue.get_nowait()
                    self.tested_passwords += 1
                    
                    if self.tested_passwords % 1000 == 0:
                        elapsed = time.time() - self.start_time
                        print(f"Testadas {self.tested_passwords} senhas. "
                              f"Velocidade: {self.tested_passwords/elapsed:.2f} senhas/segundo")
                    
                    try:
                        with zip_ref.open(file_to_test, pwd=password.encode()) as f:
                            # Se chegou aqui, a senha funciona!
                            self.found_password = password
                            self.stop_event.set()
                            print(f"\n✅ SENHA ENCONTRADA: {password}")
                            break
                    except (RuntimeError, Exception):
                        # Senha incorreta, continua tentando
                        pass
                        
                    password_queue.task_done()
                    
                except Exception as e:
                    break
    
    def crack(self):
        """Método principal para quebrar a senha"""
        print(f"Iniciando quebra de senha para: {self.zip_file}")
        print(f"Usando wordlist: {self.wordlist_file}")
        print(f"Threads: {self.max_threads}")
        print("-" * 50)
        
        # Verifica se os arquivos existem
        if not os.path.exists(self.zip_file):
            print(f"Erro: Arquivo ZIP '{self.zip_file}' não encontrado!")
            return False
            
        if not os.path.exists(self.wordlist_file):
            print(f"Erro: Wordlist '{self.wordlist_file}' não encontrada!")
            return False
        
        # Lê a wordlist
        try:
            with open(self.wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Erro ao ler wordlist: {e}")
            return False
        
        print(f"Total de senhas na wordlist: {len(passwords):,}")
        
        # Cria queue com todas as senhas
        password_queue = Queue()
        for password in passwords:
            password_queue.put(password)
        
        # Inicia as threads
        threads = []
        for i in range(self.max_threads):
            thread = Thread(target=self.worker, args=(password_queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda conclusão ou senha encontrada
        try:
            while not self.stop_event.is_set() and any(thread.is_alive() for thread in threads):
                time.sleep(0.1)
                
                if password_queue.empty():
                    self.stop_event.set()
                    
        except KeyboardInterrupt:
            print("\n⏹️  Interrompido pelo usuário")
            self.stop_event.set()
        
        # Resultado final
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 50)
        print("RESULTADO DA BUSCA:")
        print(f"Tempo decorrido: {elapsed:.2f} segundos")
        print(f"Senhas testadas: {self.tested_passwords}")
        print(f"Velocidade média: {self.tested_passwords/elapsed:.2f} senhas/segundo")
        
        if self.found_password:
            print(f"✅ SENHA ENCONTRADA: '{self.found_password}'")
            return True
        else:
            print("❌ Senha não encontrada na wordlist")
            return False

def main():
    parser = argparse.ArgumentParser(description='Quebrador de senhas ZIP para estudo')
    parser.add_argument('zip_file', help='Arquivo ZIP protegido por senha')
    parser.add_argument('wordlist', help='Arquivo de wordlist com possíveis senhas')
    parser.add_argument('-t', '--threads', type=int, default=4, 
                       help='Número de threads (padrão: 4)')
    
    args = parser.parse_args()
    
    cracker = ZIPPasswordCracker(args.zip_file, args.wordlist, args.threads)
    cracker.crack()

if __name__ == "__main__":
    main()