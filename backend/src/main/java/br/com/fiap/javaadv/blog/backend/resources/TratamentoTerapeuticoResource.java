package br.com.fiap.javaadv.blog.backend.resources;

import br.com.fiap.javaadv.blog.backend.config.docs.ApiStandardErrors;
import br.com.fiap.javaadv.blog.backend.resources.dtos.TratamentoTerapeuticoRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.TratamentoTerapeuticoResponse;
import br.com.fiap.javaadv.blog.backend.services.AnimalService;
import br.com.fiap.javaadv.blog.backend.services.TratamentoTerapeuticoService;
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
@RequestMapping("/api/tratamentos-terapeuticos")
@RequiredArgsConstructor
@Tag(name = "Tratamentos Terapêuticos", description = "Endpoints para gerenciamento de tratamentos terapêuticos")
public class TratamentoTerapeuticoResource {

    private final TratamentoTerapeuticoService service;
    private final AnimalService animalService;

    @PostMapping
    @Operation(summary = "Criar novo tratamento terapêutico")
    @ApiStandardErrors
    public ResponseEntity<TratamentoTerapeuticoResponse> create(@Valid @RequestBody TratamentoTerapeuticoRequest request) {
        UUID animalId = parseUuid(request.getIdAnimal(), "idAnimal");
        var animal = animalService.fetchById(animalId);
        var saved = service.create(request, animal);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(saved.getId()).toUri();
        return ResponseEntity.created(location).body(TratamentoTerapeuticoResponse.fromEntity(saved));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar tratamento por ID")
    @ApiStandardErrors
    public ResponseEntity<TratamentoTerapeuticoResponse> findById(@PathVariable UUID id) {
        return ResponseEntity.ok(service.findById(id));
    }

    @GetMapping
    @Operation(summary = "Listar todos os tratamentos")
    public ResponseEntity<List<TratamentoTerapeuticoResponse>> findAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @GetMapping("/animal/{animalId}")
    @Operation(summary = "Listar tratamentos por animal")
    public ResponseEntity<List<TratamentoTerapeuticoResponse>> findByAnimal(@PathVariable UUID animalId) {
        return ResponseEntity.ok(service.findAllByAnimalId(animalId));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar tratamento terapêutico")
    @ApiStandardErrors
    public ResponseEntity<TratamentoTerapeuticoResponse> update(
            @PathVariable UUID id,
            @Valid @RequestBody TratamentoTerapeuticoRequest request) {
        UUID animalId = parseUuid(request.getIdAnimal(), "idAnimal");
        var animal = animalService.fetchById(animalId);
        return ResponseEntity.ok(service.update(id, request, animal));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Excluir tratamento")
    @ApiStandardErrors
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        if (!service.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
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