# models.py
from __future__ import annotations
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


class DebitoCredito(str, Enum):
    DEBITO = "D"
    CREDITO = "C"


class TipoMercado(str, Enum):
    VISTA = "VISTA"
    TERMO = "TERMO"
    OPCAO_COMPRA = "OPCAO COMPRA"
    OPCAO_VENDA = "OPCAO VENDA"
    # Add others as needed based on SINACOR


# --- Nested Components ---


class Corretora(BaseModel):
    cnpj: str = Field(..., description="CNPJ only numbers")
    nome_social: str
    codigo: str

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
    dc: DebitoCredito


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
    nr_nota: str
    folha: str
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
    total_de_paginas: int
    paginas: List[Pagina]
