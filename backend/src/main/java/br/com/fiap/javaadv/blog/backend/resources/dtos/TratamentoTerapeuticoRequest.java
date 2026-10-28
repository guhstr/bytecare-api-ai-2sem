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
public class TratamentoTerapeuticoRequest {

    @NotBlank(message = "O nome do medicamento e obrigatorio")
    private String medicamento;

    private String dosagem;

    private String observacao;

    @NotNull(message = "O ID do animal e obrigatorio")
    private String idAnimal;
}
