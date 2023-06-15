from Funciones.Funciones.py import *
import time

st.title("Analisis de Ethereum addresses")

address = (st.text_input("Ingrese una direccion de Ethereum:")).lower()

option = st.selectbox(
    '¿Que te gustaria hacer?',
    (
     'Primero ingrese la direccion.',
     'Conocer el balance de Ethereum de una direccion', 
     'Obtener sus tx', 
     'Obtener sus ERC20',
     'Obtener sus NFTS'
     ))

if option == 'Conocer el balance de Ethereum de una direccion':
    st.subheader("Balance: ")
    eth_balance, ethusd  = get_balance_usd(address)
    st.text(f"El usuario tiene {eth_balance}ETH en su wallet.")
    st.text(f"Expresado en usd: ${ethusd}USD. Precio actual: ${get_eth_px()}")
elif option == 'Obtener sus tx':
    data = get_transactions(address)
    st.subheader('Tx Dataframe:')
    st.write(data)
    csv_tx = convert_df(data)
    st.download_button("▼ Descargar.", csv_tx, "tx_data.csv", "text/csv",key='download-csv')
    
    st.subheader('Estadisticas.')
    st.write("-" * 100)
    recib = data.loc[data['from'] != address]
    env = data.loc[data['from'] == address]

    total_recib, total_env = len(recib['from']), len(env['from'])
    st.text(f"Cantidad de tx recibidas: {total_recib}")
    st.text(f"Cantidad de tx enviadas: {total_env}")
    st.write("-" * 100)
    
    total_eth_recib, total_eth_env = recib['value(Eth)'].sum(), env['value(Eth)'].sum()
    st.text(f"Eth recibido: {total_eth_recib}")
    st.text(f"Eth enviado: {total_eth_env}")
    st.write("-" * 100)
    
    st.subheader('Grafico de barras sobre las direcciones que han enviado ETH.')
    x = recib['from'].value_counts()
    y = x.values
    
    fig, ax = plt.subplots()  
    ax.barh(range(len(x)), y)  # Usar range(len(x)) como posiciones de las barras en el eje y
    ax.set_yticks(range(len(x)))  # Establecer las ubicaciones de las etiquetas del eje y
    ax.set_yticklabels(x.index)  # Establecer las etiquetas del eje y como los índices de x        
    st.pyplot(fig)
    st.write("-" * 100)
    
    st.subheader('Grafico de barras sobre tx enviadas por la address.')
    x = env['to'].value_counts()
    y = x.values
    
    fig, ax = plt.subplots()  
    ax.barh(range(len(x)), y)  # Usar range(len(x)) como posiciones de las barras en el eje y
    ax.set_yticks(range(len(x)))  # Establecer las ubicaciones de las etiquetas del eje y
    ax.set_yticklabels(x.index)  # Establecer las etiquetas del eje y como los índices de x        
    st.pyplot(fig)
    
elif option == 'Obtener sus ERC20':
    st.subheader('Tokens ERC20 transferidos/recibidos.')
    erc = get_tokens_tx(address)
    st.write(erc)
    csv_erc = convert_df(erc)
    st.download_button("▼ Descargar.", csv_erc, "erc_data.csv", "text/csv",key='download-csv')
    st.write("-" * 100)
    
    recib = erc.loc[erc['from'] != address]
    env = erc.loc[erc['from'] == address]
    st.subheader("Pie chart sobre los tokens ERC20 recibidos:")
    x = recib['from'].value_counts()
    
    if len(x) <= 0:
        st.text('Esta address no tiene tx recibidas.')
    else:
        df = recib.groupby(['tokenSymbol', 'from']).size().reset_index(name='from_count')
        fig, ax = plt.subplots()
        ax.pie(df['from_count'], labels=df['tokenSymbol'])
        st.pyplot(fig)
    st.write("-" * 100)    
    
    st.subheader("Pie chart sobre los tokens ERC20 envidados:")    
    x = env['to'].value_counts()
    if len(x) <= 0:
        st.text('Esta address no ha enviado tokens.')
    else:
        df = env.groupby(['tokenSymbol', 'to']).size().reset_index(name='from_to')
        fig, ax = plt.subplots()
        ax.pie(df['from_to'], labels = df['tokenSymbol'])
        st.pyplot(fig)
    st.write("-" * 100)    
    
    st.subheader("Balance por token.")
    erc20 = (st.text_input('Ingrese un token ERC20 y obtenga el balance del usuario:')).lower()    
    decim = st.number_input('Ingrese los decimales del token:', min_value=0, max_value=21)
    if decim == 0:
        time.sleep(8)
    else:
        balanc = get_balance_erc20(address, erc20, decim)
        st.text(f'El usuario tiene un balance de: {balanc} tokens.')
   
elif option == 'Obtener sus NFTS':
    st.subheader("Dataframe sobre tokens ERC721.")
    resp = get_nft_response(address)
    if resp['message'] == 'No transactions found':
        st.text("'No existen tx con este tipo de tokens'")
               
    else:
        data = edit_nft(resp["result"])
        st.write(data)
        data_csv = convert_df(data)
        st.download_button("▼ Descargar.", data_csv, "nft_data.csv", "text/csv",key='download-csv')
    st.write("-" * 100)    

    
