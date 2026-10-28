package br.com.fiap.javaadv.blog.backend.infrastructure;

import br.com.fiap.javaadv.blog.backend.datasource.repositories.*;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.*;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Component
@RequiredArgsConstructor
public class DataLoader implements CommandLineRunner {

    private final UsuarioRepository usuarioRepository;
    private final AnimalRepository animalRepository;
    private final AcaoPreventivaRepository acaoPreventivaRepository;
    private final TratamentoTerapeuticoRepository tratamentoTerapeuticoRepository;
    private final AtividadeBemEstarRepository atividadeBemEstarRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    @Transactional
    public void run(String... args) throws Exception {
        if (usuarioRepository.count() == 0) {
            Usuario admin = Usuario.builder()
                    .username("admin")
                    .password(passwordEncoder.encode("123456"))
                    .role("ADMIN")
                    .ativo(true)
                    .build();
            usuarioRepository.save(admin);
            System.out.println("Usuario admin criado!");
        }

        if (animalRepository.count() == 0) {
            Animal animal = Animal.builder()
                    .nome("Rex")
                    .tipo("CACHORRO")
                    .raca("Labrador")
                    .dataNascimento(LocalDate.of(2020, 1, 1))
                    .observacaoGeral("Animal saudavel")
                    .ativo(true)
                    .subcategoriaId(101L)
                    .build();
            animalRepository.save(animal);

            AcaoPreventiva preventivo = AcaoPreventiva.builder()
                    .nomeServico("Vacina V8")
                    .descricao("Vacina polivalente")
                    .proximoPrevisto(LocalDate.now().plusMonths(6).format(DateTimeFormatter.ISO_LOCAL_DATE))
                    .dataHoraRegistro(LocalDateTime.now())
                    .animal(animal)
                    .build();
            acaoPreventivaRepository.save(preventivo);

            TratamentoTerapeutico tratamento = TratamentoTerapeutico.builder()
                    .medicamento("Antipulgas")
                    .dosagem("1 comprimido")
                    .observacao("Aplicar mensalmente")
                    .dataHoraRegistro(LocalDateTime.now())
                    .animal(animal)
                    .build();
            tratamentoTerapeuticoRepository.save(tratamento);

            AtividadeBemEstar atividade = AtividadeBemEstar.builder()
                    .atividade("Passeio")
                    .observacao("Passeio diario de 30 minutos")
                    .categoria("EXERCICIO")
                    .dataHoraRegistro(LocalDateTime.now())
                    .animal(animal)
                    .build();
            atividadeBemEstarRepository.save(atividade);

            System.out.println("Dados iniciais carregados!");
        }
    }
}
