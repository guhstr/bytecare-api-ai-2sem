package br.com.fiap.javaadv.blog.backend.services;

import br.com.fiap.javaadv.blog.backend.datasource.repositories.AcaoPreventivaRepository;
import br.com.fiap.javaadv.blog.backend.datasource.repositories.AnimalRepository;
import br.com.fiap.javaadv.blog.backend.datasource.repositories.AtividadeBemEstarRepository;
import br.com.fiap.javaadv.blog.backend.datasource.repositories.RegistroCuidadoRepository;
import br.com.fiap.javaadv.blog.backend.datasource.repositories.TratamentoTerapeuticoRepository;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.Animal;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.RegistroCuidado;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.TipoAnimalEnum;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CachePut;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AnimalService {

    private final AnimalRepository animalRepository;
    private final AcaoPreventivaRepository acaoPreventivaRepository;
    private final TratamentoTerapeuticoRepository tratamentoTerapeuticoRepository;
    private final AtividadeBemEstarRepository atividadeBemEstarRepository;
    private final RegistroCuidadoRepository registroCuidadoRepository;

    @Transactional
    @CachePut(value = "animais", key = "#result.id")
    public Animal create(Animal animal) {
        if (animalRepository.existsByNomeIgnoreCase(animal.getNome())) {
            throw new IllegalArgumentException("Já existe um animal com o nome: " + animal.getNome());
        }
        return animalRepository.save(animal);
    }

    @Transactional
    @CachePut(value = "animais", key = "#id")
    public Animal update(UUID id, Animal novo) {
        return animalRepository.findById(id)
                .map(existente -> {
                    existente.setNome(novo.getNome());
                    existente.setTipo(novo.getTipo());
                    existente.setRaca(novo.getRaca());
                    existente.setDataNascimento(novo.getDataNascimento());
                    existente.setObservacaoGeral(novo.getObservacaoGeral());
                    existente.setAtivo(novo.isAtivo());
                    return animalRepository.save(existente);
                })
                .orElseThrow(() -> new EntityNotFoundException("Animal não encontrado para o ID: " + id));
    }

    @Transactional
    @CacheEvict(value = "animais", key = "#id")
    public void delete(UUID id) {
        Animal animal = fetchById(id);

        if (animal.getPreventivos() != null && !animal.getPreventivos().isEmpty()) {
            acaoPreventivaRepository.deleteAll(animal.getPreventivos());
        }
        if (animal.getTratamentos() != null && !animal.getTratamentos().isEmpty()) {
            tratamentoTerapeuticoRepository.deleteAll(animal.getTratamentos());
        }
        if (animal.getAtividades() != null && !animal.getAtividades().isEmpty()) {
            atividadeBemEstarRepository.deleteAll(animal.getAtividades());
        }

        List<RegistroCuidado> registros = registroCuidadoRepository.findByAnimalId(animal.getId(), null).getContent();
        if (registros != null && !registros.isEmpty()) {
            registroCuidadoRepository.deleteAll(registros);
        }

        animalRepository.delete(animal);
    }

    public boolean existsById(UUID id) {
        return animalRepository.existsById(id);
    }

    @Cacheable(value = "animais", key = "#id")
    public Animal fetchById(UUID id) {
        return animalRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Animal não encontrado com ID: " + id));
    }

    public List<Animal> findAll() {
        return animalRepository.findAllByOrderByNomeAsc();
    }

    public List<Animal> findByTipo(TipoAnimalEnum tipo) {
        return animalRepository.findByTipoOrderByNomeAsc(tipo);
    }

    @Transactional
    @CachePut(value = "animais", key = "#id")
    public Animal setStatus(UUID id, boolean ativo) {
        Animal animal = fetchById(id);
        animal.setAtivo(ativo);
        return animalRepository.save(animal);
    }

    public List<Animal> findBySubcategoria(Long subcategoriaId) {
        return animalRepository.findBySubcategoriaId(subcategoriaId);
    }
}