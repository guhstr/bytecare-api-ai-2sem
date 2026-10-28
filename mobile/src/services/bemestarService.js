import api from "./api";

export const bemestarService = {
  async create(data) {
    try {
      const response = await api.post("/atividades-bem-estar", data);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar bem-estar:", error);
      throw error.response?.data || { error: "Erro ao criar bem-estar" };
    }
  },

  async findByAnimal(animalId) {
    try {
      if (!animalId) return [];
      const response = await api.get(`/atividades-bem-estar/animal/${animalId}`);
      return response.data || [];
    } catch (error) {
      console.error("Erro ao buscar bem-estar:", error);
      return [];
    }
  },

  async update(id, data) {
    try {
      const response = await api.put(`/atividades-bem-estar/${id}`, data);
      return response.data;
    } catch (error) {
      console.error("Erro ao atualizar bem-estar:", error);
      throw error.response?.data || { error: "Erro ao atualizar bem-estar" };
    }
  },

  async delete(id) {
    try {
      await api.delete(`/atividades-bem-estar/${id}`);
      return { success: true };
    } catch (error) {
      console.error("Erro ao deletar bem-estar:", error);
      throw error.response?.data || { error: "Erro ao deletar bem-estar" };
    }
  },
};
