"""
Portal KanaData - Portal Interno de Dashboards Power BI
Acesso: https://dados.kanaflex.com.br
"""

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import json
import os
import sys
from datetime import datetime
import uuid
import re

app = Flask(__name__)
app.secret_key = 'kanadata-secret-key-2025'  # Chave secreta para sessões
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

DASHBOARDS_FILE = 'dashboards.json'
SSL_CERT = 'server.crt'
SSL_KEY = 'server.key'

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

FORCE_HTTP = os.getenv('FORCE_HTTP', '').lower() in ('1', 'true', 'yes', 'on')
USE_HTTPS = not FORCE_HTTP and os.path.exists(SSL_CERT) and os.path.exists(SSL_KEY)


@app.after_request
def security_headers(response):
    """Headers otimizados para Power BI"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    if USE_HTTPS:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self' https://app.powerbi.com https://*.powerbi.com; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://app.powerbi.com https://*.powerbi.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://app.powerbi.com https://*.powerbi.com https://cdnjs.cloudflare.com; "
            "frame-src 'self' https://app.powerbi.com https://*.powerbi.com https://*.microsoftonline.com; "
            "frame-ancestors 'none'; "
            "connect-src 'self' https://app.powerbi.com https://*.powerbi.com https://login.microsoftonline.com https://*.microsoftonline.com wss://*.powerbi.com ws://*.powerbi.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com data:;"
        )
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


def load_dashboards():
    """Carrega dashboards do arquivo JSON"""
    if not os.path.exists(DASHBOARDS_FILE):
        return []
    try:
        with open(DASHBOARDS_FILE, 'r', encoding='utf-8') as f:
            dashboards = json.load(f)
            # Migração: adicionar categoria padrão para dashboards antigos
            categories = ['Comercial', 'Controladoria', 'Estoque/Fabrica', 'RH', 'Tecnologia']
            modified = False
            for dashboard in dashboards:
                if 'category' not in dashboard or not dashboard.get('category') or dashboard.get('category') not in categories:
                    dashboard['category'] = 'Comercial'
                    modified = True
            if modified:
                save_dashboards(dashboards)
            return dashboards
    except:
        return []


def save_dashboards(dashboards):
    """Salva dashboards no arquivo JSON"""
    try:
        # Limpar campos None antes de salvar
        for d in dashboards:
            if d.get('preview_image') is None:
                d.pop('preview_image', None)
        
        with open(DASHBOARDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dashboards, f, ensure_ascii=False, indent=2)
        print(f"[OK] Dashboards salvos: {len(dashboards)} dashboards")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar dashboards: {e}")
        import traceback
        traceback.print_exc()
        raise


def extract_title(iframe_html):
    """Extrai título do iframe"""
    match = re.search(r'title="([^"]+)"', iframe_html)
    return match.group(1) if match else "Dashboard sem título"


def allowed_file(filename):
    """Verifica se arquivo é uma imagem permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def login_required(f):
    """Decorator para proteger rotas admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def get_dashboard(dashboard_id):
    """Busca dashboard por ID"""
    dashboards = load_dashboards()
    return next((d for d in dashboards if d['id'] == dashboard_id), None)


@app.route('/')
def index():
    """Lista de dashboards publicados"""
    dashboards = [d for d in load_dashboards() if d.get('published', True)]
    return render_template('public/index.html', dashboards=dashboards)


@app.route('/dashboard/<dashboard_id>')
def view_dashboard(dashboard_id):
    """Visualiza dashboard"""
    dashboard = get_dashboard(dashboard_id)
    if not dashboard:
        return redirect(url_for('index'))
    return render_template('public/view_dashboard.html', dashboard=dashboard)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login admin"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == 'admin' and password == 'mkt1234':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_index'))
        else:
            return render_template('admin/login.html', error='Usuário ou senha incorretos')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    """Logout admin"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_index():
    """Lista de dashboards (admin)"""
    return render_template('admin/index.html', dashboards=load_dashboards())


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve arquivos de upload"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def admin_add():
    """Adiciona dashboard"""
    if request.method == 'POST':
        iframe_html = request.form.get('iframe_html', '').strip()
        if not iframe_html:
            return render_template('admin/add_dashboard.html', 
                                 error='Cole o código HTML do iframe')
        
        # Processar upload de imagem
        image_filename = None
        if 'preview_image' in request.files:
            file = request.files['preview_image']
            # Verificar se arquivo foi realmente selecionado
            if file and file.filename and file.filename.strip():
                if allowed_file(file.filename):
                    try:
                        filename = secure_filename(file.filename)
                        # Adicionar UUID para evitar conflitos
                        name, ext = os.path.splitext(filename)
                        filename = f"{uuid.uuid4()}{ext}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        
                        # Garantir que pasta existe
                        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                        
                        file.save(filepath)
                        
                        # Verificar se arquivo foi salvo corretamente
                        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                            image_filename = filename
                            print(f"[OK] Imagem salva: {filename} ({os.path.getsize(filepath)} bytes)")
                        else:
                            print(f"[ERRO] Falha ao salvar imagem: {filepath}")
                    except Exception as e:
                        print(f"[ERRO] Erro ao processar imagem: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"[AVISO] Formato de arquivo nao permitido: {file.filename}")
        
        dashboard = {
            'id': str(uuid.uuid4()),
            'name': request.form.get('custom_name', '').strip() or extract_title(iframe_html),
            'iframe_html': iframe_html,
            'preview_image': image_filename,
            'category': request.form.get('category', '').strip() or 'Comercial',
            'published': request.form.get('published') == 'on',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"[DEBUG] Dashboard criado - preview_image: {image_filename}")
        
        dashboards = load_dashboards()
        dashboards.append(dashboard)
        save_dashboards(dashboards)
        
        # Verificar se foi salvo corretamente
        dashboards_verificacao = load_dashboards()
        dashboard_salvo = next((d for d in dashboards_verificacao if d['id'] == dashboard['id']), None)
        if dashboard_salvo:
            print(f"[DEBUG] Dashboard salvo - preview_image no JSON: {dashboard_salvo.get('preview_image')}")
        
        return redirect(url_for('admin_index'))
    
    return render_template('admin/add_dashboard.html')


@app.route('/admin/edit/<dashboard_id>', methods=['GET', 'POST'])
@login_required
def admin_edit(dashboard_id):
    """Edita dashboard"""
    dashboards = load_dashboards()
    # Buscar dashboard na lista atual (não usar get_dashboard que carrega nova lista)
    dashboard = next((d for d in dashboards if d['id'] == dashboard_id), None)
    if not dashboard:
        return redirect(url_for('admin_index'))
    
    if request.method == 'POST':
        if request.form.get('name'):
            dashboard['name'] = request.form.get('name').strip()
        if request.form.get('iframe_html'):
            dashboard['iframe_html'] = request.form.get('iframe_html').strip()
        if request.form.get('category'):
            dashboard['category'] = request.form.get('category').strip()
        dashboard['published'] = request.form.get('published') == 'on'
        
        # Verificar se usuário quer remover a imagem
        if request.form.get('remove_preview_image') == '1':
            if dashboard.get('preview_image'):
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], dashboard['preview_image'])
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                        print(f"[OK] Imagem removida: {dashboard['preview_image']}")
                    except Exception as e:
                        print(f"[AVISO] Erro ao remover imagem antiga: {e}")
                dashboard['preview_image'] = None
                print(f"[OK] Campo preview_image removido do dashboard")
        
        # Processar upload de nova imagem (só atualiza se nova imagem for enviada)
        if 'preview_image' in request.files:
            file = request.files['preview_image']
            # Verificar se arquivo foi realmente selecionado (não apenas campo vazio)
            if file and file.filename and file.filename.strip():
                print(f"[DEBUG] Arquivo recebido: {file.filename}")
                if allowed_file(file.filename):
                    try:
                        # Remover imagem antiga se existir (só se não foi removida acima)
                        if dashboard.get('preview_image') and request.form.get('remove_preview_image') != '1':
                            old_path = os.path.join(app.config['UPLOAD_FOLDER'], dashboard['preview_image'])
                            if os.path.exists(old_path):
                                try:
                                    os.remove(old_path)
                                    print(f"[OK] Imagem antiga removida: {dashboard['preview_image']}")
                                except Exception as e:
                                    print(f"[AVISO] Erro ao remover imagem antiga: {e}")
                        
                        # Salvar nova imagem
                        filename = secure_filename(file.filename)
                        name, ext = os.path.splitext(filename)
                        filename = f"{uuid.uuid4()}{ext}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        
                        # Garantir que pasta existe
                        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                        
                        print(f"[DEBUG] Salvando arquivo em: {filepath}")
                        file.save(filepath)
                        
                        # Verificar se arquivo foi salvo
                        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                            dashboard['preview_image'] = filename
                            print(f"[OK] Imagem atualizada: {filename} ({os.path.getsize(filepath)} bytes)")
                        else:
                            print(f"[ERRO] Falha ao salvar imagem: {filepath}")
                            print(f"[DEBUG] Arquivo existe: {os.path.exists(filepath)}")
                            if os.path.exists(filepath):
                                print(f"[DEBUG] Tamanho do arquivo: {os.path.getsize(filepath)} bytes")
                    except Exception as e:
                        print(f"[ERRO] Erro ao processar imagem: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"[AVISO] Formato de arquivo nao permitido: {file.filename}")
            else:
                print(f"[DEBUG] Nenhum arquivo enviado ou arquivo vazio")
                # Se não enviou nova imagem e não pediu para remover, mantém a antiga
        
        dashboard['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"[DEBUG] ANTES DE SALVAR - preview_image no objeto dashboard: {dashboard.get('preview_image')}")
        print(f"[DEBUG] ANTES DE SALVAR - preview_image na lista dashboards: {next((d.get('preview_image') for d in dashboards if d['id'] == dashboard_id), 'NAO ENCONTRADO')}")
        
        save_dashboards(dashboards)
        
        # Verificar se foi salvo corretamente
        dashboards_verificacao = load_dashboards()
        dashboard_salvo = next((d for d in dashboards_verificacao if d['id'] == dashboard_id), None)
        if dashboard_salvo:
            print(f"[DEBUG] DEPOIS DE SALVAR - preview_image no JSON: {dashboard_salvo.get('preview_image')}")
        else:
            print(f"[ERRO] Dashboard nao encontrado apos salvar!")
        
        return redirect(url_for('admin_index'))
    
    return render_template('admin/edit_dashboard.html', dashboard=dashboard)


@app.route('/admin/delete/<dashboard_id>', methods=['POST'])
@login_required
def admin_delete(dashboard_id):
    """Deleta dashboard"""
    dashboards = load_dashboards()
    dashboard = get_dashboard(dashboard_id)
    
    # Remover imagem se existir
    if dashboard and dashboard.get('preview_image'):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], dashboard['preview_image'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    dashboards = [d for d in dashboards if d['id'] != dashboard_id]
    save_dashboards(dashboards)
    return redirect(url_for('admin_index'))


@app.route('/admin/toggle/<dashboard_id>', methods=['POST'])
@login_required
def admin_toggle(dashboard_id):
    """Publica/despublica dashboard"""
    dashboards = load_dashboards()
    dashboard = get_dashboard(dashboard_id)
    if dashboard:
        dashboard['published'] = not dashboard.get('published', True)
        dashboard['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_dashboards(dashboards)
    return redirect(url_for('admin_index'))


@app.route('/favicon.ico')
def favicon():
    return '', 204


if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 443
    PROTOCOL = 'https' if USE_HTTPS else 'http'
    
    print(f"\n{'='*60}")
    print(f"Portal KanaData - Portal Interno Power BI")
    print(f"{'='*60}")
    print(f"Area Publica: {PROTOCOL}://dados.kanaflex.com.br:{PORT}")
    print(f"Area Admin: {PROTOCOL}://dados.kanaflex.com.br:{PORT}/admin")
    
    if FORCE_HTTP:
        print(f"\n[AVISO] HTTP FORCADO (FORCE_HTTP=1)")
        print(f"   Acesse: http://dados.kanaflex.com.br:{PORT}")
    elif USE_HTTPS:
        print(f"\n[OK] HTTPS Ativo - Power BI funcionara corretamente")
        print(f"   Acesse: https://dados.kanaflex.com.br:{PORT}")
        print(f"   [IMPORTANTE] Use https:// (nao http://)")
        print(f"\n   Para REMOVER o aviso 'Nao seguro': execute criar_instalador_cliente.bat,")
        print(f"   depois rode o Instalar_Certificado_KanaData.bat (como Admin) em cada PC.")
    else:
        print(f"\n[AVISO] HTTP Ativo - Gere certificado para HTTPS")
        print(f"   Acesse: http://dados.kanaflex.com.br:{PORT}")
        print(f"   Execute: python gerar_certificado.py")
    
    print(f"{'='*60}\n")
    
    try:
        if USE_HTTPS:
            print(f"[OK] Iniciando servidor HTTPS na porta {PORT}...")
            app.run(host=HOST, port=PORT, debug=True, threaded=True, 
                    ssl_context=(SSL_CERT, SSL_KEY))
        else:
            print(f"[AVISO] Servidor iniciando em HTTP (nao seguro)")
            print(f"   Para habilitar HTTPS: python gerar_certificado.py\n")
            app.run(host=HOST, port=PORT, debug=True, threaded=True)
    except FileNotFoundError as e:
        print(f"\n[ERRO] Certificados nao encontrados!")
        print(f"   Execute: python gerar_certificado.py")
        print(f"   Erro: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] Erro ao iniciar servidor: {e}")
        print(f"   Verifique se os certificados estao corretos")
        print(f"   Execute: python gerar_certificado.py\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
