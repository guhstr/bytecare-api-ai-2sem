import React, { useState } from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Alert, SafeAreaView, ActivityIndicator } from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useTheme } from "../../context/ThemeContext";
import { useBemEstar, useCreateBemEstar, useDeleteBemEstar } from "../hooks/useBemEstar";

export default function BemEstar({ route, navigation }) {
  const { colors, dark } = useTheme();
  const { animal } = route.params || {};

  const [atividade, setAtividade] = useState("");
  const [obs, setObs] = useState("");
  const [categoria, setCategoria] = useState("EXERCICIO");
  const [reloadTrigger, setReloadTrigger] = useState(false);

  const { data: listaBemEstar = [], isLoading, isError, refetch } = useBemEstar(animal?.id);

  const createMutation = useCreateBemEstar();
  const deleteMutation = useDeleteBemEstar();

  async function salvar() {
    if (!atividade.trim()) {
      Alert.alert("Erro", "A atividade e obrigatoria");
      return;
    }

    const dados = {
      idAnimal: animal?.id,
      atividade: atividade.trim(),
      observacao: obs.trim(),
      categoria: categoria.trim().toUpperCase(),
    };

    try {
      await createMutation.mutateAsync(dados);
      await refetch();
      setReloadTrigger((prev) => !prev);
      setAtividade("");
      setObs("");
      setCategoria("EXERCICIO");
      Alert.alert("Sucesso", "Rotina registrada!");
    } catch (error) {
      Alert.alert("Erro", error?.response?.data?.message || "Nao foi possivel salvar.");
    }
  }

  function confirmarExclusao(item) {
    Alert.alert("Excluir Registro", `Deseja remover o registro de "${item.atividade || item.nomeAtividade}"?`, [
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
            Alert.alert("Erro", "Nao foi possivel excluir o registro.");
          }
        },
      },
    ]);
  }

  if (isLoading) {
    return (
      <LinearGradient colors={colors.background} style={styles.container}>
        <SafeAreaView style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FF9800" />
          <Text style={[styles.loadingText, { color: colors.text }]}>Carregando registros...</Text>
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

  const isSaving = createMutation.isPending;
  const isDeleting = deleteMutation.isPending;

  return (
    <LinearGradient colors={colors.background} style={styles.container}>
      <SafeAreaView style={{ flex: 1 }}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={[styles.backBtn, { backgroundColor: colors.iconBg }]}>
            <MaterialCommunityIcons name="arrow-left" size={26} color={colors.text} />
          </TouchableOpacity>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Bem-Estar: {animal?.nome}</Text>
          <View style={{ width: 42 }} />
        </View>

        <View style={[styles.form, { backgroundColor: colors.card }]}>
          <TextInput
            placeholder="Atividade (ex: Passeio, Racao)"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              {
                backgroundColor: dark ? "#333" : "#FFFBF5",
                color: colors.text,
                borderColor: dark ? "#444" : "#FFCC80",
              },
            ]}
            value={atividade}
            onChangeText={setAtividade}
            editable={!isSaving}
          />

          <TextInput
            placeholder="Observacoes"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              styles.textArea,
              {
                backgroundColor: dark ? "#333" : "#FFFBF5",
                color: colors.text,
                borderColor: dark ? "#444" : "#FFCC80",
              },
            ]}
            value={obs}
            onChangeText={setObs}
            editable={!isSaving}
            multiline
          />

          <TextInput
            placeholder="Categoria (EXERCICIO, ALIMENTACAO, LAZER, SAUDE, COMPORTAMENTO)"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              {
                backgroundColor: dark ? "#333" : "#FFFBF5",
                color: colors.text,
                borderColor: dark ? "#444" : "#FFCC80",
              },
            ]}
            value={categoria}
            onChangeText={setCategoria}
            editable={!isSaving}
            autoCapitalize="characters"
          />

          <TouchableOpacity style={[styles.btn, { backgroundColor: isSaving ? "#999" : "#FF9800" }]} onPress={salvar} disabled={isSaving}>
            {isSaving ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>REGISTRAR ROTINA</Text>}
          </TouchableOpacity>
        </View>

        <Text style={[styles.subtitulo, { color: colors.text }]}>HISTORICO DE BEM-ESTAR:</Text>

        <FlatList
          data={listaBemEstar}
          keyExtractor={(item) => item.id || Math.random().toString()}
          contentContainerStyle={{ paddingBottom: 30, paddingHorizontal: 20 }}
          renderItem={({ item }) => (
            <View style={[styles.card, { backgroundColor: colors.card }]}>
              <View style={[styles.iconCircle, { backgroundColor: dark ? "#3d2b1f" : "#FFF3E0" }]}>
                <MaterialCommunityIcons name="heart-pulse" size={24} color="#FF9800" />
              </View>

              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={[styles.cardNome, { color: colors.text }]}>{item.atividade || item.nomeAtividade}</Text>
                <Text style={[styles.cardSub, { color: colors.subText }]}>{item.observacao}</Text>
                <Text style={[styles.cardSub, { color: colors.subText }]}>{item.categoria}</Text>
              </View>

              <TouchableOpacity style={{ padding: 8 }} onPress={() => confirmarExclusao(item)} disabled={isDeleting}>
                {isDeleting ? (
                  <ActivityIndicator size="small" color="#ff5252" />
                ) : (
                  <MaterialCommunityIcons name="trash-can-outline" size={22} color="#ff5252" />
                )}
              </TouchableOpacity>
            </View>
          )}
          ListEmptyComponent={<Text style={[styles.emptyText, { color: colors.subText }]}>Nenhum registro encontrado.</Text>}
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
    backgroundColor: "#FF9800",
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
    paddingBottom: 20,
  },
  backBtn: {
    padding: 8,
    borderRadius: 12,
  },
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
  input: {
    borderWidth: 1,
    height: 52,
    borderRadius: 15,
    paddingHorizontal: 15,
    marginBottom: 12,
    fontSize: 15,
  },
  textArea: { height: 80, textAlignVertical: "top", paddingTop: 12 },
  btn: {
    height: 52,
    borderRadius: 15,
    justifyContent: "center",
    alignItems: "center",
  },
  btnText: { color: "white", fontWeight: "bold", fontSize: 16 },
  subtitulo: {
    marginLeft: 25,
    fontWeight: "bold",
    marginBottom: 15,
    fontSize: 14,
    opacity: 0.8,
  },
  card: {
    padding: 16,
    borderRadius: 20,
    marginBottom: 12,
    flexDirection: "row",
    alignItems: "center",
    elevation: 2,
    borderLeftWidth: 6,
    borderLeftColor: "#FF9800",
  },
  iconCircle: {
    width: 45,
    height: 45,
    borderRadius: 22.5,
    justifyContent: "center",
    alignItems: "center",
  },
  cardNome: { fontSize: 17, fontWeight: "bold" },
  cardSub: { fontSize: 14, fontStyle: "italic", marginTop: 2 },
  emptyText: { textAlign: "center", marginTop: 30, fontSize: 14 },
});
