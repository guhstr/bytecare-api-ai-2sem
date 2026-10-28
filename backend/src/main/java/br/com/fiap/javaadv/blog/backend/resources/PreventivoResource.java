package br.com.fiap.javaadv.blog.backend.resources;

import br.com.fiap.javaadv.blog.backend.resources.dtos.AcaoPreventivaRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AcaoPreventivaResponse;
import br.com.fiap.javaadv.blog.backend.services.AcaoPreventivaService;
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
@RequestMapping("/api/preventivos")
@RequiredArgsConstructor
@Tag(name = "Preventivos")
public class PreventivoResource {

    private final AcaoPreventivaService service;

    @PostMapping
    public ResponseEntity<AcaoPreventivaResponse> create(@Valid @RequestBody AcaoPreventivaRequest request) {
        var response = service.create(request);
        URI uri = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(response.getId()).toUri();
        return ResponseEntity.created(uri).body(response);
    }

    @GetMapping
    public ResponseEntity<List<AcaoPreventivaResponse>> findAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AcaoPreventivaResponse> findById(@PathVariable UUID id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/animal/{animalId}")
    public ResponseEntity<List<AcaoPreventivaResponse>> findByAnimal(@PathVariable UUID animalId) {
        return ResponseEntity.ok(service.findAllByAnimalId(animalId));
    }

    @GetMapping("/animal/{animalId}/busca")
    public ResponseEntity<List<AcaoPreventivaResponse>> buscarPorNomeServico(
            @PathVariable UUID animalId,
            @RequestParam String nome) {
        return ResponseEntity.ok(service.buscarPorNomeServico(animalId, nome));
    }

    @PutMapping("/{id}")
    public ResponseEntity<AcaoPreventivaResponse> update(
            @PathVariable UUID id,
            @Valid @RequestBody AcaoPreventivaRequest request) {
        return service.update(id, request)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
