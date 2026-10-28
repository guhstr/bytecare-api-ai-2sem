package br.com.fiap.javaadv.blog.backend.resources.dtos;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.TratamentoTerapeutico;
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
public class TratamentoTerapeuticoResponse {

    private UUID id;
    private String medicamento;
    private String dosagem;
    private String observacao;
    private LocalDateTime dataHoraRegistro;
    private UUID animalId;

    public static TratamentoTerapeuticoResponse fromEntity(TratamentoTerapeutico entity) {
        return TratamentoTerapeuticoResponse.builder()
                .id(entity.getId())
                .medicamento(entity.getMedicamento())
                .dosagem(entity.getDosagem())
                .observacao(entity.getObservacao())
                .dataHoraRegistro(entity.getDataHoraRegistro())
                .animalId(entity.getAnimal() != null ? entity.getAnimal().getId() : null)
                .build();
    }
}
