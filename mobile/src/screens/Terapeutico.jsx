
import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  Alert,
  SafeAreaView,
  ActivityIndicator,
} from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useTheme } from "../../context/ThemeContext";
import {
  useTerapeutico,
  useCreateTerapeutico,
  useUpdateTerapeutico,
  useDeleteTerapeutico,
} from "../hooks/useTerapeutico";

export default function Terapeutico({ route, navigation }) {
  const { colors, dark } = useTheme();
  const { animal } = route.params || {};

  const [medicamento, setMedicamento] = useState("");
  const [dosagem, setDosagem] = useState("");
  const [observacao, setObservacao] = useState("");
  const [editando, setEditando] = useState(null);
  const [reloadTrigger, setReloadTrigger] = useState(false);

  const {
    data: listaMedicamentos = [],
    isLoading,
    isError,
    refetch,
  } = useTerapeutico(animal?.id);

  const createMutation = useCreateTerapeutico();
  const updateMutation = useUpdateTerapeutico();
  const deleteMutation = useDeleteTerapeutico();

  async function salvar() {
    if (!medicamento.trim()) {
      Alert.alert("Erro", "O nome do medicamento e obrigatorio");
      return;
    }

    if (!dosagem.trim()) {
      Alert.alert("Erro", "A dosagem e obrigatoria");
      return;
    }

    const dados = {
      idAnimal: animal?.id,
      medicamento: medicamento.trim(),
      dosagem: dosagem.trim(),
      observacao: observacao.trim(),
    };

    try {
      if (editando !== null) {
        await updateMutation.mutateAsync({
          id: editando.id,
          data: dados,
        });
        Alert.alert("Sucesso", "Medicamento atualizado!");
      } else {
        await createMutation.mutateAsync(dados);
        Alert.alert("Sucesso", "Medicamento adicionado!");
      }
      await refetch();
      setReloadTrigger((prev) => !prev);
      limparCampos();
    } catch (error) {
      Alert.alert("Erro", error?.response?.data?.message || "Nao foi possivel salvar.");
    }
  }

  function limparCampos() {
    setMedicamento("");
    setDosagem("");
    setObservacao("");
    setEditando(null);
  }

  function editarMedicamento(item) {
    setMedicamento(item.medicamento || item.nomeMedicamento || "");
    setDosagem(item.dosagem || "");
    setObservacao(item.observacao || "");
    setEditando({ id: item.id });
  }

  function confirmarExclusao(item) {
    Alert.alert("Excluir", `Deseja remover "${item.medicamento || item.nomeMedicamento}"?`, [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Excluir",
        style: "destructive",
        onPress: async () => {
          try {
            await deleteMutation.mutateAsync(item.id);
            await refetch();
            setReloadTrigger((prev) => !prev);
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
          <ActivityIndicator size="large" color="#F44336" />
          <Text style={[styles.loadingText, { color: colors.text }]}>
            Carregando medicamentos...
          </Text>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  if (isError) {
    return (
      <LinearGradient colors={colors.background} style={styles.container}>
        <SafeAreaView style={styles.loadingContainer}>
          <MaterialCommunityIcons name="alert-circle" size={50} color="#F44336" />
          <Text style={[styles.errorText, { color: colors.text }]}>
            Erro ao carregar dados.
          </Text>
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
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.backBtn, { backgroundColor: colors.iconBg }]}
          >
            <MaterialCommunityIcons name="arrow-left" size={26} color={colors.text} />
          </TouchableOpacity>
          <Text style={[styles.headerTitle, { color: colors.text }]}>
            Terapeutico: {animal?.nome}
          </Text>
          <View style={{ width: 42 }} />
        </View>

        <View style={[styles.form, { backgroundColor: colors.card }]}>
          <Text style={[styles.formLabel, { color: "#F44336" }]}>
            {editando ? "EDITAR MEDICAMENTO" : "ADICIONAR MEDICAMENTO"}
          </Text>

          <TextInput
            placeholder="Nome do Medicamento"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              {
                backgroundColor: dark ? "#333" : "#FFF",
                color: colors.text,
                borderColor: dark ? "#444" : "#FEE2E2",
              },
            ]}
            value={medicamento}
            onChangeText={setMedicamento}
            editable={!isSaving}
          />

          <TextInput
            placeholder="Dosagem (ex: 5mg ou 2 gotas)"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              {
                backgroundColor: dark ? "#333" : "#FFF",
                color: colors.text,
                borderColor: dark ? "#444" : "#FEE2E2",
              },
            ]}
            value={dosagem}
            onChangeText={setDosagem}
            editable={!isSaving}
          />

          <TextInput
            placeholder="Observacao"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              styles.textArea,
              {
                backgroundColor: dark ? "#333" : "#FFF",
                color: colors.text,
                borderColor: dark ? "#444" : "#FEE2E2",
              },
            ]}
            multiline
            value={observacao}
            onChangeText={setObservacao}
            editable={!isSaving}
          />

          <TouchableOpacity
            style={[styles.btn, { backgroundColor: isSaving ? "#999" : "#F44336" }]}
            onPress={salvar}
            disabled={isSaving}
          >
            {isSaving ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <MaterialCommunityIcons name="check-bold" size={20} color="white" />
                <Text style={styles.btnText}>{editando ? "ATUALIZAR" : "SALVAR"}</Text>
              </>
            )}
          </TouchableOpacity>

          {editando !== null && (
            <TouchableOpacity style={styles.btnCancelar} onPress={limparCampos}>
              <Text style={styles.btnTextCancelar}>Cancelar Edicao</Text>
            </TouchableOpacity>
          )}
        </View>

        <FlatList
          data={listaMedicamentos}
          keyExtractor={(item) => item.id || Math.random().toString()}
          contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: 30 }}
          renderItem={({ item }) => (
            <View style={[styles.card, { backgroundColor: colors.card }]}>
              <View
                style={[
                  styles.iconBox,
                  { backgroundColor: dark ? "#3d1f1f" : "#ffebee" },
                ]}
              >
                <MaterialCommunityIcons name="pill" size={24} color="#F44336" />
              </View>

              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={[styles.cardNome, { color: colors.text }]}>
                  {item.medicamento || item.nomeMedicamento}
                </Text>
                <Text style={[styles.cardSub, { color: colors.subText }]}>
                  {item.dosagem} {item.horario ? `• ${item.horario}` : ""}
                </Text>
                {item.observacao ? (
                  <Text style={[styles.cardSub, { color: colors.subText }]}>
                    {item.observacao}
                  </Text>
                ) : null}
              </View>

              <TouchableOpacity
                onPress={() => editarMedicamento(item)}
                style={styles.actionBtn}
                disabled={isDeleting}
              >
                <MaterialCommunityIcons name="pencil" size={20} color="#FF9800" />
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => confirmarExclusao(item)}
                style={styles.actionBtn}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <ActivityIndicator size="small" color="#D32F2F" />
                ) : (
                  <MaterialCommunityIcons
                    name="trash-can-outline"
                    size={22}
                    color={dark ? "#ff6b6b" : "#D32F2F"}
                  />
                )}
              </TouchableOpacity>
            </View>
          )}
          ListEmptyComponent={
            <Text style={[styles.emptyText, { color: colors.subText }]}>
              Nenhum medicamento registrado.
            </Text>
          }
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
    backgroundColor: "#F44336",
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
    padding: 20,
  },
  backBtn: { padding: 8, borderRadius: 12 },
  headerTitle: { fontSize: 18, fontWeight: "bold" },
  form: {
    margin: 20,
    padding: 20,
    borderRadius: 25,
    elevation: 5,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  formLabel: {
    fontSize: 13,
    fontWeight: "bold",
    marginBottom: 15,
    textAlign: "center",
    letterSpacing: 1,
  },
  input: {
    borderWidth: 1.5,
    height: 50,
    borderRadius: 12,
    paddingHorizontal: 15,
    marginBottom: 12,
    fontSize: 15,
  },
  textArea: { height: 80, textAlignVertical: "top", paddingTop: 12 },
  btn: {
    height: 52,
    borderRadius: 12,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    gap: 8,
    marginTop: 5,
  },
  btnText: { color: "white", fontWeight: "bold", fontSize: 16 },
  btnCancelar: { marginTop: 12, alignItems: "center" },
  btnTextCancelar: { color: "#F44336", fontSize: 13, fontWeight: "600" },
  card: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    borderRadius: 20,
    marginBottom: 12,
    borderLeftWidth: 6,
    borderLeftColor: "#F44336",
    elevation: 3,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 5,
  },
  iconBox: {
    width: 45,
    height: 45,
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
  },
  cardNome: { fontSize: 17, fontWeight: "bold" },
  cardSub: { fontSize: 14, marginTop: 2 },
  actionBtn: { padding: 8 },
  emptyText: { textAlign: "center", marginTop: 40, fontSize: 15 },
});