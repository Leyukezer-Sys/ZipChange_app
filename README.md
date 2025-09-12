# ZipChange App 🔓

Um programa em C++ com interface gráfica para quebrar senhas de arquivos ZIP usando wordlists.

## 📋 Pré-requisitos

### Para Linux:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install libfltk1.3-dev libminizip-dev zlib1g-dev g++ make

# Fedora
sudo dnf install fltk-devel minizip-devel zlib-devel gcc-c++ make

# Arch Linux
sudo pacman -S fltk minizip zlib gcc make
```

### Para Windows:
1. Instale [MSYS2](https://www.msys2.org/)
2. Execute o MSYS2 MinGW 64-bit shell
3. Instale as dependências:
```bash
pacman -Syu
pacman -S mingw-w64-x86_64-fltk mingw-w64-x86_64-minizip mingw-w64-x86_64-zlib mingw-w64-x86_64-toolchain
```

## 🚀 Compilação

### Linux:
```bash
# Torne o script de compilação executável
chmod +x compile_linux.sh

# Execute o script de compilação
./compile_linux.sh
```

### Windows:
1. Abra o MSYS2 MinGW 64-bit shell
2. Navegue até o diretório do projeto
3. Execute:
```bash
# Compilar manualmente
g++ -o zipcracker.exe main.cpp -std=c++17 -IC:/msys64/mingw64/include -LC:/msys64/mingw64/lib -lfltk -lminizip -lz -lole32 -luuid -lcomctl32 -lpthread

# Ou execute o script batch (se disponível)
compile_windows.bat
```

## 🎯 Como Usar

1. **Execute o programa**:
   - Linux: `./zipcracker`
   - Windows: `zipcracker.exe`

2. **Interface gráfica**:
   - Clique em "Procurar" para selecionar um arquivo ZIP
   - Clique em "Procurar" para selecionar uma wordlist (arquivo de texto com senhas)
   - Clique em "Iniciar" para começar o processo de quebra de senha
   - Use "Parar" para interromper a qualquer momento

3. **Acompanhamento**:
   - A barra de progresso mostra o andamento
   - O log exibe informações detalhadas do processo
   - Os contadores mostram tentativas e tempo decorrido

## 📁 Estrutura de Arquivos

```
zip-cracker/
├── main.cpp          # Código fonte principal
├── compile_linux.sh  # Script de compilação para Linux
├── compile_windows.bat # Script de compilação para Windows
├── zipcracker        # Executável (Linux, após compilação)
├── zipcracker.exe    # Executável (Windows, após compilação)
└── README.md         # Este arquivo
```

## 🔧 Solução de Problemas

### Erros Comuns no Linux:
```bash
# Erro: "fltk-config not found"
sudo apt-get install libfltk1.3-dev

# Erro: "minizip/unzip.h not found"
sudo apt-get install libminizip-dev

# Erro de linking
sudo apt-get install zlib1g-dev
```

### Erros Comuns no Windows:
- Certifique-se de estar usando o **MSYS2 MinGW 64-bit shell**
- Verifique se todas as dependências foram instaladas corretamente
- Se necessário, adicione `C:\msys64\mingw64\bin` ao seu PATH

### Problemas de Execução:
```bash
# No Windows, se faltar DLLs:
cp /mingw64/bin/libfltk.dll .
cp /mingw64/bin/libminizip.dll .
cp /mingw64/bin/zlib1.dll .
```

## 📝 Notas Importantes

1. Este programa é para fins **educacionais e de recuperação de dados próprios**
2. Use apenas em arquivos dos quais você tem permissão para testar
3. O desempenho depende do tamanho da wordlist e da complexidade da senha
4. Para melhores resultados, use wordlists específicas para o contexto

## 🤝 Contribuindo

Se encontrar problemas ou tiver sugestões:
1. Verifique se todas as dependências estão instaladas
2. Confirme que está usando o shell/terminal correto
3. Reporte issues com informações detalhadas do seu sistema

## 📄 Licença

Este projeto é para fins educacionais. Use com responsabilidade.

---

**⚠️ Aviso Legal**: Use este software apenas para recuperar acesso a arquivos dos quais você é o legítimo proprietário. O uso não autorizado é ilegal.