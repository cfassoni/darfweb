# models.py
from __future__ import annotations

# from decimal import Decimal
from enum import Enum
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator

# --- Enums for controlled vocabulary ---


class TipoNota(str, Enum):
    BOVESPA = "bovespa"
    BMF = "bmf"


class CompraVenda(str, Enum):
    COMPRA = "C"
    VENDA = "V"


class CreditoDebito(str, Enum):
    CREDITO = "C"
    DEBITO = "D"


class TipoMercado(str, Enum):
    VISTA = "VISTA"
    TERMO = "TERMO"
    OPCAO_COMPRA = "OPCAO COMPRA"
    OPCAO_VENDA = "OPCAO VENDA"
    # Add others as needed based on SINACOR


# --- Nested Components ---


# class Valor(BaseModel):
#     valor: Decimal
#     cd: CreditoDebito

#     @field_validator("valor", mode="before")
#     @classmethod
#     def make_valor_absolute(cls, v: float) -> float:
#         return abs(v)


class Corretora(BaseModel):
    cnpj: str = Field(..., description="CNPJ only numbers")
    nome_social: str
    codigo: str = Field(
        ..., description="Format XXX-X (2-3 digits, dash, digit, e.g. '123-4')"
    )

    @field_validator("codigo", mode="before")
    @classmethod
    def validate_codigo(cls, v: str) -> Optional[str]:
        import re

        # Look for pattern: 2 or 3 digits, dash, 1 digit
        match = re.search(r"(\d{2,3}-\d)", v)
        if match:
            return match.group(1)
        return None

    @field_validator("cnpj", mode="before")
    @classmethod
    def clean_cnpj(cls, v: str) -> str:
        return "".join(filter(str.isdigit, v))


class Cliente(BaseModel):
    nome: str
    cpf_cnpj: str = Field(..., description="CPF or CNPJ only numbers")
    codigo_cliente: str
    assessor: Optional[str] = None

    @field_validator("cpf_cnpj", mode="before")
    @classmethod
    def clean_cnpj(cls, v: str) -> str:
        return "".join(filter(str.isdigit, v))


class Negocio(BaseModel):
    q: Optional[str] = None
    negociacao: str
    cv: CompraVenda
    tipo_mercado: TipoMercado
    prazo: Optional[str] = None  # Format MM/AA
    especificacao_do_titulo: str
    obs: Optional[str] = None
    quantidade: int
    preco_ajuste: float
    valor_operacao_ajuste: float
    dc: CreditoDebito


class ResumoNegocios(BaseModel):
    debentures: float
    vendas_a_vista: float
    compras_a_vista: float
    opcoes_compras: float
    opcoes_vendas: float
    operacoes_a_termo: float
    valor_das_operacoes_com_titulos_publicos: float
    valor_das_operacoes: float


# --- Financial Summary Sub-components ---


class ResumoClearing(BaseModel):
    valor_liquido_das_operacoes: float
    taxa_liquidacao_ccp: float
    taxa_registro: float
    total_cblc: float


class ResumoBolsa(BaseModel):
    taxa_termo_opcoes: float
    taxa_ana: float
    emolumentos: float
    total_bolsa_soma: float


class ResumoDepositaria(BaseModel):
    taxa_transferencia_ativos: float


class IssData(BaseModel):
    estado: str
    valor_iss: float


class ResumoCorretagem(BaseModel):
    clearing: float
    execucao: float
    execucao_casa: float
    iss: IssData
    iss_pis_cofins: float
    total_corretagem_despesas: float


class LiquidoNota(BaseModel):
    data_liquidez: date
    valor_liquido_da_nota: float


class ResumoFinanceiro(BaseModel):
    clearing: ResumoClearing
    bolsa: ResumoBolsa
    depositaria: ResumoDepositaria
    corretagem_despesas: ResumoCorretagem
    liquido_nota: LiquidoNota


# --- Main Note Structure ---


class Nota(BaseModel):
    nr_nota: int
    folha: int
    data_pregao: date
    corretora: Corretora
    cliente: Cliente
    negocios_realizados: List[Negocio]
    resumo_dos_negocios: ResumoNegocios
    resumo_financeiro: ResumoFinanceiro


class Pagina(BaseModel):
    pagina: int
    tipo: TipoNota
    nota: Nota


# --- Root Model ---


class BrokerageStatement(BaseModel):
    arquivo: str
    data_extracao: datetime
    sha1: str
    total_de_paginas: int
    paginas: List[Pagina]
