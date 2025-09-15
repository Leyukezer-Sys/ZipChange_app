# ZIP Password Cracker 🔓

Um quebrador de senhas para arquivos ZIP desenvolvido em Python, perfeito para estudos e recuperação de arquivos protegidos.

## 📋 Funcionalidades

- 🔍 Quebra de senhas ZIP usando wordlists
- 🧹 Limpeza automática de wordlists (remove tabs, espaços e quebras de linha)
- ⚡ Multi-threading para maior velocidade
- 📊 Estatísticas em tempo real (velocidade, senhas testadas)
- ✅ Suporte a métodos de compressão avançados (incluindo AES)
- 🖥️ Compatível com Windows e Linux

## 🛠️ Pré-requisitos

### Para Windows:

```bash
# Instale o Python (se ainda não tiver)
# Baixe em: https://python.org/downloads/

# Verifique a instalação
python --version
pip --version
```

### Para Linux (Ubuntu/Debian):

```bash
# Instale o Python e pip
sudo apt update
sudo apt install python3 python3-pip

# Verifique a instalação
python3 --version
pip3 --version
```

## 📦 Instalação

1. **Clone ou baixe o projeto**

```bash
# Via Git
git clone <url-do-repositorio>
cd ZipChange_app

# Ou baixe manualmente e extraia os arquivos
```

2. **Instale as dependências**

```bash
# Windows
pip install pyzipper

# Linux
pip3 install pyzipper
```

## 🚀 Como usar

### Sintaxe básica:

```bash
# Windows
python zipchange.py arquivo.zip wordlist.txt

# Linux
python3 zipchange.py arquivo.zip wordlist.txt
```

### Exemplos de uso:

**Uso básico (4 threads padrão):**

```bash
python zipchange.py arquivo_secreto.zip wordlist.txt
```

**Com número específico de threads:**

```bash
python zipchange.py arquivo_secreto.zip wordlist.txt -t 8
```

**Usando wordlist comum:**

```bash
python zipchange.py documento_protegido.zip rockyou.txt -t 6
```

### Parâmetros:

- `arquivo.zip` - Arquivo ZIP protegido por senha
- `wordlist.txt` - Arquivo com lista de senhas para testar
- `-t, --threads` - Número de threads (opcional, padrão: 4)

## 📁 Estrutura de arquivos

```
ZipChange_app/
├── zipchange.py          # Script principal
└── README.md            # Este arquivo
```

## 🗂️ Wordlists recomendadas

Algumas wordlists populares para uso:

1. **TOP500.txt** - 500 senhas mais comuns
2. **rockyou.txt** - Lista extensa com milhões de senhas
3. **custom_list.txt** - Sua lista personalizada

### Onde encontrar wordlists:

- [RockYou.txt](https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt)
- [Seclists](https://github.com/danielmiessler/SecLists)
- [Criar suas próprias wordlists](https://github.com/Mebus/cupp)

## ⚡ Melhores práticas

### Para melhor performance:

```bash
# Use mais threads para CPUs potentes
python zipchange.py arquivo.zip wordlist.txt -t 12

# Use wordlists organizadas (senhas mais prováveis primeiro)
# Wordlists limpas (sem caracteres especiais) funcionam melhor
```

### Para wordlists grandes:

```bash
# Divida wordlists muito grandes em partes
split -l 1000000 rockyou.txt rockyou_part_

# Execute em paralelo se necessário
python zipchange.py arquivo.zip rockyou_part_aa.txt -t 8
python zipchange.py arquivo.zip rockyou_part_ab.txt -t 8
```

## 📊 Exemplo de saída

```
Iniciando quebra de senha para: arquivo_secreto.zip
Usando wordlist: TOP500.txt
Threads: 4
--------------------------------------------------
Limpando wordlist (removendo tabs, espaços e quebras de linha)...
Linhas originais na wordlist: 602
Senhas únicas após limpeza: 556
Total de senhas únicas após limpeza: 556
Primeiras 10 senhas limpas: ['123456', 'password', '123456789', ...]

Testadas 100 senhas. Velocidade: 1250.50 senhas/segundo
Testadas 200 senhas. Velocidade: 1350.75 senhas/segundo

==================================================
RESULTADO DA BUSCA:

✅ SENHA ENCONTRADA: 'matrix'
✅ Arquivos extraídos com sucesso!

Tempo decorrido: 0.45 segundos
Senhas testadas: 288
Velocidade média: 640.00 senhas/segundo
✅ OPERAÇÃO CONCLUÍDA COM SUCESSO!
```

## 🐛 Solução de problemas

### Erro comum: `ModuleNotFoundError: No module named 'pyzipper'`

**Solução:**

# Windows

```bash
pip install pyzipper
```

# Linux

```bash
pip3 install pyzipper

# Se ainda não funcionar
python -m pip install pyzipper
```

### Erro: `That compression method is not supported`

**Solução:** O script já usa pyzipper que suporta mais métodos de compressão.

### Performance lenta:

**Soluções:**

- Aumente o número de threads: `-t 8`
- Use wordlists menores primeiro
- Verifique se a wordlist está limpa

## ⚠️ Aviso legal

Este software é destinado apenas para:

- ✅ Estudos educacionais de segurança
- ✅ Recuperação de arquivos pessoais esquecidos
- ✅ Testes de penetração autorizados

**NÃO USE** para:

- ❌ Acessar arquivos de outras pessoas sem permissão
- ❌ Qualquer atividade ilegal
- ❌ Violar privacidade alheia

O uso deste software para atividades ilegais é de sua total responsabilidade.
