import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

with st.sidebar:
    st.title('Mapa Covid')
    fecha_inicio = st.date_input(
        "Fecha Inicio",
        datetime.date(2020, 1, 1))
    fecha_final = st.date_input(
        "Fecha Fin",
        datetime.date(2022, 8, 4))
    st.title('Períodos de Interés')
    if st.button('Primeros 6 Meses de 2020'):
        fecha_inicio = datetime.date(2020, 1, 1)
        fecha_final = datetime.date(2020, 6, 30)
    if st.button('Año 2020'):
        fecha_inicio = datetime.date(2020, 1, 1)
        fecha_final = datetime.date(2020, 12, 31)
    if st.button('Año 2021'):
        fecha_inicio = datetime.date(2021, 1, 1)
        fecha_final = datetime.date(2021, 12, 31)
    if st.button('Año 2022'):
        fecha_inicio = datetime.date(2022, 1, 1)
        fecha_final = datetime.date(2022, 12, 31)
    if st.button('Cuarentena'):
        fecha_inicio = datetime.date(2020, 3, 19)
        fecha_final = datetime.date(2020, 6, 1)

    if st.button('Total Dataset'):
        fecha_inicio = datetime.date(2020, 1, 1)
        fecha_final = datetime.date(2022, 8, 4)


data = pd.read_csv('COVID-19_Reported_Patient_Impact_and_Hospital_Capacity_by_State_Timeseries.csv')
data['date'] = data['date'].apply(lambda x: x.replace('/', '-'))
data.date = data.date.map(pd.Timestamp.fromisoformat)
data = data.sort_values(by='date')
periodo = data[data.date.dt.date < fecha_final][data.date.dt.date > fecha_inicio]

#CALCULAR OCUPACION HOSPITALARIA EN UN PERIODO
mayor_occupacion_hospitalaria = periodo[['state', 'date', 'inpatient_beds_used_covid']]
mayor_occupacion_hospitalaria = mayor_occupacion_hospitalaria.groupby(by='state').mean()
mayor_occupacion_hospitalaria = mayor_occupacion_hospitalaria.sort_values(by='inpatient_beds_used_covid', ascending=False).reset_index()
mayor_occupacion_hospitalaria = mayor_occupacion_hospitalaria.rename(columns={'inpatient_beds_used_covid': 'ibuc'})
mayor_occupacion_hospitalaria.ibuc = mayor_occupacion_hospitalaria.ibuc.apply(lambda x: int(x))

#CAMAS UCI
porcentaje_camas_UCI = periodo[['state', 'adult_icu_bed_covid_utilization']]
porcentaje_camas_UCI = porcentaje_camas_UCI.groupby(by='state').mean()
porcentaje_camas_UCI = porcentaje_camas_UCI.sort_values(by='adult_icu_bed_covid_utilization', ascending=False).reset_index()
porcentaje_camas_UCI = porcentaje_camas_UCI.rename(columns={'adult_icu_bed_covid_utilization': '% ICU'})

#MUERTESYCONTAGIOSADULTOSPEDIATRIC
muertes_contagios = periodo[['date',
                             'deaths_covid',
                             'staffed_icu_adult_patients_confirmed_covid',
                             'total_pediatric_patients_hospitalized_confirmed_covid',
                             'critical_staffing_shortage_today_yes']]
muertes_contagios = muertes_contagios.groupby(by='date').sum()

#MUERTES
datos_estado = periodo[['state',
                        'deaths_covid',
                        'staffed_icu_adult_patients_confirmed_covid',
                        'total_pediatric_patients_hospitalized_confirmed_covid',
                        'critical_staffing_shortage_today_yes']]
datos_estado = datos_estado.groupby(by='state').sum()
datos_estado = datos_estado.deaths_covid.apply(lambda x: int(x))

tab1, tab2 = st.tabs(["General", "Por Estado"])

with tab1:
    st.header('Muertes Por COVID en EEUU')
    st.markdown('Analisis realizado sobre los distintos puntos médicos de EEUU durante la pandemia de COVID-19' 
                ' en el periodo 2020-2022.'
                ' Se tomaron en cuenta aspectos referentes a muertes producidas, cantidad de camas de internacion '
                'y de terapia intensiva utilizadas, pacientes adultos y pediatricos con COVID confirmado y '
                'segmetaciones por estados. '
                'Se establecieron por defecto distintos periodos de tiempo de interés y la posibilidad activa de '
                'ajustar a periodos en específico')
    st.subheader('Histórico de muertes a causa de covid')
    fig2, ax2 = plt.subplots(figsize=(20, 13), dpi=200)
    sns.lineplot(data=muertes_contagios, x='date', y='deaths_covid')
    agree = st.checkbox('Falta de Personal')
    if agree:
        sns.lineplot(data=muertes_contagios, x='date', y='critical_staffing_shortage_today_yes')
        plt.legend(labels=['Muertes', 'Alerta Falta De Personal'], fontsize='15', title='info', loc=5)
    plt.style.use("dark_background")
    st.pyplot(fig2)
    st.markdown('Número total muertes: ' + str(muertes_contagios.deaths_covid.sum()))
    st.markdown('Pico Máximo: '
                + str(muertes_contagios.sort_values('deaths_covid', ascending=False)[:1].deaths_covid[0]) +
                '  | Fecha de pico Máximo: '
                + str(muertes_contagios.sort_values('deaths_covid', ascending=False)[:1].index[0]).split(' ')[0])
    st.markdown('Pico Mínimo: '
                + str(muertes_contagios.sort_values('deaths_covid')[:1].deaths_covid[0]) +
                '  | Fecha de pico Mínimo: '
                + str(muertes_contagios.sort_values('deaths_covid')[:1].index[0]).split(' ')[0])

    st.subheader('Pacientes Adultos con COVID Confirmado')
    fig3, ax3 = plt.subplots(figsize=(20, 13), dpi=200)
    sns.lineplot(data=muertes_contagios, x='date', y='staffed_icu_adult_patients_confirmed_covid')
    plt.style.use("dark_background")
    st.pyplot(fig3)
    st.markdown('Número total pacientes adultos con COVID Confirmado: '
                + str(muertes_contagios.staffed_icu_adult_patients_confirmed_covid.sum()))
    st.markdown('Pico Máximo: '
                + str(muertes_contagios.sort_values('staffed_icu_adult_patients_confirmed_covid',
                                                    ascending=False)[:1].staffed_icu_adult_patients_confirmed_covid[0]) +
                '  | Fecha de pico Máximo: '
                + str(muertes_contagios.sort_values('staffed_icu_adult_patients_confirmed_covid',
                                                    ascending=False)[:1].index[0]).split(' ')[0])
    st.markdown('Pico Mínimo: '
                + str(muertes_contagios.sort_values('staffed_icu_adult_patients_confirmed_covid')[:1]
                      .staffed_icu_adult_patients_confirmed_covid[0]) +
                '  | Fecha de pico Mínimo: '
                + str(muertes_contagios.sort_values('staffed_icu_adult_patients_confirmed_covid')[:1]
                      .index[0]).split(' ')[0])

    st.subheader('Pacientes Pediátricos con COVID Confirmado')
    fig4, ax4 = plt.subplots(figsize=(20, 13), dpi=200)
    sns.lineplot(data=muertes_contagios, x='date', y='total_pediatric_patients_hospitalized_confirmed_covid')
    plt.style.use("dark_background")
    st.pyplot(fig4)
    st.markdown('Número total pacientes pediátricos con COVID confirmado: '
                + str(muertes_contagios.total_pediatric_patients_hospitalized_confirmed_covid.sum()))
    st.markdown('Pico Máximo: '
                + str(muertes_contagios.sort_values('total_pediatric_patients_hospitalized_confirmed_covid',
                                                    ascending=False)[:1]
                      .total_pediatric_patients_hospitalized_confirmed_covid[0]) +
                '  | Fecha de pico Máximo: '
                + str(muertes_contagios.sort_values('total_pediatric_patients_hospitalized_confirmed_covid',
                                                    ascending=False)[:1].index[0]).split(' ')[0])
    st.markdown('Pico Máximo: '
                + str(muertes_contagios.sort_values('total_pediatric_patients_hospitalized_confirmed_covid')[:1]
                      .total_pediatric_patients_hospitalized_confirmed_covid[0]) +
                '  | Fecha de pico Máximo: '
                + str(muertes_contagios.sort_values('total_pediatric_patients_hospitalized_confirmed_covid')[:1]
                      .index[0]).split(' ')[0])

with tab2:
    st.title('Hospitalizados Por Estado')
    col1, col2 = st.columns([3, 1])
    fig1 = px.choropleth(
        mayor_occupacion_hospitalaria,
        locations='state', locationmode='USA-states',
        color=mayor_occupacion_hospitalaria.ibuc,
        range_color=(mayor_occupacion_hospitalaria.ibuc.min(),
                     mayor_occupacion_hospitalaria.ibuc.max()),
        color_continuous_scale='reds')
    fig1.update_layout(
        title_text='Cantidad de hopitalizados COVID-19',
        geo=dict(
            scope='usa',
            landcolor='rgb(229, 229, 229)',
            bgcolor='rgb(40,40,40)'
        ),
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
        width=530,
        height=290)

    col1.plotly_chart(fig1)
    col2.dataframe(mayor_occupacion_hospitalaria, height=280)

    st.title('Muertes COVID Por Estado')
    muertes = datos_estado.reset_index()
    muertes = muertes[['state', 'deaths_covid']]
    muertes = muertes.sort_values('deaths_covid', ascending=False).reset_index()
    muertes = muertes.drop(columns='index')
    muertes = muertes.rename(columns={'deaths_covid': 'deaths'})
    col5, col6 = st.columns([3, 1])
    fig5 = px.choropleth(
        muertes,
        locations='state', locationmode='USA-states',
        color=muertes.deaths,
        range_color=(muertes.deaths.min(),
                     muertes.deaths.max()),
        color_continuous_scale='reds')
    fig5.update_layout(
        title_text='Muertes por COVID-19',
        geo=dict(
            scope='usa',
            landcolor='rgb(229, 229, 229)',
            bgcolor='rgb(40,40,40)'
        ),
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
        width=530,
        height=290)

    col5.plotly_chart(fig5)
    col6.dataframe(muertes, height=280)

    st.title('Utilización de Camas UCI por Estado')

    fig2 = px.choropleth(
        porcentaje_camas_UCI,
        locations='state', locationmode='USA-states',
        color=porcentaje_camas_UCI['% ICU'],
        range_color=(0, 0.4),
        color_continuous_scale='reds')
    fig2.update_layout(
        title_text='Porcentaje de utilización de camas UCI COVID por estado',
        geo=dict(
            scope='usa',
            landcolor='rgb(229, 229, 229)',
            bgcolor='rgb(40,40,40)'
        ),
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
        width=530,
        height=290)
    col3, col4 = st.columns([3, 1])
    col3.plotly_chart(fig2)
    col4.dataframe(porcentaje_camas_UCI, height=280)

    st.title('Análisis por Estado')
    est= pd.DataFrame()
    est['codigo'] = data.state.unique()
    est = est.sort_values('codigo')
    nombre_estado = ['Alaska',
                     'Alabama',
                     'Arkansas',
                     'Samoa Americana',
                     'Arizona',
                     'California',
                     'Colorado',
                     'Connecticut',
                     'Washington D. C.',
                     'Delaware',
                     'Florida',
                     'Georgia',
                     'Hawái',
                     'Iowa',
                     'Idaho',
                     'Illinois',
                     'Indiana',
                     'Kansas',
                     'Kentucky',
                     'Luisiana',
                     'Massachusetts',
                     'Maryland',
                     'Maine',
                     'Míchigan',
                     'Minnesota',
                     'Misuri',
                     'Misisipi',
                     'Montana',
                     'Carolina del Norte',
                     'Dakota del Norte',
                     'Nebraska',
                     'Nuevo Hampshire',
                     'Nueva Jersey',
                     'Nuevo México',
                     'Nevada',
                     'Nueva York',
                     'Ohio',
                     'Oklahoma',
                     'Oregón',
                     'Pensilvania',
                     'Puerto Rico',
                     'Rhode Island',
                     'Carolina del Sur',
                     'Dakota del Sur',
                     'Tennessee',
                     'Texas',
                     'Utah',
                     'Virginia',
                     'Islas Vírgenes de los Estados Unidos',
                     'Vermont',
                     'Washington',
                     'Wisconsin',
                     'Virginia Occidental',
                     'Wyoming']
    est['nombre_estado'] = nombre_estado
    est['cod_nom'] = est.codigo + '-' + est.nombre_estado
    estado = st.selectbox(
        'Elegir Un Estado',
        est.cod_nom)
    estado = estado.split('-')[0]
    # ANALISIS POR ESTADO
    muertes_camas_estado = periodo.loc[periodo.state == estado]
    muertes_camas_estado = muertes_camas_estado[['date', 'deaths_covid', 'adult_icu_bed_utilization']]
    muertes_camas_estado = muertes_camas_estado.groupby(by='date').agg(
        {'deaths_covid': 'sum', 'adult_icu_bed_utilization': 'mean'})
    muertes_camas_estado['adult_icu_bed_utilization'] = muertes_camas_estado['adult_icu_bed_utilization'] * 100
    fig, ax = plt.subplots(figsize=(20, 13), dpi=200)
    sns.lineplot(data=muertes_camas_estado, x='date', y='deaths_covid')
    sns.lineplot(data=muertes_camas_estado, x='date', y='adult_icu_bed_utilization')
    sns.lineplot(data=muertes_camas_estado, x='date', y=100)
    plt.legend(labels=['Muertes', '%total camas ocupadas ICU', 'limite_camas'], fontsize='15', title='info', loc=5)
    plt.style.use("dark_background")
    st.pyplot(fig)
    st.markdown('Número total de muertes: ' + str(muertes_camas_estado.deaths_covid.sum()))
    st.markdown('Máxima ocupación de camas: ' + str(periodo.loc[periodo.state == estado].inpatient_beds_used_covid.max()))