"""Repository Pattern — acesso a dados isolado da regra de negócio.

O isolamento por empresa é garantido pelo RLS no banco; os repositórios
nunca precisam adicionar `where empresa_id = ...` manualmente nas leituras.
Para inserts, o empresa_id é preenchido pela Service Layer.
"""
from __future__ import annotations

from typing import Any

from supabase import Client


class BaseRepository:
    table: str = ""

    def __init__(self, client: Client) -> None:
        if not self.table:
            raise ValueError("Subclasse deve definir `table`.")
        self.client = client

    def _q(self):
        return self.client.table(self.table)

    def listar(self, filtros: dict[str, Any] | None = None) -> list[dict]:
        q = self._q().select("*")
        for campo, valor in (filtros or {}).items():
            q = q.eq(campo, valor)
        return q.execute().data or []

    def obter(self, registro_id: str) -> dict | None:
        dados = self._q().select("*").eq("id", registro_id).limit(1).execute().data
        return dados[0] if dados else None

    def criar(self, dados: dict[str, Any]) -> dict:
        return self._q().insert(dados).execute().data[0]

    def atualizar(self, registro_id: str, dados: dict[str, Any]) -> dict:
        return self._q().update(dados).eq("id", registro_id).execute().data[0]

    def remover(self, registro_id: str) -> None:
        self._q().delete().eq("id", registro_id).execute()
