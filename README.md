# Control-inventario
Una aplicación de control de inventario sencillo.


# Plan de Portabilidad: Interfaz Gráfica con Base de Datos y Compilación Multiplataforma

Hemos actualizado la aplicación gráfica de control de inventarios para incluir **persistencia de datos local mediante una base de datos SQLite** y **fuentes de mayor tamaño para mejorar la lectura y accesibilidad**.

---

## 1. Características de la Interfaz Gráfica (GUI)

La aplicación gráfica ha sido escrita utilizando **CustomTkinter** y se encuentra en:
- **Código Fuente:** [control-inventarios-gui.py](file:///home/wilfod/Proyectos/control-inventarios-gui.py)

### Mejoras clave agregadas:
- **💾 Persistencia de Datos (SQLite):** Todos los cambios de inventario (productos creados, eliminados y stock ajustado) se guardan en tiempo real en una base de datos local `inventario.db`. Cuando cierras la aplicación y la vuelves a abrir, el inventario se carga automáticamente de la base de datos.
- **🔎 Tipografía Agrandada (Accesibilidad):** Se han incrementado significativamente los tamaños de letra de todos los elementos para facilitar la lectura, en línea con las configuraciones del sistema:
  - Títulos principales: **26px (negrita)**
  - Títulos de tablas y secciones: **18px (negrita)**
  - Nombres de productos y botones de ajuste: **16px**
- **Lista Scrollable Interactiva:** Muestra todos los productos y permite realizar ajustes rápidos mediante botones `➕` (Aumentar stock), `➖` (Disminuir stock) y `🗑️` (Eliminar producto).
- **Búsqueda Instantánea:** Un buscador que filtra la lista de productos a medida que escribes.
- **Impresión Directa:** El botón de **🖨️ Imprimir Reporte** genera el archivo `reporte_inventario.txt` y lo abre automáticamente en el editor de texto del sistema para su fácil impresión.

---

## 2. Compilador Multiplataforma Automatizado (CI/CD)

Para solucionar el problema de compilar binarios para diferentes sistemas operativos (Windows, macOS, Linux), mantenemos el flujo de trabajo automatizado en GitHub:
- **Archivo de Configuración:** [.github/workflows/build.yml](file:///home/wilfod/Proyectos/.github/workflows/build.yml)

Este flujo compila automáticamente la aplicación para los tres sistemas operativos utilizando máquinas virtuales dedicadas en GitHub cada vez que subes cambios o creas una etiqueta de versión (ej: `v1.0.0`), generando un release con los tres archivos portables.

---

## 3. Construcción y Ejecución Local

### Ejecutables en Linux:
1. **Ejecutable Gráfico Compilado:** Se está compilando en [dist/ControlInventariosGUI](file:///home/wilfod/Proyectos/dist/ControlInventariosGUI). Se ejecuta con:
   ```bash
   ./dist/ControlInventariosGUI
   ```

> [!NOTE]
> Al empaquetarse con PyInstaller, la base de datos `inventario.db` se creará en el mismo directorio desde donde ejecutes la aplicación, facilitando la portabilidad (puedes mover el ejecutable y la base de datos juntos en un pendrive).
