import pytest
import datetime
from app import Inventario, Producto

@pytest.fixture
def inventario_vacio():
    return Inventario("Test Almacen")

def test_agregar_producto_single(inventario_vacio):
    """Test adding a single product to an empty inventory."""
    producto = Producto("Manzana", 100, "kg", "2023-12-31", 1.5)
    inventario_vacio.agregar_producto(producto)

    assert len(inventario_vacio.productos) == 1
    assert inventario_vacio.productos[0] == producto
    assert inventario_vacio.productos[0].nombre == "Manzana"

def test_agregar_producto_multiple(inventario_vacio):
    """Test adding multiple products to the inventory."""
    prod1 = Producto("Manzana", 100, "kg", "2023-12-31", 1.5)
    prod2 = Producto("Banana", 50, "kg", "2023-11-30", 1.2)
    prod3 = Producto("Pera", 200, "kg", "2024-01-15", 2.0)

    inventario_vacio.agregar_producto(prod1)
    inventario_vacio.agregar_producto(prod2)
    inventario_vacio.agregar_producto(prod3)

    assert len(inventario_vacio.productos) == 3
    assert inventario_vacio.productos[0] == prod1
    assert inventario_vacio.productos[1] == prod2
    assert inventario_vacio.productos[2] == prod3

def test_agregar_producto_edge_cases(inventario_vacio):
    """Test adding edge case objects like None to confirm expected behavior."""
    inventario_vacio.agregar_producto(None)

    assert len(inventario_vacio.productos) == 1
    assert inventario_vacio.productos[0] is None
