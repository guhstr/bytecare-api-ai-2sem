package br.com.fiap.javaadv.blog.backend.resources;

import br.com.fiap.javaadv.blog.backend.datasource.repositories.UsuarioRepository;
import br.com.fiap.javaadv.blog.backend.domainmodel.entities.Usuario;
import br.com.fiap.javaadv.blog.backend.infrastructure.security.jwt.JwtTokenProvider;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Tag(name = "Autenticação", description = "Endpoints para autenticação e gerenciamento de usuários")
public class AuthController {

    private final UsuarioRepository usuarioRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider tokenProvider;

    @PostMapping("/login")
    @Operation(summary = "Login de usuário - Retorna token JWT")
    public ResponseEntity<Map<String, Object>> login(@Valid @RequestBody LoginRequest loginRequest) {
        Map<String, Object> response = new HashMap<>();

        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            loginRequest.getUsername(),
                            loginRequest.getPassword()
                    )
            );

            SecurityContextHolder.getContext().setAuthentication(authentication);

            String token = tokenProvider.generateToken(authentication);

            Usuario usuario = usuarioRepository.findByUsername(loginRequest.getUsername())
                    .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));

            response.put("token", token);
            response.put("type", "Bearer");
            response.put("username", usuario.getUsername());
            response.put("role", usuario.getRole());
            response.put("ativo", usuario.isAtivo());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            response.put("error", "Credenciais inválidas: " + e.getMessage());
            return ResponseEntity.status(401).body(response);
        }
    }

    @PostMapping("/register")
    @Operation(summary = "Registrar novo usuário")
    public ResponseEntity<Map<String, String>> register(@Valid @RequestBody RegisterRequest request) {
        Map<String, String> response = new HashMap<>();

        if (usuarioRepository.existsByUsername(request.getUsername())) {
            response.put("error", "Usuário já existe");
            return ResponseEntity.badRequest().body(response);
        }

        Usuario usuario = Usuario.builder()
                .username(request.getUsername())
                .password(passwordEncoder.encode(request.getPassword()))
                .role(request.getRole() != null ? request.getRole().toUpperCase() : "USER")
                .ativo(true)
                .build();

        usuarioRepository.save(usuario);

        response.put("message", "Usuário registrado com sucesso");
        response.put("username", usuario.getUsername());
        response.put("role", usuario.getRole());

        return ResponseEntity.ok(response);
    }

    @GetMapping("/me")
    @Operation(summary = "Obter informações do usuário autenticado")
    public ResponseEntity<Map<String, String>> getCurrentUser(@RequestParam String username) {
        Map<String, String> response = new HashMap<>();

        Usuario usuario = usuarioRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));

        response.put("username", usuario.getUsername());
        response.put("role", usuario.getRole());
        response.put("ativo", String.valueOf(usuario.isAtivo()));

        return ResponseEntity.ok(response);
    }

    @PostMapping("/activate/{id}")
    @Operation(summary = "Ativar/desativar usuário")
    public ResponseEntity<Map<String, String>> toggleUserStatus(@PathVariable UUID id) {
        Map<String, String> response = new HashMap<>();

        Usuario usuario = usuarioRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));

        usuario.setAtivo(!usuario.isAtivo());
        usuarioRepository.save(usuario);

        response.put("message", "Status do usuário atualizado");
        response.put("username", usuario.getUsername());
        response.put("ativo", String.valueOf(usuario.isAtivo()));

        return ResponseEntity.ok(response);
    }
}