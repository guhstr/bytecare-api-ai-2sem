import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

import { Platform } from "react-native";

let envApiUrl = "";
try {
  const env = require("@env");
  envApiUrl = env?.API_URL;
} catch (e) {
  // @env not available
}

const defaultHost =
  Platform.OS === "android"
    ? "http://10.0.2.2:8080/api"
    : "http://localhost:8080/api";

const rawApiUrl = envApiUrl || process.env.API_URL || defaultHost;
const API_URL = rawApiUrl.endsWith("/api") ? rawApiUrl : `${rawApiUrl}/api`;
console.log("API_URL:", API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  timeout: 30000,
});


let isRefreshing = false;
let failedQueue = [];
let retryCount = new Map(); 

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem("@auth_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log(`🔑 [${config.method.toUpperCase()}] ${config.url} - Token adicionado`);
      } else {
        console.warn(`⚠️ Sem token para: ${config.method.toUpperCase()} ${config.url}`);
      }
      return config;
    } catch (error) {
      console.error("Erro no interceptor:", error);
      return config;
    }
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => {
    console.log(`✅ [${response.config.method.toUpperCase()}] ${response.config.url} - ${response.status}`);
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Criar chave única para a requisição
    const requestKey = `${originalRequest.method}-${originalRequest.url}`;
    
    // Verificar se já tentou renovar para esta requisição
    if (originalRequest._retry) {
      console.log(`Já tentou renovar para ${requestKey}, parando loop...`);
      
      // Se for DELETE, mostrar erro específico
      if (originalRequest.method?.toUpperCase() === 'DELETE') {
        console.log('Falha ao deletar: token inválido mesmo após renovação');
        return Promise.reject({
          ...error,
          message: 'Sessão expirada. Faça login novamente para deletar.'
        });
      }
      
      return Promise.reject(error);
    }
    

    if (error.response?.status === 401 && !originalRequest.url.includes('/auth/login')) {
      console.warn(`401 em: ${originalRequest.method.toUpperCase()} ${originalRequest.url}`);
      

      if (isRefreshing) {
        console.log('⏳ Aguardando renovação em andamento...');
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch(err => Promise.reject(err));
      }
      

      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        const token = await AsyncStorage.getItem("@auth_token");
        console.log(`🔍 Token atual: ${token ? token.substring(0, 30) + '...' : 'NÃO EXISTE'}`);
        
        if (!token) {
          console.log('⚠️ Sem token para renovar');
          return Promise.reject(error);
        }
        
        console.log(`🔄 Tentando renovar token...`);
        
        const username = await AsyncStorage.getItem("@usuario_nome");
        const password = await AsyncStorage.getItem("@usuario_senha");
        
        if (!username || !password) {
          console.log('⚠️ Credenciais não encontradas');
          return Promise.reject(error);
        }
        
 
        const response = await axios.post(`${API_URL}/auth/login`, { 
          username, 
          password 
        }, {
          timeout: 30000
        });
        
        if (!response.data.token) {
          console.log('⚠️ Token não retornado');
          return Promise.reject(error);
        }
        
        const newToken = response.data.token;
        await AsyncStorage.setItem("@auth_token", newToken);
        console.log(`✅ Token renovado com sucesso!`);

        originalRequest.headers.Authorization = `Bearer ${newToken}`;

        processQueue(null, newToken);
        

        console.log(`🔄 Refazendo requisição: ${originalRequest.method.toUpperCase()} ${originalRequest.url}`);
        return api(originalRequest);
        
      } catch (refreshError) {
        console.error("❌ Falha ao renovar token:", refreshError.message);
        

        processQueue(refreshError, null);
        

        if (originalRequest.method?.toUpperCase() === 'DELETE') {
          console.log('❌ DELETE falhou após renovação de token');
          return Promise.reject({
            ...refreshError,
            message: 'Sessão expirada. Por favor, faça login novamente para deletar.'
          });
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    

    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.log('⏰ Timeout - servidor pode estar acordando...');
      
      if (!originalRequest._retry) {
        originalRequest._retry = true;
        console.log('⏳ Aguardando 5 segundos e tentando novamente...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        return api(originalRequest);
      }
    }
    
    return Promise.reject(error);
  }
);

export const deleteWithRetry = async (url, maxRetries = 2) => {
  let lastError = null;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`🗑️ Tentativa ${attempt} de DELETE: ${url}`);
      
      const response = await api.delete(url);
      console.log(`✅ DELETE bem-sucedido: ${url}`);
      return response;
      
    } catch (error) {
      console.error(`❌ Tentativa ${attempt} falhou:`, error.message);
      lastError = error;

      if (error.response?.status === 401 && attempt < maxRetries) {
        console.log('⏳ Token expirado, tentando renovar e repetir...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        continue;
      }
      

      if ((error.code === 'ECONNABORTED' || error.message?.includes('timeout')) && attempt < maxRetries) {
        console.log('⏳ Timeout, tentando novamente...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        continue;
      }
      

      if (attempt === maxRetries) {
        throw error;
      }
    }
  }
  
  throw lastError;
};


export const checkServerHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/health`, {
      timeout: 10000
    });
    return response.status === 200;
  } catch (error) {
    console.log('⏳ Servidor não respondeu ao health check');
    return false;
  }
};

export const loginWithRetry = async (username, password, maxRetries = 3) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`📱 Tentativa ${attempt} de login...`);
      
      const response = await api.post('/auth/login', { username, password });
      
      if (response.data.token) {
        await AsyncStorage.setItem("@auth_token", response.data.token);
        await AsyncStorage.setItem("@usuario_nome", username);
        await AsyncStorage.setItem("@usuario_senha", password);
        await AsyncStorage.setItem("@usuario_role", response.data.role || 'USER');
        
        console.log('✅ Login bem-sucedido, dados salvos');
        return response.data;
      }
      
      throw new Error('Token não recebido');
      
    } catch (error) {
      console.log(`❌ Tentativa ${attempt} falhou:`, error.message);
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      if (error.message?.includes('timeout')) {
        console.log('⏳ Timeout, esperando 5 segundos...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      } else {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
  }
};

export default api;
