"""Repositório de Produtos — exemplo concreto do Repository Pattern.

Demonstra como cada entidade ganha consultas específicas mantendo o
acesso a dados separado das regras de negócio.
"""
from __future__ import annotations

from app.repositories.base_repository import BaseRepository


class ProdutoRepository(BaseRepository):
    table = "produtos"

    def listar_ativos(self) -> list[dict]:
        return (
            self._q()
            .select("*")
            .eq("ativo", True)
            .order("nome")
            .execute()
            .data
            or []
        )

    def listar_abaixo_do_minimo(self) -> list[dict]:
        """Produtos com estoque atual abaixo do mínimo (alerta de estoque)."""
        ativos = self.listar_ativos()
        return [
            p
            for p in ativos
            if p.get("controla_estoque")
            and float(p["estoque_atual"]) < float(p["estoque_minimo"])
        ]
