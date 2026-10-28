
package br.com.fiap.javaadv.blog.backend.resources;

import br.com.fiap.javaadv.blog.backend.config.docs.ApiStandardErrors;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AcaoPreventivaRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AcaoPreventivaResponse;
import br.com.fiap.javaadv.blog.backend.services.AcaoPreventivaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/acoes-preventivas")
@RequiredArgsConstructor
@Tag(name = "Ações Preventivas", description = "Endpoints para gerenciamento de ações preventivas dos animais")
public class AcaoPreventivaResource {

    private final AcaoPreventivaService service;

    @PostMapping
    @Operation(summary = "Criar nova ação preventiva")
    @ApiResponse(responseCode = "201", description = "Ação preventiva criada com sucesso")
    @ApiStandardErrors
    public ResponseEntity<AcaoPreventivaResponse> create(@Valid @RequestBody AcaoPreventivaRequest request) {
        AcaoPreventivaResponse response = service.create(request);

        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(response.getId())
                .toUri();

        return ResponseEntity.created(location).body(response);
    }

    @GetMapping
    @Operation(summary = "Listar todas as ações preventivas")
    @ApiResponse(responseCode = "200", description = "Lista retornada com sucesso")
    @ApiStandardErrors
    public ResponseEntity<List<AcaoPreventivaResponse>> findAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar ação preventiva por ID")
    @ApiResponse(responseCode = "200", description = "Ação encontrada")
    @ApiStandardErrors
    public ResponseEntity<AcaoPreventivaResponse> findById(@PathVariable UUID id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/animal/{animalId}")
    @Operation(summary = "Listar ações preventivas por animal")
    @ApiResponse(responseCode = "200", description = "Lista retornada com sucesso")
    @ApiStandardErrors
    public ResponseEntity<List<AcaoPreventivaResponse>> findByAnimal(@PathVariable UUID animalId) {
        return ResponseEntity.ok(service.findAllByAnimalId(animalId));
    }

    @GetMapping("/animal/{animalId}/buscar")
    @Operation(summary = "Buscar ação preventiva por nome e animal")
    @ApiResponse(responseCode = "200", description = "Resultado da busca")
    @ApiStandardErrors
    public ResponseEntity<List<AcaoPreventivaResponse>> buscarPorNome(
            @PathVariable UUID animalId,
            @RequestParam String nome) {
        return ResponseEntity.ok(service.buscarPorNomeServico(animalId, nome));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar ação preventiva")
    @ApiResponse(responseCode = "200", description = "Ação atualizada com sucesso")
    @ApiStandardErrors
    public ResponseEntity<AcaoPreventivaResponse> update(
            @PathVariable UUID id,
            @Valid @RequestBody AcaoPreventivaRequest request) {
        return service.update(id, request)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Excluir ação preventiva")
    @ApiResponse(responseCode = "204", description = "Ação excluída com sucesso")
    @ApiStandardErrors
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        if (!service.existsById(id)) return ResponseEntity.notFound().build();
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}