package br.com.fiap.javaadv.blog.backend.resources.dtos;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.AcaoPreventiva;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AcaoPreventivaResponse {

    private UUID id;
    private String nomeServico;
    private String descricao;
    private String proximoPrevisto;
    private LocalDateTime dataHoraRegistro;
    private UUID animalId;

    public static AcaoPreventivaResponse fromEntity(AcaoPreventiva entity) {
        return AcaoPreventivaResponse.builder()
                .id(entity.getId())
                .nomeServico(entity.getNomeServico())
                .descricao(entity.getDescricao())
                .proximoPrevisto(entity.getProximoPrevisto())
                .dataHoraRegistro(entity.getDataHoraRegistro())
                .animalId(entity.getAnimal() != null ? entity.getAnimal().getId() : null)
                .build();
    }
}