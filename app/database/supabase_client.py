"""Fábrica do cliente Supabase.

Pontos-chave para o multi-tenant:
- Toda requisição PostgREST precisa carregar o JWT do usuário logado para
  que o RLS (Row Level Security) identifique a empresa via auth.uid().
- Como o Streamlit reexecuta o script a cada interação, a sessão é guardada
  em st.session_state e reinjetada no cliente a cada rerun.
"""
from __future__ import annotations

import streamlit as st
from supabase import Client, create_client

from app.config.settings import settings

SESSION_KEY = "sb_session"


@st.cache_resource(show_spinner=False)
def _base_client() -> Client:
    """Cliente único por processo (conexão reaproveitada)."""
    settings.validar()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_client() -> Client:
    """Retorna o cliente autenticado com a sessão atual, se houver."""
    client = _base_client()
    sessao = st.session_state.get(SESSION_KEY)
    if sessao:
        try:
            client.auth.set_session(
                sessao["access_token"], sessao["refresh_token"]
            )
        except Exception:
            # Token expirado/ inválido: limpa para forçar novo login
            st.session_state.pop(SESSION_KEY, None)
    return client
