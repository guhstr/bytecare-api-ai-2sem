package br.com.fiap.javaadv.blog.backend.resources.dtos;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.Animal;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.TipoAnimalEnum;
import lombok.*;

import java.time.LocalDate;
import java.util.UUID;

@AllArgsConstructor
@NoArgsConstructor
@Builder
@Data
public class AnimalResponse {

    private UUID id;
    private String nome;
    private TipoAnimalEnum tipo;
    private String raca;
    private LocalDate dataNascimento;
    private String observacaoGeral;
    private boolean ativo;

    private Long subcategoriaId;

    public static AnimalResponse toDto(Animal animal) {
        if (animal == null) {
            return null;
        }

        return AnimalResponse.builder()
                .id(animal.getId())
                .nome(animal.getNome())
                .tipo(parseTipo(animal.getTipo()))
                .raca(animal.getRaca())
                .dataNascimento(animal.getDataNascimento())
                .observacaoGeral(animal.getObservacaoGeral())
                .ativo(animal.isAtivo())
                .subcategoriaId(animal.getSubcategoriaId()) // 👈 ADICIONAR
                .build();
    }

    private static TipoAnimalEnum parseTipo(String tipo) {
        try {
            return (tipo != null) ? TipoAnimalEnum.valueOf(tipo.toUpperCase()) : null;
        } catch (IllegalArgumentException | NullPointerException e) {
            return null;
        }
    }
}