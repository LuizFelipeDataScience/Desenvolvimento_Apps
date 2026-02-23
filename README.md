# Portal KanaData - Portal Interno Power BI

Portal interno para exibir dashboards Power BI na rede local.

## 🚀 Início Rápido

### Primeira Instalação (Máquina Nova)
```cmd
instalar_completo.bat
```
Este script instala tudo necessário:
- Verifica Python
- Instala dependências
- Gera certificados SSL
- Configura firewall (opcional)

### Executar Servidor (Após Instalação)
```cmd
iniciar.bat
```
Este script apenas inicia o servidor (não reinstala nada).

## 📋 Como Usar

1. **Primeira vez:** Execute `instalar_completo.bat`
2. **Depois:** Execute `iniciar.bat` sempre que quiser iniciar o servidor
3. **Acessar área admin:** `https://dados.kanaflex.com.br/admin`
4. **Adicionar dashboard:** Cole o código HTML do iframe do Power BI
5. **Acessar dashboard:** `https://dados.kanaflex.com.br`

## 🔧 Utilitários

- **`criar_instalador_cliente.bat`** – No servidor: um clique gera o instalador do certificado. Abre a pasta `InstaladorCertificadoCliente` com o arquivo **`Instalar_Certificado_KanaData.bat`**. Copie esse .bat para cada PC (servidor ou cliente), execute como administrador — o aviso "Não seguro" some. Só usa o que já vem no Windows (PowerShell no servidor, CMD+certutil no cliente).
- `configurar_firewall.bat` - Abre porta 443 no firewall (executar como Admin)
  - Permite que outras máquinas acessem o servidor
- `iniciar_http.bat` - Força servidor em HTTP (se necessário)

## ⚙️ Configuração Power BI

1. **Power BI Admin Portal:**
   - Settings → Admin portal → Tenant settings
   - Ative "Allow embedding"
   - Adicione domínio: `dados.kanaflex.com.br`

2. **Certificado SSL:**
   - Gerado automaticamente pelo `instalar_completo.bat`
   - Para tirar o aviso no navegador: execute **`criar_instalador_cliente.bat`**, copie o **`Instalar_Certificado_KanaData.bat`** gerado e rode como Admin em cada PC (servidor e clientes).

## 📝 Notas

- **HTTPS obrigatório:** Power BI precisa de HTTPS
- **Certificado auto-assinado:** Navegador vai avisar (normal - aceite)
- **Acesso:** https://dados.kanaflex.com.br (porta 443 - HTTPS)
- **Login Microsoft:** Usuários fazem login no Power BI

## 🔒 Certificado só no servidor? E os clientes?

Não dá para o aviso "Não seguro" sumir em **todas** as máquinas clientes só ajustando o servidor. O navegador de cada PC é que decide se confia no certificado. Duas alternativas para não instalar manualmente em cada máquina:

1. **Clicar "Avançar" / "Continuar para o site" uma vez**  
   Em muitos navegadores (Chrome, Edge) isso grava a exceção e o aviso não volta naquele PC. Acesso continua seguro (HTTPS); só o aviso some depois da primeira vez.

2. **Rede com Active Directory (dominio)**  
   O administrador pode instalar o `server.crt` em todas as estações de uma vez via **Política de Grupo (GPO)** no servidor de domínio. Assim ninguém precisa instalar manualmente em cada máquina.
