import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Image, Alert, ActivityIndicator } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useAuth } from "../../context/AuthContext";
import { checkServerHealth } from "../services/api";

export default function Login({ navigation }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [loginAttempts, setLoginAttempts] = useState(0);
  const { login } = useAuth();

  const isButtonDisabled = username.trim() === "" || password.trim() === "" || loading;

  useEffect(() => {
    checkServerHealth();
  }, []);

  const handleLogin = async () => {
    if (loading) return;

    setLoading(true);
    setStatusMessage("🔍 Verificando servidor...");
    setLoginAttempts((prev) => prev + 1);

    try {
      console.log("👤 Tentando login com:", username);

      let isServerReady = false;
      let attempts = 0;

      while (!isServerReady && attempts < 3) {
        attempts++;
        try {
          const health = await checkServerHealth();
          if (health) {
            isServerReady = true;
            console.log("✅ Servidor pronto!");
            break;
          }
        } catch (e) {
          console.log(`⏳ Tentativa ${attempts} - servidor acordando...`);
        }

        if (attempts < 3) {
          setStatusMessage(`⏳ Acordando servidor (${attempts}/3)...`);
          await new Promise((resolve) => setTimeout(resolve, 3000));
        }
      }

      if (!isServerReady) {
        setStatusMessage("⚠️ Servidor demorando, tentando login...");
      }

      setStatusMessage("🔑 Realizando login...");

      const result = await login(username.trim(), password.trim());

      await AsyncStorage.setItem("@usuario_senha", password.trim());
      console.log("💾 Senha salva para renovação automática");

      setStatusMessage("✅ Login bem-sucedido!");

      await new Promise((resolve) => setTimeout(resolve, 500));

      console.log("👤 Login - sucesso! Navegando para Home");
      navigation.reset({
        index: 0,
        routes: [{ name: "Home" }],
      });
    } catch (error) {
      console.error("👤 Login - erro:", error);

      let errorMessage = "Credenciais inválidas. Tente novamente.";

      if (error.message?.includes("timeout") || error.message?.includes("Network")) {
        if (loginAttempts >= 2) {
          errorMessage = "O servidor está demorando para responder. Verifique sua conexão com a internet.";
        } else {
          errorMessage = "O servidor pode estar iniciando. Tente novamente em alguns segundos.";
        }
      } else if (error.error) {
        errorMessage = error.error;
      } else if (error.message) {
        errorMessage = error.message;
      }

      setStatusMessage(`${errorMessage}`);

      Alert.alert("Erro no Login", errorMessage, [
        {
          text: "Tentar Novamente",
          onPress: () => {
            setStatusMessage("");
            setLoading(false);
          },
        },
        {
          text: "Sair",
          style: "cancel",
          onPress: () => {
            setLoading(false);
            setStatusMessage("");
          },
        },
      ]);
    } finally {
      if (!loading) {
        setLoading(false);
        setStatusMessage("");
      }
    }
  };

  const handleUsernameChange = (text) => {
    setUsername(text);
    if (statusMessage && statusMessage.includes("❌")) {
      setStatusMessage("");
    }
  };

  const handlePasswordChange = (text) => {
    setPassword(text);
    if (statusMessage && statusMessage.includes("❌")) {
      setStatusMessage("");
    }
  };

  return (
    <LinearGradient colors={["#d4fc79", "#96e6a1"]} style={styles.container}>
      <View style={styles.card}>
        <Image source={require("../../assets/logo/logo2.png")} style={styles.logo} />
        <Text style={styles.title}> MedVet</Text>

        <TextInput placeholder="Usuário" style={styles.input} value={username} onChangeText={handleUsernameChange} autoCapitalize="none" editable={!loading} />

        <TextInput placeholder="Senha" style={styles.input} value={password} onChangeText={handlePasswordChange} secureTextEntry editable={!loading} />

        {statusMessage ? (
          <View style={[styles.statusContainer, statusMessage.includes("❌") ? styles.statusError : styles.statusInfo]}>
            <Text style={styles.statusText}>{statusMessage}</Text>
          </View>
        ) : null}

        <TouchableOpacity style={[styles.button, isButtonDisabled && styles.buttonDisabled]} onPress={handleLogin} disabled={isButtonDisabled}>
          {loading ? (
            <>
              <ActivityIndicator color="#fff" size="small" />
              <Text style={styles.buttonText}> AGUARDE...</Text>
            </>
          ) : (
            <Text style={styles.buttonText}>ENTRAR</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => {
            if (!loading) {
              navigation.navigate("Signup");
            }
          }}
          style={styles.link}
          disabled={loading}
        >
          <Text style={[styles.linkText, loading && styles.linkDisabled]}>Não tem conta? Cadastre-se</Text>
        </TouchableOpacity>

        {__DEV__ && loginAttempts > 0 && <Text style={styles.debugText}>Tentativas: {loginAttempts}</Text>}
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    width: "85%",
    backgroundColor: "white",
    borderRadius: 25,
    padding: 30,
    alignItems: "center",
    elevation: 10,
    shadowColor: "#000",
    shadowOpacity: 0.2,
    shadowRadius: 10,
  },
  logo: {
    width: 80,
    height: 80,
    marginBottom: 20,
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#4a8f7a",
    marginBottom: 30,
  },
  input: {
    width: "100%",
    height: 50,
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 12,
    paddingHorizontal: 15,
    marginBottom: 15,
    backgroundColor: "#fafafa",
  },
  button: {
    width: "100%",
    height: 55,
    backgroundColor: "#4a8f7a",
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 10,
    flexDirection: "row",
  },
  buttonDisabled: {
    backgroundColor: "#ccc",
  },
  buttonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },
  link: {
    marginTop: 20,
  },
  linkText: {
    color: "#4a8f7a",
    fontWeight: "600",
  },
  linkDisabled: {
    color: "#ccc",
  },
  statusContainer: {
    width: "100%",
    padding: 10,
    borderRadius: 8,
    marginBottom: 15,
    alignItems: "center",
  },
  statusInfo: {
    backgroundColor: "#e3f2fd",
    borderColor: "#2196f3",
    borderWidth: 1,
  },
  statusError: {
    backgroundColor: "#ffebee",
    borderColor: "#f44336",
    borderWidth: 1,
  },
  statusText: {
    fontSize: 14,
    color: "#333",
    textAlign: "center",
  },
  debugText: {
    marginTop: 10,
    fontSize: 12,
    color: "#999",
  },
});
