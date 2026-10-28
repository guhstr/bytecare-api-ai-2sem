package br.com.fiap.javaadv.blog.backend.resources.dtos;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AcaoPreventivaRequest {

    @NotBlank(message = "O nome do serviço é obrigatório")
    private String nomeServico;

    private String descricao;

    private String proximoPrevisto;

    @NotNull(message = "O ID do animal é obrigatório")
    private UUID idAnimal;
}