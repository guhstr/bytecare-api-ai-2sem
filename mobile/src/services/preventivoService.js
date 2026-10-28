import api from './api';

export const preventivoService = {
  async create(data) {
    try {
      const response = await api.post('/preventivos', data);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar preventivo:', error);
      throw error.response?.data || { error: 'Erro ao criar preventivo' };
    }
  },

  async findByAnimal(animalId) {
    try {
      if (!animalId) return [];
      const response = await api.get(`/preventivos/animal/${animalId}`);
      return response.data || [];
    } catch (error) {
      console.error('Erro ao buscar preventivos:', error);
      return [];
    }
  },

  async update(id, data) {
    try {
      const response = await api.put(`/preventivos/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar preventivo:', error);
      throw error.response?.data || { error: 'Erro ao atualizar preventivo' };
    }
  },

  async delete(id) {
    try {
      await api.delete(`/preventivos/${id}`);
      return { success: true };
    } catch (error) {
      console.error('Erro ao deletar preventivo:', error);
      throw error.response?.data || { error: 'Erro ao deletar preventivo' };
    }
  }
};