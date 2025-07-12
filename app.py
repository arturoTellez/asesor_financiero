import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de la Página ---
st.set_page_config(
    page_title="¿Te Conviene el Crédito?",
    page_icon="🤔",
    layout="wide"
)

# --- Título y Descripción ---
st.title('🤔 Analizador de Viabilidad de Créditos')
st.markdown("""
¿Estás pensando en pedir un préstamo? Esta herramienta te ayuda a saber si realmente puedes pagarlo. 
**Es simple:** ingresa tus finanzas y descubre si el crédito es una buena idea para ti o qué necesitas para que lo sea.
""")

# --- Barra Lateral para Entradas del Usuario ---
st.sidebar.header('Cuéntame de tus Finanzas')

# --- INGRESOS ---
with st.sidebar.expander("💰 Ingresos", expanded=True):
    st.markdown("""
    Ingresa aquí tu **sueldo mensual neto**, es decir, lo que recibes en tu cuenta después de impuestos y deducciones.
    """)
    ingreso_mensual = st.number_input(
        'Ingreso Mensual Neto (MXN)',
        min_value=0.0,
        step=500.0,
        label_visibility="collapsed"
    )

# --- GASTOS FIJOS ---
with st.sidebar.expander("🏠 Gastos Fijos", expanded=True):
    st.markdown("""
    Son los gastos que **no cambian** mes a mes.
    - Renta o hipoteca
    - Servicios (luz, agua, gas, internet)
    - Colegiaturas
    - Seguros
    - Pagos de otras deudas
    """)
    gastos_fijos = st.number_input(
        'Suma total de gastos fijos (MXN)',
        min_value=0.0,
        step=100.0,
        label_visibility="collapsed"
    )

# --- GASTOS VARIABLES ---
with st.sidebar.expander("🌮 Gastos Variables", expanded=True):
    st.markdown("""
    Un **estimado** de lo que gastas en cosas que varían.
    - Comida y supermercado
    - Transporte (gasolina, transporte público)
    - Entretenimiento (cine, salidas)
    - Compras y "gustitos"
    """)
    gastos_variables = st.number_input(
        'Estimado de gastos variables (MXN)',
        min_value=0.0,
        step=100.0,
        label_visibility="collapsed"
    )

# --- SIMULACIÓN DE CRÉDITO ---
st.sidebar.markdown("---")
with st.sidebar.expander("💸 Simulación de Crédito", expanded=True):
    st.markdown("Ingresa los datos del préstamo que quieres solicitar.")
    monto_prestamo = st.number_input(
        'Monto del préstamo (MXN)',
        min_value=0.0,
        step=1000.0
    )
    plazo_meses = st.number_input(
        'Plazo para pagar (meses)',
        min_value=1,
        step=1
    )
    tasa_anual = st.slider(
        'Tasa de Interés Anual (%)',
        min_value=0.0,
        max_value=120.0, # Aumentado para cubrir tasas de microcréditos
        value=35.0,
        step=0.5
    )

# --- Panel Principal: Cálculos y Resultados ---
st.markdown('---')
st.header('Diagnóstico Financiero 🧐')

# Solo proceder si hay datos de entrada
if ingreso_mensual > 0 and monto_prestamo > 0:
    total_gastos = gastos_fijos + gastos_variables
    flujo_libre = ingreso_mensual - total_gastos
    pago_mensual_credito = 0.0

    # --- Cálculo de la mensualidad del crédito ---
    if plazo_meses > 0:
        if tasa_anual > 0:
            tasa_mensual = (tasa_anual / 100) / 12
            numerador = tasa_mensual * ((1 + tasa_mensual) ** plazo_meses)
            denominador = ((1 + tasa_mensual) ** plazo_meses) - 1
            if denominador > 0:
                pago_mensual_credito = monto_prestamo * (numerador / denominador)
            else:
                 pago_mensual_credito = monto_prestamo / plazo_meses
        else:
            pago_mensual_credito = monto_prestamo / plazo_meses

    flujo_final = flujo_libre - pago_mensual_credito

    # --- Presentación de Resultados ---
    st.subheader('Tu Situación Actual vs. con el Crédito')
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            'Dinero que te sobra al mes (actual)',
            f"${flujo_libre:,.2f}",
            help='Esto es lo que te queda después de todos tus gastos, antes del nuevo crédito.'
        )
    with col2:
        st.metric(
            'Pago mensual del crédito',
            f"${pago_mensual_credito:,.2f}"
        )

    st.markdown("---")
    st.subheader("Veredicto: ¿Te conviene tomar este crédito?")

    # --- VEREDICTO POSITIVO ---
    if flujo_final >= 0:
        st.success(f"**¡Sí, es viable!** ✅")
        st.markdown(f"Después de pagar la mensualidad del crédito, **aún te quedarían ${flujo_final:,.2f} cada mes.** Tienes la capacidad financiera para asumir esta deuda sin problemas. ¡Procede con confianza pero siempre con responsabilidad!")
    
    # --- VEREDICTO NEGATIVO ---
    else:
        deficit_mensual = abs(flujo_final)
        st.error(f"**No, no es viable en este momento.** ❌")
        st.markdown(f"Si tomas este crédito, **te faltarían ${deficit_mensual:,.2f} cada mes** para cubrir todos tus gastos. Esto te llevaría a endeudarte cada vez más.")

        st.warning(f"""
        #### 💡 Recomendación Práctica:
        Para poder pagar este crédito sin problemas, necesitarías **aumentar tu ingreso mensual neto en por lo menos ${deficit_mensual:,.2f}**.
        """)

        st.subheader("⚠️ El Peligro de la Deuda: Proyección a Largo Plazo")
        st.markdown("Si tomaras el crédito y no aumentaras tus ingresos, esto es lo que pasaría con tu deuda a lo largo del tiempo (sin contar intereses sobre la nueva deuda):")

        años = [1, 2, 3, 5, 10, 20]
        deuda_proyectada = [deficit_mensual * 12 * año for año in años]
        
        df_proyeccion = pd.DataFrame({
            'Tiempo': [f"{año} año(s)" for año in años],
            'Deuda Acumulada': deuda_proyectada
        })

        # Formatear la columna de deuda para que se vea como moneda
        df_proyeccion['Deuda Acumulada'] = df_proyeccion['Deuda Acumulada'].apply(lambda x: f"${x:,.2f}")
        
        st.table(df_proyeccion.style.set_properties(**{'text-align': 'left'}).set_table_styles([dict(selector='th', props=[('text-align', 'left')])]))
        
        # Gráfica de la proyección negativa
        st.markdown("Así se vería tu balance mes a mes durante el plazo del crédito:")
        meses_grafica = range(int(plazo_meses) + 1)
        saldo_acumulado_grafica = [flujo_final * mes for mes in meses_grafica]
        
        df_grafica = pd.DataFrame({
            'Mes': meses_grafica,
            'Balance Acumulado (MXN)': saldo_acumulado_grafica
        })
        
        fig = px.line(
            df_grafica, 
            x='Mes', 
            y='Balance Acumulado (MXN)',
            title='Evolución de tu dinero mes a mes (con el crédito)',
            markers=True
        )
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_traces(line_color="red")
        st.plotly_chart(fig, use_container_width=True)


else:
    st.info('Por favor, ingresa tu ingreso y los datos del préstamo para ver tu diagnóstico.')

st.markdown("---")
st.write("Esta es una herramienta de simulación. Las condiciones reales de un crédito pueden variar. Úsala como una guía para tomar mejores decisiones financieras.")