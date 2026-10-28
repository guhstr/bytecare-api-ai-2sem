

import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const authService = {
  async login(username, password) {
    try {
      console.log('🔑 Tentando login em:', api.defaults.baseURL + '/auth/login');
      console.log('🔑 Usuário:', username);
      
      const response = await api.post('/auth/login', { username, password });
      
      console.log('🔑 Login response (COMPLETA):', JSON.stringify(response.data, null, 2));
      console.log('🔑 Campos da resposta:', Object.keys(response.data));
     
      const possibleTokenFields = ['token', 'accessToken', 'jwt', 'authToken', 'access_token', 'id_token', 'tokenJwt'];
      let token = null;
      let tokenField = null;
      
      for (const field of possibleTokenFields) {
        if (response.data[field]) {
          token = response.data[field];
          tokenField = field;
          break;
        }
      }
      
      if (token) {
        console.log(`✅ Token encontrado no campo: "${tokenField}"`);
        console.log('✅ Token:', token.substring(0, 30) + '...');
        
    
        await AsyncStorage.setItem('@auth_token', token);
        await AsyncStorage.setItem('@usuario_nome', response.data.username || response.data.user || '');
        await AsyncStorage.setItem('@usuario_role', response.data.role || response.data.roles || 'USER');
        await AsyncStorage.setItem('@usuario_ativo', String(response.data.ativo || response.data.active || false));
        
        await AsyncStorage.setItem('@usuario_senha', password);
        
        console.log('💾 Dados salvos no AsyncStorage!');
        console.log('💾 Senha salva para renovação automática');
        
     
        const savedToken = await AsyncStorage.getItem('@auth_token');
        console.log('🔍 Token salvo no AsyncStorage:', savedToken ? '✅ SIM' : '❌ NÃO');
        if (savedToken) {
          console.log('🔍 Token salvo:', savedToken.substring(0, 30) + '...');
        }
        
        const savedUsername = await AsyncStorage.getItem('@usuario_nome');
        const savedRole = await AsyncStorage.getItem('@usuario_role');
        console.log('👤 Usuário salvo:', savedUsername);
        console.log('👤 Role salva:', savedRole);
        
      } else {
        console.warn('⚠️ NENHUM TOKEN ENCONTRADO NA RESPOSTA!');
        console.warn('⚠️ Resposta completa:', response.data);
        console.warn('⚠️ Verifique se o backend está retornando um token.');
        console.warn('⚠️ Possíveis campos esperados: token, accessToken, jwt, authToken');
      }
      
      return response.data;
    } catch (error) {
      console.error(' Erro no login service:', error);
      
      if (error.response) {
        console.error(' Status do erro:', error.response.status);
        console.error(' Dados do erro:', error.response.data);
      } else if (error.request) {
        console.error(' Sem resposta do servidor:', error.request);
      } else {
        console.error(' Erro na configuração:', error.message);
      }
      
      throw error.response?.data || { error: 'Erro ao fazer login' };
    }
  },

  async register(username, password, role = 'USER') {
    try {
      console.log(' Tentando registrar:', username);
      console.log(' Role:', role);
      
      const response = await api.post('/auth/register', { username, password, role });
      
      console.log(' Registro response:', response.data);
      return response.data;
    } catch (error) {
      console.error(' Erro no register service:', error);
      
      if (error.response) {
        console.error(' Status do erro:', error.response.status);
        console.error(' Dados do erro:', error.response.data);
      }
      
      throw error.response?.data || { error: 'Erro ao registrar' };
    }
  },

  async logout() {
    try {
      console.log('🚪 Fazendo logout...');
      
      await AsyncStorage.removeItem('@auth_token');
      await AsyncStorage.removeItem('@usuario_nome');
      await AsyncStorage.removeItem('@usuario_role');
      await AsyncStorage.removeItem('@usuario_ativo');
      await AsyncStorage.removeItem('@usuario_senha'); // 👈 REMOVER SENHA TAMBÉM
      
      console.log(' Logout realizado, tokens e senha removidos');
    } catch (error) {
      console.error(' Erro no logout:', error);
    }
  },

  async getCurrentUser(username) {
    try {
      console.log('👤 Buscando usuário:', username);
      const response = await api.get(`/auth/me?username=${username}`);
      return response.data;
    } catch (error) {
      console.error(' Erro ao buscar usuário:', error);
      throw error.response?.data || { error: 'Erro ao buscar usuário' };
    }
  },

  async isAuthenticated() {
    try {
      const token = await AsyncStorage.getItem('@auth_token');
      console.log('🔍 isAuthenticated - token:', token ? '✅ EXISTE' : ' NÃO EXISTE');
      return !!token;
    } catch (error) {
      console.error(' Erro ao verificar autenticação:', error);
      return false;
    }
  },

  async getToken() {
    try {
      const token = await AsyncStorage.getItem('@auth_token');
      console.log('🔍 getToken - token:', token ? '✅ EXISTE' : ' NÃO EXISTE');
      if (token) {
        console.log('🔍 getToken - token value:', token.substring(0, 30) + '...');
      }
      return token;
    } catch (error) {
      console.error(' Erro ao buscar token:', error);
      return null;
    }
  },


  async getCredentials() {
    try {
      const username = await AsyncStorage.getItem('@usuario_nome');
      const password = await AsyncStorage.getItem('@usuario_senha');
      
      console.log('🔍 Credenciais:', username ? '✅ USUÁRIO' : ' NÃO', password ? '✅ SENHA' : ' NÃO');
      
      if (username && password) {
        return { username, password };
      }
      return null;
    } catch (error) {
      console.error(' Erro ao buscar credenciais:', error);
      return null;
    }
  }
};