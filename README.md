# ByteCare Intelligence — Microserviço de IA Generativa & Preditiva

<div align="center">

![ByteCare Architecture](docs/arquitetura.png)

**Global Solution 2º Semestre — FIAP**  
*Disciplina: Disruptive Architectures: IoT, IoB & Generative IA*  
*Repositório Oficial do Serviço de IA: `bytecare-api-ai-2sem`*

[![Python 3.14](https://img.shields.io/badge/Python-3.14%20%7C%203.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.0-e92063.svg)](https://docs.pydantic.dev/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4.svg)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Unit_Tests-Passing%20(100%25)-success.svg)]()
[![CFMV Compliant](https://img.shields.io/badge/CFMV%201.488%2F2022-Compliant-green.svg)]()

---

### 🔗 Links Oficiais da Entrega
**Repositório GitHub:** [https://github.com/Gutemberg149/bytecare-api-ai-2sem](https://github.com/Gutemberg149/bytecare-api-ai-2sem)  
*(Mirror alternativo: [https://github.com/guhstr/bytecare-api-ai-2sem](https://github.com/guhstr/bytecare-api-ai-2sem))*  
**Vídeo Pitch no YouTube (Não Listado):** [https://youtu.be/SEU_VIDEO_AQUI](https://youtu.be/SEU_VIDEO_AQUI) *(Roteiro completo de 5 min disponível em [docs/VIDEO_PITCH_SCRIPT.md](docs/VIDEO_PITCH_SCRIPT.md))*

</div>

---

## 📋 Sumário do Projeto

O **`bytecare-api-ai-2sem`** é o microserviço de inteligência artificial dedicado do ecossistema **ByteCare**. Construído em **Python com FastAPI**, ele é responsável por processar o histórico anamnésico dos animais cadastrados (provenientes do backend Java e consumidos pelo aplicativo mobile Expo) e fornecer:

1. **Análise Clínica Longitudinal com Cálculo Determinístico de Risco:** Avalia os três pilares clínicos (**Preventivo**, **Terapêutico** e **Bem-estar**) e consolida o histórico em scores matemáticos, identificando vacinas atrasadas e sinais de alerta.
2. **Chatbot de Triagem & Assistência Virtual em Tempo Real:** Conduz diálogos empáticos e contextualizados para a espécie do animal, aplicando salvaguardas veterinárias imediatas com detecção determinística de emergência médica.
3. **Resiliência e Fallback Seguro com Mock Integrado:** Caso a chave da API do Google Gemini não seja fornecida ou haja timeout de rede, a API aciona automaticamente um gerador sintético determinístico com **100% de paridade de esquema Pydantic**, garantindo que a aplicação nunca fique indisponível.

---

## 🏛️ Estrutura do Repositório

O repositório segue rigorosamente o padrão modular da aplicação de inteligência artificial:

```
bytecare-api-ai-2sem/
├── app/
│   ├── __init__.py
│   ├── chat_service.py       # Orquestração do chatbot, controle de histórico e salvaguardas
│   ├── gemini_service.py     # Integração oficial com Google Gemini 2.5 Flash via SDK google-genai
│   ├── main.py               # Servidor FastAPI e rotas REST (/health, /analises, /chat)
│   ├── mock_service.py       # Fallback mock determinístico com 100% de paridade Pydantic
│   ├── prompt.py             # System Prompts, Guardrails éticos e contexto multiespécie
│   ├── risk_engine.py        # Motor de Regras Determinístico e cálculo de scores vitais
│   └── schemas.py            # Modelos estruturados e tipados com Pydantic v2
├── tests/
│   ├── test_risk_engine.py   # Testes unitários do motor de regras e prioridades
│   ├── analiseDoHistorico.png# Evidência de teste da análise
│   ├── avaliacaoDoAnimal.png # Evidência de teste de avaliação
│   ├── cadastroDeVacina.png  # Evidência de teste de vacinação
│   └── proteção.png          # Evidência de teste de guardrail
├── docs/
│   ├── ARCHITECTURE.md       # Arquitetura técnica detalhada, justificativa e matriz multiespécie
│   ├── VIDEO_PITCH_SCRIPT.md # Roteiro de 5 minutos do vídeo pitch (rubrica do GS.pdf)
│   ├── LOCAL_SETUP.md        # Manual de execução local passo a passo
│   ├── arquitetura.png       # Diagrama de blocos
│   └── screenshots/          # Capturas reais do app mobile integrado à IA no emulador Android
├── requirements.txt          # Dependências Python estritas
├── .env.example              # Exemplo de variáveis de ambiente
├── .env                      # Configuração local (fallback mock ou chave Gemini)
├── .gitignore                # Ignora __pycache__, ambientes virtuais e logs
├── SUBMISSION_LINKS.txt      # Arquivo oficial com os links para entrega da FIAP
└── README.md                 # Esta documentação
```

---

## 🧠 Arquitetura Técnica de IA (Critérios da GS)

### 1. Por que uma Arquitetura Híbrida de IA?
Modelos de linguagem generativos (LLMs) são probabilísticos. Em saúde animal, uma resposta imprecisa ou alucinada pode induzir o tutor ao erro e custar a vida de um animal.

Para atender à **Resolução CFMV nº 1.488/2022** do Conselho Federal de Medicina Veterinária, o ByteCare implementou uma **Arquitetura Híbrida de Dois Níveis**:

```
[Dados do Histórico ou Mensagem do Usuário]
                     │
                     ▼
  ┌─────────────────────────────────────────────────────────┐
  │    NÍVEL 1: MOTOR DETERMINÍSTICO (risk_engine.py)       │
  │    - Regras booleanas e pontuação matemática objetiva   │
  │    - Detecção de palavras-chave vitais de emergência:   │
  │      convulsão, hemorragia, atropelamento, choque, etc. │
  │    - Score mínimo de risco: NORMAL, MODERADO ou URGENTE │
  │    - Imune a manipulação via Prompt Injection           │
  └──────────────────────────┬──────────────────────────────┘
                             │ Nível de Risco & Flags Travadas
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │     NÍVEL 2: IA GENERATIVA COM GUARDRAILS (Gemini)      │
  │    - Google Gemini 2.5 Flash com Structured Outputs     │
  │    - System Prompt rigoroso com restrições veterinárias │
  │    - Proibição de diagnóstico conclusivo e prescrição   │
  │    - Fallback transparente para Mock Service            │
  └──────────────────────────┬──────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │         VALIDAÇÃO E SERIALIZAÇÃO PYDANTIC v2            │
  │    - AnaliseSaudeResponse / ChatResponse tipados        │
  └─────────────────────────────────────────────────────────┘
```

### 2. Motor de Regras Determinístico (`risk_engine.py`)
- **Regra de Vacinas:** Se houver vacinas com mais de 365 dias sem reforço ou sem data, adiciona pontuação de risco e sinaliza necessidade preventiva.
- **Regra de Emergência:** Se o texto do tutor contiver termos como *convulsão*, *sangramento abundante*, *atropelado*, *cianose* ou *inconsciente*, a prioridade é forçada para `URGENTE`, ativando `procurar_veterinario = true`.
- **Regra de Prioridade Máxima:** O LLM **nunca pode rebaixar a prioridade** calculada pelo motor de regras.

### 3. Guardrails Veterinários (`prompt.py`)
- **Recusa de Diagnóstico:** A IA nunca afirma categoricamente a patologia; utiliza termos orientativos.
- **Proibição de Medicamentos:** Jamais receita fármacos com tarja, anti-inflamatórios ou antibióticos.
- **Disclaimer Obrigatório:** Toda saída contém a advertência formal de que a IA apoia o acompanhamento, mas **não substitui o médico-veterinário**.

---

## 🐶 Matriz de Personalização Multiespécie

| Categoria | Espécie | Foco Clínico e Sanitário | Comportamento da IA |
| :--- | :--- | :--- | :--- |
| **Pets** | Cães | V8/V10, Antirrábica, controle de ectoparasitas e torção gástrica. | Empático, foco na rotina do tutor e passeios. |
| **Pets** | Gatos | Vacina Quádrupla/Quíntupla (FeLV), estresse urinário e hidratação. | Focado em sutilezas comportamentais e enriquecimento. |
| **Agro** | Bovinos | Aftosa, Brucelose, Clostridioses, controle de mastite e ruminação. | Técnico, zootécnico e focado em sanidade do lote. |
| **Agro** | Equinos | Tétano, Influenza, Encefalomielite e alerta absoluto para cólica. | Alerta imediato e rigoroso para dor abdominal ou claudicação. |
| **Pássaros** | Aves | Higiene de gaiola, respiração com bico aberto e prostração. | Sensível à rápida evolução de quadros clínicos em aves. |
| **Pets** | Peixes | Parâmetros de água (pH, amônia tóxica, nitrito e temperatura). | Educativo sobre química da água e ciclagem de aquário. |

---

## 📡 Especificação da API REST (Endpoints)

### 1. `GET /api/v1/health`
Retorna a integridade do microserviço.
```json
{
  "status": "ok",
  "version": "1.0.0",
  "service": "ByteCare Intelligence API"
}
```

### 2. `POST /api/v1/analises`
Consolida os registros clínicos do animal e retorna a análise longitudinal estruturada.
* **Corpo da Requisição:** `AnaliseSaudeRequest` (animal, preventivos, terapeuticos, bem_estar).
* **Resposta:** `AnaliseSaudeResponse` contendo:
  - `prioridade`: `baixa`, `moderada` ou `urgente`
  - `resumo_clinico`: Síntese concisa do histórico
  - `fatores_atencao`: Lista de itens que demandam cuidado
  - `proximos_passos`: Ações preventivas recomendadas
  - `aviso_seguranca`: Disclaimer ético obrigatório
  - `modo`: `gemini` ou `mock`

### 3. `POST /api/v1/chat`
Processa mensagens no chatbot com histórico de conversa e contexto ativo do animal.
* **Corpo da Requisição:** `ChatRequest` (mensagem, historico, animal, preventivos, etc.).
* **Resposta:** `ChatResponse` contendo:
  - `resposta`: Texto humanizado e empático
  - `nivel_atencao`: `normal`, `atencao` ou `urgente`
  - `procurar_veterinario`: Booleano (dispara alerta nativo no app quando `true`)
  - `aviso_seguranca`: Salvaguarda regulatória
  - `acao`: `duvida_geral`, `triagem`, `cadastro_vacina` ou `cadastro_animal`

---

## 🚀 Como Executar Localmente

### 1. Pré-Requisitos
- Python 3.10 ou superior (testado com Python 3.14.3)
- Gerenciador de pacotes `pip`

### 2. Instalação
```powershell
# Acesse o diretório do repositório
cd C:\Users\labsfiap\Desktop\challenge\bytecare-api-ai-2sem

# Crie e ative o ambiente virtual (opcional, recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração de Ambiente (`.env`)
O arquivo `.env` pode ser configurado com sua chave da Google AI Studio:
```env
GEMINI_API_KEY=sua_chave_do_google_aistudio_aqui
PORT=8001
HOST=0.0.0.0
```
> **Nota de Resiliência:** Se `GEMINI_API_KEY` for omitida ou deixada em branco, o serviço entra automaticamente em modo **Mock Inteligente**, mantendo paridade estrita de dados e permitindo o uso completo do sistema offline.

### 4. Inicialização do Servidor
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

O serviço estará ativo em:
- **API Base:** `http://localhost:8001/api/v1`
- **Documentação Interativa Swagger:** `http://localhost:8001/docs`
- **Documentação Redoc:** `http://localhost:8001/redoc`

---

## 🧪 Testes Automatizados

Para executar a suíte de testes unitários do motor determinístico e dos guardrails:
```powershell
python -m unittest discover -s tests -v
```

Resultado:
```
test_llm_cannot_lower_priority (test_risk_engine.RiskEngineTests) ... ok
test_respiratory_red_flag_sets_urgent (test_risk_engine.RiskEngineTests) ... ok
test_therapeutic_context_sets_moderate_minimum (test_risk_engine.RiskEngineTests) ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
```

---

## 📱 Integração com o Aplicativo Mobile e Backend

Este microserviço é consumido diretamente pelo aplicativo mobile ByteCare no emulador Android através de:
- `http://10.0.2.2:8001/api/v1` (ou `http://localhost:8001/api/v1` com `adb reverse tcp:8001 tcp:8001`).

### Evidências da Execução no Emulador Android:
<div align="center">

| Tela de Análise Longitudinal (`AnaliseIA.jsx`) | Chat com Detecção de Urgência (`ChatIA.jsx`) |
| :---: | :---: |
| ![Análise IA](docs/screenshots/screen_analise_ia.png) | ![Chat Urgente](docs/screenshots/screen_chat_urgente.png) |

</div>

---

## 👥 Equipe e Submissão FIAP

- **Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA
- **Repositório Unificado:** [`bytecare-api-ai-2sem`](https://github.com/Gutemberg149/bytecare-api-ai-2sem)
- **Documento de Arquitetura:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Roteiro do Pitch de 5 Minutos:** [docs/VIDEO_PITCH_SCRIPT.md](docs/VIDEO_PITCH_SCRIPT.md)
- **Arquivo com Links de Submissão:** [SUBMISSION_LINKS.txt](SUBMISSION_LINKS.txt)
- **Pacote Compactado para Entrega:** `bytecare-api-ai-2sem.zip`
