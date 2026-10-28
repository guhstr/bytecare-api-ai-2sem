package br.com.fiap.javaadv.blog.backend.services;

import br.com.fiap.javaadv.blog.backend.datasource.repositories.AtividadeBemEstarRepository;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.AtividadeBemEstar;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.Animal;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AtividadeBemEstarRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AtividadeBemEstarResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheConfig;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@CacheConfig(cacheNames = {"atividadesBemEstar", "atividadesPorAnimal"})
public class AtividadeBemEstarService {

    private final AtividadeBemEstarRepository repository;

    @Transactional
    @CacheEvict(allEntries = true)
    public AtividadeBemEstar create(AtividadeBemEstarRequest request, Animal animal) {
        AtividadeBemEstar entity = AtividadeBemEstar.builder()
                .atividade(request.getAtividade())
                .observacao(request.getObservacao())
                .categoria(request.getCategoria())
                .dataHoraRegistro(LocalDateTime.now())
                .animal(animal)
                .build();
        return repository.save(entity);
    }

    @Transactional(readOnly = true)
    @Cacheable(key = "'all'")
    public List<AtividadeBemEstarResponse> findAll() {
        return repository.findAll().stream()
                .map(AtividadeBemEstarResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    @Cacheable(key = "#id")
    public AtividadeBemEstarResponse findById(UUID id) {
        return repository.findById(id)
                .map(AtividadeBemEstarResponse::fromEntity)
                .orElseThrow(() -> new RuntimeException("Atividade não encontrada com ID: " + id));
    }

    @Transactional(readOnly = true)
    @Cacheable(key = "#animalId + '_list'")
    public List<AtividadeBemEstarResponse> findAllByAnimalId(UUID animalId) {
        return repository.findByAnimalId(animalId).stream()
                .map(AtividadeBemEstarResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    @Cacheable(key = "#animalId + '_busca_' + #atividade")
    public List<AtividadeBemEstarResponse> buscarPorAtividade(UUID animalId, String atividade) {
        return repository.buscarPorAtividade(animalId, atividade).stream()
                .map(AtividadeBemEstarResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional
    @CacheEvict(allEntries = true)
    public AtividadeBemEstarResponse update(UUID id, AtividadeBemEstarRequest request, Animal animal) {
        AtividadeBemEstar entity = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("Atividade não encontrada com ID: " + id));

        entity.setAtividade(request.getAtividade());
        entity.setObservacao(request.getObservacao());
        entity.setCategoria(request.getCategoria());
        entity.setAnimal(animal);

        return AtividadeBemEstarResponse.fromEntity(repository.save(entity));
    }

    @Transactional
    @CacheEvict(allEntries = true)
    public void delete(UUID id) {
        if (repository.existsById(id)) {
            repository.deleteById(id);
        }
    }
}