package br.com.fiap.javaadv.blog.backend.config.docs;

import io.swagger.v3.oas.annotations.responses.ApiResponse;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@ApiResponse(responseCode = "400", description = "Requisição inválida (Erro de validação)")
@ApiResponse(responseCode = "404", description = "Recurso não encontrado")
@ApiResponse(responseCode = "500", description = "Erro interno no servidor")
public @interface ApiStandardErrors { }