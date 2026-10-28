import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { preventivoService } from "../services/preventivoService";

export const usePreventivo = (animalId) => {
  return useQuery({
    queryKey: ["preventivo", animalId], 
    queryFn: () => preventivoService.findByAnimal(animalId),
    enabled: !!animalId,
  });
};

export const useCreatePreventivo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: preventivoService.create,
    onSuccess: (data) => {
     
      queryClient.invalidateQueries({ queryKey: ["preventivo", data.idAnimal] });
    },
  });
};

export const useUpdatePreventivo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => preventivoService.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["preventivo", data.idAnimal] });
    },
  });
};

export const useDeletePreventivo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: preventivoService.delete,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["preventivo"] });
    },
  });
};
