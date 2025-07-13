import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Diagnóstico Financiero y de Crédito ",
    page_icon="💡",
    layout="wide"
)

# --- Título y Descripción ---
st.title('💡 Diagnóstico Financiero 2-en-1')
st.markdown("""
Esta herramienta te ayuda en dos pasos:
1.  **Diagnóstico de Estilo de Vida:** ¿Gastas más de lo que ganas actualmente?
2.  **Análisis de Crédito:** ¿Puedes pagar el préstamo que quieres y cuáles son los riesgos reales?
""")

# --- Barra Lateral para Entradas del Usuario ---
st.sidebar.header('Paso 1: Tus Finanzas')

# --- INGRESOS ---
with st.sidebar.expander("💰 Ingresos", expanded=True):
    st.markdown("Ingresa aquí tu **sueldo mensual neto**, después de impuestos.")
    ingreso_mensual = st.number_input('Ingreso Mensual Neto (MXN)', min_value=0.0, step=500.0, label_visibility="collapsed")

# --- GASTOS FIJOS ---
with st.sidebar.expander("🏠 Gastos Fijos", expanded=True):
    st.markdown("Son los gastos que **no cambian** mes a mes: Renta, hipoteca, servicios, colegiaturas, etc.")
    gastos_fijos = st.number_input('Suma total de gastos fijos (MXN)', min_value=0.0, step=100.0, label_visibility="collapsed")

# --- GASTOS VARIABLES ---
with st.sidebar.expander("🌮 Gastos Variables", expanded=True):
    st.markdown("Un **estimado** de gastos que varían: Comida, transporte, entretenimiento, compras, etc.")
    gastos_variables = st.number_input('Estimado de gastos variables (MXN)', min_value=0.0, step=100.0, label_visibility="collapsed")

# --- SIMULACIÓN DE CRÉDITO ---
st.sidebar.header("Paso 2: Simula un Crédito")
with st.sidebar.expander("💸 Datos del Préstamo", expanded=True):
    monto_prestamo = st.number_input('Monto del préstamo (MXN)', min_value=0.0, step=1000.0)
    plazo_meses = st.number_input('Plazo para pagar (meses)', min_value=1, step=1)
    tasa_anual = st.slider('Tasa de Interés Anual (%)', min_value=0.0, max_value=120.0, value=35.0, step=0.5)

# --- ====================================================================== ---
# --- =================== PANEL PRINCIPAL DE ANÁLISIS ====================== ---
# --- ====================================================================== ---
st.markdown('---')

if ingreso_mensual <= 0:
    st.info('Ingresa tus finanzas en la barra lateral para iniciar el diagnóstico.')
else:
    # --- ETAPA 1: DIAGNÓSTICO DE ESTILO DE VIDA ---
    st.header("Diagnóstico 1: Tu Estilo de Vida Actual")
    total_gastos = gastos_fijos + gastos_variables
    flujo_libre = ingreso_mensual - total_gastos

    col1, col2 = st.columns([2, 1]) # Columnas para el texto y el gráfico

    with col1:
        if flujo_libre >= 0:
            st.success(f"**¡Felicidades! Vives dentro de tus posibilidades.** ✅")
            st.markdown(f"Actualmente, después de todos tus gastos, te sobran **${flujo_libre:,.2f}** cada mes. Tienes una base financiera saludable.")
        else:
            st.error(f"**¡Alerta! Estás gastando más de lo que ganas.** ❌")
            st.markdown(f"Actualmente, tienes un déficit de **${abs(flujo_libre):,.2f}** cada mes. Esto significa que ya estás acumulando deudas o agotando tus ahorros. **Es crucial corregir esto antes de considerar un nuevo crédito.**")
    
    with col2:
        if total_gastos > 0:
            # Gráfico de pastel para breakdown de gastos
            labels = ['Gastos Fijos', 'Gastos Variables']
            values = [gastos_fijos, gastos_variables]
            pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, textinfo='percent+label', marker_colors=['#FF6347', '#FFD700'])])
            pie_fig.update_layout(title_text='Distribución de tus Gastos', showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(pie_fig, use_container_width=True)

    # --- ETAPA 2: ANÁLISIS DE VIABILIDAD DEL CRÉDITO ---
    if monto_prestamo > 0:
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

        # Mensaje de advertencia si ya hay déficit
        if flujo_libre < 0:
            st.warning("**ADVERTENCIA IMPORTANTE:** Estás analizando un crédito cuando tu situación actual ya es de déficit. Añadir una nueva deuda es extremadamente riesgoso.")

        st.metric('Pago Mensual del Crédito', f"${pago_mensual_credito:,.2f}")

        # VEREDICTO FINAL DEL CRÉDITO
        if flujo_final_con_credito >= 0:
            st.success(f"**Veredicto del Crédito: VIABLE.** 👍")
            st.markdown(f"Aún después de pagar la mensualidad, te quedarían **${flujo_final_con_credito:,.2f}**. Puedes asumir esta deuda.")
        else:
            deficit_total_mensual = abs(flujo_final_con_credito)
            st.error(f"**Veredicto del Crédito: NO VIABLE.** 👎")
            st.markdown(f"Si tomas este crédito, tu déficit mensual total sería de **${deficit_total_mensual:,.2f}**.")
            
            st.info(f"Para poder pagar este crédito, necesitarías **aumentar tu ingreso mensual en ${deficit_total_mensual:,.2f}** o reducir tus gastos en la misma cantidad.")
            
            # --- SECCIÓN DE PROYECCIÓN DE DEUDA MEJORADA ---
            st.subheader("⚠️ Proyección de Deuda Corregida (Más Realista)")
            st.markdown("Así es como tu deuda crecería, considerando que después de que termina el plazo del crédito, tu déficit mensual cambia.")

            años_proj = [1, 2, 3, 5, 10, 20]
            deuda_proyectada = []
            deuda_actual = 0
            deficit_estructural = abs(min(0, flujo_libre)) # El déficit que tienes sin el crédito

            for mes_actual in range(1, max(años_proj) * 12 + 1):
                # Determinar el déficit a sumar este mes
                if mes_actual <= plazo_meses:
                    deficit_a_sumar = deficit_total_mensual
                else:
                    # Después del plazo del crédito, solo se suma el déficit estructural (si existe)
                    deficit_a_sumar = deficit_estructural
                
                deuda_actual += deficit_a_sumar
                deuda_actual *= (1 + tasa_mensual)

                if mes_actual % 12 == 0:
                    año = mes_actual // 12
                    if año in años_proj:
                        deuda_proyectada.append((f"{año} año(s)", f"${deuda_actual:,.2f}"))

            df_proyeccion = pd.DataFrame(deuda_proyectada, columns=['Tiempo', 'Deuda Acumulada (con interés)'])
            st.table(df_proyeccion)
            st.caption("Nota: Esta proyección es más precisa pero aún no incluye cargos por falta de pago o penalizaciones.")

            # --- GRÁFICA MEJORADA ---
            st.subheader("Gráfica de Ganancias vs. Pérdidas")
            meses_grafica = list(range(int(plazo_meses) + 1))
            saldo_acumulado = [flujo_final_con_credito * mes for mes in meses_grafica]
            
            fig = go.Figure()
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.add_trace(go.Scatter(x=meses_grafica, y=[min(0, s) for s in saldo_acumulado], fill='tozeroy', mode='lines', line_color='rgba(255,0,0,0.7)', fillcolor='rgba(255,0,0,0.2)', name='Deuda'))
            fig.add_trace(go.Scatter(x=meses_grafica, y=[max(0, s) for s in saldo_acumulado], fill='tozeroy', mode='lines', line_color='rgba(0,128,0,0.7)', fillcolor='rgba(0,128,0,0.2)', name='Ahorro'))

            fig.update_layout(title_text='Evolución de tu Balance Acumulado (Ahorro vs. Deuda)', xaxis_title='Mes', yaxis_title='Balance (MXN)', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            # --- EXPANSORES DE CONSECUENCIAS ---
            with st.expander("El Factor Oculto: La Inflación"):
                st.markdown("La tabla es alarmante, pero la realidad es peor por la **inflación**. Cada año, tu dinero compra menos, lo que significa que tus gastos subirán y tu déficit real será mayor.")
            
            with st.expander("⚖️ Consecuencias Legales y Reales en México por No Pagar"):
                st.markdown("""
                Si dejas de pagar un crédito formal, las consecuencias son serias:
                - **Buró de Crédito:** Tu historial crediticio se destruye por años.
                - **Cobranza Extrajudicial:** Acoso telefónico de despachos de cobranza.
                - **Juicio Mercantil y Embargo:** Un juez puede ordenar el embargo de bienes (coche, casa, un porcentaje de tu sueldo) para pagar la deuda.
                - **¿Cárcel? NO.** El Artículo 17 de la Constitución prohíbe la prisión por deudas de carácter civil. No dejes que te intimiden con esa amenaza.
                """)