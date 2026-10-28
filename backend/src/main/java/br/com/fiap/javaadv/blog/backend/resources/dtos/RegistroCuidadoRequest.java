package br.com.fiap.javaadv.blog.backend.resources.dtos;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.Animal;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.RegistroCuidado;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.CategoriaCuidadoEnum;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalTime;

@AllArgsConstructor
@NoArgsConstructor
@Builder
@Data
public class RegistroCuidadoRequest {

    @NotNull(message = "A categoria é obrigatória")
    private CategoriaCuidadoEnum categoria;

    @NotNull(message = "A data do registro é obrigatória")
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "dd-MM-yyyy")
    @JsonProperty("dataHoraRegistro")
    private LocalDate dataRegistro;

    @JsonProperty("observacao")
    @Size(max = 500, message = "A descrição deve ter no máximo 500 caracteres")
    private String descricao;

    @NotBlank(message = "O ID do animal é obrigatório")
    @JsonProperty("idAnimal")
    private String idAnimal;

    public RegistroCuidado toEntity(Animal animal) {
        return RegistroCuidado.builder()
                .categoria(this.categoria)
                .dataHoraRegistro(this.dataRegistro.atTime(LocalTime.now()))
                .descricao(this.descricao)
                .animal(animal)
                .build();
    }
}