# ZIP Password Cracker 🔓

Um programa em Python para fins educacionais que demonstra como realizar quebra de senhas em arquivos ZIP usando wordlists (listas de palavras).

## ⚠️ AVISO LEGAL

**ESTE PROGRAMA É APENAS PARA FINS EDUCACIONAIS E DE TESTE DE SEGURANÇA.**

- Use apenas em arquivos ZIP dos quais você é o proprietário
- Nunca utilize para violar a privacidade ou propriedade de terceiros
- Respeite as leis locais de privacidade e propriedade intelectual

## 📋 Pré-requisitos

- Python 3.6 ou superior
- Arquivo ZIP protegido por senha
- Arquivo de wordlist (lista de senhas possíveis)

## 🚀 Como usar

### Sintaxe básica:

```bash
python zipchange.py <arquivo_zip> <wordlist> [--threads NUM]
```

### Exemplos:

#### Exemplo 1 - Uso básico:

```bash
python zipchange.py arquivo_protegido.zip wordlist.txt
```

#### Exemplo 2 - Com múltiplas threads (mais rápido):

```bash
python zipchange.py arquivo_protegido.zip wordlist.txt --threads 8
```

#### Exemplo 3 - Usando caminhos relativos:

```bash
python zipchange.py ./documentos/arquivo.zip ./wordlists/rockyou.txt -t 4
```

## 📁 Estrutura de arquivos

```
projeto/
├── zipchange.py          # Programa principal
└── README.md            # Este arquivo
```

## ⚡ Parâmetros do programa

| Parâmetro       | Descrição                            | Valor padrão  |
| --------------- | ------------------------------------ | ------------- |
| `arquivo_zip`   | Caminho para o arquivo ZIP protegido | (obrigatório) |
| `wordlist`      | Caminho para o arquivo de wordlist   | (obrigatório) |
| `-t, --threads` | Número de threads para paralelismo   | `4`           |

## 📈 Funcionalidades

- ✅ **Multi-threading** para maior velocidade
- ✅ **Barra de progresso** com estatísticas em tempo real
- ✅ **Tratamento de erros** robusto
- ✅ **Compatível** com diferentes encodings de arquivo
- ✅ **Interrupção segura** com Ctrl+C
- ✅ **Relatório detalhado** de performance ao final

## 🎯 Exemplo de saída

```
Iniciando quebra de senha para: arquivo_protegido.zip
Usando wordlist: wordlist.txt
Threads: 4
--------------------------------------------------
Total de senhas na wordlist: 10,000

Testadas 1000 senhas. Velocidade: 850.32 senhas/segundo
Testadas 2000 senhas. Velocidade: 880.15 senhas/segundo

✅ SENHA ENCONTRADA: minhasenha

==================================================
RESULTADO DA BUSCA:
Tempo decorrido: 12.45 segundos
Senhas testadas: 2345
Velocidade média: 188.35 senhas/segundo
✅ SENHA ENCONTRADA: 'minhasenha'
```

## 🔍 Dicas para uso eficiente

1. **Ordene sua wordlist** - Coloque as senhas mais prováveis no início
2. **Use threads adequadas** - 4-8 threads geralmente é o ideal
3. **Wordlists grandes** - Para listas muito grandes, considere filtrar senhas irrelevantes
4. **Monitoramento** - O programa mostra progresso a cada 1000 tentativas

## 🛠️ Solução de problemas

### Erro: "Arquivo ZIP não encontrado"

- Verifique o caminho do arquivo
- Use caminhos absolutos se necessário

### Erro: "Wordlist não encontrada"

- Confirme que o arquivo de wordlist existe
- Verifique permissões de leitura

### Erro de encoding:

- O programa trata automaticamente diferentes encodings
- Para wordlists problemáticas, tente salvar como UTF-8

### Desempenho lento:

- Aumente o número de threads com `--threads`
- Verifique a performance do seu disco e CPU

## 📚 Aprendizados educacionais

Este programa demonstra:

- Manipulação de arquivos ZIP em Python
- Programação multi-threaded
- Tratamento de exceções
- Parsing de argumentos de linha de comando
- Leitura e processamento de grandes arquivos
- Cálculo de performance e estatísticas

## ⚠️ Limitações conhecidas

- Funciona apenas com arquivos ZIP tradicionais (não ZIP criptografado AES)
- A velocidade depende muito do hardware
- Não inclui técnicas avançadas como rainbow tables

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs
- Sugerir melhorias
- Adicionar novas funcionalidades

---

**Lembre-se: Use sempre de forma ética e responsável!** 🔐
