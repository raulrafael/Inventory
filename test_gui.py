import tkinter as tk
from app import SistemaInventario, SistemaAutenticacion, InventarioGUI

def test_roles():
    print("Iniciando prueba de roles y pestañas...")

    root = tk.Tk()
    root.geometry("800x600")

    sistema_inventario = SistemaInventario()
    sistema_autenticacion = SistemaAutenticacion()

    sistema_autenticacion.registrar_usuario("admin", "admin123", "admin")
    sistema_autenticacion.registrar_usuario("usuario", "user123", "usuario")

    app = InventarioGUI(root, sistema_inventario, sistema_autenticacion)

    print("Probando login de admin...")
    # Simulate login as admin
    app.nombre_usuario_entry.insert(0, "admin")
    app.contraseña_entry.insert(0, "admin123")
    app.login()

    tabs_admin = [app.notebook.tab(i, option="text") for i in app.notebook.tabs()]
    print(f"Pestañas de admin: {tabs_admin}")
    assert "Almacén" in tabs_admin
    assert "Productos" in tabs_admin
    assert "Transporte" in tabs_admin
    assert "Reportes" in tabs_admin
    assert "Admin Permisos" in tabs_admin

    print("Probando login de usuario...")
    # Simulate logout and login as usuario
    app.login_interfaz()
    app.nombre_usuario_entry.insert(0, "usuario")
    app.contraseña_entry.insert(0, "user123")
    app.login()

    tabs_usuario = [app.notebook.tab(i, option="text") for i in app.notebook.tabs()]
    print(f"Pestañas de usuario: {tabs_usuario}")
    assert "Almacén" in tabs_usuario
    assert "Productos" in tabs_usuario
    assert "Transporte" not in tabs_usuario
    assert "Reportes" not in tabs_usuario
    assert "Admin Permisos" not in tabs_usuario

    print("Prueba exitosa.")

    root.destroy()

if __name__ == "__main__":
    test_roles()
