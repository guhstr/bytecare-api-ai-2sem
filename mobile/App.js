import { StatusBar } from "expo-status-bar";
import { StyleSheet, LogBox } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { NavigationContainer } from "@react-navigation/native";
import { QueryClientProvider } from "@tanstack/react-query";
import Routes from "./src/routes/stack.routs";
import { ThemeProvider } from "./context/ThemeContext";
import { AuthProvider } from "./context/AuthContext";
import { queryClient } from "./src/services/queryClient";

LogBox.ignoreAllLogs(true);
console.warn = () => {};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <QueryClientProvider client={queryClient}>
          <SafeAreaProvider style={styles.APPGlobal}>
            <StatusBar style="auto" />
            <NavigationContainer>
              <Routes />
            </NavigationContainer>
          </SafeAreaProvider>
        </QueryClientProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  APPGlobal: {
    flex: 1,
  },
});

