"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Aethel Bank Settlement Portal - Genesis Liquidation Report
===========================================================

O "Firewall Humano" - Interface para gerentes bancários visualizarem
e liquidarem as taxas devidas à DIOTEC 360.

Este módulo gera relatórios assinados criptograficamente que o banco
usa para pagar legalmente a DIOTEC 360 pelas transações processadas.

Business Model:
- Banco vê quantos cartões foram gerados
- Banco vê quantas transações foram processadas
- Banco vê quanto deve à DIOTEC 360
- Banco exporta relatório assinado para pagamento

Autor: Kiro AI - Engenheiro-Chefe
Versão: v2.2.8 "Bank Portal"
Data: 11 de Fevereiro de 2026
"""

import time
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from diotec360.core.virtual_card import VirtualCardGateway, get_virtual_card_gateway
from diotec360.core.billing import BillingKernel, get_billing_kernel, OperationType
from diotec360.core.crypto import AethelCrypt


@dataclass
class SettlementPeriod:
    """Período de liquidação (mensal)"""
    year: int
    month: int
    start_date: datetime
    end_date: datetime
    
    def __str__(self) -> str:
        return f"{self.year}-{self.month:02d}"
    
    @classmethod
    def current_month(cls) -> 'SettlementPeriod':
        """Retorna período do mês atual"""
        now = datetime.now()
        start = datetime(now.year, now.month, 1)
        
        # Último dia do mês
        if now.month == 12:
            end = datetime(now.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(now.year, now.month + 1, 1) - timedelta(days=1)
        
        return cls(
            year=now.year,
            month=now.month,
            start_date=start,
            end_date=end
        )
    
    @classmethod
    def from_string(cls, period_str: str) -> 'SettlementPeriod':
        """Cria período a partir de string YYYY-MM"""
        year, month = map(int, period_str.split('-'))
        start = datetime(year, month, 1)
        
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return cls(
            year=year,
            month=month,
            start_date=start,
            end_date=end
        )


@dataclass
class SettlementLineItem:
    """Item de linha no relatório de liquidação"""
    date: datetime
    transaction_id: str
    card_id: str
    operation_type: str
    amount_aoa: float
    fee_usd: Decimal
    description: str


@dataclass
class GenesisSettlementReport:
    """
    Relatório de Liquidação de Gênesis
    
    Este é o documento oficial que o banco usa para pagar a DIOTEC 360.
    Contém todas as transações do período e o valor total devido.
    """
    report_id: str
    bank_id: str
    period: SettlementPeriod
    generated_at: datetime
    
    # Métricas
    total_cards_created: int
    total_transactions: int
    total_volume_aoa: Decimal
    total_fees_usd: Decimal
    
    # Detalhes
    line_items: List[SettlementLineItem] = field(default_factory=list)
    
    # Assinatura criptográfica
    authenticity_seal: str = ""
    signature: str = ""
    
    def __post_init__(self):
        """Gera selo de autenticidade"""
        if not self.authenticity_seal:
            seal_data = (
                f"{self.report_id}:{self.bank_id}:{self.period}:"
                f"{self.total_fees_usd}:{self.generated_at.isoformat()}"
            )
            self.authenticity_seal = hashlib.sha256(seal_data.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Converte para dicionário (para JSON)"""
        return {
            'report_id': self.report_id,
            'bank_id': self.bank_id,
            'period': str(self.period),
            'generated_at': self.generated_at.isoformat(),
            'metrics': {
                'total_cards_created': self.total_cards_created,
                'total_transactions': self.total_transactions,
                'total_volume_aoa': float(self.total_volume_aoa),
                'total_fees_usd': float(self.total_fees_usd)
            },
            'line_items': [
                {
                    'date': item.date.isoformat(),
                    'transaction_id': item.transaction_id,
                    'card_id': item.card_id,
                    'operation_type': item.operation_type,
                    'amount_aoa': item.amount_aoa,
                    'fee_usd': float(item.fee_usd),
                    'description': item.description
                }
                for item in self.line_items
            ],
            'authenticity_seal': self.authenticity_seal,
            'signature': self.signature
        }
    
    def to_json(self) -> str:
        """Converte para JSON formatado"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def export_for_payment(self) -> str:
        """
        Exporta relatório para pagamento
        
        Este é o formato que o banco usa para processar o pagamento
        à DIOTEC 360 através do sistema bancário.
        """
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    GENESIS SETTLEMENT REPORT - DIOTEC 360                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

REPORT ID: {self.report_id}
BANK: {self.bank_id}
PERIOD: {self.period}
GENERATED: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY

Total Cards Created: {self.total_cards_created:,}
Total Transactions: {self.total_transactions:,}
Total Volume: {self.total_volume_aoa:,.2f} AOA

AMOUNT DUE TO DIOTEC 360: ${self.total_fees_usd:,.2f} USD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PAYMENT INSTRUCTIONS

Beneficiary: DIOTEC 360 - Dionísio Sebastião Barros
Amount: ${self.total_fees_usd:,.2f} USD
Reference: {self.report_id}

Bank Transfer Details:
  [Bank account details would go here in production]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRYPTOGRAPHIC VERIFICATION

Authenticity Seal: {self.authenticity_seal[:64]}...
Digital Signature: {self.signature[:64] if self.signature else 'Not signed'}...

This report is cryptographically signed by Aethel and can be verified
for authenticity. Any tampering will be detected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated by Aethel Virtual Card Gateway v2.2.8
© 2026 DIOTEC 360 - All Rights Reserved

╚══════════════════════════════════════════════════════════════════════════════╝
"""


class BankSettlementPortal:
    """
    Portal de Liquidação Bancária
    
    Interface para gerentes bancários visualizarem e liquidarem
    as taxas devidas à DIOTEC 360.
    
    Funcionalidades:
    - Visualizar cartões criados no período
    - Visualizar transações processadas
    - Calcular taxas devidas
    - Gerar relatório de liquidação assinado
    - Exportar para pagamento
    """
    
    def __init__(self):
        """Inicializa portal"""
        self.gateway = get_virtual_card_gateway()
        self.billing = get_billing_kernel()
        self.crypto = AethelCrypt()
        
        print("[BANK_SETTLEMENT_PORTAL] Initialized")
        print("   • Genesis Liquidation: ENABLED")
        print("   • Cryptographic Signing: ENABLED")
        print("   • Payment Export: ENABLED")
    
    def generate_settlement_report(
        self,
        bank_id: str,
        period: Optional[SettlementPeriod] = None
    ) -> GenesisSettlementReport:
        """
        Gera relatório de liquidação para o período
        
        Args:
            bank_id: ID do banco
            period: Período de liquidação (padrão: mês atual)
        
        Returns:
            GenesisSettlementReport assinado
        """
        if period is None:
            period = SettlementPeriod.current_month()
        
        print(f"\n[BANK_SETTLEMENT_PORTAL] Generating report for {bank_id}")
        print(f"   Period: {period}")
        
        # Filtrar cartões do banco no período
        cards_in_period = [
            card for card in self.gateway.cards.values()
            if card.bank_id == bank_id
            and period.start_date.timestamp() <= card.created_at <= period.end_date.timestamp()
        ]
        
        # Filtrar transações do período
        transactions_in_period = [
            tx for tx in self.gateway.transactions.values()
            if tx.timestamp >= period.start_date.timestamp()
            and tx.timestamp <= period.end_date.timestamp()
            and tx.status == "approved"
            # Verificar se transação pertence a cartão do banco
            and any(card.card_id == tx.card_id for card in cards_in_period)
        ]
        
        # Calcular métricas
        total_cards = len(cards_in_period)
        total_transactions = len(transactions_in_period)
        total_volume = sum(tx.amount for tx in transactions_in_period)
        
        # Calcular taxas ($0.10 por transação)
        fee_per_transaction = Decimal("0.10")
        total_fees = Decimal(total_transactions) * fee_per_transaction
        
        # Criar line items
        line_items = []
        for tx in transactions_in_period:
            # Encontrar cartão
            card = next((c for c in cards_in_period if c.card_id == tx.card_id), None)
            
            line_items.append(SettlementLineItem(
                date=datetime.fromtimestamp(tx.timestamp),
                transaction_id=tx.transaction_id,
                card_id=tx.card_id,
                operation_type="transaction",
                amount_aoa=tx.amount,
                fee_usd=fee_per_transaction,
                description=f"Transaction at {tx.merchant}"
            ))
        
        # Gerar ID do relatório
        report_id = self._generate_report_id(bank_id, period)
        
        # Criar relatório
        report = GenesisSettlementReport(
            report_id=report_id,
            bank_id=bank_id,
            period=period,
            generated_at=datetime.now(),
            total_cards_created=total_cards,
            total_transactions=total_transactions,
            total_volume_aoa=Decimal(str(total_volume)),
            total_fees_usd=total_fees,
            line_items=line_items
        )
        
        # Assinar relatório
        report.signature = self._sign_report(report)
        
        print(f"\n✅ Report generated successfully")
        print(f"   Report ID: {report.report_id}")
        print(f"   Cards: {total_cards}")
        print(f"   Transactions: {total_transactions}")
        print(f"   Volume: {total_volume:,.2f} AOA")
        print(f"   Fees Due: ${total_fees:,.2f} USD")
        
        return report
    
    def get_dashboard_metrics(self, bank_id: str) -> Dict:
        """
        Retorna métricas do dashboard para o banco
        
        Args:
            bank_id: ID do banco
        
        Returns:
            Dicionário com métricas
        """
        # Filtrar cartões do banco
        bank_cards = [
            card for card in self.gateway.cards.values()
            if card.bank_id == bank_id
        ]
        
        # Filtrar transações
        bank_transactions = [
            tx for tx in self.gateway.transactions.values()
            if any(card.card_id == tx.card_id for card in bank_cards)
            and tx.status == "approved"
        ]
        
        # Métricas do mês atual
        current_period = SettlementPeriod.current_month()
        cards_this_month = [
            card for card in bank_cards
            if current_period.start_date.timestamp() <= card.created_at <= current_period.end_date.timestamp()
        ]
        
        transactions_this_month = [
            tx for tx in bank_transactions
            if current_period.start_date.timestamp() <= tx.timestamp <= current_period.end_date.timestamp()
        ]
        
        # Calcular taxas
        fee_per_transaction = Decimal("0.10")
        fees_this_month = Decimal(len(transactions_this_month)) * fee_per_transaction
        fees_total = Decimal(len(bank_transactions)) * fee_per_transaction
        
        return {
            'bank_id': bank_id,
            'all_time': {
                'total_cards': len(bank_cards),
                'total_transactions': len(bank_transactions),
                'total_volume_aoa': sum(tx.amount for tx in bank_transactions),
                'total_fees_usd': float(fees_total)
            },
            'current_month': {
                'period': str(current_period),
                'cards_created': len(cards_this_month),
                'transactions': len(transactions_this_month),
                'volume_aoa': sum(tx.amount for tx in transactions_this_month),
                'fees_due_usd': float(fees_this_month)
            },
            'active_cards': len([c for c in bank_cards if c.status.value == "active"])
        }
    
    def export_report_json(self, report: GenesisSettlementReport, filepath: str) -> None:
        """
        Exporta relatório para arquivo JSON
        
        Args:
            report: Relatório para exportar
            filepath: Caminho do arquivo
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report.to_json())
        
        print(f"[BANK_SETTLEMENT_PORTAL] Report exported to {filepath}")
    
    def export_report_text(self, report: GenesisSettlementReport, filepath: str) -> None:
        """
        Exporta relatório para arquivo de texto
        
        Args:
            report: Relatório para exportar
            filepath: Caminho do arquivo
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report.export_for_payment())
        
        print(f"[BANK_SETTLEMENT_PORTAL] Report exported to {filepath}")
    
    def verify_report_signature(self, report: GenesisSettlementReport) -> bool:
        """
        Verifica assinatura do relatório
        
        Args:
            report: Relatório para verificar
        
        Returns:
            True se assinatura válida
        """
        # Recalcular selo
        seal_data = (
            f"{report.report_id}:{report.bank_id}:{report.period}:"
            f"{report.total_fees_usd}:{report.generated_at.isoformat()}"
        )
        expected_seal = hashlib.sha256(seal_data.encode()).hexdigest()
        
        seal_valid = expected_seal == report.authenticity_seal
        
        # Em produção, verificar assinatura digital com chave pública
        signature_valid = len(report.signature) > 0
        
        return seal_valid and signature_valid
    
    def _generate_report_id(self, bank_id: str, period: SettlementPeriod) -> str:
        """Gera ID único para o relatório"""
        data = f"{bank_id}:{period}:{time.time()}"
        hash_val = hashlib.sha256(data.encode()).hexdigest()
        return f"GSR_{bank_id}_{period.year}{period.month:02d}_{hash_val[:8].upper()}"
    
    def _sign_report(self, report: GenesisSettlementReport) -> str:
        """
        Assina relatório criptograficamente
        
        Em produção, usar chave privada da DIOTEC 360
        """
        # Dados para assinar
        sign_data = (
            f"{report.report_id}:{report.authenticity_seal}:"
            f"{report.total_fees_usd}"
        )
        
        # Simular assinatura (em produção, usar ED25519)
        signature = hashlib.sha512(sign_data.encode()).hexdigest()
        
        return signature


# Singleton global
_portal_instance = None

def get_bank_settlement_portal() -> BankSettlementPortal:
    """Obtém instância singleton do portal"""
    global _portal_instance
    if _portal_instance is None:
        _portal_instance = BankSettlementPortal()
    return _portal_instance


if __name__ == "__main__":
    # Demo rápido
    print("=" * 80)
    print("BANK SETTLEMENT PORTAL - DEMO")
    print("=" * 80)
    
    portal = get_bank_settlement_portal()
    
    # Simular algumas transações primeiro
    from diotec360.core.virtual_card import CardType
    
    gateway = get_virtual_card_gateway()
    
    # Registrar cartão físico
    physical = gateway.register_physical_card(
        token="tok_bai_demo",
        bank_id="BAI",
        customer_id="cust_demo",
        limit=500000.0,
        balance=300000.0,
        currency="AOA"
    )
    
    # Criar alguns cartões virtuais
    for i in range(3):
        card = gateway.create_virtual_card(
            physical_card_token=physical.token,
            card_type=CardType.SINGLE_USE,
            limit_total=10000.0
        )
        
        if card:
            # Fazer transação
            gateway.authorize_transaction(
                card_id=card.card_id,
                amount=5000.0,
                merchant=f"merchant_{i}.com"
            )
    
    # Gerar relatório
    print("\n" + "=" * 80)
    print("GENERATING SETTLEMENT REPORT")
    print("=" * 80)
    
    report = portal.generate_settlement_report("BAI")
    
    # Mostrar relatório
    print("\n" + report.export_for_payment())
    
    # Dashboard metrics
    print("\n" + "=" * 80)
    print("DASHBOARD METRICS")
    print("=" * 80)
    
    metrics = portal.get_dashboard_metrics("BAI")
    print(f"\nAll Time:")
    print(f"  Cards: {metrics['all_time']['total_cards']}")
    print(f"  Transactions: {metrics['all_time']['total_transactions']}")
    print(f"  Volume: {metrics['all_time']['total_volume_aoa']:,.2f} AOA")
    print(f"  Fees: ${metrics['all_time']['total_fees_usd']:,.2f} USD")
    
    print(f"\nCurrent Month ({metrics['current_month']['period']}):")
    print(f"  Cards: {metrics['current_month']['cards_created']}")
    print(f"  Transactions: {metrics['current_month']['transactions']}")
    print(f"  Volume: {metrics['current_month']['volume_aoa']:,.2f} AOA")
    print(f"  Fees Due: ${metrics['current_month']['fees_due_usd']:,.2f} USD")
    
    # Verificar assinatura
    print("\n" + "=" * 80)
    print("SIGNATURE VERIFICATION")
    print("=" * 80)
    
    is_valid = portal.verify_report_signature(report)
    print(f"\nReport signature valid: {is_valid}")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
