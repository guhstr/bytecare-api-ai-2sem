package br.com.fiap.javaadv.blog.backend.datasource.repositories;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.RegistroCuidado;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.CategoriaCuidadoEnum;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface RegistroCuidadoRepository extends JpaRepository<RegistroCuidado, UUID> {

    @Override
    @EntityGraph(attributePaths = {"animal"})
    Page<RegistroCuidado> findAll(Pageable pageable);

    @Override
    @EntityGraph(attributePaths = {"animal"})
    Optional<RegistroCuidado> findById(UUID id);

    @EntityGraph(attributePaths = {"animal"})
    Page<RegistroCuidado> findByAnimalId(UUID animalId, Pageable pageable);

    @EntityGraph(attributePaths = {"animal"})
    Page<RegistroCuidado> findByAnimalIdAndCategoria(UUID animalId, CategoriaCuidadoEnum categoria, Pageable pageable);

    @Query("SELECT r FROM RegistroCuidado r LEFT JOIN FETCH r.animal WHERE r.animal.id = :animalId")
    Page<RegistroCuidado> buscarDiarioPorAnimal(@Param("animalId") UUID animalId, Pageable pageable);

    long countByAnimalIdAndCategoria(UUID animalId, CategoriaCuidadoEnum categoria);
}