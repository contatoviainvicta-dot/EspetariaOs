"""Configuração central da aplicação.

Lê credenciais de variáveis de ambiente (.env local) ou de st.secrets
(Streamlit Cloud). Não há segredos hard-coded no código.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

try:  # st.secrets só existe quando rodando dentro do Streamlit
    import streamlit as st

    _secrets = dict(st.secrets) if hasattr(st, "secrets") else {}
except Exception:  # pragma: no cover
    _secrets = {}


def _get(key: str, default: str = "") -> str:
    return os.getenv(key) or str(_secrets.get(key, default))


@dataclass(frozen=True)
class Settings:
    supabase_url: str = _get("SUPABASE_URL")
    supabase_anon_key: str = _get("SUPABASE_ANON_KEY")

    def validar(self) -> None:
        faltando = [
            nome
            for nome, valor in (
                ("SUPABASE_URL", self.supabase_url),
                ("SUPABASE_ANON_KEY", self.supabase_anon_key),
            )
            if not valor
        ]
        if faltando:
            raise RuntimeError(
                "Configuração ausente: "
                + ", ".join(faltando)
                + ". Preencha o arquivo .env ou os secrets do Streamlit."
            )


settings = Settings()
