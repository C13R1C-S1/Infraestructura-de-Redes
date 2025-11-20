from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "cambia_esto"

# ==========================
#  CONFIGURACIÓN BD (LOCAL)
# ==========================
db_config = {
    "host": "python123321123.mysql.pythonanywhere-services.com",
    "user": "python123321123",
    "password": "#4HFA@x*5Y*z+!C",          # pon aquí tu pass de MySQL si tienes
    "database": "python123321123$default"
}

def db():
    return mysql.connector.connect(**db_config)


# ==========================
#         LOGIN
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios_admin WHERE usuario = %s", (usuario,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["usuario"] = user["usuario"]
            # Al loguearse bien, lo mandamos a la página de infraestructura
            return redirect(url_for("infra_index"))
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)


# ==========================
#  PÁGINA PRINCIPAL (PROTEGIDA)
# ==========================
@app.route("/infra")
def infra_index():
    # Solo entra si está logueado
    if "user_id" not in session:
        return redirect(url_for("login"))
    # Tu página original:
    return render_template("index.html")


# ==========================
#       REGISTRO
# ==========================
@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    error = None

    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            error = "Las contraseñas no coinciden."
            return render_template("register.html", error=error)

        password_hash = generate_password_hash(password)

        try:
            conn = db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios_admin (usuario, password_hash) VALUES (%s, %s)",
                (usuario, password_hash)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("login"))
        except Exception:
            error = "No se pudo registrar el usuario (¿ya existe?)."

    return render_template("register.html", error=error)


# ==========================
#        LOGOUT
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
