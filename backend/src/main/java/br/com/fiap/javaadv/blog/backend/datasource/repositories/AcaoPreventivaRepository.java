package br.com.fiap.javaadv.blog.backend.datasource.repositories;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.AcaoPreventiva;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface AcaoPreventivaRepository extends JpaRepository<AcaoPreventiva, UUID> {


    @Override
    @EntityGraph(attributePaths = {"animal"})
    List<AcaoPreventiva> findAll();

    @Override
    @EntityGraph(attributePaths = {"animal"})
    Optional<AcaoPreventiva> findById(UUID id);


    @EntityGraph(attributePaths = {"animal"})
    List<AcaoPreventiva> findByAnimalId(UUID animalId);

    @Query("SELECT a FROM AcaoPreventiva a JOIN FETCH a.animal WHERE a.animal.id = :animalId " +
            "AND LOWER(a.nomeServico) LIKE LOWER(CONCAT('%', :nome, '%'))")
    List<AcaoPreventiva> buscarPorNomeServico(@Param("animalId") UUID animalId,
                                              @Param("nome") String nome);
}