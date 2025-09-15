import pyzipper
import argparse
import time
from threading import Thread, Event
from queue import Queue
import os
import re

class ZIPPasswordCracker:
    def __init__(self, zip_file, wordlist_file, max_threads=4):
        self.zip_file = zip_file
        self.wordlist_file = wordlist_file
        self.max_threads = max_threads
        self.found_password = None
        self.stop_event = Event()
        self.tested_passwords = 0
        self.start_time = time.time()
        
    def clean_password(self, password):
        """Remove tabs, espaços extras e caracteres não imprimíveis"""
        # Remove tabs, espaços no início/fim e caracteres de controle
        cleaned = password.strip()
        # Remove tabs internos e múltiplos espaços
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # Remove qualquer caractere não imprimível
        cleaned = ''.join(char for char in cleaned if char.isprintable())
        return cleaned
        
    def test_password(self, zip_ref, password):
        """Tenta abrir o arquivo ZIP com uma senha usando pyzipper"""
        try:
            # Tenta extrair um arquivo pequeno para teste
            file_to_test = zip_ref.namelist()[0]
            with zip_ref.open(file_to_test, pwd=password.encode('utf-8')) as f:
                # Lê um pequeno trecho para verificar se a senha funciona
                f.read(1)
                return True
        except (RuntimeError, pyzipper.BadZipFile):
            return False
        except Exception as e:
            # Ignora outros erros e continua tentando
            return False
    
    def worker(self, password_queue):
        """Thread worker que testa senhas"""
        with pyzipper.AESZipFile(self.zip_file) as zip_ref:
            while not self.stop_event.is_set() and not password_queue.empty():
                try:
                    password = password_queue.get_nowait()
                    self.tested_passwords += 1
                    
                    if self.tested_passwords % 100 == 0:
                        elapsed = time.time() - self.start_time
                        print(f"Testadas {self.tested_passwords} senhas. "
                              f"Velocidade: {self.tested_passwords/elapsed:.2f} senhas/segundo")
                    
                    # Testa a senha
                    if self.test_password(zip_ref, password):
                        self.found_password = password
                        self.stop_event.set()
                        break
                        
                    password_queue.task_done()
                    
                except Exception as e:
                    break
    
    def read_and_clean_wordlist(self):
        """Lê e limpa a wordlist removendo tabs, espaços e quebras de linha"""
        cleaned_passwords = []
        original_count = 0
        
        try:
            with open(self.wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    original_count += 1
                    # Limpa a linha
                    cleaned_line = self.clean_password(line)
                    
                    if cleaned_line:
                        # Verifica se já não adicionamos esta senha (evita duplicatas)
                        if cleaned_line not in cleaned_passwords:
                            cleaned_passwords.append(cleaned_line)
            
            print(f"Linhas originais na wordlist: {original_count}")
            print(f"Senhas únicas após limpeza: {len(cleaned_passwords)}")
            
            return cleaned_passwords
            
        except Exception as e:
            print(f"Erro ao ler e limpar wordlist: {e}")
            return None
    
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
        
        # Lê e limpa a wordlist
        print("Limpando wordlist (removendo tabs, espaços e quebras de linha)...")
        passwords = self.read_and_clean_wordlist()
        
        if passwords is None:
            return False
        
        print(f"Total de senhas únicas após limpeza: {len(passwords):,}")
        print(f"Primeiras 10 senhas limpas: {passwords[:10]}")
        
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
        if elapsed > 0:
            print(f"Velocidade média: {self.tested_passwords/elapsed:.2f} senhas/segundo")
        
        if self.found_password:
            print(f"✅ SENHA ENCONTRADA: '{self.found_password}'")
            
            # Tenta extrair os arquivos com a senha encontrada
            try:
                with pyzipper.AESZipFile(self.zip_file) as zip_ref:
                    zip_ref.extractall(pwd=self.found_password.encode('utf-8'))
                    print(f"✅ Arquivos extraídos com sucesso!")
            except Exception as e:
                print(f"⚠️  Senha encontrada mas erro na extração: {e}")
            
            return True
        else:
            print("❌ Senha não encontrada na wordlist")
            
            # Verifica se todas as senhas foram testadas
            if self.tested_passwords < len(passwords):
                print(f"⚠️  Apenas {self.tested_passwords} de {len(passwords)} senhas foram testadas")
            else:
                print("ℹ️  Todas as senhas da wordlist foram testadas")
            
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