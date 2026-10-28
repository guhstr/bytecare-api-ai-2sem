import React, { useState, useEffect, useCallback } from "react";
import {
  Text,
  StyleSheet,
  View,
  TouchableOpacity,
  Image,
  FlatList,
  ScrollView,
  SafeAreaView,
  Alert,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons, MaterialCommunityIcons } from "@expo/vector-icons";
import { useTheme } from "../../context/ThemeContext.js";
import { useAuth } from "../../context/AuthContext";
import { usePermissions } from "../hooks/usePermissions";

import categorias from "../../dados/categorias.json";
import subcategoriasData from "../../dados/subcategorias.json";

import doggy from "../../assets/subcategoriaIMG/doggy.png";
import gato from "../../assets/subcategoriaIMG/gato.png";
import peixe from "../../assets/subcategoriaIMG/peixe.png";
import vaca from "../../assets/subcategoriaIMG/vaca.png";
import equino from "../../assets/subcategoriaIMG/equino.png";
import galinha from "../../assets/subcategoriaIMG/galinha.png";
import papagaio from "../../assets/subcategoriaIMG/papagaio.png";
import canario from "../../assets/subcategoriaIMG/canario.png";
import calopsita from "../../assets/subcategoriaIMG/Calopsita.png";

const dogIcon = require("../../assets/PNG_ICons/dog.png");
const bullIcon = require("../../assets/PNG_ICons/bull.png");
const pigeonIcon = require("../../assets/PNG_ICons/pigeon.png");

const IMAGES = {
  101: doggy,
  102: gato,
  103: peixe,
  104: vaca,
  105: equino,
  106: galinha,
  107: papagaio,
  108: canario,
  109: calopsita,
};

const ICONS = {
  Pets: dogIcon,
  Agro: bullIcon,
  Pássaros: pigeonIcon,
};

const CATEGORY_RANGES = {
  Pets: [101, 103],
  Agro: [104, 106],
  Pássaros: [107, 109],
};

export default function Home({ navigation }) {
  const { colors, dark, toggleTheme } = useTheme();
  const { logout } = useAuth();
  const { isAdmin } = usePermissions();
  const [selectedCategory, setSelectedCategory] = useState("Pets");
  const [displayedSubcategories, setDisplayedSubcategories] = useState([]);
  const [nomeUsuario, setNomeUsuario] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const carregarNomeUsuario = useCallback(async () => {
    try {
      const nomeSalvo = await AsyncStorage.getItem("@usuario_nome");
      setNomeUsuario(nomeSalvo || "Visitante");
    } catch (e) {
      console.error("Erro ao carregar nome do usuário:", e);
    }
  }, []);

  const handleCategoryPress = useCallback((nome) => {
    setSelectedCategory(nome);
    const range = CATEGORY_RANGES[nome] || CATEGORY_RANGES.Pets;
    const filtered = subcategoriasData.subcategorias.filter(
      (s) => s.id >= range[0] && s.id <= range[1]
    );
    setDisplayedSubcategories(filtered);
  }, []);

  useEffect(() => {
    carregarNomeUsuario();
    handleCategoryPress("Pets");

    const unsubscribe = navigation.addListener("focus", () => {
      carregarNomeUsuario();
      setRefreshKey((prev) => prev + 1);
    });

    return unsubscribe;
  }, [navigation, carregarNomeUsuario, handleCategoryPress]);

  const handleLogout = useCallback(() => {
    Alert.alert("Sair", "Tem certeza que deseja sair?", [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Sair",
        style: "destructive",
        onPress: async () => {
          await logout();
          navigation.reset({
            index: 0,
            routes: [{ name: "Login" }],
          });
        },
      },
    ]);
  }, [logout, navigation]);

  const getIcon = useCallback((cat) => ICONS[cat] || dogIcon, []);
  const getImagensubcategoria = useCallback((id) => IMAGES[id] || dogIcon, []);

  const renderSubcategoryItem = useCallback(
    ({ item }) => (
      <TouchableOpacity
        style={[styles.subcategoryBox, { backgroundColor: colors.card }]}
        onPress={() => {
          navigation.navigate("SubcategoriaListagem", {
            subcategory: item,
            timestamp: Date.now(),
          });
        }}
      >
        <View style={[styles.subcategoryCircle, { backgroundColor: colors.iconBg }]}>
          <Image
            source={getImagensubcategoria(item.id)}
            style={styles.subcategoryImage}
            resizeMode="contain"
          />
        </View>
        <Text style={[styles.subcategoryNome, { color: colors.text }]}>
          {item.nome}
        </Text>
      </TouchableOpacity>
    ),
    [colors, navigation, getImagensubcategoria]
  );

  return (
    <LinearGradient colors={colors.background} style={styles.container}>
      <SafeAreaView style={{ flex: 1 }}>
        <ScrollView showsVerticalScrollIndicator={false}>
          <View style={[styles.headerContainer, { backgroundColor: colors.card }]}>
            <View style={styles.headerTop}>
              <View style={styles.bannerTitle}>
                <Image
                  style={styles.logo}
                  source={require("../../assets/logo/logo2.png")}
                />
                <Text style={[styles.bannerNome, { color: colors.text }]}>
                  MedVet
                </Text>
              </View>
              <View style={styles.headerActions}>
                <TouchableOpacity
                  onPress={() => navigation.navigate("ChatIA")}
                  style={styles.iconButton}
                  accessibilityLabel="Assistente IA"
                >
                  <MaterialCommunityIcons
                    name="robot-outline"
                    size={24}
                    color={colors.primary}
                  />
                </TouchableOpacity>
                <TouchableOpacity onPress={toggleTheme} style={styles.iconButton}>
                  <Ionicons
                    name={dark ? "sunny" : "moon"}
                    size={24}
                    color={dark ? "#FFD700" : "#444"}
                  />
                </TouchableOpacity>
                <TouchableOpacity onPress={handleLogout} style={styles.iconButton}>
                  <MaterialCommunityIcons
                    name="logout"
                    size={24}
                    color="#F44336"
                  />
                </TouchableOpacity>
              </View>
            </View>

            <View style={styles.userInfo}>
              <View>
                <Text style={[styles.welcomeText, { color: colors.subText }]}>
                  Olá,
                </Text>
                <Text style={[styles.userName, { color: colors.text }]}>
                  {nomeUsuario}
                </Text>
                {isAdmin && (
                  <Text style={[styles.adminBadge, { color: "#4CAF50" }]}>
                    👑 ADMIN
                  </Text>
                )}
              </View>
              <Image
                style={styles.userImg}
                source={require("../../assets/userIMG/user.jpeg")}
              />
            </View>
          </View>

          <View style={styles.content}>
            {/* Banner ByteCare Intelligence */}
            <TouchableOpacity
              style={[
                styles.aiBanner,
                {
                  backgroundColor: dark ? "#1E293B" : "#F0FDF4",
                  borderColor: colors.primary,
                },
              ]}
              onPress={() => navigation.navigate("ChatIA")}
              activeOpacity={0.85}
            >
              <View style={[styles.aiBannerIcon, { backgroundColor: colors.primary }]}>
                <MaterialCommunityIcons name="robot" size={24} color="#FFF" />
              </View>
              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={[styles.aiBannerTitle, { color: colors.text }]}>
                  Assistente ByteCare IA
                </Text>
                <Text style={[styles.aiBannerSub, { color: colors.subText }]}>
                  Orientações inteligentes, triagem e suporte clínico
                </Text>
              </View>
              <MaterialCommunityIcons name="chevron-right" size={22} color={colors.primary} />
            </TouchableOpacity>

            <View style={styles.categoriesRow}>
              {categorias.categorias.map((categoria) => (
                <TouchableOpacity
                  key={categoria.id}
                  onPress={() => handleCategoryPress(categoria.nome)}
                  style={styles.categoryItem}
                >
                  <View
                    style={[
                      styles.circle,
                      {
                        backgroundColor: colors.card,
                        borderColor:
                          selectedCategory === categoria.nome
                            ? colors.primary
                            : "transparent",
                      },
                    ]}
                  >
                    <Image
                      source={getIcon(categoria.nome)}
                      style={styles.imagem}
                      resizeMode="contain"
                    />
                  </View>
                  <Text
                    style={[
                      styles.categoriaNome,
                      {
                        color: colors.text,
                        fontWeight:
                          selectedCategory === categoria.nome ? "700" : "400",
                      },
                    ]}
                  >
                    {categoria.nome}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={[styles.sectionTitle, { color: colors.text }]}>
              {selectedCategory} disponíveis
            </Text>
            <FlatList
              key={refreshKey}
              data={displayedSubcategories}
              renderItem={renderSubcategoryItem}
              keyExtractor={(item) => item.id.toString()}
              numColumns={2}
              columnWrapperStyle={styles.row}
              scrollEnabled={false}
            />
          </View>
        </ScrollView>
        <TouchableOpacity
          style={styles.notificacao}
          onPress={() => navigation.navigate("Push")}
          activeOpacity={0.8}
        >
          <Text style={styles.notificacaoTexto}>
            Agendamento de Notificação
          </Text>
        </TouchableOpacity> 
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  notificacao: {
    backgroundColor: "#4CAF50",
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    marginVertical: 10,
    marginHorizontal: 40, 
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
  },
  notificacaoTexto: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
  },
  container: { flex: 1 },
  headerContainer: {
    margin: 20,
    padding: 20,
    borderRadius: 25,
    elevation: 8,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  headerTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
  },
  bannerTitle: { flexDirection: "row", alignItems: "center" },
  logo: { width: 40, height: 40, marginRight: 10 },
  bannerNome: { fontSize: 22, fontWeight: "800" },
  headerActions: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  iconButton: {
    padding: 8,
    borderRadius: 12,
    backgroundColor: "rgba(150,150,150,0.1)",
  },
  userInfo: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  welcomeText: { fontSize: 16 },
  userName: { fontSize: 20, fontWeight: "bold" },
  adminBadge: { fontSize: 12, fontWeight: "bold" },
  userImg: {
    width: 50,
    height: 50,
    borderRadius: 25,
    borderWidth: 2,
    borderColor: "#4CAF50",
  },
  content: { paddingHorizontal: 20 },
  aiBanner: {
    flexDirection: "row",
    alignItems: "center",
    padding: 14,
    borderRadius: 18,
    borderWidth: 1.5,
    marginBottom: 20,
    elevation: 2,
  },
  aiBannerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  aiBannerTitle: {
    fontSize: 15,
    fontWeight: "bold",
  },
  aiBannerSub: {
    fontSize: 12,
    marginTop: 2,
  },
  categoriesRow: {
    flexDirection: "row",
    justifyContent: "space-around",
    marginBottom: 25,
  },
  categoryItem: { alignItems: "center" },
  circle: {
    width: 70,
    height: 70,
    borderRadius: 35,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 2,
    marginBottom: 8,
    elevation: 4,
  },
  imagem: { width: 35, height: 35 },
  categoriaNome: { fontSize: 12 },
  sectionTitle: { fontSize: 18, fontWeight: "bold", marginBottom: 15, marginLeft: 5 },
  row: { justifyContent: "space-between" },
  subcategoryBox: {
    width: "48%",
    borderRadius: 20,
    padding: 15,
    alignItems: "center",
    marginBottom: 15,
    elevation: 3,
  },
  subcategoryCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: "center",
    alignItems: "center",
  },
  subcategoryImage: { width: 80, height: 80, position: "absolute", top: -10 },
  subcategoryNome: { marginTop: 45, fontSize: 16, fontWeight: "600" },
});
