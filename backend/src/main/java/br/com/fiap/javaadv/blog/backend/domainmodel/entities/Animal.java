package br.com.fiap.javaadv.blog.backend.domainmodel.entities;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Entity
@Table(name = "ANIMAL")
@NoArgsConstructor
@AllArgsConstructor
@ToString(exclude = {"preventivos", "tratamentos", "atividades", "registrosCuidado"})
@Builder
@Getter
@Setter
public class Animal {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "ID", columnDefinition = "RAW(16)")
    private UUID id;

    @Column(name = "NOME", nullable = false, length = 100)
    private String nome;

    @Column(name = "TIPO", nullable = false, length = 50)
    private String tipo;

    @Column(name = "RACA", length = 50)
    private String raca;

    @Column(name = "DATA_NASCIMENTO")
    private LocalDate dataNascimento;

    @Column(name = "OBSERVACAO_GERAL", length = 500)
    private String observacaoGeral;

    @Column(name = "ATIVO", nullable = false)
    private boolean ativo = true;

    @Column(name = "SUBCATEGORIA_ID", nullable = false)
    private Long subcategoriaId;

    @OneToMany(mappedBy = "animal", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<AcaoPreventiva> preventivos = new ArrayList<>();

    @OneToMany(mappedBy = "animal", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<TratamentoTerapeutico> tratamentos = new ArrayList<>();

    @OneToMany(mappedBy = "animal", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<AtividadeBemEstar> atividades = new ArrayList<>();

    @OneToMany(mappedBy = "animal", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<RegistroCuidado> registrosCuidado = new ArrayList<>();

    public Animal(String nome, String tipo, String raca, LocalDate dataNascimento,
                  String observacaoGeral, Long subcategoriaId) {
        this.nome = nome;
        this.tipo = tipo;
        this.raca = raca;
        this.dataNascimento = dataNascimento;
        this.observacaoGeral = observacaoGeral;
        this.ativo = true;
        this.subcategoriaId = subcategoriaId;
        this.preventivos = new ArrayList<>();
        this.tratamentos = new ArrayList<>();
        this.atividades = new ArrayList<>();
        this.registrosCuidado = new ArrayList<>();
    }

    public static Animal create(String nome, String tipo, String raca,
                                LocalDate dataNascimento, String observacaoGeral,
                                Long subcategoriaId) {
        return Animal.builder()
                .nome(nome)
                .tipo(tipo)
                .raca(raca)
                .dataNascimento(dataNascimento)
                .observacaoGeral(observacaoGeral)
                .ativo(true)
                .subcategoriaId(subcategoriaId)
                .preventivos(new ArrayList<>())
                .tratamentos(new ArrayList<>())
                .atividades(new ArrayList<>())
                .registrosCuidado(new ArrayList<>())
                .build();
    }

    public void addPreventivo(AcaoPreventiva preventivo) {
        preventivos.add(preventivo);
        preventivo.setAnimal(this);
    }

    public void removePreventivo(AcaoPreventiva preventivo) {
        preventivos.remove(preventivo);
        preventivo.setAnimal(null);
    }

    public void addTratamento(TratamentoTerapeutico tratamento) {
        tratamentos.add(tratamento);
        tratamento.setAnimal(this);
    }

    public void removeTratamento(TratamentoTerapeutico tratamento) {
        tratamentos.remove(tratamento);
        tratamento.setAnimal(null);
    }

    public void addAtividade(AtividadeBemEstar atividade) {
        atividades.add(atividade);
        atividade.setAnimal(this);
    }

    public void removeAtividade(AtividadeBemEstar atividade) {
        atividades.remove(atividade);
        atividade.setAnimal(null);
    }

    public void addRegistroCuidado(RegistroCuidado registro) {
        registrosCuidado.add(registro);
        registro.setAnimal(this);
    }

    public void removeRegistroCuidado(RegistroCuidado registro) {
        registrosCuidado.remove(registro);
        registro.setAnimal(null);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Animal animal = (Animal) o;
        return Objects.equals(id, animal.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }
}