package br.com.fiap.javaadv.blog.backend.resources;

import br.com.fiap.javaadv.blog.backend.config.docs.ApiStandardErrors;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.TipoAnimalEnum;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AnimalRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.AnimalResponse;
import br.com.fiap.javaadv.blog.backend.services.AnimalService;
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
@RequestMapping("/api/animais")
@RequiredArgsConstructor
@Tag(name = "Animais")
public class AnimalResource {

    private final AnimalService service;

    @PostMapping
    public ResponseEntity<AnimalResponse> create(@Valid @RequestBody AnimalRequest req) {
        var saved = service.create(req.toEntity());
        URI uri = ServletUriComponentsBuilder.fromCurrentRequest().path("/{id}").buildAndExpand(saved.getId()).toUri();
        return ResponseEntity.created(uri).body(AnimalResponse.toDto(saved));
    }

    @PutMapping("/{id}")
    public ResponseEntity<AnimalResponse> update(@PathVariable UUID id, @Valid @RequestBody AnimalRequest req) {
        return ResponseEntity.ok(AnimalResponse.toDto(service.update(id, req.toEntity())));
    }

    @GetMapping
    public ResponseEntity<List<AnimalResponse>> findAll() {
        return ResponseEntity.ok(service.findAll().stream().map(AnimalResponse::toDto).toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AnimalResponse> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(AnimalResponse.toDto(service.fetchById(id)));
    }


    @GetMapping("/subcategoria/{subcategoriaId}")
    public ResponseEntity<List<AnimalResponse>> findBySubcategoria(@PathVariable Long subcategoriaId) {
        return ResponseEntity.ok(
                service.findBySubcategoria(subcategoriaId)
                        .stream()
                        .map(AnimalResponse::toDto)
                        .toList()
        );
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

    @PatchMapping("/{id}/{status}")
    public ResponseEntity<Void> patch(@PathVariable UUID id, @PathVariable String status) {
        service.setStatus(id, "ativar".equalsIgnoreCase(status));
        return ResponseEntity.noContent().build();
    }
}