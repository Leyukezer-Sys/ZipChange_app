#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <thread>
#include <chrono>
#include <atomic>
#include <cstdlib>

// Bibliotecas para interface gráfica (FLTK)
#include <FL/Fl.H>
#include <FL/Fl_Window.H>
#include <FL/Fl_Button.H>
#include <FL/Fl_Input.H>
#include <FL/Fl_Output.H>
#include <FL/Fl_Text_Display.H>
#include <FL/Fl_Text_Buffer.H>
#include <FL/Fl_Progress.H>
#include <FL/Fl_Box.H>
#include <FL/Fl_Native_File_Chooser.H>
#include <FL/fl_ask.H>

#ifdef _WIN32
    #include <windows.h>
    #include <minizip/unzip.h>
    #pragma comment(lib, "fltk.lib")
    #pragma comment(lib, "comctl32.lib")
#else
    #include <unzip.h>
    #include <zlib.h>
#endif

using namespace std;
using namespace std::chrono;

// Variáveis globais para a interface
Fl_Window* window;
Fl_Input* zipInput;
Fl_Input* wordlistInput;
Fl_Button* browseZipButton;
Fl_Button* browseWordlistButton;
Fl_Button* startButton;
Fl_Button* stopButton;
Fl_Text_Display* logDisplay;
Fl_Text_Buffer* logBuffer;
Fl_Progress* progressBar;
Fl_Output* statusOutput;
Fl_Output* attemptsOutput;
Fl_Output* timeOutput;

// Variáveis para controle da thread
atomic<bool> stopRequested(false);
thread crackingThread;

// Função para adicionar mensagem ao log
void addToLog(const string& message) {
    Fl::lock();
    logBuffer->append(message.c_str());
    logBuffer->append("\n");
    logDisplay->scroll(logBuffer->length(), 0);
    Fl::awake();
    Fl::unlock();
}

// Função para testar senha
bool testPassword(const string& zipPath, const string& password) {
    unzFile zipFile = unzOpen(zipPath.c_str());
    if (!zipFile) {
        addToLog("Erro: Não foi possível abrir o arquivo ZIP");
        return false;
    }

    // Tenta abrir o primeiro arquivo dentro do ZIP
    int result = unzOpenCurrentFilePassword(zipFile, password.c_str());
    
    if (result == UNZ_OK) {
        // Senha correta - fecha o arquivo e retorna true
        unzCloseCurrentFile(zipFile);
        unzClose(zipFile);
        return true;
    }
    
    // Fecha o arquivo em caso de erro
    if (result != UNZ_BADPASSWORD) {
        unzCloseCurrentFile(zipFile);
    }
    unzClose(zipFile);
    
    return false;
    
    // Simulação: supondo que a senha seja "password123"
    //this_thread::sleep_for(milliseconds(1)); // Simula tempo de verificação
    //return password == "password123";
}

// Função principal de cracking
void crackPassword(const string& zipPath, const string& wordlistPath) {
    stopRequested = false;
    
    ifstream wordlistFile(wordlistPath);
    if (!wordlistFile.is_open()) {
        addToLog("Erro: Não foi possível abrir a wordlist!");
        return;
    }

    addToLog("Iniciando quebra de senha...");
    addToLog("Arquivo: " + zipPath);
    addToLog("Wordlist: " + wordlistPath);
    addToLog("-----------------------------------");

    auto startTime = high_resolution_clock::now();
    string password;
    int attempts = 0;
    int totalPasswords = 0;

    // Contar total de senhas na wordlist
    ifstream countFile(wordlistPath);
    while (getline(countFile, password)) {
        totalPasswords++;
    }
    countFile.close();

    wordlistFile.clear();
    wordlistFile.seekg(0);

    if (totalPasswords == 0) {
        addToLog("Erro: Wordlist vazia!");
        return;
    }

    addToLog("Total de senhas para testar: " + to_string(totalPasswords));

    // Loop principal de teste de senhas
    while (getline(wordlistFile, password) && !stopRequested) {
        attempts++;
        
        // Atualizar interface a cada 100 tentativas
        if (attempts % 100 == 0) {
            Fl::lock();
            attemptsOutput->value(to_string(attempts).c_str());
            
            auto currentTime = high_resolution_clock::now();
            auto elapsed = duration_cast<seconds>(currentTime - startTime);
            timeOutput->value(to_string(elapsed.count()).c_str());
            
            progressBar->value((attempts * 100.0) / totalPasswords);
            Fl::awake();
            Fl::unlock();
        }

        if (testPassword(zipPath, password)) {
            auto endTime = high_resolution_clock::now();
            auto duration = duration_cast<seconds>(endTime - startTime);
            
            string successMsg = "✅ SENHA ENCONTRADA: " + password;
            string attemptsMsg = "Tentativas: " + to_string(attempts);
            string timeMsg = "Tempo: " + to_string(duration.count()) + " segundos";
            
            addToLog(successMsg);
            addToLog(attemptsMsg);
            addToLog(timeMsg);
            
            Fl::lock();
            statusOutput->value("Senha encontrada!");
            progressBar->value(100);
            Fl::awake();
            Fl::unlock();
            
            wordlistFile.close();
            return;
        }
    }

    wordlistFile.close();
    
    if (stopRequested) {
        addToLog("Operação interrompida pelo usuário");
        Fl::lock();
        statusOutput->value("Interrompido");
        Fl::awake();
        Fl::unlock();
    } else {
        addToLog("❌ Senha não encontrada na wordlist");
        Fl::lock();
        statusOutput->value("Senha não encontrada");
        Fl::awake();
        Fl::unlock();
    }
}

// Callbacks para os botões
void browseZipCallback(Fl_Widget* widget, void* data) {
    Fl_Native_File_Chooser chooser;
    chooser.title("Selecionar arquivo ZIP");
    chooser.type(Fl_Native_File_Chooser::BROWSE_FILE);
    chooser.filter("ZIP Files\t*.zip");
    
    if (chooser.show() == 0) {
        zipInput->value(chooser.filename());
    }
}

void browseWordlistCallback(Fl_Widget* widget, void* data) {
    Fl_Native_File_Chooser chooser;
    chooser.title("Selecionar wordlist");
    chooser.type(Fl_Native_File_Chooser::BROWSE_FILE);
    chooser.filter("Text Files\t*.txt");
    
    if (chooser.show() == 0) {
        wordlistInput->value(chooser.filename());
    }
}

void startCallback(Fl_Widget* widget, void* data) {
    string zipPath = zipInput->value();
    string wordlistPath = wordlistInput->value();
    
    if (zipPath.empty() || wordlistPath.empty()) {
        fl_alert("Por favor, selecione um arquivo ZIP e uma wordlist.");
        return;
    }
    
    // Verificar se os arquivos existem
    ifstream zipFile(zipPath);
    if (!zipFile.good()) {
        fl_alert("Arquivo ZIP não encontrado!");
        return;
    }
    zipFile.close();
    
    ifstream wordlistFile(wordlistPath);
    if (!wordlistFile.good()) {
        fl_alert("Wordlist não encontrada!");
        return;
    }
    wordlistFile.close();
    
    // Reiniciar interface
    logBuffer->text("");
    attemptsOutput->value("0");
    timeOutput->value("0");
    statusOutput->value("Executando...");
    progressBar->value(0);
    
    // Desabilitar botões durante a execução
    startButton->deactivate();
    stopButton->activate();
    browseZipButton->deactivate();
    browseWordlistButton->deactivate();
    
    // Iniciar thread de cracking
    crackingThread = thread([zipPath, wordlistPath]() {
        crackPassword(zipPath, wordlistPath);
        
        Fl::lock();
        startButton->activate();
        stopButton->deactivate();
        browseZipButton->activate();
        browseWordlistButton->activate();
        Fl::awake();
        Fl::unlock();
    });
    
    crackingThread.detach();
}

void stopCallback(Fl_Widget* widget, void* data) {
    stopRequested = true;
    addToLog("Solicitando interrupção...");
}

// Função para criar a interface
void createGUI() {
    window = new Fl_Window(600, 500, "Zip Password Cracker");
    window->begin();
    
    // Título
    Fl_Box* titleBox = new Fl_Box(20, 10, 560, 30, "🔓 Zip Password Cracker");
    titleBox->labelfont(FL_BOLD);
    titleBox->labelsize(18);
    titleBox->align(FL_ALIGN_CENTER);
    
    // Entrada do arquivo ZIP
    Fl_Box* zipLabel = new Fl_Box(20, 50, 100, 25, "Arquivo ZIP:");
    zipLabel->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    
    zipInput = new Fl_Input(120, 50, 350, 25);
    browseZipButton = new Fl_Button(480, 50, 100, 25, "Procurar");
    browseZipButton->callback(browseZipCallback);
    
    // Entrada da wordlist
    Fl_Box* wordlistLabel = new Fl_Box(20, 85, 100, 25, "Wordlist:");
    wordlistLabel->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    
    wordlistInput = new Fl_Input(120, 85, 350, 25);
    browseWordlistButton = new Fl_Button(480, 85, 100, 25, "Procurar");
    browseWordlistButton->callback(browseWordlistCallback);
    
    // Botões de controle
    startButton = new Fl_Button(150, 120, 120, 30, "Iniciar");
    startButton->callback(startCallback);
    
    stopButton = new Fl_Button(290, 120, 120, 30, "Parar");
    stopButton->callback(stopCallback);
    stopButton->deactivate();
    
    // Área de status
    Fl_Box* statusLabel = new Fl_Box(20, 160, 100, 25, "Status:");
    statusLabel->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    
    statusOutput = new Fl_Output(120, 160, 200, 25);
    statusOutput->value("Pronto");
    
    Fl_Box* attemptsLabel = new Fl_Box(330, 160, 100, 25, "Tentativas:");
    attemptsLabel->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    
    attemptsOutput = new Fl_Output(430, 160, 150, 25);
    attemptsOutput->value("0");
    
    Fl_Box* timeLabel = new Fl_Box(20, 190, 100, 25, "Tempo (s):");
    timeLabel->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    
    timeOutput = new Fl_Output(120, 190, 200, 25);
    timeOutput->value("0");
    
    // Barra de progresso
    Fl_Box* progressLabel = new Fl_Box(20, 220, 100, 25, "Progresso:");
    progressLabel->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    
    progressBar = new Fl_Progress(120, 220, 460, 25);
    progressBar->minimum(0);
    progressBar->maximum(100);
    
    // Área de log
    Fl_Box* logLabel = new Fl_Box(20, 255, 100, 25, "Log:");
    logLabel->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    
    logBuffer = new Fl_Text_Buffer();
    logDisplay = new Fl_Text_Display(20, 280, 560, 200);
    logDisplay->buffer(logBuffer);
    logDisplay->textfont(FL_COURIER);
    
    window->end();
    window->show();
}

int main(int argc, char** argv) {
    Fl::lock(); // Necessário para threads com FLTK
    
    createGUI();
    addToLog("Zip Password Cracker inicializado.");
    addToLog("Selecione um arquivo ZIP e uma wordlist para começar.");
    
    return Fl::run();
}