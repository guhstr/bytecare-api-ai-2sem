import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  SafeAreaView,
  Alert,
} from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useTheme } from "../../context/ThemeContext";
import { conversarChatIA } from "../services/aiService";

export default function ChatIA({ route, navigation }) {
  const { colors, dark } = useTheme();
  const {
    animal,
    preventivos = [],
    terapeuticos = [],
    bemEstar = [],
  } = route.params || {};

  const [inputMensagem, setInputMensagem] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [mensagens, setMensagens] = useState([
    {
      id: "1",
      role: "assistant",
      content: animal
        ? `Olá! Sou o Assistente ByteCare. Já consultei as informações de ${animal.nome} (${animal.tipo || "Pet"}). Como posso ajudar você hoje no acompanhamento da saúde dele?`
        : "Olá! Sou o Assistente ByteCare. Em que posso te orientar sobre cuidados preventivos, rotina de medicação ou sinais de saúde dos animais?",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const flatListRef = useRef(null);

  const sugestoesRapidas = animal
    ? [
        `Como está o histórico de ${animal.nome}?`,
        "Ele parece um pouco desanimado hoje.",
        "Quais vacinas são recomendadas?",
        "Ele não quer comer desde cedo.",
      ]
    : [
        "Quais cuidados com filhotes?",
        "Qual o calendário básico de vacinas?",
        "Como identificar sinais de dor?",
      ];

  useEffect(() => {
    if (flatListRef.current) {
      setTimeout(() => {
        flatListRef.current.scrollToEnd({ animated: true });
      }, 150);
    }
  }, [mensagens]);

  const enviarMensagem = async (textoPersonalizado) => {
    const texto = (textoPersonalizado || inputMensagem).trim();
    if (!texto || enviando) return;

    const novaMensagemUsuario = {
      id: Date.now().toString(),
      role: "user",
      content: texto,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const novoHistorico = [...mensagens, novaMensagemUsuario];
    setMensagens(novoHistorico);
    setInputMensagem("");
    setEnviando(true);

    try {
      const respostaIA = await conversarChatIA({
        mensagem: texto,
        historico: novoHistorico.map((m) => ({
          role: m.role,
          content: m.content,
        })),
        animal: animal || null,
        preventivos,
        terapeuticos,
        bemEstar,
      });

      const novaMensagemIA = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: respostaIA.resposta,
        nivel_atencao: respostaIA.nivel_atencao,
        procurar_veterinario: respostaIA.procurar_veterinario,
        aviso_seguranca: respostaIA.aviso_seguranca,
        acao: respostaIA.acao,
        vacina_cadastro: respostaIA.vacina_cadastro,
        animal_cadastro: respostaIA.animal_cadastro,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMensagens((prev) => [...prev, novaMensagemIA]);

      // Alerta de emergência determinístico
      if (respostaIA.procurar_veterinario || respostaIA.nivel_atencao === "urgente") {
        Alert.alert(
          "Atenção Médica Recomendada",
          "O Assistente ByteCare detectou relatos que podem sugerir urgência veterinária. Mantenha o animal confortável e procure uma clínica de atendimento.",
          [{ text: "Entendido" }]
        );
      }
    } catch (error) {
      const mensagemErro = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "Desculpe, ocorreu uma instabilidade na comunicação com o Assistente ByteCare. Verifique se o serviço de IA está em execução e tente novamente.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        isError: true,
      };
      setMensagens((prev) => [...prev, mensagemErro]);
    } finally {
      setEnviando(false);
    }
  };

  const renderMensagem = ({ item }) => {
    const isUser = item.role === "user";

    return (
      <View
        style={[
          styles.messageRow,
          isUser ? styles.messageRowUser : styles.messageRowAssistant,
        ]}
      >
        {!isUser && (
          <View style={[styles.avatarIcon, { backgroundColor: colors.primary }]}>
            <MaterialCommunityIcons name="robot" size={18} color="#FFF" />
          </View>
        )}

        <View
          style={[
            styles.bubble,
            isUser
              ? [styles.bubbleUser, { backgroundColor: colors.primary }]
              : [
                  styles.bubbleAssistant,
                  {
                    backgroundColor: colors.card,
                    borderColor:
                      item.nivel_atencao === "urgente"
                        ? "#D32F2F"
                        : item.nivel_atencao === "atencao"
                        ? "#F57C00"
                        : dark
                        ? "#334155"
                        : "#E2E8F0",
                  },
                ],
          ]}
        >
          {item.nivel_atencao === "urgente" && (
            <View style={styles.urgentBadge}>
              <MaterialCommunityIcons name="alert-octagon" size={16} color="#D32F2F" />
              <Text style={styles.urgentBadgeText}>SINAL DE ALERTA</Text>
            </View>
          )}

          <Text
            style={[
              styles.messageText,
              { color: isUser ? "#FFF" : colors.text },
              item.isError && { color: "#F44336" },
            ]}
          >
            {item.content}
          </Text>

          {item.aviso_seguranca && !isUser && item.nivel_atencao === "urgente" && (
            <Text style={styles.warningText}>{item.aviso_seguranca}</Text>
          )}

          <Text
            style={[
              styles.timestamp,
              { color: isUser ? "rgba(255,255,255,0.7)" : colors.subText },
            ]}
          >
            {item.timestamp}
          </Text>
        </View>
      </View>
    );
  };

  return (
    <LinearGradient colors={colors.background} style={styles.container}>
      <SafeAreaView style={{ flex: 1 }}>
        {/* Header */}
        <View style={[styles.header, { borderBottomColor: dark ? "#333" : "#E5E7EB" }]}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.backButton, { backgroundColor: colors.iconBg }]}
          >
            <MaterialCommunityIcons name="arrow-left" size={24} color={colors.text} />
          </TouchableOpacity>

          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={[styles.headerTitle, { color: colors.text }]}>
              Assistente ByteCare
            </Text>
            <Text style={[styles.headerSubtitle, { color: colors.subText }]}>
              {animal ? `Contexto ativo: ${animal.nome}` : "Triagem & Acompanhamento"}
            </Text>
          </View>

          <View style={[styles.statusBadge, { backgroundColor: "#E8F5E9" }]}>
            <View style={styles.statusDot} />
            <Text style={styles.statusText}>Online</Text>
          </View>
        </View>

        {/* Mensagens */}
        <FlatList
          ref={flatListRef}
          data={mensagens}
          keyExtractor={(item) => item.id}
          renderItem={renderMensagem}
          contentContainerStyle={styles.messagesList}
          showsVerticalScrollIndicator={false}
          ListFooterComponent={
            enviando ? (
              <View style={styles.typingContainer}>
                <ActivityIndicator size="small" color={colors.primary} />
                <Text style={[styles.typingText, { color: colors.subText }]}>
                  Assistente ByteCare está digitando...
                </Text>
              </View>
            ) : null
          }
        />

        {/* Sugestões Rápidas */}
        {mensagens.length <= 3 && (
          <View style={styles.suggestionsContainer}>
            <FlatList
              horizontal
              data={sugestoesRapidas}
              keyExtractor={(item, index) => index.toString()}
              showsHorizontalScrollIndicator={false}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.suggestionChip,
                    { backgroundColor: colors.card, borderColor: dark ? "#444" : "#DDD" },
                  ]}
                  onPress={() => enviarMensagem(item)}
                >
                  <Text style={[styles.suggestionChipText, { color: colors.text }]}>
                    {item}
                  </Text>
                </TouchableOpacity>
              )}
            />
          </View>
        )}

        {/* Input bar */}
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
        >
          <View
            style={[
              styles.inputBar,
              { backgroundColor: colors.card, borderTopColor: dark ? "#333" : "#E5E7EB" },
            ]}
          >
            <TextInput
              style={[
                styles.textInput,
                {
                  backgroundColor: dark ? "#1E293B" : "#F3F4F6",
                  color: colors.text,
                },
              ]}
              placeholder="Descreva a dúvida ou comportamento..."
              placeholderTextColor={dark ? "#94A3B8" : "#9CA3AF"}
              value={inputMensagem}
              onChangeText={setInputMensagem}
              onSubmitEditing={() => enviarMensagem()}
              returnKeyType="send"
              maxLength={500}
            />

            <TouchableOpacity
              style={[
                styles.sendButton,
                {
                  backgroundColor: inputMensagem.trim() ? colors.primary : "#9CA3AF",
                },
              ]}
              onPress={() => enviarMensagem()}
              disabled={!inputMensagem.trim() || enviando}
            >
              <MaterialCommunityIcons name="send" size={20} color="#FFF" />
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingTop: 10,
    paddingBottom: 12,
    borderBottomWidth: 1,
  },
  backButton: {
    padding: 8,
    borderRadius: 12,
  },
  headerTitle: {
    fontSize: 17,
    fontWeight: "bold",
  },
  headerSubtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  statusBadge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
    gap: 6,
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: "#4CAF50",
  },
  statusText: {
    fontSize: 11,
    color: "#2E7D32",
    fontWeight: "600",
  },
  messagesList: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  messageRow: {
    flexDirection: "row",
    marginBottom: 14,
    alignItems: "flex-end",
  },
  messageRowUser: {
    justifyContent: "flex-end",
  },
  messageRowAssistant: {
    justifyContent: "flex-start",
  },
  avatarIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 8,
    marginBottom: 4,
  },
  bubble: {
    maxWidth: "82%",
    padding: 14,
    borderRadius: 18,
  },
  bubbleUser: {
    borderBottomRightRadius: 4,
  },
  bubbleAssistant: {
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    elevation: 1,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  urgentBadge: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 6,
    gap: 4,
  },
  urgentBadgeText: {
    fontSize: 11,
    fontWeight: "bold",
    color: "#D32F2F",
    letterSpacing: 0.5,
  },
  messageText: {
    fontSize: 14,
    lineHeight: 21,
  },
  warningText: {
    fontSize: 11,
    color: "#D32F2F",
    marginTop: 8,
    fontStyle: "italic",
    lineHeight: 15,
  },
  timestamp: {
    fontSize: 10,
    marginTop: 6,
    alignSelf: "flex-end",
  },
  typingContainer: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 8,
    paddingLeft: 36,
    gap: 8,
  },
  typingText: {
    fontSize: 12,
    fontStyle: "italic",
  },
  suggestionsContainer: {
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  suggestionChip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    marginRight: 8,
  },
  suggestionChipText: {
    fontSize: 12,
  },
  inputBar: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingTop: 8,
    paddingBottom: Platform.OS === "android" ? 28 : 12,
    borderTopWidth: 1,
    gap: 8,
  },
  textInput: {
    flex: 1,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    maxHeight: 100,
    fontSize: 14,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
  },
});
