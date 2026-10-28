package br.com.fiap.javaadv.blog.backend.resources;


import br.com.fiap.javaadv.blog.backend.datasource.repositories.RegistroCuidadoRepository;
import br.com.fiap.javaadv.blog.backend.datasource.repositories.AnimalRepository;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.CategoriaCuidadoEnum;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/relatorios")
@RequiredArgsConstructor
@Tag(name = "Relatórios", description = "Endpoints para geração de relatórios")
public class RelatorioResource {

    private final RegistroCuidadoRepository registroCuidadoRepository;
    private final AnimalRepository animalRepository;

    @GetMapping("/resumo/animal/{animalId}")
    @Operation(summary = "Gerar relatório resumo de cuidados por animal")
    public ResponseEntity<Map<String, Object>> gerarRelatorioAnimal(@PathVariable UUID animalId) {
        Map<String, Object> relatorio = new HashMap<>();

        var animal = animalRepository.findById(animalId);
        if (animal.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        long totalPreventivo = registroCuidadoRepository.countByAnimalIdAndCategoria(
                animalId, CategoriaCuidadoEnum.PREVENTIVO);
        long totalTerapeutico = registroCuidadoRepository.countByAnimalIdAndCategoria(
                animalId, CategoriaCuidadoEnum.TERAPEUTICO);
        long totalBemEstar = registroCuidadoRepository.countByAnimalIdAndCategoria(
                animalId, CategoriaCuidadoEnum.BEM_ESTAR);

        relatorio.put("animal", animal.get().getNome());
        relatorio.put("tipo", animal.get().getTipo());
        relatorio.put("total_cuidados", totalPreventivo + totalTerapeutico + totalBemEstar);
        relatorio.put("cuidados_preventivos", totalPreventivo);
        relatorio.put("cuidados_terapeuticos", totalTerapeutico);
        relatorio.put("cuidados_bem_estar", totalBemEstar);

        return ResponseEntity.ok(relatorio);
    }

    @GetMapping("/estatisticas/geral")
    @Operation(summary = "Gerar estatísticas gerais do sistema")
    public ResponseEntity<Map<String, Object>> gerarEstatisticasGerais() {
        Map<String, Object> stats = new HashMap<>();

        long totalAnimais = animalRepository.count();
        long totalRegistros = registroCuidadoRepository.count();

        stats.put("total_animais", totalAnimais);
        stats.put("total_registros_cuidado", totalRegistros);
        stats.put("media_cuidados_por_animal", totalAnimais > 0 ? (double) totalRegistros / totalAnimais : 0);

        return ResponseEntity.ok(stats);
    }
}
