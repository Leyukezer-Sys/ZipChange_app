# 🔓 ZIP Password Cracker Pro

Uma aplicação moderna e sofisticada para recuperação de senhas de arquivos ZIP, desenvolvida com CustomTkinter para uma interface elegante e funcional.

## ✨ Características

- **Interface Moderna**: Design escuro com elementos visuais contemporâneos
- **Quebra de Senhas com Múltiplas Threads**: Suporte a até 16 threads simultâneas
- **Visualização em Tempo Real**: Gráfico de velocidade de teste de senhas
- **Estatísticas Detalhadas**: Monitoramento em tempo real do progresso
- **Limpeza Automática de Wordlists**: Remove senhas duplicadas e caracteres inválidos
- **Suporte a AES**: Compatível com arquivos ZIP criptografados com AES via pyzipper

## 📦 Requisitos

- Python 3.8 ou superior
- Dependências listadas no arquivo `requirements.txt`

## 🚀 Instalação

1. Clone ou baixe o projeto
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

Ou execute o script que instalará automaticamente as dependências necessárias.

## 📋 Como Usar

1. Execute o aplicativo:
```bash
python zip_cracker_pro.py
```

2. Selecione o arquivo ZIP protegido por senha
3. Selecione o arquivo de wordlist (lista de senhas para teste)
4. Ajuste o número de threads conforme a capacidade do seu processador
5. Clique em "Iniciar" para começar o processo de recuperação
6. Monitore o progresso nas abas "Output" e "Estatísticas"

## 🎯 Funcionalidades

### Painel Principal
- Seleção de arquivo ZIP e wordlist
- Controle de número de threads (1-16)
- Botões de Iniciar, Parar e Limpar

### Aba de Output
- Log detalhado de todas as operações
- Exibição das primeiras senhas da wordlist
- Resultados finais do processo

### Aba de Estatísticas
- Contador de senhas testadas
- Velocidade de testes por segundo
- Tempo decorrido
- Progresso percentual
- Gráfico de velocidade em tempo real

### Recursos Avançados
- Limpeza automática de wordlists (remove duplicatas e caracteres inválidos)
- Suporte a arquivos ZIP com criptografia AES
- Extração automática de arquivos após descoberta da senha
- Interface responsiva e moderna

## 🛠️ Tecnologias Utilizadas

- **CustomTkinter**: Interface gráfica moderna e elegante
- **PyZipper**: Manipulação de arquivos ZIP com suporte a AES
- **Matplotlib**: Visualização gráfica do desempenho
- **Threading**: Processamento paralelo para maior velocidade

## 📊 Performance

O desempenho varia de acordo com:
- Tamanho da wordlist
- Número de threads utilizadas
- Velocidade do processador
- Complexidade das senhas

## ⚠️ Notas Legais

Este software é destinado para:
- Recuperação de arquivos ZIP dos quais você é o legítimo proprietário
- Testes de segurança em sistemas próprios
- Fins educacionais sobre segurança e criptografia

Não utilize esta ferramenta para:
- Acessar arquivos de terceiros sem autorização
- Qualquer atividade ilegal

---

**Desenvolvido com Python e CustomTkinter** 🐍🎨