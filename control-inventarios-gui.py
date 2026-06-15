import customtkinter as ctk
import datetime
import os
import sqlite3
import subprocess
from tkinter import messagebox

ctk.set_appearance_mode("System")  # Modos: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

# =====================================================================
# GESTIÓN DE LA BASE DE DATOS (SQLite)
# =====================================================================
DB_PATH = "inventario.db"

def inicializar_db():
    """Crea la tabla de inventario si no existe y carga datos iniciales por defecto."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            nombre TEXT PRIMARY KEY,
            cantidad INTEGER NOT NULL
        )
    """)
    conn.commit()
    
    # Comprobar si está vacía para precargar algunos datos demostrativos
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        datos_iniciales = [
            ("Chinola-Crema", 15),
            ("Batata", 8),
            ("Dulce de leche", 24),
            ("Bosque Blanco", 5),
            ("Limonada coco", 12),
            ("Mango Crema", 18)
        ]
        cursor.executemany("INSERT INTO productos (nombre, cantidad) VALUES (?, ?)", datos_iniciales)
        conn.commit()
    conn.close()

def cargar_inventario_db():
    """Recupera todos los productos y cantidades guardados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad FROM productos")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def guardar_o_actualizar_producto_db(nombre, cantidad):
    """Guarda un producto nuevo o actualiza el stock de uno existente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO productos (nombre, cantidad) VALUES (?, ?)", (nombre, cantidad))
    conn.commit()
    conn.close()

def eliminar_producto_db(nombre):
    """Elimina permanentemente un producto de la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()

def vaciar_inventario_db():
    """Elimina todos los registros de la tabla de productos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos")
    conn.commit()
    conn.close()


# =====================================================================
# CLASE DE LA APLICACIÓN GRÁFICA (GUI)
# =====================================================================
class InventarioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Inicializar la base de datos SQLite
        inicializar_db()
        
        # Cargar los datos guardados en la base de datos
        self.inventario = cargar_inventario_db()
        
        self.title("Sistema de Control de Inventario")
        self.geometry("900x650")
        self.resizable(True, True)
        
        # Fuentes con tamaño incrementado (Accesibilidad / Mayor lectura)
        self.font_logo = ctk.CTkFont(size=26, weight="bold")
        self.font_header = ctk.CTkFont(size=18, weight="bold")
        self.font_body = ctk.CTkFont(size=16, weight="normal")
        self.font_bold_body = ctk.CTkFont(size=16, weight="bold")
        self.font_ui_small = ctk.CTkFont(size=14, weight="normal")
        
        # Configurar layout de grid (1 fila, 2 columnas)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ---- BARRA LATERAL (SIDEBAR) ----
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Inventario Pro 🚀", font=self.font_logo)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Botones de la barra lateral con fuente mayor
        self.btn_imprimir = ctk.CTkButton(self.sidebar_frame, text="🖨️ Imprimir Reporte", font=self.font_bold_body, command=self.imprimir_reporte)
        self.btn_imprimir.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_limpiar = ctk.CTkButton(self.sidebar_frame, text="🧹 Vaciar Todo", font=self.font_bold_body, fg_color="transparent", border_width=1, text_color=("black", "white"), command=self.confirmar_vaciar)
        self.btn_limpiar.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Control del Tema (Claro / Oscuro)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Tema Visual:", font=self.font_ui_small, anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"], font=self.font_ui_small, command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.appearance_mode_optionemenu.set("System")
        
        # ---- PANEL PRINCIPAL (MAIN AREA) ----
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1) # El listado se expande verticalmente
        
        # Formulario de Nuevo Producto (Fila 0) - Mayor tamaño de letra y inputs
        self.form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.form_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.form_frame.grid_columnconfigure(0, weight=3)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        self.entry_nombre = ctk.CTkEntry(self.form_frame, placeholder_text="Nombre del producto...", font=self.font_body, height=40)
        self.entry_nombre.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        self.entry_stock = ctk.CTkEntry(self.form_frame, placeholder_text="Stock inicial...", font=self.font_body, height=40)
        self.entry_stock.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.btn_agregar = ctk.CTkButton(self.form_frame, text="➕ Agregar", font=self.font_bold_body, height=40, width=120, command=self.agregar_nuevo_producto)
        self.btn_agregar.grid(row=0, column=2, padx=(10, 0), pady=10)
        
        # Barra de Búsqueda (Fila 1)
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)
        
        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text="🔍 Buscar producto en inventario...", font=self.font_body, height=40)
        self.entry_search.grid(row=0, column=0, padx=0, pady=5, sticky="ew")
        self.entry_search.bind("<KeyRelease>", self.actualizar_lista)
        
        # Lista de Productos (Fila 2)
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Listado de Inventario")
        self.scrollable_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Ajustar fuente del título del ScrollableFrame internamente
        self.scrollable_frame._label.configure(font=self.font_header)
        
        # Panel de Estadísticas / Footer (Fila 3)
        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stats_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.lbl_stats = ctk.CTkLabel(self.stats_frame, text="Productos: 0 | Total Unidades: 0", font=self.font_header)
        self.lbl_stats.pack(side="left")
        
        # Renderizar datos iniciales
        self.actualizar_lista()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        
    def actualizar_lista(self, event=None):
        # Limpiar elementos del frame scrollable
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        busqueda = self.entry_search.get().strip().lower()
        
        total_unidades = 0
        total_productos = 0
        
        # Cabecera de columnas
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(header_frame, text="Producto", font=self.font_header).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Acciones", font=self.font_header).pack(side="right", padx=20)
        ctk.CTkLabel(header_frame, text="Stock", font=self.font_header).pack(side="right", padx=55)
        
        sep = ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="gray")
        sep.pack(fill="x", padx=10, pady=5)
        
        # Generar filas de productos
        for producto, cantidad in self.inventario.items():
            if busqueda and busqueda not in producto.lower():
                continue
                
            total_productos += 1
            total_unidades += cantidad
            
            row_frame = ctk.CTkFrame(self.scrollable_frame)
            row_frame.pack(fill="x", padx=5, pady=4)
            
            # Etiqueta del Producto
            lbl_name = ctk.CTkLabel(row_frame, text=producto, font=self.font_body)
            lbl_name.pack(side="left", padx=15, pady=8)
            
            # Botones de ajuste
            btn_add = ctk.CTkButton(row_frame, text="➕", width=38, height=34, font=self.font_bold_body, fg_color="#2eb85c", hover_color="#218838", text_color="white", command=lambda p=producto: self.modificar_stock_dialog(p, "sumar"))
            btn_add.pack(side="right", padx=(5, 15), pady=5)
            
            btn_sub = ctk.CTkButton(row_frame, text="➖", width=38, height=34, font=self.font_bold_body, fg_color="#e55353", hover_color="#c82333", text_color="white", command=lambda p=producto: self.modificar_stock_dialog(p, "restar"))
            btn_sub.pack(side="right", padx=5, pady=5)
            
            btn_delete = ctk.CTkButton(row_frame, text="🗑️", width=38, height=34, font=self.font_bold_body, fg_color="transparent", text_color="#e55353", hover_color=("gray85", "gray25"), command=lambda p=producto: self.eliminar_producto(p))
            btn_delete.pack(side="right", padx=5, pady=5)
            
            # Cantidad en stock
            lbl_qty = ctk.CTkLabel(row_frame, text=str(cantidad), font=self.font_bold_body, width=80)
            lbl_qty.pack(side="right", padx=25, pady=5)
            
        # Actualizar la etiqueta de estadísticas
        self.lbl_stats.configure(text=f"Productos listados: {total_productos} | Stock Total: {total_unidades} unidades")
        
    def agregar_nuevo_producto(self):
        nombre = self.entry_nombre.get().strip().title()
        if not nombre:
            messagebox.showerror("Error de Validación", "El nombre del producto es obligatorio.")
            return
            
        if nombre in self.inventario:
            messagebox.showwarning("Producto Existente", f"El producto '{nombre}' ya se encuentra registrado.")
            return
            
        stock_str = self.entry_stock.get().strip()
        stock_inicial = 0
        if stock_str:
            try:
                stock_inicial = int(stock_str)
                if stock_inicial < 0:
                    messagebox.showerror("Error", "El stock inicial no puede ser un número negativo.")
                    return
            except ValueError:
                messagebox.showerror("Error", "El stock inicial debe ser un número entero.")
                return
                
        # Guardar en memoria local y persistir en SQLite
        self.inventario[nombre] = stock_inicial
        guardar_o_actualizar_producto_db(nombre, stock_inicial)
        
        self.entry_nombre.delete(0, "end")
        self.entry_stock.delete(0, "end")
        self.actualizar_lista()
        
    def modificar_stock_dialog(self, producto, operacion):
        accion = "añadir a" if operacion == "sumar" else "retirar de"
        dialog = ctk.CTkInputDialog(text=f"Cantidad a {accion} '{producto}':", title="Actualizar Stock")
        valor_str = dialog.get_input()
        
        if valor_str is None or valor_str.strip() == "":
            return
            
        try:
            cantidad = int(valor_str)
            if cantidad <= 0:
                messagebox.showerror("Error", "Por favor ingresa una cantidad positiva mayor a cero.")
                return
                
            if operacion == "sumar":
                self.inventario[producto] += cantidad
            else:
                if cantidad > self.inventario[producto]:
                    messagebox.showerror("Error de Stock", f"Stock insuficiente de '{producto}'.\nDisponible: {self.inventario[producto]} | Solicitado: {cantidad}")
                    return
                self.inventario[producto] -= cantidad
                
            # Persistir los cambios en la base de datos
            guardar_o_actualizar_producto_db(producto, self.inventario[producto])
            self.actualizar_lista()
            
        except ValueError:
            messagebox.showerror("Error de Formato", "Debe ingresar un número entero válido.")

    def eliminar_producto(self, producto):
        confirmar = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar '{producto}' del sistema?")
        if confirmar:
            # Eliminar de memoria y base de datos
            del self.inventario[producto]
            eliminar_producto_db(producto)
            self.actualizar_lista()

    def confirmar_vaciar(self):
        confirmar = messagebox.askyesno("Confirmar Acción", "⚠️ ¡ADVERTENCIA!\n¿Está seguro de que desea vaciar todo el inventario? Esta acción borrará permanentemente todos los datos de la base de datos.")
        if confirmar:
            # Vaciar memoria y base de datos
            self.inventario.clear()
            vaciar_inventario_db()
            self.actualizar_lista()

    def imprimir_reporte(self):
        nombre_archivo = "reporte_inventario.txt"
        try:
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                f.write("====================================\n")
                f.write("   REPORTE DE INVENTARIO ACTUAL\n")
                f.write(f"   Fecha: {fecha_actual}\n")
                f.write("====================================\n")
                f.write(f"| {'Producto':<20} | {'Cantidad':>8} |\n")
                f.write("------------------------------------\n")
                total_unidades = 0
                for producto, cantidad in self.inventario.items():
                    f.write(f"| {producto:<20} | {cantidad:>8} |\n")
                    total_unidades += cantidad
                f.write("------------------------------------\n")
                f.write(f"| {'Total Unidades':<20} | {total_unidades:>8} |\n")
                f.write("====================================\n")
            
            abierto = False
            if os.name == 'posix':
                for cmd in ['xdg-open', 'open']:
                    try:
                        subprocess.run([cmd, nombre_archivo], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        abierto = True
                        break
                    except FileNotFoundError:
                        continue
            elif os.name == 'nt':
                try:
                    os.startfile(nombre_archivo)
                    abierto = True
                except AttributeError:
                    pass
            
            if abierto:
                messagebox.showinfo("Reporte Impreso", f"El reporte de inventario se guardó en '{nombre_archivo}' y se ha abierto automáticamente.")
            else:
                messagebox.showinfo("Reporte Guardado", f"El reporte se guardó en '{nombre_archivo}'. Ábrelo manualmente para imprimirlo.")
                
        except Exception as e:
            messagebox.showerror("Error de Archivo", f"Error al generar o abrir el reporte: {e}")

if __name__ == "__main__":
    app = InventarioApp()
    app.mainloop()
