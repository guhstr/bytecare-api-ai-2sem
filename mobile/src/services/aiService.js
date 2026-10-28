import axios from "axios";
import { Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";

let envAiUrl = "";
try {
  const env = require("@env");
  envAiUrl = env?.AI_API_URL;
} catch (e) {
  // @env not available
}

const defaultAiHost =
  Platform.OS === "android"
    ? "http://10.0.2.2:8001/api/v1"
    : "http://localhost:8001/api/v1";

export const AI_BASE_URL = (
  envAiUrl ||
  process.env.AI_API_URL ||
  defaultAiHost
).replace(/\/$/, "");

console.log("🤖 AI_BASE_URL configurada:", AI_BASE_URL);

const aiApi = axios.create({
  baseURL: AI_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  timeout: 45000,
});

export const checkAiHealth = async () => {
  try {
    const response = await aiApi.get("/health", { timeout: 6000 });
    return response.data;
  } catch (error) {
    console.warn("⚠️ ByteCare Intelligence API indisponível:", error.message);
    return null;
  }
};

export const gerarAnaliseIA = async ({
  animal,
  preventivos = [],
  terapeuticos = [],
  bemEstar = [],
}) => {
  try {
    const payload = {
      animal: {
        id: animal.id,
        nome: animal.nome,
        tipo: (animal.tipo || "CACHORRO").toUpperCase(),
        raca: animal.raca || "Não informada",
        idade: animal.idade || animal.dataNascimento || null,
        observacaoGeral: animal.observacaoGeral || "",
        subcategoria: animal.subcategoria || "",
      },
      preventivos: preventivos || [],
      terapeuticos: terapeuticos || [],
      bem_estar: bemEstar || [],
    };

    console.log("📤 Enviando contexto para ByteCare Intelligence:", payload.animal.nome);
    const response = await aiApi.post("/analises", payload);
    return response.data;
  } catch (error) {
    console.error("❌ Erro ao solicitar análise de IA:", error?.response?.data || error.message);
    throw error;
  }
};

export const conversarChatIA = async ({
  mensagem,
  historico = [],
  animal = null,
  preventivos = [],
  terapeuticos = [],
  bemEstar = [],
}) => {
  try {
    const usuarioNome = await AsyncStorage.getItem("@usuario_nome");

    const payload = {
      usuario: usuarioNome || "Tutor",
      mensagem: mensagem.trim(),
      historico: (historico || []).map((msg) => ({
        role: msg.role === "assistant" || msg.role === "bot" ? "assistant" : "user",
        content: msg.content || msg.text || "",
      })),
      animal: animal
        ? {
            id: animal.id,
            nome: animal.nome,
            tipo: (animal.tipo || "CACHORRO").toUpperCase(),
            raca: animal.raca || "",
            idade: animal.idade || null,
            observacaoGeral: animal.observacaoGeral || "",
          }
        : null,
      preventivos: preventivos || [],
      terapeuticos: terapeuticos || [],
      bem_estar: bemEstar || [],
    };

    console.log("💬 Enviando mensagem para Assistente ByteCare:", mensagem);
    const response = await aiApi.post("/chat", payload);
    return response.data;
  } catch (error) {
    console.error("❌ Erro no Assistente ByteCare:", error?.response?.data || error.message);
    throw error;
  }
};

export default {
  checkAiHealth,
  gerarAnaliseIA,
  conversarChatIA,
  AI_BASE_URL,
};
