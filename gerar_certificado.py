"""Gera certificado SSL auto-assinado para rede interna usando cryptography"""

import os
import sys
import ipaddress
from datetime import datetime, timedelta

def gerar():
    print("=" * 60)
    print("  GERANDO CERTIFICADO SSL - dados.kanaflex.com.br")
    print("=" * 60)
    print()
    
    try:
        # Tentar usar cryptography
        print("[1/3] Verificando biblioteca cryptography...")
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            print("  [OK] cryptography encontrado")
        except ImportError:
            print("  [ERRO] cryptography nao encontrado")
            print("  Instale: pip install cryptography")
            return False
        
        # Gerar chave privada
        print("[2/3] Gerando chave privada e certificado...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Criar certificado para dados.kanaflex.com.br
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "KanaData"),
            x509.NameAttribute(NameOID.COMMON_NAME, "dados.kanaflex.com.br"),
        ])
        
        # Subject Alternative Names: dominio e localhost
        san_list = [
            x509.DNSName("dados.kanaflex.com.br"),
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Salvar chave privada
        print("  [OK] Chave privada gerada")
        with open("server.key", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Salvar certificado
        print("  [OK] Certificado gerado")
        with open("server.crt", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Verificar se os arquivos foram criados
        print("[3/3] Verificando arquivos...")
        if os.path.exists('server.key') and os.path.exists('server.crt'):
            print("  [OK] server.key")
            print("  [OK] server.crt")
        else:
            print("  [ERRO] Arquivos nao encontrados")
            return False
        
        print()
        print("=" * 60)
        print("  CERTIFICADO GERADO COM SUCESSO!")
        print("=" * 60)
        print()
        print("Arquivos criados:")
        print("  [OK] server.key (chave privada)")
        print("  [OK] server.crt (certificado)")
        print()
        print("IMPORTANTE:")
        print("  1. Reinicie o servidor: python app.py")
        print("  2. Acesse: https://dados.kanaflex.com.br")
        print("  3. Aceite o aviso do certificado no navegador")
        print("     (certificado auto-assinado e normal em rede interna)")
        print("  4. Power BI funcionara com login Microsoft via HTTPS")
        print()
        return True
        
    except ImportError as e:
        print(f"[ERRO] Falta biblioteca: {e}")
        print("  Instale: pip install cryptography")
        return False
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    gerar()
