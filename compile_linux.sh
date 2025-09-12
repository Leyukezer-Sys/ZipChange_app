#!/bin/bash

echo "Compilando Zip Password Cracker para Linux..."

# Instalar dependências se necessário
if ! command -v fltk-config &> /dev/null; then
    echo "Instalando FLTK..."
    sudo apt-get install libfltk1.3-dev
fi

if ! command -v unzip &> /dev/null; then
    echo "Instalando unzip..."
    sudo apt-get install unzip
fi

# Compilar o programa
g++ -o zipcracker main.cpp -std=c++17 $(fltk-config --cxxflags) $(fltk-config --ldflags) -lz -lpthread

if [ $? -eq 0 ]; then
    echo "Compilação concluída com sucesso!"
    echo "Execute o programa com: ./zipcracker"
else
    echo "Erro durante a compilação."
fi