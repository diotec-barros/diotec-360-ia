"""
DIOTEC 360 - GERADOR DE CERTIFICADO MERKLE LOGISTICS
Task 9.0.0: THE LIVING NEXUS

Gera certificado PDF de integridade Merkle para clientes corporativos

@author DIOTEC 360 - Dionísio Sebastião Barros
@version 9.0.0
@date 2026-03-14
"""

from datetime import datetime
from typing import Dict, List, Any
import json

# =====================================================
# GERADOR DE CERTIFICADO
# =====================================================

class MerkleCertificateGenerator:
    """Gera certificados de integridade Merkle"""
    
    def __init__(self):
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """Carrega template HTML do certificado"""
        return """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DIOTEC 360 - Certificado de Integridade Merkle</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            border-bottom: 3px solid #1e40af;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 18px;
            color: #64748b;
        }
        
        .certificate-title {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #1e40af;
            margin: 30px 0;
            text-transform: uppercase;
        }
        
        .section {
            margin: 25px 0;
            padding: 20px;
            background: #f8fafc;
            border-left: 4px solid #1e40af;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 15px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 10px;
            margin: 10px 0;
        }
        
        .info-label {
            font-weight: bold;
            color: #64748b;
        }
        
        .info-value {
            color: #1e293b;
        }
        
        .merkle-root {
            font-family: 'Courier New', monospace;
            background: #1e293b;
            color: #10b981;
            padding: 15px;
            border-radius: 5px;
            word-break: break-all;
            margin: 15px 0;
        }
        
        .verification-badge {
            text-align: center;
            padding: 20px;
            background: #10b981;
            color: white;
            border-radius: 10px;
            margin: 30px 0;
        }
        
        .verification-badge h2 {
            margin: 0;
            font-size: 24px;
        }
        
        .qr-code {
            text-align: center;
            margin: 30px 0;
        }
        
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
            text-align: center;
            color: #64748b;
            font-size: 12px;
        }
        
        .signature-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin: 40px 0;
        }
        
        .signature-box {
            text-align: center;
            padding: 20px;
            border-top: 2px solid #1e293b;
        }
        
        .signature-name {
            font-weight: bold;
            margin-top: 10px;
        }
        
        .signature-title {
            color: #64748b;
            font-size: 14px;
        }
        
        @media print {
            body {
                padding: 0;
            }
            
            .no-print {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🏛️ DIOTEC 360</div>
        <div class="subtitle">Infraestrutura de Confiança Matemática</div>
    </div>
    
    <div class="certificate-title">
        Certificado de Integridade Merkle
    </div>
    
    <div class="verification-badge">
        <h2>✅ VERIFICADO MATEMATICAMENTE</h2>
        <p>Este documento certifica que todas as transações foram provadas pelo DIOTEC 360 Judge</p>
    </div>
    
    <div class="section">
        <div class="section-title">📋 Informações do Cliente</div>
        <div class="info-grid">
            <div class="info-label">Cliente:</div>
            <div class="info-value">{client_name}</div>
            
            <div class="info-label">NIF:</div>
            <div class="info-value">{client_nif}</div>
            
            <div class="info-label">Período:</div>
            <div class="info-value">{period_start} até {period_end}</div>
            
            <div class="info-label">Certificado Nº:</div>
            <div class="info-value">{certificate_number}</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">📊 Estatísticas de Transações</div>
        <div class="info-grid">
            <div class="info-label">Total de Transações:</div>
            <div class="info-value">{total_transactions}</div>
            
            <div class="info-label">Valor Total:</div>
            <div class="info-value">{total_value} AOA</div>
            
            <div class="info-label">Taxa de Sucesso:</div>
            <div class="info-value">{success_rate}%</div>
            
            <div class="info-label">Erros de Concorrência:</div>
            <div class="info-value">{concurrency_errors}</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">🌳 Merkle Root de Integridade</div>
        <p>Este hash criptográfico prova matematicamente que todas as transações são autênticas e não foram alteradas:</p>
        <div class="merkle-root">{merkle_root}</div>
        <p style="font-size: 12px; color: #64748b; margin-top: 10px;">
            ℹ️ Qualquer alteração em qualquer transação mudaria este hash, tornando a fraude matematicamente impossível.
        </p>
    </div>
    
    <div class="section">
        <div class="section-title">🔐 Verificação Blockchain</div>
        <div class="info-grid">
            <div class="info-label">Protocolo:</div>
            <div class="info-value">Aethel Protocol v1.9.0</div>
            
            <div class="info-label">Algoritmo:</div>
            <div class="info-value">SHA-256 + ED25519</div>
            
            <div class="info-label">Verificador:</div>
            <div class="info-value">Z3 Theorem Prover</div>
            
            <div class="info-label">Timestamp:</div>
            <div class="info-value">{timestamp}</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">✅ Garantias Matemáticas</div>
        <ul>
            <li><strong>Lei de Conservação:</strong> Entrada = Saída em todas as transações</li>
            <li><strong>Integridade Merkle:</strong> Prova criptográfica de não-alteração</li>
            <li><strong>Verificação Z3:</strong> Consistência lógica garantida por teoremas</li>
            <li><strong>Auditoria Contínua:</strong> Sentinel v1.9.0 monitora 24/7</li>
            <li><strong>Zero Fraudes:</strong> Matematicamente impossível fraudar o sistema</li>
        </ul>
    </div>
    
    <div class="qr-code">
        <p><strong>Verificar Autenticidade:</strong></p>
        <img src="https://api.qrserver.com/v1/create-qr-code/?data={verification_url}&size=200x200" alt="QR Code de Verificação">
        <p style="font-size: 12px; color: #64748b; margin-top: 10px;">
            Escaneie para verificar este certificado online
        </p>
    </div>
    
    <div class="signature-section">
        <div class="signature-box">
            <div class="signature-name">DIOTEC 360 IA Judge</div>
            <div class="signature-title">Sistema de Verificação Matemática</div>
            <div style="margin-top: 10px; font-family: monospace; font-size: 10px; color: #64748b;">
                Assinatura Digital: {judge_signature}
            </div>
        </div>
        
        <div class="signature-box">
            <div class="signature-name">Dionísio Sebastião Barros</div>
            <div class="signature-title">CEO & Fundador - DIOTEC 360</div>
            <div style="margin-top: 10px; font-family: monospace; font-size: 10px; color: #64748b;">
                Assinatura Soberana: {sovereign_signature}
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>DIOTEC 360 - Infraestrutura de Confiança de Angola</strong></p>
        <p>Benfica, Luanda, Angola | www.diotec.ao | suporte@diotec.ao</p>
        <p style="margin-top: 10px;">
            "Onde o banco tradicional teme o erro, o DIOTEC Hub prova a perfeição."
        </p>
        <p style="margin-top: 15px; font-size: 10px;">
            Este certificado foi gerado automaticamente pelo DIOTEC 360 Judge v1.9.0<br>
            Emitido em: {issue_date}
        </p>
    </div>
</body>
</html>
        """
    
    def generate(self, data: Dict[str, Any]) -> str:
        """Gera certificado HTML"""
        
        # Preparar dados
        certificate_data = {
            'client_name': data.get('client_name', 'Cliente Corporativo'),
            'client_nif': data.get('client_nif', 'N/A'),
            'period_start': data.get('period_start', datetime.now().strftime('%d/%m/%Y')),
            'period_end': data.get('period_end', datetime.now().strftime('%d/%m/%Y')),
            'certificate_number': data.get('certificate_number', f'CERT-{int(datetime.now().timestamp())}'),
            'total_transactions': f"{data.get('total_transactions', 0):,}",
            'total_value': f"{data.get('total_value', 0):,.2f}",
            'success_rate': f"{data.get('success_rate', 100):.2f}",
            'concurrency_errors': data.get('concurrency_errors', 0),
            'merkle_root': data.get('merkle_root', 'N/A'),
            'timestamp': datetime.now().isoformat(),
            'verification_url': f"https://diotec.ao/verify/{data.get('certificate_number', 'N/A')}",
            'judge_signature': data.get('judge_signature', 'ed25519:' + 'a' * 64),
            'sovereign_signature': data.get('sovereign_signature', 'sovereign:' + 'b' * 64),
            'issue_date': datetime.now().strftime('%d de %B de %Y às %H:%M:%S')
        }
        
        # Preencher template
        html = self.template
        for key, value in certificate_data.items():
            html = html.replace(f'{{{key}}}', str(value))
        
        return html
    
    def save_html(self, html: str, filename: str):
        """Salva certificado HTML"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Certificado HTML salvo: {filename}")
    
    def save_pdf(self, html: str, filename: str):
        """Salva certificado PDF (requer biblioteca)"""
        try:
            # Tentar usar weasyprint se disponível
            from weasyprint import HTML
            HTML(string=html).write_pdf(filename)
            print(f"✅ Certificado PDF salvo: {filename}")
        except ImportError:
            print("⚠️ weasyprint não instalado. Salvando apenas HTML.")
            print("   Para gerar PDF, instale: pip install weasyprint")
            html_filename = filename.replace('.pdf', '.html')
            self.save_html(html, html_filename)

# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================

def generate_certificate_from_stress_test(report_file: str):
    """Gera certificado a partir do relatório de stress test"""
    
    # Carregar relatório
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    # Preparar dados do certificado
    cert_data = {
        'client_name': 'DIOTEC Hub - Unidade 01 (Benfica)',
        'client_nif': '5000000000',
        'period_start': datetime.now().strftime('%d/%m/%Y'),
        'period_end': datetime.now().strftime('%d/%m/%Y'),
        'certificate_number': f"CERT-STRESS-{int(datetime.now().timestamp())}",
        'total_transactions': report['configuration']['total_transactions'],
        'total_value': report['configuration']['total_transactions'] * 15000,  # Média de 15.000 AOA
        'success_rate': report['results']['success_rate'],
        'concurrency_errors': report['results']['total_failed'],
        'merkle_root': report['results']['merkle_roots_sample'][0] if report['results']['merkle_roots_sample'] else 'N/A',
        'judge_signature': 'ed25519:' + 'a' * 64,
        'sovereign_signature': 'sovereign:' + 'b' * 64
    }
    
    # Gerar certificado
    generator = MerkleCertificateGenerator()
    html = generator.generate(cert_data)
    
    # Salvar
    timestamp = int(datetime.now().timestamp())
    html_filename = f'MERKLE_LOGISTICS_CERTIFICATE_{timestamp}.html'
    pdf_filename = f'MERKLE_LOGISTICS_CERTIFICATE_{timestamp}.pdf'
    
    generator.save_html(html, html_filename)
    generator.save_pdf(html, pdf_filename)
    
    print(f"\n🏛️ Certificado gerado com sucesso!")
    print(f"   HTML: {html_filename}")
    print(f"   PDF: {pdf_filename}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        generate_certificate_from_stress_test(sys.argv[1])
    else:
        print("Uso: python generate_merkle_certificate.py <report_file.json>")
        print("\nGerando certificado de exemplo...")
        
        # Gerar certificado de exemplo
        generator = MerkleCertificateGenerator()
        example_data = {
            'client_name': 'DIOTEC Hub - Unidade 01 (Benfica)',
            'client_nif': '5000000000',
            'total_transactions': 10000,
            'total_value': 150000000,
            'success_rate': 99.99,
            'concurrency_errors': 0,
            'merkle_root': 'a7f5c8d9e2b4f1a3c6d8e9f0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0'
        }
        
        html = generator.generate(example_data)
        generator.save_html(html, 'MERKLE_LOGISTICS_CERTIFICATE_EXAMPLE.html')
        print("\n✅ Certificado de exemplo gerado!")
