import api from "./api";

export const terapeuticoService = {
  async create(data) {
    try {
      
      const response = await api.post("/tratamentos-terapeuticos", data);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar terapêutico:", error);
      throw error.response?.data || { error: "Erro ao criar terapêutico" };
    }
  },

  async findByAnimal(animalId) {
    try {
      if (!animalId) return [];
     
      const response = await api.get(`/tratamentos-terapeuticos/animal/${animalId}`);
      return response.data?.content || response.data || [];
    } catch (error) {
      console.error("Erro ao buscar terapêuticos:", error);
      return [];
    }
  },

  async update(id, data) {
    try {
    
      const response = await api.put(`/tratamentos-terapeuticos/${id}`, data);
      return response.data;
    } catch (error) {
      console.error("Erro ao atualizar terapêutico:", error);
      throw error.response?.data || { error: "Erro ao atualizar terapêutico" };
    }
  },

  async delete(id) {
    try {
   
      await api.delete(`/tratamentos-terapeuticos/${id}`);
      return { success: true };
    } catch (error) {
      console.error("Erro ao deletar terapêutico:", error);
      throw error.response?.data || { error: "Erro ao deletar terapêutico" };
    }
  },
};