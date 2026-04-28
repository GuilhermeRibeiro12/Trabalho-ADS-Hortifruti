from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# APP
# =========================
app = Flask(__name__)
app.secret_key = "chave_super_secreta"

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'banco.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'imagens')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# =========================
# MODELOS
# =========================
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True)
    senha = db.Column(db.String(200))
    admin = db.Column(db.Boolean, default=False)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float)
    imagem = db.Column(db.String(100))

# =========================
# CRIAR BANCO + ADMIN
# =========================
with app.app_context():
    db.create_all()

    user = Usuario.query.filter_by(usuario="admin").first()

    if not user:
        admin = Usuario(
            usuario="admin",
            senha=generate_password_hash("123"),
            admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin criado!")
    else:
        user.admin = True
        db.session.commit()
        print("Admin garantido!")
# =========================
# DECORATORS
# =========================
def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logado" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def admin_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            return "Acesso negado"
        return f(*args, **kwargs)
    return decorated_function

# =========================
# ROTAS
# =========================
@app.route("/")
def index():
    produtos = Produto.query.all()
    print(session)
    return render_template("index.html", produtos=produtos)


@app.route("/produto/<int:id>")
def ver_produto(id):
    produto = Produto.query.get_or_404(id)
    return render_template("produto.html", produto=produto)

from werkzeug.utils import secure_filename
import os

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']

        imagem = request.files['imagem']

        nome_arquivo = secure_filename(imagem.filename)

        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        imagem.save(caminho)

        # 👇 SALVA SÓ O NOME NO BANCO
        novo_produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco,
            imagem=nome_arquivo
        )

        db.session.add(novo_produto)
        db.session.commit()

        return redirect('/')

# =========================
# AUTH
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        user = Usuario.query.filter_by(usuario=usuario).first()

        if user and check_password_hash(user.senha, senha):
            session["logado"] = True
            session["usuario"] = user.usuario
            session["admin"] = user.admin
            return redirect("/")
        else:
            return "Login inválido"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        # evita usuário duplicado
        if Usuario.query.filter_by(usuario=usuario).first():
            return "Usuário já existe!"

        senha_hash = generate_password_hash(senha)

        novo_usuario = Usuario(
            usuario=usuario,
            senha=senha_hash,
            admin=False
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect("/login")

    return render_template("registrar.html")

# =========================
# ADMIN
# =========================
@app.route("/admin", methods=["GET", "POST"])
@login_obrigatorio
@admin_obrigatorio
def admin():
    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        preco = float(request.form["preco"].replace(",", "."))

        arquivo = request.files.get("imagem")
        filename = None

        if arquivo and arquivo.filename != "":
            filename = secure_filename(arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            arquivo.save(caminho)

        novo_produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco,
            imagem=filename
        )

        db.session.add(novo_produto)
        db.session.commit()

        return redirect("/admin/produtos")

    return render_template("admin.html")


@app.route("/admin/produtos")
@login_obrigatorio
@admin_obrigatorio
def admin_produtos():
    busca = request.args.get("busca")

    if busca:
        produtos = Produto.query.filter(Produto.nome.contains(busca)).all()
    else:
        produtos = Produto.query.all()

    return render_template("admin_produtos.html", produtos=produtos)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_obrigatorio
@admin_obrigatorio
def editar(id):
    produto = Produto.query.get_or_404(id)

    if request.method == "POST":
        produto.nome = request.form["nome"]
        produto.descricao = request.form["descricao"]
        produto.preco = float(request.form["preco"].replace(",", "."))

        arquivo = request.files.get("imagem")

        if arquivo and arquivo.filename != "":
            filename = secure_filename(arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            arquivo.save(caminho)
            produto.imagem = filename

        db.session.commit()
        return redirect("/admin/produtos")

    return render_template("editar.html", produto=produto)


@app.route("/deletar/<int:id>")
@login_obrigatorio
@admin_obrigatorio
def deletar(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect("/admin/produtos")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)