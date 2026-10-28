import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { terapeuticoService } from "../services/terapeuticoService";

export const useTerapeutico = (animalId) => {
  return useQuery({
    queryKey: ["terapeutico", animalId],
    queryFn: () => terapeuticoService.findByAnimal(animalId),
    enabled: !!animalId,
    staleTime: 1000 * 60 * 5,
  });
};

export const useCreateTerapeutico = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: terapeuticoService.create,
    onSuccess: (data) => {
  
      queryClient.invalidateQueries({
        queryKey: ["terapeutico", data.idAnimal],
      });
    },
    onError: (error) => {
      console.error("Erro ao criar tratamento:", error);
    },
  });
};

export const useUpdateTerapeutico = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => terapeuticoService.update(id, data),
    onSuccess: (data) => {
      // 🔧 CORRIGIDO: data.idAnimal (não data.animalId)
      queryClient.invalidateQueries({
        queryKey: ["terapeutico", data.idAnimal],
      });
    },
    onError: (error) => {
      console.error("Erro ao atualizar tratamento:", error);
    },
  });
};

export const useDeleteTerapeutico = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: terapeuticoService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["terapeutico"],
      });
    },
    onError: (error) => {
      console.error("Erro ao deletar tratamento:", error);
    },
  });
};
