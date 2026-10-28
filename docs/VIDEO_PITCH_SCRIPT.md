# Roteiro Completo do Vídeo Pitch — ByteCare (5 Minutos)

**Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA  
**Projeto:** ByteCare — Inteligência Artificial Generativa e Preditiva para Saúde Animal  
**Duração Estimada:** 4:50 a 5:10 min  
**Formato de Entrega:** Vídeo no YouTube (Não Listado / Unlisted)  
**Link do Vídeo no YouTube:** `https://youtu.be/SEU_VIDEO_AQUI` *(substituir pelo link após gravação)*  

---

## 1. Visão Geral da Apresentação

O objetivo do pitch é apresentar com clareza o problema de negócio no setor veterinário, a proposta de valor do ByteCare, a justificativa e os diferenciais técnicos da nossa **Arquitetura Híbrida de IA** (Motor de Regras Determinístico + Gemini LLM + Guardrails), demonstrar o aplicativo mobile funcionando em tempo real e concluir com o impacto para tutores e clínicas.

---

## 2. Cronograma e Roteiro Minuto a Minuto

```
00:00 ── 00:45  [01] Abertura, Contexto do Mercado e O Problema
00:45 ── 01:45  [02] A Solução ByteCare e os Três Pilares Clínicos
01:45 ── 03:00  [03] Arquitetura Híbrida de IA e Conformidade Veterinária
03:00 ── 04:15  [04] Demonstração Prática (Mobile + Backend + IA)
04:15 ── 05:00  [05] Benefícios, Modelo de Impacto e Conclusão
```

---

### Bloco 1: Abertura, Contexto e O Problema (00:00 – 00:45)
**Cena / Visual:**  
Apresentador em foco com slide inicial do ByteCare na tela ou logo animada.

**Fala do Apresentador:**  
> *"Olá a todos, professores e avaliadores da Global Solution FIAP! Somos o time responsável pelo **ByteCare**, uma solução inovadora concebida na disciplina de Disruptive Architectures.*  
>  
> *Hoje, o Brasil possui a terceira maior população de animais de estimação do mundo, com mais de 160 milhões de pets, além de um setor agropecuário gigantesco. No entanto, o acompanhamento da saúde desses animais ainda é marcado pela **fragmentação total das informações**. Receitas em papel que se perdem, atrasos recorrentes no calendário vacinal, tutor esquecendo horários de antibióticos e, pior de tudo: a incapacidade de reconhecer sinais precoces de urgência, levando o animal à clínica quando a condição já é crítica.*  
>  
> *Foi para resolver essa lacuna de cuidado contínuo e salvar vidas animais que criamos o **ByteCare**."*

---

### Bloco 2: A Solução ByteCare e os Três Pilares (00:45 – 01:45)
**Cena / Visual:**  
Transição para a tela do app mobile mostrando a Home com o perfil de usuário, categorias (Pets, Agro, Pássaros) e os cards clínicos do animal.

**Fala do Apresentador:**  
> *"O ByteCare é uma plataforma holística de saúde animal baseada em dados longitudinais e no conceito de Internet of Behaviors (IoB). Nossa arquitetura organiza os registros de qualquer espécie — de cães e gatos a equinos, bovinos e aves — em **três pilares clínicos fundamentais**:*  
>  
> 1. *O **Pilar Preventivo**: onde gerenciamos vacinas, vermífugos, antiparasitários e check-ups periódicos com alertas inteligentes.*  
> 2. *O **Pilar Terapêutico**: que acompanha tratamentos ativos, garantindo que medicamentos prescritos sejam ministrados na dosagem e horário corretos, combatendo a baixa adesão.*  
> 3. *O **Pilar de Bem-Estar**: que monitora escore de condição corporal, peso, nutrição, hidratação e alterações comportamentais.*  
>  
> *Mas ter dados armazenados não é suficiente. Era necessário um cérebro analítico capaz de conectar esses três pilares e orientar o tutor de forma ética e segura. É aí que entra o **ByteCare Intelligence**."*

---

### Bloco 3: Arquitetura Híbrida de IA e Rigor Veterinário (01:45 – 03:00)
**Cena / Visual:**  
Exibição do diagrama de arquitetura técnica (Mermaid/Slide) destacando o fluxo entre o Mobile (Expo), Backend (Spring Boot), Motor de Regras Python e Google Gemini.

**Fala do Apresentador:**  
> *"Ao desenhar a inteligência artificial do ByteCare, enfrentamos um dilema crítico do setor médico: **como usar a flexibilidade de um LLM sem colocar o animal em risco por alucinações ou diagnósticos incorretos?***  
>  
> *Em respeito estrito à **Resolução CFMV nº 1.488/2022**, decidimos que **nenhuma decisão de risco à vida animal poderia depender exclusivamente da probabilidade de um modelo de linguagem**.*  
>  
> *Por isso, criamos uma **Arquitetura Híbrida em duas etapas**:*  
> - *Na primeira etapa, um **Motor de Regras Determinístico em Python (`risk_engine.py`)** calcula scores matemáticos objetivos sobre o histórico de vacinas e palavras-chave de risco vital (como hemorragia, convulsão, desidratação severa ou prostração). Se houver emergência, o risco é travado como URGENTE de forma imutável.*  
> - *Na segunda etapa, acionamos o **Google Gemini 2.5 Flash**, que atua sob guardrails estritos e schemas tipados via **Pydantic**. O Gemini não inventa diagnósticos nem receita remédios; ele sintetiza o histórico clínico em linguagem acessível e empática para o tutor, contextualizada para a espécie específica do animal.*  
> - *E se a conexão com a nuvem falhar, o sistema aciona de forma transparente nosso **Mock Service com 100% de paridade de schema**, garantindo zero downtime para o tutor."*

---

### Bloco 4: Demonstração Prática do Sistema (03:00 – 04:15)
**Cena / Visual:**  
Gravação da tela do emulador Android Pixel 7 em execução:
1. Navegação até o animal cadastrado ("BAU", cão da raça Akita).
2. Clique no card "ByteCare Intelligence" — carregando a análise de saúde com score, badges e recomendações.
3. Demonstração do Chat IA: o apresentador envia a mensagem *"O cachorro está convulsionando!"*.
4. Imediatamente o app dispara o alerta nativo em tela cheia: *"Atenção Médica Recomendada — Procure uma clínica veterinária"*.

**Fala do Apresentador:**  
> *"Vamos ver o sistema em ação no nosso emulador Android Pixel 7, conectado ao nosso backend Spring Boot local com banco Oracle e ao microserviço FastAPI de IA.*  
>  
> *Aqui estamos no perfil do BAU, um cão da raça Akita. Ao tocarmos no card **ByteCare Intelligence**, a aplicação mobile consulta a API de IA enviando o histórico completo dos três pilares. O motor analisa os registros e gera este painel intuitivo: nível de risco identificado, contadores de registros, fatores relevantes e próximos passos recomendados, com o disclaimer ético obrigatório no rodapé.*  
>  
> *Agora reparem no poder do nosso **Assistente Virtual integrado**. O tutor pode tirar dúvidas sobre cuidados com filhotes ou rotina de vacinas. Mas vejam o que acontece quando o tutor relata um sinal de perigo: digitamos 'O cachorro está convulsionando'.*  
>  
> *Imediatamente, o motor determinístico detecta a emergência médica, sobrepõe qualquer alucinação do modelo e dispara este Alerta Nativo na tela, instruindo o tutor a manter a calma e buscar atendimento presencial urgente. É a tecnologia salvando vidas em tempo real!"*

---

### Bloco 5: Benefícios para Tutores, Clínicas e Encerramento (04:15 – 05:00)
**Cena / Visual:**  
Retorno ao apresentador com slide resumindo os benefícios para Tutores e Clínicas, repositório GitHub e QR Code.

**Fala do Apresentador:**  
> *"Os benefícios dessa abordagem são imediatos:*  
> - *Para os **Tutores**: tranquilidade, centralização de dados, fim do esquecimento medicamentoso e um copiloto de orientação preventiva 24 horas por dia.*  
> - *Para as **Clínicas e Veterinários**: pacientes que chegam com anamnese digital completa, histórico longitudinal fidedigno e tutores mais aderentes aos tratamentos prescritos.*  
>  
> *O código-fonte completo de toda a solução — backend Java Spring Boot, microserviço de IA em Python FastAPI e aplicativo mobile React Native Expo — está totalmente versionado, documentado e pronto para execução local no repositório **bytecare-api-ai-2sem**.*  
>  
> *Agradecemos a atenção de todos os professores da FIAP. ByteCare: cuidando de quem sempre cuida de você. Muito obrigado!"*

---

## 3. Checklist de Gravação do Vídeo

- [ ] Microfone com áudio limpo, sem ruídos de fundo.
- [ ] Gravação em Full HD (1080p).
- [ ] Compartilhamento de tela nítido do emulador Android e do backend.
- [ ] Duração total conferida entre 4:30 e 5:10 min.
- [ ] Upload no YouTube configurado como **Não Listado (Unlisted)**.
- [ ] URL pública inserida no arquivo `SUBMISSION_LINKS.txt` e no topo do `README.md`.
