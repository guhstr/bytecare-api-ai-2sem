package br.com.fiap.javaadv.blog.backend.services;

import br.com.fiap.javaadv.blog.backend.datasource.repositories.TratamentoTerapeuticoRepository;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.Animal;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.TratamentoTerapeutico;
import br.com.fiap.javaadv.blog.backend.resources.dtos.TratamentoTerapeuticoRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.TratamentoTerapeuticoResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheConfig;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@CacheConfig(cacheNames = {"tratamentosTerapeuticos", "tratamentosPorAnimal"})
public class TratamentoTerapeuticoService {

    private final TratamentoTerapeuticoRepository repository;

    @Transactional
    @CacheEvict(allEntries = true)
    public TratamentoTerapeutico create(TratamentoTerapeuticoRequest request, Animal animal) {
        TratamentoTerapeutico entity = TratamentoTerapeutico.builder()
                .medicamento(request.getMedicamento())
                .dosagem(request.getDosagem())
                .observacao(request.getObservacao())
                .dataHoraRegistro(LocalDateTime.now())
                .animal(animal)
                .build();
        return repository.save(entity);
    }

    @Transactional(readOnly = true)
    @Cacheable(key = "#id")
    public TratamentoTerapeuticoResponse findById(UUID id) {
        return repository.findById(id)
                .map(TratamentoTerapeuticoResponse::fromEntity)
                .orElseThrow(() -> new RuntimeException("Tratamento nao encontrado com ID: " + id));
    }

    @Transactional(readOnly = true)
    @Cacheable(key = "'all'")
    public List<TratamentoTerapeuticoResponse> findAll() {
        return repository.findAll().stream()
                .map(TratamentoTerapeuticoResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    @Cacheable(key = "#animalId + '_list'")
    public List<TratamentoTerapeuticoResponse> findAllByAnimalId(UUID animalId) {
        return repository.findByAnimalId(animalId).stream()
                .map(TratamentoTerapeuticoResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<TratamentoTerapeuticoResponse> findByAnimalIdPaged(UUID animalId, Pageable pageable) {
        return repository.findByAnimalId(animalId, pageable)
                .map(TratamentoTerapeuticoResponse::fromEntity);
    }

    @Transactional(readOnly = true)
    public Page<TratamentoTerapeuticoResponse> buscarPorMedicamento(UUID animalId, String medicamento, Pageable pageable) {
        return repository.buscarPorMedicamento(animalId, medicamento, pageable)
                .map(TratamentoTerapeuticoResponse::fromEntity);
    }

    @Transactional(readOnly = true)
    public boolean existsById(UUID id) {
        return repository.existsById(id);
    }

    @Transactional
    @CacheEvict(allEntries = true)
    public TratamentoTerapeuticoResponse update(UUID id, TratamentoTerapeuticoRequest request, Animal animal) {
        TratamentoTerapeutico entity = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("Tratamento nao encontrado com ID: " + id));

        entity.setMedicamento(request.getMedicamento());
        entity.setDosagem(request.getDosagem());
        entity.setObservacao(request.getObservacao());
        entity.setAnimal(animal);

        return TratamentoTerapeuticoResponse.fromEntity(repository.save(entity));
    }

    @Transactional
    @CacheEvict(allEntries = true)
    public void delete(UUID id) {
        if (repository.existsById(id)) {
            repository.deleteById(id);
        }
    }
}
