package br.com.fiap.javaadv.blog.backend.resources.dtos;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.RegistroCuidado;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.time.LocalDate;

@AllArgsConstructor
@NoArgsConstructor
@Builder
@Data
public class RegistroCuidadoResponse {

    private String id;
    private String categoria;


    @JsonProperty("dataHoraRegistro")
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "dd-MM-yyyy")
    private LocalDate dataRegistro;

    @JsonProperty("observacao")
    private String observacao;

    private String idAnimal;
    private String nomeAnimal;

    public static RegistroCuidadoResponse toDto(final RegistroCuidado entity) {
        if (entity == null) return null;

        return RegistroCuidadoResponse.builder()
                .id(entity.getId() != null ? entity.getId().toString() : null)
                .categoria(entity.getCategoria() != null ? entity.getCategoria().name() : null)
                .dataRegistro(entity.getDataHoraRegistro() != null ? entity.getDataHoraRegistro().toLocalDate() : null)
                .observacao(entity.getDescricao())
                .idAnimal(entity.getAnimal() != null ? entity.getAnimal().getId().toString() : null)
                .nomeAnimal(entity.getAnimal() != null ? entity.getAnimal().getNome() : null)
                .build();
    }
}