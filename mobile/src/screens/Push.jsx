import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, SafeAreaView } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useTheme } from "../../context/ThemeContext";

export default function Push({ navigation }) {
  const { colors, dark } = useTheme();

  const schedule = async () => {
    console.log("🔔 [Lembrete Notificação] Agendado para daqui a 15s");
    Alert.alert(
      "Lembrete Configurado",
      "Lembrete MedVet 🐾: Notificação agendada para daqui a 15 segundos! Fique atento às vacinas e consultas do pet.",
      [{ text: "OK", onPress: () => navigation.navigate("Home") }]
    );
  };

  return (
    <LinearGradient colors={colors.background} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <TouchableOpacity style={[styles.backButton, { backgroundColor: colors.card }]} onPress={() => navigation.goBack()}>
          <Ionicons name="chevron-back" size={24} color={colors.text} />
        </TouchableOpacity>

        <View style={[styles.card, { backgroundColor: colors.card }]}>
          <View style={[styles.iconWrapper, { backgroundColor: dark ? "rgba(76, 175, 80, 0.15)" : "#E8F5E9" }]}>
            <Ionicons name="notifications" size={48} color="#4CAF50" />
          </View>

          <Text style={[styles.title, { color: colors.text }]}>Lembretes de Saúde</Text>

          <Text style={[styles.description, { color: colors.subText || "#666" }]}>
            Agende um alerta para não esquecer as consultas, exames ou o calendário de vacinação do seu pet.
          </Text>

          <TouchableOpacity style={styles.actionButton} onPress={schedule} activeOpacity={0.8}>
            <Ionicons name="alarm-outline" size={20} color="#FFF" style={styles.buttonIcon} />
            <Text style={styles.buttonText}>Agendar Lembrete (15s)</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
    paddingHorizontal: 20,
    justifyContent: "center",
  },
  backButton: {
    position: "absolute",
    top: 50,
    left: 20,
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
    elevation: 3,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    zIndex: 10,
  },
  card: {
    padding: 28,
    borderRadius: 24,
    alignItems: "center",
    elevation: 6,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    marginHorizontal: 10,
  },
  iconWrapper: {
    width: 90,
    height: 90,
    borderRadius: 45,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 20,
  },
  title: {
    fontSize: 22,
    fontWeight: "700",
    marginBottom: 10,
    textAlign: "center",
  },
  description: {
    fontSize: 14,
    textAlign: "center",
    lineHeight: 20,
    marginBottom: 28,
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#4CAF50",
    width: "100%",
    paddingVertical: 14,
    borderRadius: 14,
    elevation: 2,
    shadowColor: "#4CAF50",
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
  },
  buttonIcon: {
    marginRight: 8,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
  },
});
