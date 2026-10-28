package br.com.fiap.javaadv.blog.backend.resources.dtos;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.AtividadeBemEstar;
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
public class AtividadeBemEstarResponse {

    private UUID id;
    private String atividade;
    private String observacao;
    private String categoria;
    private LocalDateTime dataHoraRegistro;
    private UUID animalId;

    public static AtividadeBemEstarResponse fromEntity(AtividadeBemEstar entity) {
        return AtividadeBemEstarResponse.builder()
                .id(entity.getId())
                .atividade(entity.getAtividade())
                .observacao(entity.getObservacao())
                .categoria(entity.getCategoria())
                .dataHoraRegistro(entity.getDataHoraRegistro())
                .animalId(entity.getAnimal() != null ? entity.getAnimal().getId() : null)
                .build();
    }
}