import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="🏋️ Control Nutricional",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def calcular_frecuencia_cualitativa(serie):
    df = serie.value_counts().reset_index()
    df.columns = ['Categoría', 'Frecuencia']
    total = df['Frecuencia'].sum()
    df['Porcentaje'] = (df['Frecuencia'] / total * 100).round(2)
    df['Frec. Acumulada'] = df['Frecuencia'].cumsum()
    df['% Acumulado'] = df['Porcentaje'].cumsum().round(2)
    df['hi'] = (df['Frecuencia'] / total).round(4)
    df['Hi'] = df['hi'].cumsum().round(4)
    return df

def calcular_frecuencia_cuantitativa(serie, agrupar=False, n_intervalos=5):
    datos = serie.dropna()
    n = len(datos)
    
    if not agrupar:
        df = datos.value_counts().sort_index().reset_index()
        df.columns = ['Valor', 'Frecuencia']
    else:
        if n > 0:
            n_intervalos = int(np.ceil(1 + 3.322 * np.log10(n)))
        
        cortes = pd.cut(datos, bins=n_intervalos, include_lowest=True, right=False)
        df = cortes.value_counts().sort_index().reset_index()
        df.columns = ['Intervalo', 'Frecuencia']
        
        df['Marca de Clase'] = df['Intervalo'].apply(lambda x: round(x.mid, 2))
        
        def fmt_intervalo(intervalo):
            return f"[{intervalo.left:.2f}, {intervalo.right:.2f})"
        
        df['Intervalo'] = df['Intervalo'].apply(fmt_intervalo)

    df['Frec. Relativa'] = (df['Frecuencia'] / n).round(4)
    df['Porcentaje'] = (df['Frec. Relativa'] * 100).round(2)
    df['Frec. Acumulada'] = df['Frecuencia'].cumsum()
    df['% Acumulado'] = (df['Frec. Acumulada'] / n * 100).round(2)
    df['hi'] = df['Frec. Relativa']
    df['Fi'] = df['Frec. Acumulada']
    df['Hi'] = df['hi'].cumsum().round(4)
    return df

def crear_grafico_barras(df_freq, variable, es_cualitativa=True):
    fig, ax = plt.subplots(figsize=(10, 6))
    x_col = 'Categoría' if es_cualitativa else 'Valor'
    ax.bar(df_freq[x_col], df_freq['Frecuencia'], edgecolor='black')
    ax.set_xlabel(variable.title())
    ax.set_ylabel('Frecuencia')
    ax.set_title(f'Gráfico de Barras - {variable.title()}', fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return fig

def crear_grafico_baston(df_freq, variable):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.vlines(x=df_freq['Valor'], ymin=0, ymax=df_freq['Frecuencia'], color='navy', linewidth=2)
    ax.plot(df_freq['Valor'], df_freq['Frecuencia'], "o", color='red')
    ax.set_xticks(df_freq['Valor'])
    ax.set_xlabel(variable.title())
    ax.set_ylabel('Frecuencia Absoluta (fi)')
    ax.set_title(f'Gráfico de Bastón - {variable.title()}', fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return fig

def crear_histograma_poligono(variable, datos, n_bins=5):
    fig, ax = plt.subplots(figsize=(12, 6))
    n, bins, _ = ax.hist(datos, bins=n_bins, color='#11caa0', edgecolor='white', alpha=0.6, label='Histograma')
    marcas = (bins[:-1] + bins[1:]) / 2
    ax.plot(marcas, n, color='red', marker='D', linewidth=2, label='Polígono')
    ax.set_xlabel('Intervalos de Clase / Marca de Clase (Xi)')
    ax.set_ylabel('Frecuencia Absoluta (fi)')
    ax.set_title(f'Histograma y Polígono - {variable.title()}', fontweight='bold')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return fig

def crear_ogiva(variable, datos, n_bins=5):
    fig, ax = plt.subplots(figsize=(10, 5))
    n, bins = np.histogram(datos, bins=n_bins)
    fi_acum = np.cumsum(n)
    marcas = (bins[:-1] + bins[1:]) / 2
    ax.plot(marcas, fi_acum, color='red', marker='s', linewidth=2, label='Ojiva')
    ax.fill_between(marcas, fi_acum, color='purple', alpha=0.3)
    ax.set_xlabel('Intervalos de Clase (años)')
    ax.set_ylabel('Frecuencia Absoluta Acumulada (Fi)')
    ax.set_title(f'Gráfico Ogiva - {variable.title()}', fontweight='bold')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return fig

def crear_grafico_torta(df_freq, variable, es_cualitativa=True):
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = df_freq['Categoría'] if es_cualitativa else df_freq['Valor'].astype(str)
    ax.pie(df_freq['hi'], labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
    ax.set_title(f'Gráfico de Torta - {variable.title()}', fontweight="bold")
    plt.tight_layout()
    return fig

def renderizar_grafico(tipo, df_freq, variable, datos_raw, n_bins, es_cualitativa=True):
    if tipo == "1. Gráfico de Barras":
        return crear_grafico_barras(df_freq, variable, es_cualitativa)
    elif tipo == "2. Gráfico de Bastón":
        if not es_cualitativa:
            return crear_grafico_baston(df_freq, variable)
        else:
            df_temp = df_freq.copy()
            df_temp['Valor'] = range(len(df_temp))
            return crear_grafico_baston(df_temp, variable)
    elif tipo == "3. Histograma con Polígono":
        return crear_histograma_poligono(variable, datos_raw, n_bins)
    elif tipo == "4. Gráfico Ogiva":
        return crear_ogiva(variable, datos_raw, n_bins)
    else:
        return crear_grafico_torta(df_freq, variable, es_cualitativa)

def main():
    st.title("🏋️ Dashboard de Control Nutricional")
    st.markdown("*Análisis de pacientes en programa de nutrición*")
    st.divider()

    st.header("📂 Carga tu archivo de datos")
    uploaded_file = st.file_uploader("Sube un archivo CSV con los datos", type=['csv'])

    if uploaded_file is None:
        return

    try:
        with st.spinner("⏳ Cargando archivo..."):
            df = pd.read_csv(uploaded_file)
        st.success("✅ Archivo cargado correctamente!")
        st.divider()

        with st.expander("📋 Vista previa del dataset", expanded=True):
            c1, c2 = st.columns(2)
            c1.metric("Registros", len(df))
            c2.metric("Columnas", len(df.columns))
            st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.header("📊 Análisis de Variables")

        tab1, tab2 = st.tabs(["Variables Cualitativas", "Variables Cuantitativas"])

        with tab1:
            vars_cual = df.select_dtypes(include=['object']).columns.tolist()
            if not vars_cual:
                st.warning("⚠️ No se encontraron variables cualitativas.")
            else:
                variable = st.selectbox("Selecciona una variable cualitativa:", vars_cual, key="cual_select")
                df_freq = calcular_frecuencia_cualitativa(df[variable])
                
                st.subheader("📋 Tabla de Frecuencias")
                st.dataframe(df_freq, use_container_width=True, hide_index=True)

                st.subheader("📈 Selecciona el tipo de gráfico")
                tipo = st.radio("Elige una de las 5 visualizaciones:", 
                    ["1. Gráfico de Barras", "2. Gráfico de Bastón", "3. Histograma con Polígono", "4. Gráfico Ogiva", "5. Gráfico de Torta"],
                    key="cual_radio"
                )
                
                datos_para_grafico = df[variable].dropna() if tipo in ["3. Histograma con Polígono", "4. Gráfico Ogiva"] else None
                st.pyplot(renderizar_grafico(tipo, df_freq, variable, datos_para_grafico, len(df_freq), True))

        with tab2:
            vars_cuant = df.select_dtypes(include=[np.number]).columns.tolist()
            if not vars_cuant:
                st.warning("⚠️ No se encontraron variables cuantitativas.")
            else:
                variable = st.selectbox("Selecciona una variable cuantitativa:", vars_cuant, key="cuant_select")
                
                st.subheader("📈 Selecciona el tipo de gráfico")
                tipo = st.radio("Elige una de las 5 visualizaciones:", 
                    ["1. Gráfico de Barras", "2. Gráfico de Bastón", "3. Histograma con Polígono", "4. Gráfico Ogiva", "5. Gráfico de Torta"],
                    key="cuant_radio"
                )

                if tipo in ["1. Gráfico de Barras", "5. Gráfico de Torta"]:
                    df_freq = calcular_frecuencia_cuantitativa(df[variable], agrupar=False)
                    st.subheader("📋 Tabla de Frecuencias")
                    st.dataframe(df_freq, use_container_width=True, hide_index=True)
                    st.pyplot(renderizar_grafico(tipo, df_freq, variable, None, 0, False))

                elif tipo == "2. Gráfico de Bastón":
                    df_freq = calcular_frecuencia_cuantitativa(df[variable], agrupar=False)
                    st.subheader("📋 Tabla de Frecuencias")
                    st.dataframe(df_freq, use_container_width=True, hide_index=True)
                    st.pyplot(renderizar_grafico(tipo, df_freq, variable, None, 0, False))

                else:
                    n_bins = st.slider("Número de intervalos:", 3, 15, 5, key="bins_slider")
                    df_freq = calcular_frecuencia_cuantitativa(df[variable], agrupar=True, n_intervalos=n_bins)
                    st.subheader("📋 Tabla de Frecuencias Agrupadas")
                    st.dataframe(df_freq, use_container_width=True, hide_index=True)
                    st.pyplot(renderizar_grafico(tipo, df_freq, variable, df[variable].dropna(), n_bins, False))

                with st.expander("📐 Estadísticas descriptivas"):
                    stats = df[variable].describe()
                    labels = {
                        'count': 'Total de registros', 'mean': 'Promedio (Media)', 'std': 'Desviación Estándar',
                        'min': 'Valor Mínimo', '25%': 'Primer Cuartil (25%)', '50%': 'Mediana (50%)',
                        '75%': 'Tercer Cuartil (75%)', 'max': 'Valor Máximo'
                    }
                    
                    formatted = []
                    for k in labels.keys():
                        val = stats.get(k)
                        if isinstance(val, (int, float)):
                            formatted.append(f"{int(val)}" if val == int(val) else f"{val:.2f}")
                        else:
                            formatted.append(val)
                    
                    st.dataframe(pd.DataFrame({variable.title(): formatted}, index=list(labels.values())), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")

if __name__ == "__main__":
    main()