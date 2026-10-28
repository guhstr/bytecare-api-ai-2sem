import React, { createContext, useState, useContext, useEffect, useCallback } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { authService } from "../src/services/authService";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    setLoading(true);
    try {
      const token = await AsyncStorage.getItem("@auth_token");
      const username = await AsyncStorage.getItem("@usuario_nome");
      const role = await AsyncStorage.getItem("@usuario_role");
      const ativo = await AsyncStorage.getItem("@usuario_ativo");

      if (token && username) {
        const userData = {
          username,
          role: role || "USER",
          ativo: ativo === "true",
        };
        setUser(userData);
        return userData;
      } else {
        setUser(null);
        return null;
      }
    } catch (error) {
      console.error("Erro ao carregar usuário:", error);
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (username, password) => {
    try {
      const data = await authService.login(username, password);
      
      const newUser = {
        username: data.username,
        role: data.role || 'USER',
        ativo: data.ativo || false,
      };
      
      setUser(newUser);
      return data;
    } catch (error) {
      console.error("AuthContext - erro no login:", error);
      throw error;
    }
  };

  const logout = async () => {
    console.log("AuthContext - fazendo logout manual");
    try {
      await authService.logout();
    } catch (error) {
      console.error("Erro ao fazer logout:", error);
    } finally {
      setUser(null);
    }
  };

  const register = async (username, password, role = "USER") => {
    try {
      const data = await authService.register(username, password, role);
      return data;
    } catch (error) {
      console.error("AuthContext - erro no registro:", error);
      throw error;
    }
  };

  const refreshUser = useCallback(async () => {
    return await loadUser();
  }, [loadUser]);

  const isAuthenticated = useCallback(() => {
    return !!user;
  }, [user]);

  const value = {
    user,
    loading,
    login,
    logout,
    register,
    refreshUser,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return context;
};