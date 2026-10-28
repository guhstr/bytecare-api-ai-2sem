# Guia Completo de Execução Local — ByteCare (2º Semestre)

Este guia documenta o passo a passo exato e testado para configurar, compilar e executar todos os componentes do **ByteCare** em ambiente de desenvolvimento local Windows/Linux/macOS.

---

## 1. Pré-Requisitos de Ambiente

| Ferramenta | Versão Recomendada | Testada no Projeto |
| :--- | :--- | :--- |
| **Java JDK** | 17 LTS ou superior | OpenJDK 25.0.2 / 21 LTS |
| **Apache Maven** | 3.8+ (ou usar wrapper `./mvnw`) | Maven Wrapper incluído |
| **Python** | 3.10 a 3.14 | Python 3.14.3 com pip |
| **Node.js & npm** | Node 18+ / npm 9+ | Node v24.16.0 / npm 11.14.1 |
| **Android SDK & Emulator** | Android API 33+ / AVD Pixel 7 | Android Studio Ladybug/Otter, Pixel_7 API 34 |
| **Git** | 2.40+ | Git 2.54.0 |

---

## 2. Estrutura do Projeto Unificado

```
bytecare-api-ai-2sem/
├── ai/              # Microserviço de IA ByteCare Intelligence (Python FastAPI)
├── backend/         # Backend Central RESTful (Java Spring Boot 3.3.4 + Oracle)
├── mobile/          # Aplicativo Mobile Híbrido (React Native Expo 57)
├── docs/            # Documentação técnica, arquitetura, pitch e prints
└── README.md        # Documentação principal de entrega da GS
```

---

## 3. Passo a Passo de Execução

Recomenda-se abrir **3 abas de terminal** no PowerShell ou Bash para executar os serviços em paralelo.

### Terminal 1: Backend Central (Spring Boot — Porta 8080)

1. Navegue até a pasta do backend:
   ```powershell
   cd bytecare-api-ai-2sem/backend
   ```
2. *(Opcional)* Verifique a compilação e dependências:
   ```powershell
   .\mvnw.cmd test-compile
   ```
3. Inicie o servidor Spring Boot:
   ```powershell
   .\mvnw.cmd spring-boot:run
   ```
   *O backend inicializará na porta `8080`. Ele se conecta à instância Oracle Database da FIAP em `oracle.fiap.com.br:1521:ORCL`.*
4. **Verificação de Saúde do Backend:**
   Abra no navegador ou execute via PowerShell:
   ```powershell
   Invoke-RestMethod http://localhost:8080/health
   # Retorno esperado: {"status":"UP","service":"ByteCare Backend API","timestamp":...}
   ```

---

### Terminal 2: Microserviço de IA (FastAPI — Porta 8001)

1. Navegue até a pasta da IA:
   ```powershell
   cd bytecare-api-ai-2sem/ai
   ```
2. Crie e ative um ambiente virtual Python (recomendado):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
4. *(Opcional)* Configure a chave do Google Gemini no arquivo `.env`:
   ```env
   GEMINI_API_KEY=sua_chave_do_google_aistudio_aqui
   PORT=8001
   HOST=0.0.0.0
   ```
   > **Nota de Resiliência:** Se a chave não for configurada, o sistema entra automaticamente em modo Mock inteligente com 100% de paridade de esquema Pydantic, permitindo testar tudo offline!

5. Inicie o servidor FastAPI:
   ```powershell
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```
6. **Verificação de Saúde da IA:**
   ```powershell
   Invoke-RestMethod http://localhost:8001/api/v1/health
   # Retorno esperado: {"status":"ok","version":"1.0.0","service":"ByteCare Intelligence API"}
   ```

---

### Terminal 3: Configuração do Emulador Android e App Mobile

1. **Iniciar o Emulador Android:**
   Abra o Android Studio > Device Manager e inicie seu AVD (ex: `Pixel_7`), ou execute via terminal:
   ```powershell
   & "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd Pixel_7
   ```
2. **Configurar Redirecionamento de Portas ADB (Garante conectividade bidirecional):**
   ```powershell
   adb reverse tcp:8080 tcp:8080
   adb reverse tcp:8001 tcp:8001
   adb reverse tcp:8081 tcp:8081
   ```
3. **Instalar Dependências do Mobile:**
   Navegue até a pasta do mobile:
   ```powershell
   cd bytecare-api-ai-2sem/mobile
   npm install
   ```
4. **Iniciar o Expo Metro Bundler no Emulador:**
   ```powershell
   npx expo start --android
   ```
   *O Expo compilará o bundle e abrirá automaticamente o aplicativo no Pixel 7.*

---

## 4. Credenciais de Teste Homologadas

Ao abrir o app no emulador:
- **Usuário:** `admin`
- **Senha:** `123456`

---

## 5. Roteiro de Validação dos Casos de Uso

1. **Login e Acesso à Home:**
   - Faça login com `admin` / `123456`.
   - Observe o banner do **Assistente ByteCare IA** e as categorias (Pets, Agro, Pássaros).
2. **Navegação até o Animal:**
   - Clique em **Cães**.
   - Selecione o animal **BAU** (ou outro cadastrado).
   - Visualize os pilares clínicos (Preventivo, Terapêutico, Bem-estar) e os dois novos cards de inteligência artificial.
3. **Execução da Análise de Saúde (`AnaliseIA`):**
   - Clique em **ByteCare Intelligence**.
   - Observe o cálculo automático do risco (`BAIXA`), contadores de registros e recomendações longitudinais.
4. **Chatbot com Detecção de Emergência em Tempo Real (`ChatIA`):**
   - Clique em **Tirar Dúvidas com o Assistente ByteCare** ou no banner da Home.
   - Teste uma pergunta preventiva: *"Quais cuidados com filhotes?"*.
   - Teste a salvaguarda de urgência: digite *"O cachorro está convulsionando!"*.
   - Observe o **Alert Nativo de Emergência** disparado imediatamente pelo motor determinístico!

---

## 6. Execução dos Testes Automatizados

Para rodar a suíte completa de testes unitários do motor de regras e schemas da IA:
```powershell
cd bytecare-api-ai-2sem/ai
python -m unittest discover -s tests -v
```

Resultado esperado:
```
test_calculo_risco_normal (tests.test_risk_engine.TestRiskEngine) ... ok
test_calculo_risco_urgente (tests.test_risk_engine.TestRiskEngine) ... ok
test_deteccao_emergencia_texto (tests.test_risk_engine.TestRiskEngine) ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.003s

OK
```
