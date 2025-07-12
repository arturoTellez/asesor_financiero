import streamlit as st
import pandas as pd
import numpy_financial as npf
import plotly.express as px

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Analizador de Gastos y Créditos",
    page_icon="🇲🇽",
    layout="wide"
)

# --- Título y Descripción ---
st.title('📊 Analizador de Gastos y Créditos')
st.markdown("""
Esta herramienta te ayuda a entender tu situación financiera mensual y a determinar si puedes pagar un crédito. 
**Sigue estos 3 pasos:**
1.  **Ingresa tus finanzas** en la barra lateral izquierda.
2.  **Activa la simulación de crédito** si quieres evaluar un préstamo.
3.  **Revisa tu diagnóstico** y la gráfica de proyección.
""")

# --- Barra Lateral para Entradas del Usuario ---
st.sidebar.header('Paso 1: Ingresa tus Finanzas')

ingreso_mensual = st.sidebar.number_input(
    '💰 Tu Ingreso Mensual Neto (MXN)',
    min_value=0.0,
    step=500.0,
    help='Ingresa el dinero que recibes al mes después de impuestos.'
)

st.sidebar.markdown('---')
st.sidebar.header('Paso 2: Registra tus Gastos')
gastos_fijos = st.sidebar.number_input(
    '🏠 Gastos Fijos Mensuales (MXN)',
    min_value=0.0,
    step=100.0,
    help='Suma de todos tus gastos que no cambian mes a mes: renta, hipoteca, servicios (luz, agua, gas), internet, colegiaturas, etc.'
)

gastos_variables = st.sidebar.number_input(
    '🌮 Gastos Variables Mensuales (MXN)',
    min_value=0.0,
    step=100.0,
    help='Un estimado de lo que gastas en promedio en cosas que varían: comida, transporte, entretenimiento, compras, etc.'
)

# --- Sección de Simulación de Crédito ---
st.sidebar.markdown('---')
st.sidebar.header('Paso 3: Simulación de Crédito (Opcional)')
simular_credito = st.sidebar.checkbox('Quiero simular un crédito')

monto_prestamo = 0.0
plazo_meses = 0
tasa_anual = 0.0
pago_mensual_credito = 0.0

if simular_credito:
    monto_prestamo = st.sidebar.number_input(
        '💸 Monto del préstamo que necesitas (MXN)',
        min_value=0.0,
        step=1000.0
    )
    plazo_meses = st.sidebar.number_input(
        '🗓️ Plazo para pagar (en meses)',
        min_value=1,
        step=1
    )
    tasa_anual = st.sidebar.slider(
        '📈 Tasa de Interés Anual (%)',
        min_value=0.0,
        max_value=100.0,
        value=25.0, # Un valor común para empezar
        step=0.5
    )

# --- Panel Principal: Cálculos y Resultados ---
st.markdown('---')
st.header('Diagnóstico Financiero 🧐')

if ingreso_mensual > 0:
    # --- Cálculos Financieros ---
    total_gastos = gastos_fijos + gastos_variables
    flujo_libre = ingreso_mensual - total_gastos

    if simular_credito and monto_prestamo > 0:
        if tasa_anual > 0:
            # Usamos la función PMT de numpy_financial para calcular el pago mensual
            tasa_mensual = tasa_anual / 100 / 12
            pago_mensual_credito = -npf.pmt(tasa_mensual, plazo_meses, monto_prestamo)
        else:
            # Crédito sin intereses
            pago_mensual_credito = monto_prestamo / plazo_meses if plazo_meses > 0 else 0
    
    flujo_final = flujo_libre - pago_mensual_credito

    # --- Presentación de Resultados ---
    st.subheader('Resumen Mensual Actual')
    col1, col2, col3 = st.columns(3)
    col1.metric('🟢 Ingreso', f"${ingreso_mensual:,.2f}")
    col2.metric('🔴 Gastos Totales', f"${total_gastos:,.2f}")
    col3.metric('🔵 Flujo Libre', f"${flujo_libre:,.2f}", 
                help='Este es el dinero que te queda después de tus gastos fijos y variables, antes de considerar el crédito.')

    if simular_credito and monto_prestamo > 0:
        st.markdown('---')
        st.subheader('Análisis del Crédito Solicitado')

        col_credito1, col_credito2 = st.columns(2)
        col_credito1.metric('💳 Pago Mensual del Crédito', f"${pago_mensual_credito:,.2f}")
        col_credito2.metric('💰 Flujo Libre Final', f"${flujo_final:,.2f}", delta=f"{flujo_final - flujo_libre:,.2f}",
                            help='Este es el dinero que te quedaría cada mes DESPUÉS de pagar el crédito.')

        # --- Veredicto ---
        if flujo_final >= 0:
            st.success(f"**¡Sí puedes pagarlo!** Después de cubrir todos tus gastos y el pago mensual del crédito, aún te quedarían **${flujo_final:,.2f}** cada mes. ¡Felicidades por tu buena administración! ✅")
        else:
            st.error(f"**¡Cuidado! No podrías pagarlo.** El pago del crédito supera tu capacidad de ahorro por **${abs(flujo_final):,.2f}** cada mes. Adquirir esta deuda te dejaría con un déficit mensual. ❌")
        
        # --- Gráfica de Proyección ---
        st.subheader('Proyección de tu Dinero Durante el Plazo del Crédito')
        
        # Crear un DataFrame para la gráfica
        meses = range(int(plazo_meses) + 1)
        saldo_acumulado = [flujo_final * mes for mes in meses]
        
        df_proyeccion = pd.DataFrame({
            'Mes': meses,
            'Saldo Acumulado': saldo_acumulado
        })

        # Generar la gráfica con Plotly
        fig = px.line(
            df_proyeccion, 
            x='Mes', 
            y='Saldo Acumulado', 
            title='Evolución de tu saldo mes a mes (considerando el crédito)',
            markers=True,
            labels={'Saldo Acumulado': 'Saldo Acumulado (MXN)'}
        )
        
        # Línea de referencia en cero
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        
        # Cambiar el color de la línea según el resultado
        line_color = "green" if flujo_final >= 0 else "red"
        fig.update_traces(line_color=line_color)

        st.plotly_chart(fig, use_container_width=True)
        st.info("Esta gráfica muestra cómo se acumularía tu dinero (o tu deuda) a lo largo del tiempo si mantienes los mismos ingresos y gastos cada mes mientras pagas el crédito.")

else:
    st.info('Ingresa tu sueldo en la barra de la izquierda para empezar el análisis.')

st.markdown("---")
st.write("Creado como una herramienta de simulación. Las condiciones reales de un crédito pueden variar. Siempre consulta con tu institución financiera.")