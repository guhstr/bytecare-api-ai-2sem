package br.com.fiap.javaadv.blog.backend.resources;

import br.com.fiap.javaadv.blog.backend.config.docs.ApiStandardErrors;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AtividadeBemEstarRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AtividadeBemEstarResponse;
import br.com.fiap.javaadv.blog.backend.services.AnimalService;
import br.com.fiap.javaadv.blog.backend.services.AtividadeBemEstarService;
import io.swagger.v3.oas.annotations.Operation;
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
@RequestMapping("/api/atividades-bem-estar")
@RequiredArgsConstructor
@Tag(name = "Atividades de Bem-Estar", description = "Endpoints para gerenciamento de atividades de bem-estar")
public class AtividadeBemEstarResource {

    private final AtividadeBemEstarService service;
    private final AnimalService animalService;

    @PostMapping
    @Operation(summary = "Criar nova atividade de bem-estar")
    @ApiStandardErrors
    public ResponseEntity<AtividadeBemEstarResponse> create(@Valid @RequestBody AtividadeBemEstarRequest request) {
        UUID animalId = parseUuid(request.getIdAnimal(), "idAnimal");
        var animal = animalService.fetchById(animalId);
        var saved = service.create(request, animal);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(saved.getId()).toUri();
        return ResponseEntity.created(location).body(AtividadeBemEstarResponse.fromEntity(saved));
    }

    @GetMapping
    @Operation(summary = "Listar todas as atividades")
    public ResponseEntity<List<AtividadeBemEstarResponse>> findAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar atividade por ID")
    @ApiStandardErrors
    public ResponseEntity<AtividadeBemEstarResponse> findById(@PathVariable UUID id) {
        return ResponseEntity.ok(service.findById(id));
    }

    @GetMapping("/animal/{animalId}")
    @Operation(summary = "Listar atividades por animal")
    public ResponseEntity<List<AtividadeBemEstarResponse>> findByAnimal(@PathVariable UUID animalId) {
        return ResponseEntity.ok(service.findAllByAnimalId(animalId));
    }

    @GetMapping("/buscar")
    @Operation(summary = "Buscar atividades por animal e nome")
    public ResponseEntity<List<AtividadeBemEstarResponse>> buscarPorAtividade(
            @RequestParam UUID animalId, @RequestParam String atividade) {
        return ResponseEntity.ok(service.buscarPorAtividade(animalId, atividade));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar atividade de bem-estar")
    @ApiStandardErrors
    public ResponseEntity<AtividadeBemEstarResponse> update(@PathVariable UUID id,
                                                            @Valid @RequestBody AtividadeBemEstarRequest request) {
        UUID animalId = parseUuid(request.getIdAnimal(), "idAnimal");
        var animal = animalService.fetchById(animalId);
        return ResponseEntity.ok(service.update(id, request, animal));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Excluir atividade")
    @ApiStandardErrors
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

    private UUID parseUuid(String uuidString, String fieldName) {
        try {
            return UUID.fromString(uuidString);
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("O campo '" + fieldName + "' não é um UUID válido: " + uuidString);
        }
    }
}