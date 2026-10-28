
import React, { useState } from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Alert, SafeAreaView, ActivityIndicator } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useTheme } from "../../context/ThemeContext";
import { usePermissions } from "../hooks/usePermissions";
import { useAnimals, useCreateAnimal, useDeleteAnimal } from "../hooks/useAnimals";

const getTipoPadrao = (subcategoriaId) => {
  const tipos = {
    101: "CACHORRO",
    102: "GATO",
    103: "PEIXE",
    104: "BOVINO",
    105: "EQUINO",
    106: "GALINHA",
    107: "PASSARO",
    108: "PASSARO",
    109: "PASSARO",
  };
  return tipos[subcategoriaId] || "CACHORRO";
};

export default function SubcategoriaListagem({ route, navigation }) {
  const { colors, dark } = useTheme();
  const { isAdmin } = usePermissions();
  const { subcategory } = route.params || {};

  const [nome, setNome] = useState("");
  const [idade, setIdade] = useState("");
  const [raca, setRaca] = useState("");
  const [tipo, setTipo] = useState(getTipoPadrao(subcategory?.id));

  const { data: animais = [], isLoading, isError, refetch } = useAnimals(subcategory?.id);

  const createMutation = useCreateAnimal();
  const deleteMutation = useDeleteAnimal();

  useFocusEffect(
    React.useCallback(() => {
      refetch();
    }, [refetch])
  );

  async function cadastrarAnimal() {
    if (!nome.trim() || !idade.trim() || !raca.trim() || !tipo.trim()) {
      return Alert.alert("Atenção", "Preencha todos os campos do animal.");
    }

    const anoAtual = new Date().getFullYear();
    const anoNascimento = anoAtual - parseInt(idade);
    const dataNascimento = `${anoNascimento}-01-01`;

    const dados = {
      nome: nome.trim(),
      tipo: tipo.trim().toUpperCase(),
      raca: raca.trim(),
      dataNascimento: dataNascimento,
      observacaoGeral: `Idade: ${idade} anos`,
      ativo: true,
      subcategoriaId: subcategory.id,
    };

    try {
      await createMutation.mutateAsync(dados);
      setNome("");
      setIdade("");
      setRaca("");
      setTipo(getTipoPadrao(subcategory?.id));
      Alert.alert("Sucesso", `${dados.nome} cadastrado(a)!`);
    } catch (error) {
      Alert.alert("Erro", error?.response?.data?.message || "Não foi possível salvar o animal.");
    }
  }

  function confirmarExclusao(animal) {
    Alert.alert("Excluir Animal", `Tem certeza que deseja remover ${animal.nome} da lista?`, [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Excluir",
        style: "destructive",
        onPress: async () => {
          try {
            await deleteMutation.mutateAsync(animal.id);
          } catch (error) {
            Alert.alert("Erro", "Não foi possível deletar o animal.");
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
          <Text style={[styles.loadingText, { color: colors.text }]}>Carregando animais...</Text>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  if (isError) {
    return (
      <LinearGradient colors={colors.background} style={styles.container}>
        <SafeAreaView style={styles.loadingContainer}>
          <MaterialCommunityIcons name="alert-circle" size={50} color="#F44336" />
          <Text style={[styles.errorText, { color: colors.text }]}>Erro ao carregar animais.</Text>
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
          <Text style={[styles.title, { color: colors.text }]}>{subcategory?.nome}</Text>
          <View style={{ width: 42 }} />
        </View>

        <View style={[styles.form, { backgroundColor: colors.card }]}>
          <Text style={[styles.formTitle, { color: colors.primary }]}>CADASTRAR NOVO</Text>

          <TextInput
            placeholder="Nome do Animal"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              {
                backgroundColor: dark ? "#333" : "#fafafa",
                color: colors.text,
                borderColor: dark ? "#444" : "#ddd",
              },
            ]}
            value={nome}
            onChangeText={setNome}
            editable={!isSaving}
          />

          <View style={{ flexDirection: "row", gap: 10 }}>
            <TextInput
              placeholder="Idade"
              placeholderTextColor={dark ? "#999" : "#666"}
              style={[
                styles.input,
                {
                  flex: 1,
                  backgroundColor: dark ? "#333" : "#fafafa",
                  color: colors.text,
                  borderColor: dark ? "#444" : "#ddd",
                },
              ]}
              value={idade}
              onChangeText={setIdade}
              keyboardType="numeric"
              editable={!isSaving}
            />
            <TextInput
              placeholder="Raça"
              placeholderTextColor={dark ? "#999" : "#666"}
              style={[
                styles.input,
                {
                  flex: 2,
                  backgroundColor: dark ? "#333" : "#fafafa",
                  color: colors.text,
                  borderColor: dark ? "#444" : "#ddd",
                },
              ]}
              value={raca}
              onChangeText={setRaca}
              editable={!isSaving}
            />
          </View>

          <TextInput
            placeholder="Tipo (CACHORRO, GATO, PASSARO, PEIXE, EQUINO, BOVINO)"
            placeholderTextColor={dark ? "#999" : "#666"}
            style={[
              styles.input,
              {
                backgroundColor: dark ? "#333" : "#fafafa",
                color: colors.text,
                borderColor: dark ? "#444" : "#ddd",
              },
            ]}
            value={tipo}
            onChangeText={setTipo}
            editable={!isSaving}
            autoCapitalize="characters"
          />

          <TouchableOpacity style={[styles.btn, { backgroundColor: isSaving ? "#999" : colors.primary }]} onPress={cadastrarAnimal} disabled={isSaving}>
            {isSaving ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>ADICIONAR ANIMAL</Text>}
          </TouchableOpacity>
        </View>

        <Text style={[styles.listTitle, { color: colors.text }]}>MEUS ANIMAIS:</Text>

        <FlatList
          data={animais}
          keyExtractor={(item) => item.id || Math.random().toString()}
          contentContainerStyle={{ paddingBottom: 30, paddingHorizontal: 20 }}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[styles.animalCard, { backgroundColor: colors.card }]}
              onPress={() => navigation.navigate("animal", { animal: item, subcategory })}
              disabled={isDeleting}
            >
              <View style={[styles.iconCircle, { backgroundColor: dark ? "#1b2e26" : "#e8f5f0" }]}>
                <MaterialCommunityIcons name="paw" size={26} color={colors.primary} />
              </View>

              <View style={{ flex: 1, marginLeft: 15 }}>
                <Text style={[styles.animalNome, { color: colors.text }]}>{item.nome}</Text>
                <Text style={[styles.animalInfo, { color: colors.subText }]}>
                  {item.raca} • {item.idade || "Idade não informada"} {parseInt(item.idade) === 1 ? "ano" : "anos"}
                </Text>
              </View>

              {isAdmin ? (
                <TouchableOpacity style={styles.deleteBtn} onPress={() => confirmarExclusao(item)} disabled={isDeleting}>
                  {isDeleting ? (
                    <ActivityIndicator size="small" color="#ff5252" />
                  ) : (
                    <MaterialCommunityIcons name="trash-can-outline" size={22} color="#ff5252" />
                  )}
                </TouchableOpacity>
              ) : (
                <View style={{ width: 30 }} />
              )}

              <MaterialCommunityIcons name="chevron-right" size={24} color={colors.subText} />
            </TouchableOpacity>
          )}
          ListEmptyComponent={<Text style={[styles.empty, { color: colors.subText }]}>Nenhum animal cadastrado nesta categoria.</Text>}
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
    padding: 20,
  },
  backBtn: { padding: 8, borderRadius: 12 },
  title: { fontSize: 20, fontWeight: "bold" },
  form: {
    margin: 20,
    padding: 20,
    borderRadius: 25,
    elevation: 4,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  formTitle: {
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
  btn: {
    height: 50,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 5,
  },
  btnText: { color: "#fff", fontWeight: "bold", fontSize: 15 },
  listTitle: {
    marginLeft: 25,
    fontSize: 14,
    fontWeight: "bold",
    marginBottom: 15,
    opacity: 0.8,
  },
  animalCard: {
    padding: 16,
    borderRadius: 20,
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
    elevation: 2,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 5,
  },
  iconCircle: {
    width: 50,
    height: 50,
    borderRadius: 15,
    justifyContent: "center",
    alignItems: "center",
  },
  animalNome: { fontSize: 18, fontWeight: "bold" },
  animalInfo: { fontSize: 14, marginTop: 2 },
  deleteBtn: {
    padding: 8,
    marginRight: 4,
  },
  empty: { textAlign: "center", marginTop: 40, fontSize: 15 },
});
