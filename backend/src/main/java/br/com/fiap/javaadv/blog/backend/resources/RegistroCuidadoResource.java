package br.com.fiap.javaadv.blog.backend.resources;

import br.com.fiap.javaadv.blog.backend.config.docs.ApiStandardErrors;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.RegistroCuidado;
import br.com.fiap.javaadv.blog.backend.domainmodel.enums.CategoriaCuidadoEnum;
import br.com.fiap.javaadv.blog.backend.resources.dtos.RegistroCuidadoRequest;
import br.com.fiap.javaadv.blog.backend.resources.dtos.RegistroCuidadoResponse;
import br.com.fiap.javaadv.blog.backend.services.RegistroCuidadoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/registros-cuidado")
@RequiredArgsConstructor
@Tag(name = "Registros de Cuidado", description = "Endpoints para gerenciamento de registros de cuidado dos animais")
public class RegistroCuidadoResource {

    private final RegistroCuidadoService service;

    @PostMapping
    @Operation(summary = "Criar novo registro de cuidado")
    @ApiStandardErrors
    public ResponseEntity<RegistroCuidadoResponse> create(@Valid @RequestBody RegistroCuidadoRequest request) {
        var saved = service.create(request);
        URI uri = ServletUriComponentsBuilder.fromCurrentRequest().path("/{id}")
                .buildAndExpand(saved.getId()).toUri();
        return ResponseEntity.created(uri).body(service.toResponse(saved));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar registro existente")
    @ApiStandardErrors
    public ResponseEntity<RegistroCuidadoResponse> update(@PathVariable UUID id, @Valid @RequestBody RegistroCuidadoRequest request) {
        return ResponseEntity.ok(service.toResponse(service.update(id, request)));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Excluir registro")
    @ApiStandardErrors
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/listar")
    @Operation(summary = "Listar todos os registros")
    public ResponseEntity<List<RegistroCuidadoResponse>> fetchAll(@ParameterObject @PageableDefault(size = 10) Pageable pageable) {
        return ResponseEntity.ok(service.findAll(pageable).map(service::toResponse).getContent());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar registro por ID")
    public ResponseEntity<RegistroCuidadoResponse> fetchById(@PathVariable UUID id) {
        var entity = service.findByIdOrThrow(id);
        return ResponseEntity.ok(service.toResponse(entity));
    }

    @GetMapping("/animal/{animalId}")
    @Operation(summary = "Listar registros por animal")
    public ResponseEntity<List<RegistroCuidadoResponse>> fetchByAnimal(
            @PathVariable UUID animalId,
            @ParameterObject @PageableDefault(size = 10) Pageable pageable) {
        return ResponseEntity.ok(service.findByAnimalId(animalId, pageable).map(service::toResponse).getContent());
    }

    @GetMapping("/animal/{animalId}/categoria/{categoria}")
    @Operation(summary = "Listar registros por categoria")
    public ResponseEntity<List<RegistroCuidadoResponse>> fetchByCategoria(
            @PathVariable UUID animalId,
            @PathVariable String categoria,
            @ParameterObject @PageableDefault(size = 10) Pageable pageable) {

        var catEnum = CategoriaCuidadoEnum.valueOf(categoria.toUpperCase());
        return ResponseEntity.ok(service.findByAnimalIdAndCategoria(animalId, catEnum, pageable).map(service::toResponse).getContent());
    }

    @GetMapping("/animal/{animalId}/diario")
    @Operation(summary = "Listar diário de cuidados por animal")
    public ResponseEntity<List<RegistroCuidadoResponse>> fetchDiarioPorAnimal(
            @PathVariable UUID animalId,
            @ParameterObject @PageableDefault(size = 10) Pageable pageable) {
        return ResponseEntity.ok(service.buscarDiarioPorAnimal(animalId, pageable).map(service::toResponse).getContent());
    }
}