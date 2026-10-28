package br.com.fiap.javaadv.blog.backend.datasource.repositories;

import br.com.fiap.javaadv.blog.backend.domainmodel.entities.TratamentoTerapeutico;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface TratamentoTerapeuticoRepository extends JpaRepository<TratamentoTerapeutico, UUID> {

    List<TratamentoTerapeutico> findByAnimalId(UUID animalId);


    Page<TratamentoTerapeutico> findByAnimalId(UUID animalId, Pageable pageable);


    @Query("SELECT t FROM TratamentoTerapeutico t WHERE t.animal.id = :animalId AND LOWER(t.medicamento) LIKE LOWER(CONCAT('%', :medicamento, '%'))")
    Page<TratamentoTerapeutico> buscarPorMedicamento(@Param("animalId") UUID animalId,
                                                     @Param("medicamento") String medicamento,
                                                     Pageable pageable);
}