import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { animalService } from '../services/animalService';

export const useAnimals = (subcategoriaId) => {
  return useQuery({
    queryKey: ['animals', subcategoriaId],
    queryFn: async () => {
      const result = await animalService.findBySubcategoria(subcategoriaId);

      return result || [];
    },
    enabled: !!subcategoriaId,
    initialData: [], 
  });
};

export const useCreateAnimal = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: animalService.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['animals', data?.subcategoriaId] });
    },
  });
};

export const useDeleteAnimal = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: animalService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animals'] });
    },
  });
};