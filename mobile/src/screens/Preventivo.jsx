
import React, { useState } from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Alert, SafeAreaView, ActivityIndicator } from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useTheme } from "../../context/ThemeContext";
import { usePreventivo, useCreatePreventivo, useUpdatePreventivo, useDeletePreventivo } from "../hooks/usePreventivo";

export default function Preventivo({ route, navigation }) {
  const { colors, dark } = useTheme();
  const { animal } = route.params || {};

  const [nomeServico, setNomeServico] = useState("");
  const [descricaoServico, setDescricaoServico] = useState("");
  const [dataServico, setDataServico] = useState("");
  const [servicoEditado, setServicoEditado] = useState(null);
  const [reloadTrigger, setReloadTrigger] = useState(false);

  const { data: listaServicos = [], isLoading, isError, refetch } = usePreventivo(animal?.id);

  const createMutation = useCreatePreventivo();
  const updateMutation = useUpdatePreventivo();
  const deleteMutation = useDeletePreventivo();

  async function salvar() {
    if (!nomeServico.trim() || !descricaoServico.trim() || !dataServico.trim()) {
      Alert.alert("Erro", "Por favor, preencha todos os campos");
      return;
    }

    const dados = {
      idAnimal: animal?.id,
      nomeServico: nomeServico.trim(),
      descricao: descricaoServico.trim(),
      proximoPrevisto: dataServico.trim(),
    };

    try {
      if (servicoEditado !== null) {
        await updateMutation.mutateAsync({
          id: servicoEditado.id,
          data: dados,
        });
        Alert.alert("Sucesso", "Registro atualizado!");
      } else {
        await createMutation.mutateAsync(dados);
        Alert.alert("Sucesso", "Salvo com sucesso!");
      }
      
      await refetch();
      setReloadTrigger(prev => !prev);
      limparCampos();
    } catch (error) {
      Alert.alert("Erro", error?.response?.data?.message || "Nao foi possivel salvar.");
    }
  }

  function limparCampos() {
    setNomeServico("");
    setDescricaoServico("");
    setDataServico("");
    setServicoEditado(null);
  }

  function editarServico(item) {
    setNomeServico(item.nomeServico);
    setDescricaoServico(item.descricao);
    setDataServico(item.proximoPrevisto || "");
    setServicoEditado({ id: item.id });
  }

  function confirmarExclusao(item) {
    Alert.alert("Confirmar Exclusao", `Excluir o servico "${item.nomeServico}"?`, [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Excluir",
        style: "destructive",
        onPress: async () => {
          try {
            await deleteMutation.mutateAsync(item.id);
            await refetch();
            setReloadTrigger(prev => !prev);
          } catch (error) {
            Alert.alert("Erro", "Nao foi possivel excluir.");
          }
        },
      },
    ]);
  }

  if (isLoading) {
    return (
      <LinearGradient colors={colors.background} style={styles.container}>
        <SafeAreaView style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.text }]}>Carregando historico...</Text>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  if (isError) {
    return (
      <LinearGradient colors={colors.background} style={styles.container}>
        <SafeAreaView style={styles.loadingContainer}>
          <MaterialCommunityIcons name="alert-circle" size={50} color="#F44336" />
          <Text style={[styles.errorText, { color: colors.text }]}>Erro ao carregar dados.</Text>
          <TouchableOpacity onPress={() => refetch()} style={styles.retryButton}>
            <Text style={styles.retryText}>Tentar novamente</Text>
          </TouchableOpacity>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  const isSaving = createMutation.isPending || updateMutation.isPending;
  const isDeleting = deleteMutation.isPending;

  return (
    <LinearGradient colors={colors.background} style={styles.container}>
      <SafeAreaView style={{ flex: 1 }}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={[styles.backBtn, { backgroundColor: colors.iconBg }]}>
            <MaterialCommunityIcons name="arrow-left" size={26} color={colors.text} />
          </TouchableOpacity>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Preventivo: {animal?.nome}</Text>
          <View style={{ width: 42 }} />
        </View>

        <View style={[styles.form, { backgroundColor: colors.card }]}>
          <Text style={[styles.formTitulo, { color: colors.primary }]}>{servicoEditado !== null ? "EDITAR REGISTRO" : "NOVO REGISTRO"}</Text>

          <TextInput
            placeholder="Nome do servico (ex: Vacina)"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              {
                backgroundColor: dark ? "#333" : "#fafafa",
                color: colors.text,
                borderColor: dark ? "#444" : "#eee",
              },
            ]}
            value={nomeServico}
            onChangeText={setNomeServico}
            editable={!isSaving}
          />

          <TextInput
            placeholder="Descricao"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              styles.textArea,
              {
                backgroundColor: dark ? "#333" : "#fafafa",
                color: colors.text,
                borderColor: dark ? "#444" : "#eee",
              },
            ]}
            multiline
            value={descricaoServico}
            onChangeText={setDescricaoServico}
            editable={!isSaving}
          />

          <TextInput
            placeholder="Proximo previsto (DD/MM)"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              {
                backgroundColor: dark ? "#333" : "#fafafa",
                color: colors.text,
                borderColor: dark ? "#444" : "#eee",
              },
            ]}
            value={dataServico}
            onChangeText={setDataServico}
            editable={!isSaving}
          />

          <TouchableOpacity style={[styles.btnSalvar, { backgroundColor: isSaving ? "#999" : colors.primary }]} onPress={salvar} disabled={isSaving}>
            {isSaving ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.btnText}>{servicoEditado !== null ? "ATUALIZAR" : "SALVAR NO HISTORICO"}</Text>
            )}
          </TouchableOpacity>

          {servicoEditado !== null && (
            <TouchableOpacity style={styles.btnCancelar} onPress={limparCampos}>
              <Text style={styles.btnTextCancelar}>Cancelar Edicao</Text>
            </TouchableOpacity>
          )}
        </View>

        <Text style={[styles.subtitulo, { color: colors.text }]}>HISTORICO:</Text>

        <FlatList
          data={listaServicos}
          keyExtractor={(item) => item.id || Math.random().toString()}
          contentContainerStyle={{ paddingBottom: 30, paddingHorizontal: 20 }}
          ListEmptyComponent={<Text style={[styles.emptyText, { color: colors.subText }]}>Nenhum servico registrado.</Text>}
          renderItem={({ item }) => (
            <View style={[styles.listaItens, { backgroundColor: colors.card }]}>
              <View style={styles.itemHeader}>
                <View style={[styles.iconBox, { backgroundColor: dark ? "#1b2e26" : "#e8f5f0" }]}>
                  <MaterialCommunityIcons name="shield-check" size={24} color={colors.primary} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.nomeServico, { color: colors.text }]}>{item.nomeServico}</Text>
                  <Text style={[styles.itemDataText, { color: colors.subText }]}>{item.proximoPrevisto || "Sem data definida"}</Text>
                </View>
              </View>

              <Text style={[styles.descricaoServico, { color: colors.subText }]}>{item.descricao}</Text>

              <View style={styles.botoesContainer}>
                <TouchableOpacity
                  onPress={() => editarServico(item)}
                  style={[styles.iconBtn, { backgroundColor: dark ? "#3d2b1f" : "#fff8e1" }]}
                  disabled={isDeleting}
                >
                  <MaterialCommunityIcons name="pencil" size={18} color="#FF9800" />
                </TouchableOpacity>

                <TouchableOpacity
                  onPress={() => confirmarExclusao(item)}
                  style={[styles.iconBtn, { backgroundColor: dark ? "#3d1f1f" : "#ffebee" }]}
                  disabled={isDeleting}
                >
                  {isDeleting ? <ActivityIndicator size="small" color="#F44336" /> : <MaterialCommunityIcons name="delete" size={18} color="#F44336" />}
                </TouchableOpacity>
              </View>
            </View>
          )}
        />
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
  },
  errorText: {
    marginTop: 12,
    fontSize: 16,
    textAlign: "center",
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 24,
    paddingVertical: 10,
    backgroundColor: "#4CAF50",
    borderRadius: 10,
  },
  retryText: {
    color: "#fff",
    fontWeight: "bold",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: 20,
    paddingHorizontal: 20,
    paddingBottom: 15,
  },
  backBtn: { padding: 8, borderRadius: 12 },
  headerTitle: { fontSize: 18, fontWeight: "bold" },
  form: {
    margin: 20,
    padding: 20,
    borderRadius: 25,
    elevation: 4,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  formTitulo: {
    fontSize: 14,
    fontWeight: "bold",
    marginBottom: 15,
    textAlign: "center",
    letterSpacing: 1,
  },
  input: {
    borderWidth: 1,
    height: 48,
    borderRadius: 12,
    paddingHorizontal: 15,
    marginBottom: 12,
    fontSize: 15,
  },
  textArea: { height: 70, textAlignVertical: "top", paddingTop: 10 },
  btnSalvar: {
    height: 50,
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 5,
    elevation: 2,
  },
  btnCancelar: { marginTop: 12, alignItems: "center" },
  btnTextCancelar: { color: "#F44336", fontSize: 13, fontWeight: "600" },
  btnText: { color: "white", fontWeight: "bold", fontSize: 15 },
  subtitulo: {
    marginLeft: 25,
    fontWeight: "bold",
    marginBottom: 15,
    fontSize: 14,
    opacity: 0.8,
  },
  listaItens: {
    padding: 16,
    borderRadius: 20,
    marginBottom: 12,
    elevation: 2,
    borderLeftWidth: 6,
    borderLeftColor: "#4a8f7a",
  },
  itemHeader: { flexDirection: "row", alignItems: "center", gap: 12 },
  iconBox: {
    width: 45,
    height: 45,
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
  },
  nomeServico: { fontSize: 17, fontWeight: "bold" },
  itemDataText: { fontSize: 12, marginTop: 2 },
  descricaoServico: {
    fontSize: 14,
    marginTop: 10,
    marginBottom: 12,
    lineHeight: 20,
  },
  botoesContainer: { flexDirection: "row", justifyContent: "flex-end", gap: 12 },
  iconBtn: { padding: 10, borderRadius: 10 },
  emptyText: { textAlign: "center", marginTop: 40, fontSize: 15 },
});