import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  SafeAreaView,
  RefreshControl,
} from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useTheme } from "../../context/ThemeContext";
import { gerarAnaliseIA } from "../services/aiService";
import { preventivoService } from "../services/preventivoService";
import { terapeuticoService } from "../services/terapeuticoService";
import { bemestarService } from "../services/bemestarService";

const PRIORITY_COLORS = {
  urgente: { bg: "#FFEBEE", border: "#D32F2F", text: "#B71C1C", icon: "alert-octagon" },
  alta: { bg: "#FFF3E0", border: "#F57C00", text: "#E65100", icon: "alert" },
  moderada: { bg: "#FFFDE7", border: "#FBC02D", text: "#F57F17", icon: "information" },
  baixa: { bg: "#E8F5E9", border: "#388E3C", text: "#1B5E20", icon: "check-circle" },
};

export default function AnaliseIA({ route, navigation }) {
  const { colors, dark } = useTheme();
  const { animal, subcategory } = route.params || {};

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [analise, setAnalise] = useState(null);
  const [erro, setErro] = useState(null);
  const [dadosLocais, setDadosLocais] = useState({
    preventivos: [],
    terapeuticos: [],
    bemEstar: [],
  });

  const carregarDadosEAnalisar = useCallback(async () => {
    if (!animal?.id) return;
    setLoading(true);
    setErro(null);

    try {
      // 1. Busca os dados dos três pilares no backend
      let preventivos = [];
      let terapeuticos = [];
      let bemEstar = [];

      try {
        preventivos = (await preventivoService.findByAnimal(animal.id)) || [];
      } catch (e) {
        console.warn("Aviso ao buscar preventivos:", e.message);
      }

      try {
        terapeuticos = (await terapeuticoService.findByAnimal(animal.id)) || [];
      } catch (e) {
        console.warn("Aviso ao buscar terapêuticos:", e.message);
      }

      try {
        bemEstar = (await bemestarService.findByAnimal(animal.id)) || [];
      } catch (e) {
        console.warn("Aviso ao buscar bem-estar:", e.message);
      }

      setDadosLocais({ preventivos, terapeuticos, bemEstar });

      // 2. Envia para o serviço de Inteligência Artificial
      const resultado = await gerarAnaliseIA({
        animal,
        preventivos,
        terapeuticos,
        bemEstar,
      });

      setAnalise(resultado);
    } catch (error) {
      console.error("Erro na análise de IA:", error);
      setErro(
        "Não foi possível obter a análise de IA no momento. Verifique se o serviço de IA e o backend estão rodando."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [animal]);

  useEffect(() => {
    carregarDadosEAnalisar();
  }, [carregarDadosEAnalisar]);

  const onRefresh = () => {
    setRefreshing(true);
    carregarDadosEAnalisar();
  };

  const prioridadeInfo =
    PRIORITY_COLORS[analise?.prioridade?.toLowerCase()] || PRIORITY_COLORS.baixa;

  return (
    <LinearGradient colors={colors.background} style={styles.container}>
      <SafeAreaView style={{ flex: 1 }}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.backButton, { backgroundColor: colors.iconBg }]}
          >
            <MaterialCommunityIcons name="arrow-left" size={24} color={colors.text} />
          </TouchableOpacity>
          <View style={{ flex: 1, alignItems: "center" }}>
            <Text style={[styles.headerTitle, { color: colors.text }]}>
              ByteCare Intelligence
            </Text>
            <Text style={[styles.headerSubtitle, { color: colors.subText }]}>
              Análise de Saúde: {animal?.nome || "Pet"}
            </Text>
          </View>
          <TouchableOpacity
            onPress={carregarDadosEAnalisar}
            style={[styles.backButton, { backgroundColor: colors.iconBg }]}
          >
            <MaterialCommunityIcons name="refresh" size={22} color={colors.primary} />
          </TouchableOpacity>
        </View>

        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              colors={[colors.primary]}
            />
          }
        >
          {loading ? (
            <View style={styles.centerContainer}>
              <ActivityIndicator size="large" color={colors.primary} />
              <Text style={[styles.loadingText, { color: colors.text }]}>
                Processando histórico com IA...
              </Text>
              <Text style={[styles.loadingSubtext, { color: colors.subText }]}>
                Avaliando dados preventivos, terapêuticos, sinais de risco e guardrails clínicos
              </Text>
            </View>
          ) : erro ? (
            <View style={[styles.card, { backgroundColor: colors.card, borderColor: "#F44336" }]}>
              <MaterialCommunityIcons name="alert-circle-outline" size={48} color="#F44336" />
              <Text style={[styles.errorTitle, { color: colors.text }]}>
                Atenção na Conexão
              </Text>
              <Text style={[styles.errorDescription, { color: colors.subText }]}>
                {erro}
              </Text>
              <TouchableOpacity
                style={[styles.actionBtn, { backgroundColor: colors.primary }]}
                onPress={carregarDadosEAnalisar}
              >
                <Text style={styles.actionBtnText}>Tentar Novamente</Text>
              </TouchableOpacity>
            </View>
          ) : analise ? (
            <>
              {/* Badge de Prioridade */}
              <View
                style={[
                  styles.priorityCard,
                  {
                    backgroundColor: dark ? "#1E293B" : prioridadeInfo.bg,
                    borderColor: prioridadeInfo.border,
                  },
                ]}
              >
                <View style={styles.priorityHeader}>
                  <MaterialCommunityIcons
                    name={prioridadeInfo.icon}
                    size={30}
                    color={prioridadeInfo.border}
                  />
                  <View style={{ marginLeft: 12, flex: 1 }}>
                    <Text style={styles.priorityLabel}>NÍVEL DE PRIORIDADE</Text>
                    <Text
                      style={[
                        styles.priorityValue,
                        { color: dark ? "#FFF" : prioridadeInfo.text },
                      ]}
                    >
                      {analise.prioridade?.toUpperCase()}
                    </Text>
                  </View>
                  <View
                    style={[
                      styles.modeTag,
                      { backgroundColor: dark ? "#334155" : "#E2E8F0" },
                    ]}
                  >
                    <Text style={styles.modeTagText}>
                      Modo: {analise.modo || "IA"}
                    </Text>
                  </View>
                </View>

                {analise.procurar_veterinario && (
                  <View style={styles.vetAlert}>
                    <MaterialCommunityIcons name="hospital-box" size={20} color="#D32F2F" />
                    <Text style={styles.vetAlertText}>
                      Recomendado acompanhamento ou avaliação veterinária
                    </Text>
                  </View>
                )}
              </View>

              {/* Resumo Geral */}
              <View style={[styles.card, { backgroundColor: colors.card }]}>
                <View style={styles.cardHeader}>
                  <MaterialCommunityIcons
                    name="text-box-search-outline"
                    size={22}
                    color={colors.primary}
                  />
                  <Text style={[styles.cardTitle, { color: colors.text }]}>
                    Resumo do Histórico
                  </Text>
                </View>
                <Text style={[styles.bodyText, { color: colors.text }]}>
                  {analise.resumo}
                </Text>
              </View>

              {/* Contadores Analisados */}
              <View style={styles.countersRow}>
                <View style={[styles.counterBox, { backgroundColor: colors.card }]}>
                  <MaterialCommunityIcons name="shield-check" size={20} color="#4CAF50" />
                  <Text style={[styles.counterNumber, { color: colors.text }]}>
                    {analise.registros_analisados?.preventivos ?? dadosLocais.preventivos.length}
                  </Text>
                  <Text style={[styles.counterLabel, { color: colors.subText }]}>
                    Preventivos
                  </Text>
                </View>
                <View style={[styles.counterBox, { backgroundColor: colors.card }]}>
                  <MaterialCommunityIcons name="pill" size={20} color="#F44336" />
                  <Text style={[styles.counterNumber, { color: colors.text }]}>
                    {analise.registros_analisados?.terapeuticos ?? dadosLocais.terapeuticos.length}
                  </Text>
                  <Text style={[styles.counterLabel, { color: colors.subText }]}>
                    Terapêuticos
                  </Text>
                </View>
                <View style={[styles.counterBox, { backgroundColor: colors.card }]}>
                  <MaterialCommunityIcons name="heart-pulse" size={20} color="#FF9800" />
                  <Text style={[styles.counterNumber, { color: colors.text }]}>
                    {analise.registros_analisados?.bem_estar ?? dadosLocais.bemEstar.length}
                  </Text>
                  <Text style={[styles.counterLabel, { color: colors.subText }]}>
                    Bem-Estar
                  </Text>
                </View>
              </View>

              {/* Fatores Relevantes */}
              {analise.fatores_relevantes && analise.fatores_relevantes.length > 0 && (
                <View style={[styles.card, { backgroundColor: colors.card }]}>
                  <View style={styles.cardHeader}>
                    <MaterialCommunityIcons
                      name="clipboard-check-outline"
                      size={22}
                      color="#2196F3"
                    />
                    <Text style={[styles.cardTitle, { color: colors.text }]}>
                      Fatores Relevantes Identificados
                    </Text>
                  </View>
                  {analise.fatores_relevantes.map((fator, index) => (
                    <View key={index} style={styles.bulletRow}>
                      <MaterialCommunityIcons
                        name="circle-medium"
                        size={20}
                        color={colors.primary}
                      />
                      <Text style={[styles.bulletText, { color: colors.text }]}>
                        {fator}
                      </Text>
                    </View>
                  ))}
                </View>
              )}

              {/* Sinais de Atenção */}
              {analise.sinais_atencao && analise.sinais_atencao.length > 0 && (
                <View style={[styles.card, { backgroundColor: colors.card }]}>
                  <View style={styles.cardHeader}>
                    <MaterialCommunityIcons
                      name="alert-rhombus-outline"
                      size={22}
                      color="#E65100"
                    />
                    <Text style={[styles.cardTitle, { color: colors.text }]}>
                      Sinais que Exigem Atenção
                    </Text>
                  </View>
                  {analise.sinais_atencao.map((sinal, index) => (
                    <View key={index} style={styles.bulletRow}>
                      <MaterialCommunityIcons
                        name="alert-circle-outline"
                        size={18}
                        color="#E65100"
                      />
                      <Text
                        style={[
                          styles.bulletText,
                          { color: dark ? "#FFA726" : "#E65100" },
                        ]}
                      >
                        {sinal}
                      </Text>
                    </View>
                  ))}
                </View>
              )}

              {/* Próximos Passos */}
              {analise.proximos_passos && analise.proximos_passos.length > 0 && (
                <View style={[styles.card, { backgroundColor: colors.card }]}>
                  <View style={styles.cardHeader}>
                    <MaterialCommunityIcons
                      name="arrow-right-circle-outline"
                      size={22}
                      color="#4CAF50"
                    />
                    <Text style={[styles.cardTitle, { color: colors.text }]}>
                      Próximos Passos Recomendados
                    </Text>
                  </View>
                  {analise.proximos_passos.map((passo, index) => (
                    <View key={index} style={styles.stepRow}>
                      <View style={[styles.stepNumber, { backgroundColor: colors.primary }]}>
                        <Text style={styles.stepNumberText}>{index + 1}</Text>
                      </View>
                      <Text style={[styles.bulletText, { color: colors.text }]}>
                        {passo}
                      </Text>
                    </View>
                  ))}
                </View>
              )}

              {/* Botão para Chat com o Assistente */}
              <TouchableOpacity
                style={[styles.chatBtn, { backgroundColor: colors.primary }]}
                onPress={() =>
                  navigation.navigate("ChatIA", {
                    animal,
                    analise,
                    preventivos: dadosLocais.preventivos,
                    terapeuticos: dadosLocais.terapeuticos,
                    bemEstar: dadosLocais.bemEstar,
                  })
                }
              >
                <MaterialCommunityIcons name="chat-processing-outline" size={24} color="#FFF" />
                <Text style={styles.chatBtnText}>
                  Tirar Dúvidas com o Assistente ByteCare
                </Text>
              </TouchableOpacity>

              {/* Guardrail / Aviso Clínico Legal */}
              <View style={[styles.disclaimerCard, { backgroundColor: dark ? "#1F2937" : "#F3F4F6" }]}>
                <MaterialCommunityIcons name="shield-alert-outline" size={20} color="#6B7280" />
                <Text style={styles.disclaimerText}>
                  {analise.aviso_seguranca ||
                    "Esta análise é um apoio inteligente à organização do histórico e jornada de cuidado. Ela não substitui consulta, diagnóstico nem tratamento de um médico-veterinário."}
                </Text>
              </View>
            </>
          ) : null}
        </ScrollView>
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
    paddingTop: 12,
    paddingBottom: 14,
  },
  backButton: {
    padding: 8,
    borderRadius: 12,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: "bold",
  },
  headerSubtitle: {
    fontSize: 13,
    marginTop: 2,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  centerContainer: {
    marginTop: 80,
    alignItems: "center",
    paddingHorizontal: 20,
  },
  loadingText: {
    fontSize: 17,
    fontWeight: "600",
    marginTop: 18,
    textAlign: "center",
  },
  loadingSubtext: {
    fontSize: 13,
    marginTop: 8,
    textAlign: "center",
    lineHeight: 18,
  },
  card: {
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    elevation: 2,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 10,
    gap: 8,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: "bold",
  },
  bodyText: {
    fontSize: 14,
    lineHeight: 22,
  },
  priorityCard: {
    borderRadius: 18,
    padding: 18,
    marginBottom: 16,
    borderWidth: 2,
  },
  priorityHeader: {
    flexDirection: "row",
    alignItems: "center",
  },
  priorityLabel: {
    fontSize: 11,
    fontWeight: "bold",
    color: "#6B7280",
    letterSpacing: 0.5,
  },
  priorityValue: {
    fontSize: 22,
    fontWeight: "900",
    marginTop: 2,
  },
  modeTag: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  modeTagText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#475569",
  },
  vetAlert: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 12,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "rgba(211, 47, 47, 0.2)",
    gap: 8,
  },
  vetAlertText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#D32F2F",
    flex: 1,
  },
  countersRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 16,
    gap: 10,
  },
  counterBox: {
    flex: 1,
    borderRadius: 14,
    padding: 12,
    alignItems: "center",
    elevation: 1,
  },
  counterNumber: {
    fontSize: 20,
    fontWeight: "bold",
    marginVertical: 4,
  },
  counterLabel: {
    fontSize: 11,
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginTop: 6,
    gap: 6,
  },
  stepRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginTop: 8,
    gap: 10,
  },
  stepNumber: {
    width: 22,
    height: 22,
    borderRadius: 11,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 2,
  },
  stepNumberText: {
    color: "#FFF",
    fontSize: 12,
    fontWeight: "bold",
  },
  bulletText: {
    fontSize: 14,
    lineHeight: 20,
    flex: 1,
  },
  chatBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 14,
    marginVertical: 10,
    gap: 10,
    elevation: 3,
  },
  chatBtnText: {
    color: "#FFF",
    fontSize: 15,
    fontWeight: "bold",
  },
  disclaimerCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    padding: 12,
    borderRadius: 12,
    marginTop: 8,
    gap: 8,
  },
  disclaimerText: {
    fontSize: 11,
    color: "#6B7280",
    lineHeight: 16,
    flex: 1,
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginTop: 12,
    textAlign: "center",
  },
  errorDescription: {
    fontSize: 13,
    marginTop: 6,
    textAlign: "center",
    lineHeight: 18,
    marginBottom: 16,
  },
  actionBtn: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 10,
  },
  actionBtnText: {
    color: "#FFF",
    fontWeight: "bold",
    fontSize: 14,
  },
});
