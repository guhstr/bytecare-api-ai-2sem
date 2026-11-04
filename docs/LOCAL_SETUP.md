# Execução local do sistema completo

Três serviços, cada um em um terminal:

| Serviço | Pasta | Porta |
|---|---|---|
| API principal (Spring Boot) | `ByteCare/backend` | 8080 |
| ByteCare Intelligence (FastAPI) | `bytecare-api-ai-2sem` | 8001 |
| App mobile (Expo / Metro) | `ByteCare2SemestreMobile` | 8081 |

## Pré-requisitos (macOS)

- Java 21 e Maven (`brew install openjdk@21 maven`)
- Python 3.10+
- Node.js 20+
- Xcode com Simulador iOS (App Store), ou o app **Expo Go** no iPhone

A API principal usa o banco Oracle da FIAP (`oracle.fiap.com.br:1521`), que precisa estar acessível pela rede.

## 1. API principal (terminal 1)

```bash
cd ByteCare/backend
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
mvn spring-boot:run
```

Teste: `curl http://localhost:8080/api/health`

Swagger: http://localhost:8080/swagger-ui.html

## 2. ByteCare Intelligence (terminal 2)

```bash
cd bytecare-api-ai-2sem
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # só na primeira vez
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Teste: `curl http://localhost:8001/api/v1/health`

Swagger: http://localhost:8001/docs

Para usar o Gemini, edite o `.env` com `BYTECARE_AI_MODE=gemini` e `GEMINI_API_KEY`.

## 3. App mobile (terminal 3)

O arquivo `.env` do app define os endereços das APIs. Use o IP do Mac na rede local:

```bash
ipconfig getifaddr en0
```

```env
API_URL=http://SEU_IP:8080/api
AI_API_URL=http://SEU_IP:8001/api/v1
```

| Onde o app roda | Endereço |
|---|---|
| Simulador iOS | IP do Mac ou `localhost` |
| iPhone com Expo Go (mesma rede Wi-Fi) | IP do Mac |
| Emulador Android | `10.0.2.2` |

Inicie (o `-c` limpa o cache, necessário sempre que o `.env` mudar):

```bash
cd ByteCare2SemestreMobile
npm install                 # só na primeira vez
npx expo start -c
```

Depois:

- **Simulador iOS:** pressione `i` no terminal do Expo;
- **iPhone:** abra a câmera e leia o QR Code exibido (requer o app Expo Go).

## 4. Usuário de teste

Crie um usuário pela tela de cadastro do app ou pela API:

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"seu_usuario","password":"SuaSenha@123","email":"voce@exemplo.com","nome":"Seu Nome"}'
```

## 5. Encerrar

Pressione `Ctrl + C` em cada terminal.

## Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| App mostra "Network Error" | IP errado no `.env` ou cache antigo | Confira o IP e rode `npx expo start -c` |
| Porta 8080 ocupada | Outro processo | `lsof -i :8080` e encerre o processo |
| `xcrun: unable to find utility "simctl"` | Xcode não instalado | Instale o Xcode e rode `sudo xcode-select -s /Applications/Xcode.app` |
| Erro de conexão com Oracle | Rede bloqueando a porta 1521 | Teste com `nc -z oracle.fiap.com.br 1521` |
