import api from "./api";

export const animalService = {

  async create(data) {
    try {
      const response = await api.post("/animais", data);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar animal:", error);
      throw error.response?.data || { error: "Erro ao criar animal" };
    }
  },

  async findBySubcategoria(subcategoriaId) {
    try {
      if (!subcategoriaId) {
        console.warn("⚠️ subcategoriaId não fornecido");
        return []; 
      }

      console.log(`📡 Buscando animais da subcategoria: ${subcategoriaId}`);
      const response = await api.get(`/animais/subcategoria/${subcategoriaId}`);

      return response.data || [];
    } catch (error) {
      console.error("Erro ao buscar animais:", error);
  
      return [];
    }
  },


  async findAll() {
    try {
      const response = await api.get("/animais");
      return response.data || [];
    } catch (error) {
      console.error("Erro ao buscar todos os animais:", error);
      return [];
    }
  },

  async findById(id) {
    try {
      const response = await api.get(`/animais/${id}`);
      return response.data;
    } catch (error) {
      console.error("Erro ao buscar animal por ID:", error);
      throw error.response?.data || { error: "Erro ao buscar animal" };
    }
  },


  async update(id, data) {
    try {
      const response = await api.put(`/animais/${id}`, data);
      return response.data;
    } catch (error) {
      console.error("Erro ao atualizar animal:", error);
      throw error.response?.data || { error: "Erro ao atualizar animal" };
    }
  },


  async delete(id) {
    try {
      await api.delete(`/animais/${id}`);
      return { success: true };
    } catch (error) {
      console.error("Erro ao deletar animal:", error);
      throw error.response?.data || { error: "Erro ao deletar animal" };
    }
  },
};
