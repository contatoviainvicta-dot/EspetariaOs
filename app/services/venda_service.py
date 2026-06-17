"""Service Layer — Vendas (Módulos 5 e 6).

A finalização da venda chama a RPC `registrar_venda`, que executa de forma
ATÔMICA no banco: cria a venda, grava os itens, baixa o estoque e registra
as movimentações. Isso garante consistência mesmo sob concorrência.
"""
from __future__ import annotations

from supabase import Client

FORMAS_PAGAMENTO = ("pix", "dinheiro", "cartao_debito", "cartao_credito")


class VendaService:
    def __init__(self, client: Client) -> None:
        self.client = client

    def registrar(
        self,
        *,
        itens: list[dict],
        forma_pagamento: str,
        valor_recebido: float | None = None,
        observacoes: str = "",
    ) -> str:
        """Finaliza uma venda e retorna o id criado.

        itens: [{"produto_id": "...", "quantidade": 2, "observacoes": ""}]
        """
        if forma_pagamento not in FORMAS_PAGAMENTO:
            raise ValueError("Forma de pagamento inválida.")
        if not itens:
            raise ValueError("O carrinho está vazio.")

        resp = self.client.rpc(
            "registrar_venda",
            {
                "p_forma_pagamento": forma_pagamento,
                "p_valor_recebido": valor_recebido,
                "p_observacoes": observacoes or None,
                "p_itens": itens,
            },
        ).execute()
        return resp.data  # uuid da venda

    @staticmethod
    def calcular_troco(total: float, recebido: float) -> float:
        return max(round(recebido - total, 2), 0.0)
