package br.com.fiap.javaadv.blog.backend.resources.dtos;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AtividadeBemEstarRequest {

    @NotBlank(message = "A atividade é obrigatória")
    private String atividade;

    private String observacao;

    private String categoria;

    @NotNull(message = "O ID do animal é obrigatório")
    private String idAnimal;
}