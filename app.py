import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Diagnóstico Financiero y de Crédito",
    page_icon="💡",
    layout="wide"
)

# --- INICIALIZACIÓN DEL ESTADO DE SESIÓN ---
if 'lifestyle_calculated' not in st.session_state:
    st.session_state.lifestyle_calculated = False
if 'credit_calculated' not in st.session_state:
    st.session_state.credit_calculated = False

# --- Título y Descripción ---
st.title('💡 Diagnóstico Financiero 2-en-1')
st.markdown("Sigue los pasos para ingresar tus datos y presiona los botones para analizar tu situación.")

# --- ====================================================================== ---
# --- =============== SECCIÓN DE ENTRADA DE DATOS (NUEVO ORDEN) ============ ---
# --- ====================================================================== ---

# --- ETAPA 1: INGRESOS Y GASTOS ---
st.header("Paso 1: Tu Estilo de Vida Actual")
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("💰 Ingresos")
    st.markdown("Tu sueldo mensual neto, después de impuestos.")
    ingreso_mensual = st.number_input('Ingreso Mensual Neto (MXN)', min_value=0.0, step=500.0, label_visibility="collapsed")

with col2:
    st.subheader("🏠 Gastos")
    st.markdown("Suma de gastos **fijos** y **variables**.")
    gastos_fijos = st.number_input('Gastos Fijos (MXN)', min_value=0.0, step=100.0)
    gastos_variables = st.number_input('Gastos Variables (MXN)', min_value=0.0, step=100.0)

# --- ETAPA 2: DATOS DEL CRÉDITO ---
st.header("Paso 2: Simula un Crédito (Opcional)")
st.markdown("Ingresa los datos del préstamo que quieres solicitar para analizar su viabilidad.")
credit_cols = st.columns(3) # Columnas para los datos del crédito

with credit_cols[0]:
    monto_prestamo = st.number_input('Monto del préstamo (MXN)', min_value=0.0, step=1000.0)
with credit_cols[1]:
    plazo_meses = st.number_input('Plazo para pagar (meses)', min_value=1, step=1)
with credit_cols[2]:
    tasa_anual = st.slider('Tasa de Interés Anual (%)', min_value=0.0, max_value=120.0, value=35.0, step=0.5)

# --- ====================================================================== ---
# --- =================== SECCIÓN DE ANÁLISIS (CON BOTONES) ================ ---
# --- ====================================================================== ---
st.markdown('---')

if ingreso_mensual <= 0:
    st.info('Ingresa tu ingreso mensual para poder iniciar el diagnóstico.')
else:
    # --- CÁLCULOS BASE ---
    total_gastos = gastos_fijos + gastos_variables
    flujo_libre = ingreso_mensual - total_gastos

    # --- BOTÓN PARA ETAPA 1 ---
    if st.button('1. Analizar mi Estilo de Vida', use_container_width=True):
        st.session_state.lifestyle_calculated = True
        st.session_state.credit_calculated = False 

    # --- VISUALIZACIÓN ETAPA 1 ---
    if st.session_state.lifestyle_calculated:
        st.header("Diagnóstico 1: Tu Estilo de Vida Actual")
        
        diag_col1, diag_col2 = st.columns([2, 1])

        with diag_col1:
            if flujo_libre >= 0:
                st.success(f"**¡Felicidades! Vives dentro de tus posibilidades.** ✅")
                st.markdown(f"Actualmente, te sobran **${flujo_libre:,.2f}** cada mes.")
            else:
                st.error(f"**¡Alerta! Estás gastando más de lo que ganas.** ❌")
                st.markdown(f"Actualmente, tienes un déficit de **${abs(flujo_libre):,.2f}** cada mes.")
        
        with diag_col2:
            if total_gastos > 0:
                labels = ['Gastos Fijos', 'Gastos Variables']
                values = [gastos_fijos, gastos_variables]
                pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, textinfo='percent', marker_colors=['#FF6347', '#FFD700'])])
                pie_fig.update_layout(title_text='Distribución de Gastos', showlegend=True, margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(pie_fig, use_container_width=True)
        
        # --- BOTÓN PARA ETAPA 2 ---
        if monto_prestamo > 0:
            if st.button('2. Analizar Viabilidad del Crédito', use_container_width=True):
                st.session_state.credit_calculated = True

    # --- VISUALIZACIÓN ETAPA 2 ---
    if st.session_state.credit_calculated and monto_prestamo > 0:
        st.markdown("---")
        st.header("Diagnóstico 2: Análisis de Viabilidad del Crédito")

        pago_mensual_credito = 0.0
        tasa_mensual = (tasa_anual / 100) / 12

        if plazo_meses > 0:
            if tasa_anual > 0:
                numerador = tasa_mensual * ((1 + tasa_mensual) ** plazo_meses)
                denominador = ((1 + tasa_mensual) ** plazo_meses) - 1
                if denominador > 0: pago_mensual_credito = monto_prestamo * (numerador / denominador)
                else: pago_mensual_credito = monto_prestamo / plazo_meses
            else: pago_mensual_credito = monto_prestamo / plazo_meses

        flujo_final_con_credito = flujo_libre - pago_mensual_credito

        if flujo_libre < 0:
            st.warning("**ADVERTENCIA:** Ya tienes un déficit. Añadir un crédito es extremadamente riesgoso.")

        st.metric('Pago Mensual del Crédito', f"${pago_mensual_credito:,.2f}")

        if flujo_final_con_credito >= 0:
            st.success(f"**Veredicto del Crédito: VIABLE.** 👍")
            st.markdown(f"Aún después de pagar la mensualidad, te quedarían **${flujo_final_con_credito:,.2f}**.")
        else:
            deficit_total_mensual = abs(flujo_final_con_credito)
            st.error(f"**Veredicto del Crédito: NO VIABLE.** 👎")
            st.markdown(f"Si tomas este crédito, tu déficit mensual total sería de **${deficit_total_mensual:,.2f}**.")
            
            st.info(f"Para poder pagar este crédito, necesitarías **aumentar tu ingreso en ${deficit_total_mensual:,.2f}** o reducir tus gastos.")
            
            # (El resto del código para las proyecciones y explicaciones permanece igual)
            st.subheader("⚠️ Proyección de Deuda Realista")
            st.markdown("Así crecería tu deuda, considerando que el déficit cambia al terminar el plazo del crédito:")

            años_proj = [1, 2, 3, 5, 10, 20]
            deuda_proyectada = []
            deuda_actual = 0
            deficit_estructural = abs(min(0, flujo_libre))

            for mes_actual in range(1, max(años_proj) * 12 + 1):
                if mes_actual <= plazo_meses:
                    deficit_a_sumar = deficit_total_mensual
                else:
                    deficit_a_sumar = deficit_estructural
                
                deuda_actual += deficit_a_sumar
                deuda_actual *= (1 + tasa_mensual)

                if mes_actual % 12 == 0:
                    año = mes_actual // 12
                    if año in años_proj:
                        deuda_proyectada.append((f"{año} año(s)", f"${deuda_actual:,.2f}"))

            df_proyeccion = pd.DataFrame(deuda_proyectada, columns=['Tiempo', 'Deuda Acumulada'])
            st.table(df_proyeccion)
            st.caption("Nota: No incluye cargos por falta de pago o penalizaciones.")

            st.subheader("Gráfica de Ganancias vs. Pérdidas")
            meses_grafica = list(range(int(plazo_meses) + 1))
            saldo_acumulado = [flujo_final_con_credito * mes for mes in meses_grafica]
            
            fig = go.Figure()
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.add_trace(go.Scatter(x=meses_grafica, y=[min(0, s) for s in saldo_acumulado], fill='tozeroy', mode='lines', line_color='rgba(255,0,0,0.7)', fillcolor='rgba(255,0,0,0.2)', name='Deuda'))
            fig.add_trace(go.Scatter(x=meses_grafica, y=[max(0, s) for s in saldo_acumulado], fill='tozeroy', mode='lines', line_color='rgba(0,128,0,0.7)', fillcolor='rgba(0,128,0,0.2)', name='Ahorro'))
            fig.update_layout(title_text='Evolución de tu Balance (Ahorro vs. Deuda)', xaxis_title='Mes', yaxis_title='Balance (MXN)')
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("El Factor Oculto: La Inflación"):
                st.markdown("La realidad es peor por la **inflación**. Cada año, tu dinero compra menos, tus gastos subirán y tu déficit real será mayor.")
            
            with st.expander("⚖️ Consecuencias Legales y Reales en México por No Pagar"):
                st.markdown("""
                Si dejas de pagar un crédito formal, las consecuencias son serias:
                - **Buró de Crédito:** Tu historial crediticio se destruye.
                - **Cobranza Extrajudicial:** Acoso telefónico.
                - **Juicio y Embargo:** Un juez puede ordenar el embargo de bienes.
                - **¿Cárcel? NO.** El Art. 17 de la Constitución prohíbe la prisión por deudas civiles.
                """)