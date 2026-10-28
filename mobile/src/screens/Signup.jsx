import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ActivityIndicator } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { authService } from "../services/authService";

export default function Signup({ navigation }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const isButtonDisabled = username.trim() === "" || password.trim() === "" || confirmPassword.trim() === "" || loading;

  const handleSignup = async () => {
    if (password !== confirmPassword) {
      Alert.alert("Erro", "As senhas não coincidem");
      return;
    }

    setLoading(true);
    try {
      await authService.register(username.trim(), password.trim());
      Alert.alert("Sucesso", "Cadastro realizado! Faça login.");
      navigation.goBack();
    } catch (error) {
      Alert.alert("Erro", error.error || "Não foi possível cadastrar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient colors={["#96e6a1", "#192f6a"]} style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Criar Conta</Text>

        <TextInput 
          placeholder="Usuário" 
          style={styles.input} 
          value={username} 
          onChangeText={setUsername}
          autoCapitalize="none"
        />

        <TextInput 
          placeholder="Senha" 
          style={styles.input} 
          value={password} 
          onChangeText={setPassword} 
          secureTextEntry 
        />

        <TextInput 
          placeholder="Confirmar Senha" 
          style={styles.input} 
          value={confirmPassword} 
          onChangeText={setConfirmPassword} 
          secureTextEntry 
        />

        <TouchableOpacity 
          style={[styles.button, isButtonDisabled && styles.buttonDisabled]} 
          onPress={handleSignup} 
          disabled={isButtonDisabled}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>FINALIZAR CADASTRO</Text>
          )}
        </TouchableOpacity>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center" },
  card: {
    width: "85%",
    backgroundColor: "white",
    borderRadius: 25,
    padding: 30,
    alignItems: "center",
    elevation: 10,
  },
  title: { fontSize: 22, fontWeight: "bold", color: "#4a8f7a", marginBottom: 30 },
  input: {
    width: "100%",
    height: 50,
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 12,
    paddingHorizontal: 15,
    marginBottom: 15,
  },
  button: {
    width: "100%",
    height: 55,
    backgroundColor: "#192f6a",
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 10,
  },
  buttonDisabled: { backgroundColor: "#ccc" },
  buttonText: { color: "white", fontWeight: "bold", fontSize: 16 },
});