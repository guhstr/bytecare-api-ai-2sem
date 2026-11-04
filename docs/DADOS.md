# Dados utilizados pela IA

Todos os dados chegam pelo aplicativo, que os obtém da API principal (Spring Boot / Oracle). A API de IA não armazena nada.

## 1. Perfil do pet (`animal`)

| Campo | Tipo | Origem | Utilização |
|---|---|---|---|
| `id` | UUID / número | Tabela de animais | Identificação na resposta |
| `nome` | texto | Tabela de animais | Personalização da mensagem |
| `tipo` | texto (CACHORRO, GATO, EQUINO, BOVINO, PEIXE, aves...) | Tabela de animais | Protocolo de vacinas e orientações da espécie |
| `raca` | texto | Tabela de animais | Contexto para o LLM |
| `dataNascimento` / `idade` | data ou texto ("3", "4 meses") | Tabela de animais | Cálculo da fase de vida |
| `peso` | número | Registro da clínica | Contexto nutricional |
| `castrado` | booleano | Registro da clínica | Recomendação de avaliação para castração |
| `observacaoGeral` | texto | Tabela de animais | Sinais, comportamento e condições permanentes registradas pelo chat |
| `tutor` | texto | Tabela de animais (coluna `TUTOR`) | Usuário que cadastrou o pet; só ele ou a clínica pode apagá-lo (a IA ignora esse campo) |

## 2. Vacinas e preventivos (`preventivos`)

| Campo | Utilização |
|---|---|
| `nomeServico` | Identifica a vacina ou preventivo (V10, antirrábica, vermífugo...) |
| `descricao` | Contexto adicional |
| `proximoPrevisto` | Data do próximo reforço: atrasado (alta) ou a vencer em 30 dias (lembrete) |
| `dataHoraRegistro` | Reforço anual sem próxima data cadastrada |

## 3. Tratamentos e medicamentos (`terapeuticos`)

| Campo | Utilização |
|---|---|
| `medicamento` | Lista de tratamentos em andamento na ação de adesão |
| `dosagem`, `observacao` | Contexto (a IA nunca altera doses) |
| `dataHoraRegistro` | Tratamento dos últimos 60 dias gera consulta de retorno |

## 4. Consultas (`consultas`)

| Campo | Utilização |
|---|---|
| `data` | Tempo desde a última consulta (12 meses, ou 6 meses para sênior) |
| `motivo`, `veterinario` | Contexto e sinais recentes |

## 5. Bem-estar (`bem_estar`) e comportamento (`comportamento`)

| Campo | Utilização |
|---|---|
| `atividade`, `categoria`, `descricao`, `observacao` | Detecção de termos de comportamento, peso, dentes, pele, parasitas e sinais de urgência |
| `dataHoraRegistro` | Apenas registros dos últimos 30 dias contam como sinal atual |

## 6. Conversa (`/chat`)

| Campo | Utilização |
|---|---|
| `mensagem` | Intenção do usuário e avaliação de risco |
| `historico` | Últimas 16 mensagens para manter o contexto |
| `usuario` | Personalização do tratamento |

## 7. Agendamentos (tabela `AGENDAMENTO`, API principal)

A IA não lê essa tabela; ela só monta o pedido a partir da conversa. O app grava pela API principal.

| Coluna | Descrição |
|---|---|
| `SOLICITANTE` | Usuário que pediu |
| `ANIMAL_ID`, `ANIMAL_NOME` | Pet do pedido |
| `SERVICOS` | Ex.: "Consulta de rotina, Vacinação" |
| `DATA_PREFERIDA`, `HORARIO_PREFERIDO`, `PERIODO` | Dia e horário informados pelo tutor (obrigatórios para enviar, ou "qualquer dia") |
| `OBSERVACAO` | Detalhes para a clínica, ex.: vacinas a avaliar |
| `STATUS` | SOLICITADO, CONFIRMADO, RECUSADO ou CANCELADO |
| `DATA_HORA_CONFIRMADA`, `RESPOSTA_CLINICA` | Resposta da clínica, enviada ao tutor como notificação |

As tabelas `AGENDAMENTO` e `NOTIFICACAO` e a coluna `ANIMAL.TUTOR` são criadas na inicialização do backend, se ainda não existirem.

## 8. Saída produzida

| Campo | Descrição |
|---|---|
| `perfil` | Espécie, fase de vida, vacinas essenciais registradas e pendentes |
| `acoes[]` | Título, descrição, categoria, prioridade, prazo em dias, motivo e dados de origem |
| `servicos_recomendados[]` | Código, nome, motivo, prioridade e score |
| `score_risco` | 0 a 100 |
| `prioridade` | baixa, moderada, alta ou urgente |
| `mensagem_tutor` / `resumo_clinica` | Textos personalizados (LLM no modo gemini) |
| `procurar_veterinario` | Indica necessidade de atendimento |
| `acao` (chat) | nenhuma, cadastrar_animal, cadastrar_vacina, registrar_observacao, agendar, listar_animais ou apagar_animal, com os dados para a confirmação |

## 9. Privacidade

- só o contexto necessário é enviado para a IA (sem dados pessoais do tutor além do primeiro nome no chat);
- no modo `mock`, nenhum dado sai do ambiente local;
- no modo `gemini`, o plano já calculado e o perfil do pet são enviados ao Google Gemini para gerar os textos.
