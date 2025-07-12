import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="¿Te Conviene el Crédito?",
    page_icon="⚖️",
    layout="wide"
)

# --- Título y Descripción ---
st.title('⚖️ Analizador de Viabilidad de Créditos')
st.markdown("""
¿Estás pensando en pedir un préstamo? Esta herramienta te ayuda a saber si realmente puedes pagarlo. 
**Es simple:** ingresa tus finanzas y descubre si el crédito es una buena idea para ti o qué necesitas para que lo sea.
""")

# --- Barra Lateral para Entradas del Usuario ---
st.sidebar.header('Cuéntame de tus Finanzas')

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
st.sidebar.markdown("---")
with st.sidebar.expander("💸 Simulación de Crédito", expanded=True):
    st.markdown("Ingresa los datos del préstamo que quieres solicitar.")
    monto_prestamo = st.number_input('Monto del préstamo (MXN)', min_value=0.0, step=1000.0)
    plazo_meses = st.number_input('Plazo para pagar (meses)', min_value=1, step=1)
    tasa_anual = st.slider('Tasa de Interés Anual (%)', min_value=0.0, max_value=120.0, value=35.0, step=0.5)

# --- Panel Principal: Cálculos y Resultados ---
st.markdown('---')
st.header('Diagnóstico Financiero 🧐')

if ingreso_mensual > 0 and monto_prestamo > 0:
    total_gastos = gastos_fijos + gastos_variables
    flujo_libre = ingreso_mensual - total_gastos
    pago_mensual_credito = 0.0
    tasa_mensual = (tasa_anual / 100) / 12

    if plazo_meses > 0:
        if tasa_anual > 0:
            numerador = tasa_mensual * ((1 + tasa_mensual) ** plazo_meses)
            denominador = ((1 + tasa_mensual) ** plazo_meses) - 1
            if denominador > 0:
                pago_mensual_credito = monto_prestamo * (numerador / denominador)
            else:
                 pago_mensual_credito = monto_prestamo / plazo_meses
        else:
            pago_mensual_credito = monto_prestamo / plazo_meses

    flujo_final = flujo_libre - pago_mensual_credito

    st.subheader("Veredicto: ¿Te conviene tomar este crédito?")

    # --- VEREDICTO POSITIVO ---
    if flujo_final >= 0:
        st.success(f"**¡Sí, es viable!** ✅")
        st.markdown(f"""
        Después de pagar la mensualidad de **${pago_mensual_credito:,.2f}**, aún **te quedarían ${flujo_final:,.2f} cada mes.** Tienes la capacidad financiera para asumir esta deuda. ¡Procede con responsabilidad!
        """)
        # Gráfica de proyección POSITIVA
        st.markdown("Así se vería la acumulación de tu ahorro mes a mes durante el plazo del crédito:")
        meses_grafica = range(int(plazo_meses) + 1)
        saldo_acumulado_grafica = [flujo_final * mes for mes in meses_grafica]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(meses_grafica), y=saldo_acumulado_grafica, fill='tozeroy', mode='lines', line_color='green', name='Ahorro'))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(title='Evolución de tu Ahorro Acumulado', xaxis_title='Mes', yaxis_title='Balance (MXN)')
        st.plotly_chart(fig, use_container_width=True)

    # --- VEREDICTO NEGATIVO ---
    else:
        deficit_mensual = abs(flujo_final)
        st.error(f"**No, no es viable en este momento.** ❌")
        st.markdown(f"""
        Si tomas este crédito, **te faltarían ${deficit_mensual:,.2f} cada mes** para cubrir tus gastos. 
        Esto te llevaría a una espiral de deuda creciente.
        """)

        st.warning(f"""
        #### 💡 Recomendación Práctica:
        Para poder pagar este crédito sin problemas, necesitarías **aumentar tu ingreso mensual neto en por lo menos ${deficit_mensual:,.2f}**.
        """)

        st.subheader("⚠️ El Peligro Real de la Deuda: Proyección con Intereses")
        st.markdown(f"Si tomaras el crédito, tu déficit mensual de **${deficit_mensual:,.2f}** generaría más intereses a una tasa del **{tasa_anual:.1f}% anual**. Así crecería tu deuda:")

        años_proj = [1, 2, 3, 5, 10, 20]
        deuda_proyectada = []
        deuda_actual = 0
        for año in range(1, max(años_proj) + 1):
            for mes in range(12):
                deuda_actual += deficit_mensual  # Sumas el déficit del mes
                deuda_actual *= (1 + tasa_mensual) # Aplicas el interés a la deuda total
            if año in años_proj:
                deuda_proyectada.append((f"{año} año(s)", f"${deuda_actual:,.2f}"))

        df_proyeccion = pd.DataFrame(deuda_proyectada, columns=['Tiempo', 'Deuda Acumulada (con interés)'])
        st.table(df_proyeccion.style.set_properties(**{'text-align': 'left'}).set_table_styles([dict(selector='th', props=[('text-align', 'left')])]))
        st.caption("Nota: Esta proyección no incluye cargos por falta de pago o penalizaciones, que harían la deuda aún mayor.")
        
        # Gráfica de proyección NEGATIVA
        st.markdown("Así se vería tu balance hundiéndose mes a mes:")
        meses_grafica = range(int(plazo_meses) + 1)
        saldo_acumulado_grafica = [flujo_final * mes for mes in meses_grafica]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(meses_grafica), y=saldo_acumulado_grafica, fill='tozeroy', mode='lines', line_color='red', name='Deuda'))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(title='Evolución de tu Deuda Acumulada', xaxis_title='Mes', yaxis_title='Balance (MXN)')
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("El Factor Oculto: La Inflación  महंगाई"):
            st.markdown("""
            La tabla anterior es alarmante, pero la realidad es peor por la **inflación**. Cada año, tu dinero compra menos. Esto significa que:
            - Tus gastos fijos y variables (renta, comida, transporte) **subirán de precio**.
            - Tu déficit mensual real será **mayor** al que calculamos.
            - Necesitarías **ganar aún más** solo para mantener tu nivel de vida, y eso sin contar el pago de la deuda creciente.
            
            En resumen, una deuda te empobrece activamente mientras el costo de vida aumenta.
            """)

        with st.expander("⚖️ Consecuencias Legales y Reales en México por No Pagar"):
            st.markdown("""
            Si dejas de pagar un crédito formal (banco, SOFOM, financiera), esto es lo que realmente sucede:

            #### 1. Reporte a Buró de Crédito
            Es la primera y más segura consecuencia. La institución te reportará con una mala calificación. Esto **destruye tu historial crediticio** por años, impidiéndote acceder a:
            - Otros préstamos (personales, automotrices, hipotecarios).
            - Tarjetas de crédito.
            - En algunos casos, planes de telefonía celular o incluso la contratación en ciertos empleos.
            
            #### 2. Cobranza Extrajudicial
            El banco o un despacho de cobranza te contactará de forma insistente. Aunque existen reglas (REDECO de CONDUSEF), muchos despachos recurren al acoso telefónico a todas horas, e incluso contactan a tus referencias.

            #### 3. Juicio Mercantil y Embargo
            Si la deuda es considerable, el acreedor puede iniciar un **juicio mercantil** para recuperar el dinero. Si el juez falla a su favor, puede ordenar un **embargo de bienes**.
            - **¿Qué pueden embargar?** Bienes a tu nombre que no sean esenciales para vivir, como tu coche, televisor, computadoras, joyas, e incluso un porcentaje de tu sueldo (si excede el salario mínimo).
            - **No es automático.** Requiere un proceso judicial y la orden de un juez. No pueden llegar a tu casa y llevarse tus cosas sin una orden.

            #### 4. ¿Puedo ir a la cárcel por deudas?
            **NO.** El **Artículo 17 de la Constitución Mexicana** prohíbe la prisión por deudas de carácter puramente civil, como un préstamo personal o una tarjeta de crédito. No dejes que los cobradores te intimiden con esa amenaza.
            """)
else:
    st.info('Por favor, ingresa tu ingreso y los datos del préstamo para ver tu diagnóstico completo.')

st.markdown("---")
st.write("Esta es una herramienta de simulación. Las condiciones reales de un crédito pueden variar. Úsala como una guía para tomar mejores decisiones financieras.")