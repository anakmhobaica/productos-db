from datetime import datetime
from urllib import request
from flask import *
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient("mongodb+srv://anakmhobaica:EtKEH5Rrcx7OscM1@cluster0.igu6u.mongodb.net/productsDBretryWrites=true&w=majority")
db = client.productsDB
records = db['users']
products = db['products']

app = Flask(__name__)
app.secret_key = 'my_secret_key'

@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/ingresar', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session.permanent = False
        user = request.form["nombre_usuario"]
        password = request.form["pass"]

        session['usuario'] = user

        # user_found = records.find_one({"usuario": user, "password": password})
        user_found = records.find_one({"usuario": user})
    
        if user_found and check_password_hash(user_found["password"], password):
            return redirect("/home")
        else:
            # message= "Usuario y/o contraseña incorrectos"
            flash("Credenciales inválidas. Vuelva a intentar.")
            return render_template('Login.html')
    # else:
    #     if "usuario" in session:
    #         return redirect('/home')
   
    return render_template('Login.html')

@app.route('/registrarse', methods=['GET','POST'])
def registrarse():
    if request.method == 'POST':
        session.permanent = False
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        user = request.form['usuario']
        # password = request.form['password']
        hashed_pass = generate_password_hash(request.form['password'], method="sha256")

        session['usuario'] = user

        email_found = records.find_one({"correo": email})
        user_found = records.find_one({"usuario": user})

        if email_found: 
            flash("Este email ya existe en la base de datos.")
            # msg = "Este email ya existe en la base de datos."
            return render_template('Login.html')

        elif user_found:
            flash("Este usuario ya existe en la base de datos.")
            # msg = "Este usuario ya existe en la base de datos."
            return render_template('Login.html')
        else:
            records.insert_one({
                "nombre": nombre,
                "apellido": apellido,
                "correo": email,
                "usuario": user,
                "password": hashed_pass,
            })
            return redirect('/home')

    return render_template('Login.html')

@app.route('/home')
def home():
    if 'usuario' in session:
        usuario = session['usuario']
        print(usuario)
    return render_template('home.html')

@app.route('/usuario', methods=['GET','POST'])
def usuario():
    if request.method == 'GET':
        user_data = records.find_one({"usuario": session['usuario']})
        return render_template(
            "usuario.html",
            user_data=user_data
        )
    else:
        email = request.form['email']
        usuario = request.form['usuario']
        # password = request.form['password']
        hashed_pass = generate_password_hash(request.form['password'], method="sha256")

        session['usuario'] = usuario
        user_data = records.find_one({"usuario": usuario})

        records.update_one({"correo":email}, {"$set":{
            "usuario": usuario,
            "password": hashed_pass,
        }})
        user_data = records.find_one({"usuario": session['usuario']})
        flash("Información Actualizada.")
        return render_template(
            "usuario.html",
            user_data=user_data
        )

@app.route('/products-page', methods=['GET','POST'])
def products_page():
    product_data = products.find()
    return render_template("productos.html", product_data=product_data)

@app.route('/create-product', methods=['GET','POST'])
def create_product():
    if request.method == 'POST':
        codigo = request.form['codigo']
        producto = request.form['producto']
        precio = request.form['precio']
        categoria = request.form['categoria']
        fecha = {"precio": precio, "fecha": datetime.now(), "valor": "nuevo"}
        precios_viejos = [fecha]

        code_found = products.find_one({"barcode":codigo})

        if code_found:
            # msg = "Ya existe un producto con el código especificado."
            flash("Ya existe un producto con el código especificado.")
            return render_template('crear-producto.html')
        else:
            products.insert_one({
                "barcode": codigo,
                "nombre": producto,
                "categoria": categoria,
                "precio": precio,
                "fecha": fecha,
                "precios_viejos": precios_viejos,
            })
            msg = "El producto fue agregado a la base de datos."
            return render_template('crear-producto.html', msg=msg)
    return render_template('crear-producto.html')
    
@app.route('/info/<barcode>', methods=['GET','POST'])
def leerProducto(barcode):
    if request.method == 'GET':
        codigo = products.find_one({"barcode":barcode})
        return render_template('leer-producto.html', codigo=codigo)
    elif request.method == 'POST':
        precio = request.form['precio']
        codigo = products.find_one({"barcode":barcode})
        precios_viejos = codigo['precios_viejos']

        if precio > codigo['precio']:
            fecha = {"precio": precio, "fecha": datetime.now(), "valor":"sube"}
            lista = [fecha]
        else:
            fecha = {"precio": precio, "fecha": datetime.now(), "valor":"baja"}
            lista = [fecha]

        if codigo['precio'] != precio:
            lista.extend(precios_viejos)
            products.update_one({"barcode":barcode}, {"$set":{
                "precio": precio,
                "fecha": fecha,
                "precios_viejos": lista,
            }})
            codigo = products.find_one({"barcode":barcode})
            flash("Precio Actualizado.  ")
            return render_template('leer-producto.html', codigo=codigo)
        else:
            return render_template('leer-producto.html', codigo=codigo)

@app.route('/<barcode>/historico-precios')
def historial(barcode):
    producto = products.find_one({"barcode":barcode})
    precios = producto['precios_viejos']
    return render_template('historial.html', precios=precios)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)