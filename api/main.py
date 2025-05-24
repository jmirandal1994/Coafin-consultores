from flask import Flask, request, send_file, render_template
import pandas as pd
import os
import tempfile
import traceback

app = Flask(__name__, static_url_path='/static')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        archivo_sii = request.files['file']
        if not archivo_sii:
            return 'No se subió ningún archivo.'
        try:
            # Leer archivo del SII
            df_sii = pd.read_csv(archivo_sii, encoding='latin1', sep=None, engine='python', dtype=str)
            df_sii.columns = df_sii.columns.str.strip()

            # Filtrar por Nro = 33
            df_filtrado = df_sii[df_sii['Nro'].astype(str) == '33']
            rut_proveedores = df_filtrado['Tipo Compra'].dropna().reset_index(drop=True)
            folios = df_filtrado['Razon Social'].astype(str).dropna().reset_index(drop=True)

            # Leer archivo base desde /api
            base_path = os.path.dirname(__file__)
            base_file = os.path.join(base_path, 'archivo_base_fijo.csv')
            df_base = pd.read_csv(base_file, encoding='latin1', sep=';', dtype=str)

            # Reemplazar datos
            min_filas = min(len(rut_proveedores), len(folios))
            df_modificada = df_base.iloc[:min_filas].copy()
            df_modificada['Rut-DV'] = rut_proveedores[:min_filas]
            df_modificada['Folio_Doc'] = folios[:min_filas]

            # Guardar archivo temporal para Vercel
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            df_modificada.to_csv(temp_file.name, index=False, sep=';', encoding='latin1')
            temp_file.close()

            return send_file(temp_file.name, as_attachment=True, download_name="archivo_modificado.csv")

        except Exception as e:
            return f'Error al procesar el archivo:<br><pre>{traceback.format_exc()}</pre>'

    return render_template('index.html')

def handler(request):
    return app
