package br.com.fiap.javaadv.blog.backend.services;

import br.com.fiap.javaadv.blog.backend.datasource.repositories.AnimalRepository;
import br.com.fiap.javaadv.blog.backend.datasource.repositories.RegistroCuidadoRepository;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.Animal;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.RegistroCuidado;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.CategoriaCuidadoEnum;
import br.com.fiap.javaadv.blog.backend.resources.dtos.RegistroCuidadoRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.RegistroCuidadoResponse;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class RegistroCuidadoService {

    private final RegistroCuidadoRepository repository;
    private final AnimalRepository animalRepository;

    @Transactional
    public RegistroCuidado create(RegistroCuidadoRequest request) {
        Animal animal = findAnimalOrThrow(request.getIdAnimal());
        RegistroCuidado entity = request.toEntity(animal);
        return repository.save(entity);
    }

    @Transactional
    public RegistroCuidado update(UUID id, RegistroCuidadoRequest request) {
        RegistroCuidado existente = findByIdOrThrow(id);
        Animal novoAnimal = findAnimalOrThrow(request.getIdAnimal());

        existente.setCategoria(request.getCategoria());
        existente.setDescricao(request.getDescricao());
        existente.setDataHoraRegistro(request.getDataRegistro().atTime(LocalTime.now()));
        existente.setAnimal(novoAnimal);

        return repository.save(existente);
    }

    @Transactional
    public void delete(UUID id) {
        if (!repository.existsById(id)) {
            throw new EntityNotFoundException("Registro de cuidado não encontrado com ID: " + id);
        }
        repository.deleteById(id);
    }

    @Transactional(readOnly = true)
    public RegistroCuidado findByIdOrThrow(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Registro de cuidado não encontrado com ID: " + id));
    }

    @Transactional(readOnly = true)
    public Page<RegistroCuidado> findAll(Pageable pageable) {
        return repository.findAll(pageable);
    }

    @Transactional(readOnly = true)
    public Page<RegistroCuidado> findByAnimalId(UUID animalId, Pageable pageable) {
        return repository.findByAnimalId(animalId, pageable);
    }

    @Transactional(readOnly = true)
    public Page<RegistroCuidado> findByAnimalIdAndCategoria(UUID animalId, CategoriaCuidadoEnum cat, Pageable pageable) {
        return repository.findByAnimalIdAndCategoria(animalId, cat, pageable);
    }

    @Transactional(readOnly = true)
    public Page<RegistroCuidado> buscarDiarioPorAnimal(UUID animalId, Pageable pageable) {
        return repository.buscarDiarioPorAnimal(animalId, pageable);
    }

    private Animal findAnimalOrThrow(String idAnimal) {
        try {
            return animalRepository.findById(UUID.fromString(idAnimal))
                    .orElseThrow(() -> new EntityNotFoundException("Animal não encontrado com ID: " + idAnimal));
        } catch (IllegalArgumentException e) {
            throw new EntityNotFoundException("Formato de ID inválido: " + idAnimal);
        }
    }

    public RegistroCuidadoResponse toResponse(RegistroCuidado entity) {
        return RegistroCuidadoResponse.toDto(entity);
    }
}