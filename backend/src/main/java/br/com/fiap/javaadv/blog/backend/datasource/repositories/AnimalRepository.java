package br.com.fiap.javaadv.blog.backend.datasource.repositories;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.Animal;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.TipoAnimalEnum;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface AnimalRepository extends JpaRepository<Animal, UUID> {


    List<Animal> findByTipo(TipoAnimalEnum tipo);
    List<Animal> findByTipoOrderByNomeAsc(TipoAnimalEnum tipo);


    Optional<Animal> findByNome(String nome);
    List<Animal> findByNomeContainingIgnoreCase(String nome);
    boolean existsByNomeIgnoreCase(String nome);


    List<Animal> findBySubcategoriaId(Long subcategoriaId);


    List<Animal> findAllByOrderByNomeAsc();
}