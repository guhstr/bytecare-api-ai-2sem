import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bemestarService } from '../services/bemestarService';

export const useBemEstar = (animalId) => {
  return useQuery({
    queryKey: ['bemestar', animalId],
    queryFn: () => bemestarService.findByAnimal(animalId),
    enabled: !!animalId,
    staleTime: 1000 * 60 * 5,
  });
};

export const useCreateBemEstar = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: bemestarService.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ 
        queryKey: ['bemestar', data.idAnimal] 
      });
    },
    onError: (error) => {
      console.error('Erro ao criar bem-estar:', error);
    },
  });
};

export const useDeleteBemEstar = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: bemestarService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: ['bemestar'] 
      });
    },
    onError: (error) => {
      console.error('Erro ao deletar bem-estar:', error);
    },
  });
};