package br.com.fiap.javaadv.blog.backend.datasource.repositories;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.AtividadeBemEstar;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface AtividadeBemEstarRepository extends JpaRepository<AtividadeBemEstar, UUID> {


    List<AtividadeBemEstar> findByAnimalId(UUID animalId);


    @Query("SELECT a FROM AtividadeBemEstar a WHERE a.animal.id = :animalId AND LOWER(a.atividade) LIKE LOWER(CONCAT('%', :atividade, '%'))")
    List<AtividadeBemEstar> buscarPorAtividade(@Param("animalId") UUID animalId, @Param("atividade") String atividade);
}