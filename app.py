import datetime
import csv
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter.simpledialog import askstring
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fpdf import FPDF
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Producto:
    def __init__(self, nombre, cantidad, unidad_medida, fecha_vencimiento, tarifa):
        self.nombre = nombre
        self.cantidad = cantidad
        self.unidad_medida = unidad_medida
        self.fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        self.tarifa = tarifa
        self.temperatura = None  # Añadimos el control de temperatura del producto

    def __str__(self):
        return f"{self.nombre} - {self.cantidad} {self.unidad_medida} - Vence: {self.fecha_vencimiento.strftime('%Y-%m-%d')} - Tarifa: {self.tarifa} - Temp: {self.temperatura}"

class Inventario:
    def __init__(self, nombre):
        self.nombre = nombre
        self.productos = []
    
    def agregar_producto(self, producto):
        self.productos.append(producto)
    
    def remover_producto(self, nombre_producto, cantidad):
        for producto in self.productos:
            if producto.nombre == nombre_producto:
                if producto.cantidad >= cantidad:
                    producto.cantidad -= cantidad
                    if producto.cantidad == 0:
                        self.productos.remove(producto)
                    return True
                else:
                    return False
        return False

    def editar_producto(self, nombre_producto, cantidad, unidad_medida, fecha_vencimiento, tarifa, temperatura):
        for producto in self.productos:
            if producto.nombre == nombre_producto:
                if cantidad is not None:
                    producto.cantidad = cantidad
                if unidad_medida is not None:
                    producto.unidad_medida = unidad_medida
                if fecha_vencimiento is not None:
                    producto.fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
                if tarifa is not None:
                    producto.tarifa = tarifa
                if temperatura is not None:
                    producto.temperatura = temperatura
                return True
        return False
    
    def consultar_inventario(self, unidad_medida=None):
        inventario = {}
        for producto in self.productos:
            if unidad_medida is None or producto.unidad_medida == unidad_medida:
                if producto.nombre in inventario:
                    inventario[producto.nombre] += producto.cantidad
                else:
                    inventario[producto.nombre] = producto.cantidad
        return inventario
    
    def verificar_fechas_vencimiento(self):
        productos_vencidos = []
        hoy = datetime.datetime.now()
        for producto in self.productos:
            if producto.fecha_vencimiento < hoy:
                productos_vencidos.append(producto)
        return productos_vencidos
    
    def exportar_a_csv(self, nombre_archivo):
        with open(nombre_archivo, mode='w', newline='') as archivo:
            escritor_csv = csv.writer(archivo)
            escritor_csv.writerow(["Nombre", "Cantidad", "Unidad de Medida", "Fecha de Vencimiento", "Tarifa", "Temperatura"])
            for producto in self.productos:
                escritor_csv.writerow([producto.nombre, producto.cantidad, producto.unidad_medida, producto.fecha_vencimiento.strftime('%Y-%m-%d'), producto.tarifa, producto.temperatura])
        print(f"Inventario exportado a {nombre_archivo}")

    def generar_reporte(self, criterio, valor):
        reporte = []
        for producto in self.productos:
            if criterio == "fecha" and producto.fecha_vencimiento.strftime('%Y-%m-%d') == valor:
                reporte.append(producto)
            elif criterio == "producto" and producto.nombre == valor:
                reporte.append(producto)
            elif criterio == "unidad_medida" and producto.unidad_medida == valor:
                reporte.append(producto)
        return reporte
    
    def guardar_inventario(self, nombre_archivo):
        with open(nombre_archivo, 'w', newline='') as archivo:
            escritor_csv = csv.writer(archivo)
            escritor_csv.writerow(["Nombre", "Cantidad", "Unidad de Medida", "Fecha de Vencimiento", "Tarifa", "Temperatura"])
            for producto in self.productos:
                escritor_csv.writerow([producto.nombre, producto.cantidad, producto.unidad_medida, producto.fecha_vencimiento.strftime('%Y-%m-%d'), producto.tarifa, producto.temperatura])
        print(f"Inventario guardado en {nombre_archivo}")

    def cargar_inventario(self, nombre_archivo):
        self.productos = []
        try:
            with open(nombre_archivo, 'r') as archivo:
                lector_csv = csv.reader(archivo)
                next(lector_csv)  # Saltar la cabecera
                for fila in lector_csv:
                    if len(fila) == 6:
                        nombre, cantidad, unidad_medida, fecha_vencimiento, tarifa, temperatura = fila
                        producto = Producto(nombre, float(cantidad), unidad_medida, fecha_vencimiento, float(tarifa))
                        producto.temperatura = temperatura
                        self.productos.append(producto)
            print(f"Inventario cargado desde {nombre_archivo}")
        except FileNotFoundError:
            print(f"El archivo {nombre_archivo} no existe.")

    def buscar_producto(self, nombre_producto):
        for producto in self.productos:
            if producto.nombre.lower() == nombre_producto.lower():
                return producto
        return None

class Transporte:
    def __init__(self, operador, temperatura, hora_llegada, hora_retiro):
        self.operador = operador
        self.temperatura = temperatura
        self.hora_llegada = hora_llegada
        self.hora_retiro = hora_retiro

class Registro:
    def __init__(self, tipo, producto, cantidad, transporte, fecha):
        self.tipo = tipo
        self.producto = producto
        self.cantidad = cantidad
        self.transporte = transporte
        self.fecha = fecha

class Cliente:
    def __init__(self, nombre, contacto):
        self.nombre = nombre
        self.contacto = contacto

class Proveedor:
    def __init__(self, nombre, contacto):
        self.nombre = nombre
        self.contacto = contacto

class SistemaInventario:
    def __init__(self):
        self.almacenes = {}
        self.registros = []
        self.clientes = {}
        self.proveedores = {}

    def agregar_almacen(self, nombre):
        if nombre not in self.almacenes:
            self.almacenes[nombre] = Inventario(nombre)
    
    def registrar_ingreso_egreso(self, tipo, nombre_almacen, nombre_producto, cantidad, unidad_medida, fecha_vencimiento, tarifa, operador, temperatura, hora_llegada, hora_retiro):
        if nombre_almacen in self.almacenes:
            inventario = self.almacenes[nombre_almacen]
            producto = inventario.buscar_producto(nombre_producto)
            if producto:
                if tipo == "egreso":
                    inventario.remover_producto(nombre_producto, cantidad)
                elif tipo == "ingreso":
                    inventario.agregar_producto(Producto(nombre_producto, cantidad, unidad_medida, fecha_vencimiento, tarifa))
            else:
                producto = Producto(nombre_producto, cantidad, unidad_medida, fecha_vencimiento, tarifa)
                inventario.agregar_producto(producto)
            
            transporte = Transporte(operador, temperatura, hora_llegada, hora_retiro)
            registro = Registro(tipo, producto, cantidad, transporte, datetime.datetime.now())
            self.registros.append(registro)
            return True
        return False

    def generar_reporte_transporte(self):
        reporte = []
        for registro in self.registros:
            linea = f"{registro.tipo} - {registro.producto.nombre} - {registro.cantidad} {registro.producto.unidad_medida} - {registro.transporte.operador} - {registro.transporte.temperatura} - {registro.transporte.hora_llegada} - {registro.transporte.hora_retiro} - {registro.fecha.strftime('%Y-%m-%d %H:%M:%S')}"
            reporte.append(linea)
        return reporte

    def enviar_reporte_por_correo(self, email, asunto, cuerpo, archivo):
        mensaje = MIMEMultipart()
        mensaje['From'] = "tucorreo@example.com"
        mensaje['To'] = email
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        with open(archivo, "rb") as adjunto:
            mensaje.attach(MIMEText(adjunto.read(), "base64", "utf-8"))
            mensaje.add_header('Content-Disposition', f'attachment; filename={os.path.basename(archivo)}')

        try:
            with smtplib.SMTP('smtp.example.com', 587) as servidor:
                servidor.starttls()
                servidor.login("tucorreo@example.com", "tucontraseña")
                servidor.send_message(mensaje)
                print(f"Correo enviado a {email}")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")

    def generar_pdf(self, nombre_archivo, contenido):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for linea in contenido:
            pdf.cell(200, 10, txt=linea, ln=True, align='L')
        pdf.output(nombre_archivo)

    def generar_grafico(self, nombre_archivo):
        productos = [producto.nombre for producto in self.almacenes["default"].productos]
        cantidades = [producto.cantidad for producto in self.almacenes["default"].productos]
        
        fig, ax = plt.subplots()
        ax.bar(productos, cantidades)
        ax.set_xlabel('Productos')
        ax.set_ylabel('Cantidades')
        ax.set_title('Inventario de Productos')
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig(nombre_archivo)
        plt.close()

    def agregar_cliente(self, nombre, contacto):
        if nombre not in self.clientes:
            self.clientes[nombre] = Cliente(nombre, contacto)
            return True
        return False

    def agregar_proveedor(self, nombre, contacto):
        if nombre not in self.proveedores:
            self.proveedores[nombre] = Proveedor(nombre, contacto)
            return True
        return False

    def generar_notificacion(self, mensaje):
        # Aquí puedes implementar un sistema de notificaciones push
        print(f"Notificación: {mensaje}")

class Usuario:
    def __init__(self, nombre_usuario, contraseña, rol="usuario"):
        self.nombre_usuario = nombre_usuario
        self.contraseña = contraseña
        self.rol = rol

class SistemaAutenticacion:
    def __init__(self):
        self.usuarios = {}
        self.roles_permisos = {
            'admin': ['Almacen', 'Productos', 'Transporte', 'Reportes', 'Admin'],
            'usuario': ['Almacen', 'Productos']
        }
    
    def registrar_usuario(self, nombre_usuario, contraseña, rol="usuario"):
        if nombre_usuario not in self.usuarios:
            self.usuarios[nombre_usuario] = Usuario(nombre_usuario, contraseña, rol)
            return True
        return False
    
    def modificar_permisos(self, rol, pantalla, acceso):
        if rol not in self.roles_permisos:
            self.roles_permisos[rol] = []
        if acceso and pantalla not in self.roles_permisos[rol]:
            self.roles_permisos[rol].append(pantalla)
        elif not acceso and pantalla in self.roles_permisos[rol]:
            self.roles_permisos[rol].remove(pantalla)

    def autenticar_usuario(self, nombre_usuario, contraseña):
        if nombre_usuario in self.usuarios and self.usuarios[nombre_usuario].contraseña == contraseña:
            return True
        return False

class InventarioGUI:
    def __init__(self, root, sistema_inventario, sistema_autenticacion):
        self.sistema_inventario = sistema_inventario
        self.sistema_autenticacion = sistema_autenticacion
        self.inventario = None
        self.root = root
        self.root.title("Inventario de Almacenamiento Frío")
        
        self.login_interfaz()
    
    def login_interfaz(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.nombre_usuario_lbl = tk.Label(self.root, text="Nombre de Usuario:")
        self.nombre_usuario_lbl.grid(row=0, column=0)
        self.nombre_usuario_entry = tk.Entry(self.root)
        self.nombre_usuario_entry.grid(row=0, column=1)

        self.contraseña_lbl = tk.Label(self.root, text="Contraseña:")
        self.contraseña_lbl.grid(row=1, column=0)
        self.contraseña_entry = tk.Entry(self.root, show="*")
        self.contraseña_entry.grid(row=1, column=1)

        self.login_btn = tk.Button(self.root, text="Login", command=self.login)
        self.login_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.registro_btn = tk.Button(self.root, text="Registrar", command=self.registrar)
        self.registro_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def login(self):
        nombre_usuario = self.nombre_usuario_entry.get()
        contraseña = self.contraseña_entry.get()
        if self.sistema_autenticacion.autenticar_usuario(nombre_usuario, contraseña):
            self.usuario_actual_rol = self.sistema_autenticacion.usuarios[nombre_usuario].rol
            self.crear_interfaz()
        else:
            messagebox.showerror("Error", "Nombre de usuario o contraseña incorrectos.")

    def registrar(self):
        nombre_usuario = self.nombre_usuario_entry.get()
        contraseña = self.contraseña_entry.get()
        if self.sistema_autenticacion.registrar_usuario(nombre_usuario, contraseña):
            messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
        else:
            messagebox.showerror("Error", "El nombre de usuario ya existe.")

    def crear_interfaz(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configurar Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        permisos = self.sistema_autenticacion.roles_permisos.get(self.usuario_actual_rol, [])

        if 'Almacen' in permisos:
            self._crear_pestana_almacen()
        if 'Productos' in permisos:
            self._crear_pestana_productos()
        if 'Transporte' in permisos:
            self._crear_pestana_transporte()
        if 'Reportes' in permisos:
            self._crear_pestana_reportes()
        if 'Admin' in permisos:
            self._crear_pestana_admin()

        # Logout button
        self.salir_btn = tk.Button(self.root, text="Cerrar Sesión", command=self.login_interfaz)
        self.salir_btn.pack(pady=10)

    def _crear_pestana_almacen(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Almacén")

        self.almacen_lbl = tk.Label(frame, text="Nombre del Almacén:")
        self.almacen_lbl.grid(row=0, column=0, padx=5, pady=5)
        self.almacen_entry = tk.Entry(frame)
        self.almacen_entry.grid(row=0, column=1, padx=5, pady=5)

        self.agregar_almacen_btn = tk.Button(frame, text="Agregar Almacén", command=self.agregar_almacen)
        self.agregar_almacen_btn.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(frame, text="Seleccionar Almacén:").grid(row=1, column=0, padx=5, pady=5)
        self.almacenes_combo = ttk.Combobox(frame, state="readonly")
        self.almacenes_combo.grid(row=1, column=1, padx=5, pady=5)
        self.almacenes_combo.bind("<<ComboboxSelected>>", self.seleccionar_almacen)

        # Populate if already exists
        self.almacenes_combo['values'] = list(self.sistema_inventario.almacenes.keys())

    def _crear_pestana_productos(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Productos")

        self.nombre_lbl = tk.Label(frame, text="Nombre del Producto:")
        self.nombre_lbl.grid(row=2, column=0)
        self.nombre_entry = tk.Entry(frame)
        self.nombre_entry.grid(row=2, column=1)

        self.cantidad_lbl = tk.Label(frame, text="Cantidad:")
        self.cantidad_lbl.grid(row=3, column=0)
        self.cantidad_entry = tk.Entry(frame)
        self.cantidad_entry.grid(row=3, column=1)

        self.unidad_medida_lbl = tk.Label(frame, text="Unidad de Medida:")
        self.unidad_medida_lbl.grid(row=4, column=0)
        self.unidad_medida_entry = tk.Entry(frame)
        self.unidad_medida_entry.grid(row=4, column=1)

        self.fecha_vencimiento_lbl = tk.Label(frame, text="Fecha Vencimiento (YYYY-MM-DD):")
        self.fecha_vencimiento_lbl.grid(row=5, column=0)
        self.fecha_vencimiento_entry = tk.Entry(frame)
        self.fecha_vencimiento_entry.grid(row=5, column=1)

        self.tarifa_lbl = tk.Label(frame, text="Tarifa:")
        self.tarifa_lbl.grid(row=6, column=0)
        self.tarifa_entry = tk.Entry(frame)
        self.tarifa_entry.grid(row=6, column=1)

        self.temperatura_lbl = tk.Label(frame, text="Temperatura:")
        self.temperatura_lbl.grid(row=7, column=0)
        self.temperatura_entry = tk.Entry(frame)
        self.temperatura_entry.grid(row=7, column=1)

        self.agregar_btn = tk.Button(frame, text="Agregar Producto", command=self.agregar_producto)
        self.agregar_btn.grid(row=8, column=0, pady=10)

        # Remove
        self.remover_lbl = tk.Label(frame, text="Remover Producto:")
        self.remover_lbl.grid(row=9, column=0)
        self.remover_entry = tk.Entry(frame)
        self.remover_entry.grid(row=9, column=1)

        self.remover_cantidad_lbl = tk.Label(frame, text="Cantidad a Remover:")
        self.remover_cantidad_lbl.grid(row=10, column=0)
        self.remover_cantidad_entry = tk.Entry(frame)
        self.remover_cantidad_entry.grid(row=10, column=1)

        self.remover_btn = tk.Button(frame, text="Remover", command=self.remover_producto)
        self.remover_btn.grid(row=11, column=0, pady=10)

        # Edit
        self.editar_lbl = tk.Label(frame, text="Editar Producto:")
        self.editar_lbl.grid(row=12, column=0)
        self.editar_entry = tk.Entry(frame)
        self.editar_entry.grid(row=12, column=1)

        self.editar_cantidad_lbl = tk.Label(frame, text="Nueva Cantidad:")
        self.editar_cantidad_lbl.grid(row=13, column=0)
        self.editar_cantidad_entry = tk.Entry(frame)
        self.editar_cantidad_entry.grid(row=13, column=1)

        self.editar_unidad_lbl = tk.Label(frame, text="Nueva Unidad:")
        self.editar_unidad_lbl.grid(row=14, column=0)
        self.editar_unidad_entry = tk.Entry(frame)
        self.editar_unidad_entry.grid(row=14, column=1)

        self.editar_fecha_lbl = tk.Label(frame, text="Nueva Fecha (YYYY-MM-DD):")
        self.editar_fecha_lbl.grid(row=15, column=0)
        self.editar_fecha_entry = tk.Entry(frame)
        self.editar_fecha_entry.grid(row=15, column=1)

        self.editar_tarifa_lbl = tk.Label(frame, text="Nueva Tarifa:")
        self.editar_tarifa_lbl.grid(row=16, column=0)
        self.editar_tarifa_entry = tk.Entry(frame)
        self.editar_tarifa_entry.grid(row=16, column=1)

        self.editar_temperatura_lbl = tk.Label(frame, text="Nueva Temperatura:")
        self.editar_temperatura_lbl.grid(row=17, column=0)
        self.editar_temperatura_entry = tk.Entry(frame)
        self.editar_temperatura_entry.grid(row=17, column=1)

        self.editar_btn = tk.Button(frame, text="Editar", command=self.editar_producto)
        self.editar_btn.grid(row=18, column=0, pady=10)

        # Table
        self.tabla = ttk.Treeview(frame, columns=("Nombre", "Cantidad", "Unidad de Medida", "Fecha de Vencimiento", "Tarifa", "Temperatura"), show='headings')
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Cantidad", text="Cantidad")
        self.tabla.heading("Unidad de Medida", text="Unidad de Medida")
        self.tabla.heading("Fecha de Vencimiento", text="Fecha de Vencimiento")
        self.tabla.heading("Tarifa", text="Tarifa")
        self.tabla.heading("Temperatura", text="Temperatura")
        self.tabla.grid(row=0, column=3, rowspan=20, padx=10, pady=10)

    def _crear_pestana_transporte(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Transporte")

        self.transporte_nombre_lbl = tk.Label(frame, text="Nombre Producto:")
        self.transporte_nombre_lbl.grid(row=0, column=0)
        self.transporte_nombre_entry = tk.Entry(frame)
        self.transporte_nombre_entry.grid(row=0, column=1)

        self.transporte_cantidad_lbl = tk.Label(frame, text="Cantidad:")
        self.transporte_cantidad_lbl.grid(row=1, column=0)
        self.transporte_cantidad_entry = tk.Entry(frame)
        self.transporte_cantidad_entry.grid(row=1, column=1)

        self.transporte_unidad_lbl = tk.Label(frame, text="Unidad:")
        self.transporte_unidad_lbl.grid(row=2, column=0)
        self.transporte_unidad_entry = tk.Entry(frame)
        self.transporte_unidad_entry.grid(row=2, column=1)

        self.transporte_fecha_lbl = tk.Label(frame, text="Fecha (YYYY-MM-DD):")
        self.transporte_fecha_lbl.grid(row=3, column=0)
        self.transporte_fecha_entry = tk.Entry(frame)
        self.transporte_fecha_entry.grid(row=3, column=1)

        self.transporte_tarifa_lbl = tk.Label(frame, text="Tarifa:")
        self.transporte_tarifa_lbl.grid(row=4, column=0)
        self.transporte_tarifa_entry = tk.Entry(frame)
        self.transporte_tarifa_entry.grid(row=4, column=1)

        self.ingreso_egreso_lbl = tk.Label(frame, text="Ingreso/Egreso:")
        self.ingreso_egreso_lbl.grid(row=5, column=0)
        self.ingreso_egreso_entry = ttk.Combobox(frame, values=["ingreso", "egreso"])
        self.ingreso_egreso_entry.grid(row=5, column=1)

        self.operador_lbl = tk.Label(frame, text="Operador:")
        self.operador_lbl.grid(row=6, column=0)
        self.operador_entry = tk.Entry(frame)
        self.operador_entry.grid(row=6, column=1)

        self.temperatura_lbl = tk.Label(frame, text="Temperatura:")
        self.temperatura_lbl.grid(row=7, column=0)
        self.transporte_temperatura_entry = tk.Entry(frame)
        self.transporte_temperatura_entry.grid(row=7, column=1)

        self.hora_llegada_lbl = tk.Label(frame, text="Hora Llegada:")
        self.hora_llegada_lbl.grid(row=8, column=0)
        self.hora_llegada_entry = tk.Entry(frame)
        self.hora_llegada_entry.grid(row=8, column=1)

        self.hora_retiro_lbl = tk.Label(frame, text="Hora Retiro:")
        self.hora_retiro_lbl.grid(row=9, column=0)
        self.hora_retiro_entry = tk.Entry(frame)
        self.hora_retiro_entry.grid(row=9, column=1)

        self.registrar_transporte_btn = tk.Button(frame, text="Registrar Transporte", command=self.registrar_transporte)
        self.registrar_transporte_btn.grid(row=10, column=0, pady=10)

    def _crear_pestana_admin(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Admin Permisos")

        tk.Label(frame, text="Seleccionar Rol:").grid(row=0, column=0, pady=10, padx=10)

        self.rol_combo = ttk.Combobox(frame, state="readonly")
        self.rol_combo.grid(row=0, column=1, pady=10, padx=10)
        self.rol_combo['values'] = list(self.sistema_autenticacion.roles_permisos.keys())
        self.rol_combo.bind("<<ComboboxSelected>>", self.cargar_permisos_rol)

        self.check_vars = {}
        pantallas_disponibles = ['Almacen', 'Productos', 'Transporte', 'Reportes', 'Admin']

        for i, pantalla in enumerate(pantallas_disponibles):
            var = tk.BooleanVar()
            self.check_vars[pantalla] = var
            chk = tk.Checkbutton(frame, text=pantalla, variable=var)
            chk.grid(row=i+1, column=0, columnspan=2, sticky='w', padx=20)

        guardar_btn = tk.Button(frame, text="Guardar Permisos", command=self.guardar_permisos)
        guardar_btn.grid(row=len(pantallas_disponibles)+1, column=0, columnspan=2, pady=20)

    def cargar_permisos_rol(self, event):
        rol = self.rol_combo.get()
        permisos_rol = self.sistema_autenticacion.roles_permisos.get(rol, [])
        for pantalla, var in self.check_vars.items():
            var.set(pantalla in permisos_rol)

    def guardar_permisos(self):
        rol = self.rol_combo.get()
        if not rol:
            messagebox.showerror("Error", "Seleccione un rol")
            return

        for pantalla, var in self.check_vars.items():
            self.sistema_autenticacion.modificar_permisos(rol, pantalla, var.get())

        messagebox.showinfo("Éxito", f"Permisos actualizados para el rol {rol}")
        # Refresh interface to apply changes if editing own role
        if rol == self.usuario_actual_rol:
            self.crear_interfaz()

    def _crear_pestana_reportes(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Reportes")

        self.consultar_btn = tk.Button(frame, text="Consultar Inventario", command=self.consultar_inventario)
        self.consultar_btn.grid(row=19, column=0, pady=10)

        self.verificar_fechas_btn = tk.Button(frame, text="Verificar Fechas", command=self.verificar_fechas_vencimiento)
        self.verificar_fechas_btn.grid(row=20, column=0, pady=10)

        self.exportar_lbl = tk.Label(frame, text="Nombre del archivo CSV:")
        self.exportar_lbl.grid(row=21, column=0)
        self.exportar_entry = tk.Entry(frame)
        self.exportar_entry.grid(row=21, column=1)

        self.exportar_btn = tk.Button(frame, text="Exportar a CSV", command=self.exportar_a_csv)
        self.exportar_btn.grid(row=22, column=0, pady=10)

        self.guardar_btn = tk.Button(frame, text="Guardar Inventario", command=self.guardar_inventario)
        self.guardar_btn.grid(row=22, column=1, pady=10)

        self.cargar_btn = tk.Button(frame, text="Cargar Inventario", command=self.cargar_inventario)
        self.cargar_btn.grid(row=22, column=2, pady=10)

        self.reporte_transporte_btn = tk.Button(frame, text="Reporte Transporte", command=self.generar_reporte_transporte)
        self.reporte_transporte_btn.grid(row=29, column=0, pady=10)

        self.enviar_correo_btn = tk.Button(frame, text="Enviar Correo", command=self.enviar_reporte_por_correo)
        self.enviar_correo_btn.grid(row=30, column=0, pady=10)

        self.generar_pdf_btn = tk.Button(frame, text="Generar PDF", command=self.generar_pdf)
        self.generar_pdf_btn.grid(row=31, column=0, pady=10)

        self.generar_grafico_btn = tk.Button(frame, text="Generar Gráfico", command=self.generar_grafico)
        self.generar_grafico_btn.grid(row=32, column=0, pady=10)

        self.reporte_lbl = tk.Label(frame, text="Generar Reporte por:")
        self.reporte_lbl.grid(row=33, column=0)
        self.reporte_criterio = ttk.Combobox(frame, values=["fecha", "producto", "unidad_medida"])
        self.reporte_criterio.grid(row=33, column=1)

        self.reporte_valor_lbl = tk.Label(frame, text="Valor del criterio:")
        self.reporte_valor_lbl.grid(row=34, column=0)
        self.reporte_valor = tk.Entry(frame)
        self.reporte_valor.grid(row=34, column=1)

        self.reporte_btn = tk.Button(frame, text="Generar", command=self.generar_reporte)
        self.reporte_btn.grid(row=35, column=0, pady=10)

        self.factura_btn = tk.Button(frame, text="Imprimir Factura", command=self.imprimir_factura)
        self.factura_btn.grid(row=36, column=0, pady=10)

    def agregar_almacen(self):
        nombre_almacen = self.almacen_entry.get()
        if nombre_almacen and nombre_almacen not in self.sistema_inventario.almacenes:
            self.sistema_inventario.agregar_almacen(nombre_almacen)
            self.almacenes_combo['values'] = list(self.sistema_inventario.almacenes.keys())
            self.almacen_entry.delete(0, tk.END)
            messagebox.showinfo("Éxito", f"Almacén {nombre_almacen} agregado.")
        else:
            messagebox.showerror("Error", "Nombre de almacén inválido o ya existente.")
    
    def seleccionar_almacen(self, event):
        nombre_almacen = self.almacenes_combo.get()
        if nombre_almacen in self.sistema_inventario.almacenes:
            self.inventario = self.sistema_inventario.almacenes[nombre_almacen]
            self.actualizar_tabla()

    def agregar_producto(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        nombre = getattr(self, "nombre_entry", None)
        cantidad = getattr(self, "cantidad_entry", None)
        unidad_medida = getattr(self, "unidad_medida_entry", None)
        fecha_vencimiento = getattr(self, "fecha_vencimiento_entry", None)
        tarifa = getattr(self, "tarifa_entry", None)
        temperatura = getattr(self, "temperatura_entry", None)

        if any(v is None for v in [nombre, cantidad, unidad_medida, fecha_vencimiento, tarifa, temperatura]):
             messagebox.showerror("Error", "Faltan permisos para acceder a todos los campos necesarios.")
             return

        nombre = nombre.get()
        cantidad = cantidad.get()
        unidad_medida = unidad_medida.get()
        fecha_vencimiento = fecha_vencimiento.get()
        tarifa = tarifa.get()
        temperatura = temperatura.get()

        if not validar_cantidad(cantidad):
            messagebox.showerror("Error", "Cantidad no válida. Debe ser un número positivo.")
            return
        if not validar_fecha(fecha_vencimiento):
            messagebox.showerror("Error", "Fecha de vencimiento no válida. Debe ser en formato YYYY-MM-DD.")
            return

        producto = Producto(nombre, float(cantidad), unidad_medida, fecha_vencimiento, float(tarifa))
        producto.temperatura = temperatura
        self.inventario.agregar_producto(producto)
        self.actualizar_tabla()
        messagebox.showinfo("Éxito", f"Producto {nombre} agregado.")

    def remover_producto(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        nombre = getattr(self, "remover_entry", None)
        cantidad = getattr(self, "remover_cantidad_entry", None)
        if nombre is None or cantidad is None:
            messagebox.showerror("Error", "Faltan permisos para acceder a los campos.")
            return

        nombre = nombre.get()
        cantidad = cantidad.get()

        if not validar_cantidad(cantidad):
            messagebox.showerror("Error", "Cantidad no válida. Debe ser un número positivo.")
            return

        if self.inventario.remover_producto(nombre, float(cantidad)):
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", f"Producto {nombre} removido.")
        else:
            messagebox.showerror("Error", "No se pudo remover el producto. Verifique el nombre y la cantidad.")
   
    def editar_producto(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        nombre = getattr(self, "editar_entry", None)
        cantidad = getattr(self, "editar_cantidad_entry", None)
        unidad_medida = getattr(self, "editar_unidad_entry", None)
        fecha_vencimiento = getattr(self, "editar_fecha_entry", None)
        tarifa = getattr(self, "editar_tarifa_entry", None)
        temperatura = getattr(self, "editar_temperatura_entry", None)

        if any(v is None for v in [nombre, cantidad, unidad_medida, fecha_vencimiento, tarifa, temperatura]):
             messagebox.showerror("Error", "Faltan permisos para acceder a todos los campos necesarios.")
             return

        nombre = nombre.get()
        cantidad = cantidad.get()
        unidad_medida = unidad_medida.get()
        fecha_vencimiento = fecha_vencimiento.get()
        tarifa = tarifa.get()
        temperatura = temperatura.get()

        cantidad = float(cantidad) if validar_cantidad(cantidad) else None
        unidad_medida = unidad_medida if unidad_medida else None
        fecha_vencimiento = fecha_vencimiento if validar_fecha(fecha_vencimiento) else None
        tarifa = float(tarifa) if tarifa else None

        if self.inventario.editar_producto(nombre, cantidad, unidad_medida, fecha_vencimiento, tarifa, temperatura):
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", f"Producto {nombre} editado.")
        else:
            messagebox.showerror("Error", "No se pudo editar el producto. Verifique el nombre.")

    def consultar_inventario(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        unidad_medida = getattr(self, "unidad_medida_entry", None)
        if unidad_medida and unidad_medida.winfo_exists():
            unidad_medida = unidad_medida.get()
        else:
            unidad_medida = None
        inventario_consultado = self.inventario.consultar_inventario(unidad_medida)
        if inventario_consultado:
            resultado = f"Inventario en {unidad_medida}:\n"
            for nombre, cantidad in inventario_consultado.items():
                resultado += f"- {nombre}: {cantidad}\n"
            messagebox.showinfo("Inventario", resultado)
        else:
            messagebox.showinfo("Inventario", f"No hay productos en {unidad_medida}.")

    def verificar_fechas_vencimiento(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        productos_vencidos = self.inventario.verificar_fechas_vencimiento()
        if productos_vencidos:
            resultado = "Productos vencidos:\n"
            for producto in productos_vencidos:
                resultado += f"- {producto}\n"
            messagebox.showinfo("Productos Vencidos", resultado)
        else:
            messagebox.showinfo("Productos Vencidos", "No hay productos vencidos.")

    def exportar_a_csv(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        nombre_archivo = getattr(self, "exportar_entry", None)
        if not nombre_archivo:
             messagebox.showerror("Error", "No tiene permisos para acceder a este campo.")
             return
        nombre_archivo = nombre_archivo.get()

        self.inventario.exportar_a_csv(nombre_archivo)
        messagebox.showinfo("Éxito", f"Inventario exportado a {nombre_archivo}")

    def guardar_inventario(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        nombre_archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if nombre_archivo:
            self.inventario.guardar_inventario(nombre_archivo)
            messagebox.showinfo("Éxito", f"Inventario guardado en {nombre_archivo}")

    def cargar_inventario(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        nombre_archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if nombre_archivo:
            self.inventario.cargar_inventario(nombre_archivo)
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", f"Inventario cargado desde {nombre_archivo}")

    def registrar_transporte(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        tipo = getattr(self, "ingreso_egreso_entry", None)
        nombre = getattr(self, "transporte_nombre_entry", None)
        cantidad = getattr(self, "transporte_cantidad_entry", None)
        unidad_medida = getattr(self, "transporte_unidad_entry", None)
        fecha_vencimiento = getattr(self, "transporte_fecha_entry", None)
        tarifa = getattr(self, "transporte_tarifa_entry", None)
        operador = getattr(self, "operador_entry", None)
        temperatura = getattr(self, "transporte_temperatura_entry", None)
        hora_llegada = getattr(self, "hora_llegada_entry", None)
        hora_retiro = getattr(self, "hora_retiro_entry", None)

        if any(v is None for v in [tipo, nombre, cantidad, unidad_medida, fecha_vencimiento, tarifa, operador, temperatura, hora_llegada, hora_retiro]):
            messagebox.showerror("Error", "Faltan permisos para acceder a todos los campos necesarios.")
            return

        tipo = tipo.get()
        nombre = nombre.get()
        cantidad = cantidad.get()
        unidad_medida = unidad_medida.get()
        fecha_vencimiento = fecha_vencimiento.get()
        tarifa = tarifa.get()
        operador = operador.get()
        temperatura = temperatura.get()
        hora_llegada = hora_llegada.get()
        hora_retiro = hora_retiro.get()

        if not validar_cantidad(cantidad):
            messagebox.showerror("Error", "Cantidad no válida. Debe ser un número positivo.")
            return
        if not validar_fecha(fecha_vencimiento):
            messagebox.showerror("Error", "Fecha de vencimiento no válida. Debe ser en formato YYYY-MM-DD.")
            return

        if self.sistema_inventario.registrar_ingreso_egreso(tipo, self.almacenes_combo.get(), nombre, float(cantidad), unidad_medida, fecha_vencimiento, float(tarifa), operador, temperatura, hora_llegada, hora_retiro):
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", f"Registro de transporte {tipo} para {nombre} registrado.")
        else:
            messagebox.showerror("Error", "Error al registrar el transporte.")

    def generar_reporte_transporte(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        reporte = self.sistema_inventario.generar_reporte_transporte()
        if reporte:
            nombre_archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if nombre_archivo:
                with open(nombre_archivo, 'w') as archivo:
                    for linea in reporte:
                        archivo.write(linea + "\n")
                messagebox.showinfo("Éxito", f"Reporte de transporte guardado en {nombre_archivo}")
        else:
            messagebox.showinfo("Reporte", "No hay registros de transporte.")

    def enviar_reporte_por_correo(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        email = askstring("Enviar por correo", "Ingrese la dirección de correo:")
        asunto = askstring("Enviar por correo", "Ingrese el asunto del correo:")
        cuerpo = askstring("Enviar por correo", "Ingrese el cuerpo del correo:")
        nombre_archivo = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

        if email and asunto and cuerpo and nombre_archivo:
            self.sistema_inventario.enviar_reporte_por_correo(email, asunto, cuerpo, nombre_archivo)
            messagebox.showinfo("Éxito", f"Correo enviado a {email}")
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")

    def generar_pdf(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        contenido = [f"{producto.nombre} - {producto.cantidad} {producto.unidad_medida} - {producto.fecha_vencimiento.strftime('%Y-%m-%d')} - {producto.tarifa} - {producto.temperatura}" for producto in self.inventario.productos]
        nombre_archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if nombre_archivo:
            self.sistema_inventario.generar_pdf(nombre_archivo, contenido)
            messagebox.showinfo("Éxito", f"PDF generado en {nombre_archivo}")

    def generar_grafico(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        nombre_archivo = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if nombre_archivo:
            self.sistema_inventario.generar_grafico(nombre_archivo)
            messagebox.showinfo("Éxito", f"Gráfico generado en {nombre_archivo}")

    def generar_reporte(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        criterio = getattr(self, "reporte_criterio", None)
        valor = getattr(self, "reporte_valor", None)
        if not criterio or not valor or not criterio.winfo_exists() or not valor.winfo_exists():
             messagebox.showerror("Error", "Faltan permisos para los campos de reporte.")
             return
        criterio = criterio.get()
        valor = valor.get()
        reporte = self.inventario.generar_reporte(criterio, valor)
        if reporte:
            resultado = f"Reporte por {criterio} ({valor}):\n"
            for producto in reporte:
                resultado += f"- {producto}\n"
            messagebox.showinfo("Reporte", resultado)
        else:
            messagebox.showinfo("Reporte", f"No se encontraron productos para el criterio {criterio} con el valor {valor}.")

    def imprimir_factura(self):
        if not self.inventario:
            messagebox.showerror("Error", "Seleccione un almacén.")
            return

        factura = "Factura:\n"
        for producto in self.inventario.productos:
            factura += f"{producto.nombre} - {producto.cantidad} {producto.unidad_medida} - Vence: {producto.fecha_vencimiento.strftime('%Y-%m-%d')} - Tarifa: {producto.tarifa} - Temperatura: {producto.temperatura}\n"
        messagebox.showinfo("Factura", factura)

    def actualizar_tabla(self):
        if not self.inventario:
            return

        if not hasattr(self, "tabla") or not self.tabla.winfo_exists():
            return

        for i in self.tabla.get_children():
            self.tabla.delete(i)
        for producto in self.inventario.productos:
            self.tabla.insert("", "end", values=(producto.nombre, producto.cantidad, producto.unidad_medida, producto.fecha_vencimiento.strftime('%Y-%m-%d'), producto.tarifa, producto.temperatura))

# Función principal para ejecutar la GUI
def main():
    root = tk.Tk()
    root.geometry("800x600")  # Ajustar tamaño de la ventana
    sistema_inventario = SistemaInventario()
    sistema_autenticacion = SistemaAutenticacion()

    # Crear usuarios iniciales (para prueba)
    sistema_autenticacion.registrar_usuario("admin", "admin123", "admin")
    sistema_autenticacion.registrar_usuario("usuario", "user123", "usuario")

    app = InventarioGUI(root, sistema_inventario, sistema_autenticacion)
    root.mainloop()

if __name__ == "__main__":
    main()
