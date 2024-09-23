import customtkinter as ctk
import requests
from tkinter import messagebox
from dotenv import load_dotenv
from typing import List
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import matplotlib
import numpy as np  # Importado para suavização do gráfico
import os

matplotlib.use('TkAgg')

# Load environment variables from .env file
load_dotenv()

SUPPORTED_CURRENCIES = [
    'USD', 'EUR', 'BRL', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'INR'
]

def get_currency_list() -> List[str]:
    return SUPPORTED_CURRENCIES

def update_exchange_rate(base_currency: str, target_currency: str) -> dict:
    url = f"https://economia.awesomeapi.com.br/json/last/{base_currency}-{target_currency}"
    response = requests.get(url)
    data = response.json()
    return data

# Variáveis para o gráfico em tempo real
rates = []
timestamps = []

# Função modificada com suavização do gráfico
def update_real_time_graph(base_currency='USD'):
    target_currency = 'BRL'
    data = update_exchange_rate(base_currency, target_currency)
    
    if data and f"{base_currency}{target_currency}" in data:
        rate = float(data[f"{base_currency}{target_currency}"]['bid'])
        now = datetime.datetime.now()

        # Atualizando os dados do gráfico
        rates.append(rate)
        timestamps.append(now)

        ax.clear()
        
        # Suavização opcional dos dados da taxa para um gráfico menos irregular
        if len(rates) > 3:
            smooth_rates = np.convolve(rates, np.ones(3)/3, mode='valid')
        else:
            smooth_rates = rates

        # Plotando a linha suavizada
        ax.plot(timestamps[:len(smooth_rates)], smooth_rates, marker='o', color='#7FFF00')  # Cor verde-clara
        ax.fill_between(timestamps[:len(smooth_rates)], smooth_rates, color='#7FFF00', alpha=0.1)  # Área sombreada
        
        # Definindo título e rótulos do gráfico
        ax.set_title(f'{base_currency} to BRL (Real-Time)', color='white')
        ax.set_xlabel('Tempo', color='white')
        ax.set_ylabel('Taxa de Câmbio', color='white')
        
        # Removendo a grade para uma aparência mais limpa (opcional)
        ax.grid(False)

        # Tema escuro para o fundo do gráfico e da área de plotagem
        fig.patch.set_facecolor('#1a1a1a')  # Fundo escuro da figura
        ax.set_facecolor('#1a1a1a')  # Fundo escuro da área de plotagem
        
        # Cor branca para os ticks para melhor visibilidade
        ax.tick_params(colors='white')

        # Exibindo o valor atual da taxa de câmbio
        current_rate_label.configure(text=f"Valor Atual: {rate:.2f} {target_currency}")

        # Redesenhando o gráfico atualizado
        canvas.draw()
        
        # Atualizando o gráfico a cada minuto
        app.after(60000, lambda: update_real_time_graph(base_currency))

def convert_currency():
    try:
        base_currency = from_currency.get()
        target_currency = to_currency.get()
        amount = float(entry_amount.get())
        
        if base_currency == target_currency:
            result = amount
        else:
            data = update_exchange_rate(base_currency, target_currency)
            if data and f"{base_currency}{target_currency}" in data:
                rate = float(data[f"{base_currency}{target_currency}"]['bid'])
                result = amount * rate
            else:
                messagebox.showerror("Erro", "Falha ao obter taxa de câmbio.")
                return
        
        result_label.configure(text=f"{amount:.2f} {base_currency} = {result:.2f} {target_currency}")
        update_real_time_graph(base_currency)

    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um valor válido.")

# Criando a interface gráfica
def create_gui():
    global from_currency, to_currency, entry_amount, result_label, ax, canvas, current_rate_label, app, fig
    
    app = ctk.CTk()
    app.title("Conversor de Moedas com Gráfico")
    app.geometry("800x600")
    
    ctk.CTkLabel(app, text="Conversor de Moedas", font=("Arial", 24)).pack(pady=10)
    
    frame = ctk.CTkFrame(app)
    frame.pack(pady=10)
    
    # Lista de moedas
    from_currency = ctk.CTkComboBox(frame, values=get_currency_list())
    from_currency.set("USD")
    from_currency.grid(row=0, column=0, padx=10)

    to_currency = ctk.CTkComboBox(frame, values=get_currency_list())
    to_currency.set("BRL")
    to_currency.grid(row=0, column=1, padx=10)
    
    # Entrada de valor
    entry_amount = ctk.CTkEntry(frame, placeholder_text="Valor")
    entry_amount.grid(row=0, column=2, padx=10)
    
    # Botão para converter
    ctk.CTkButton(frame, text="Converter", command=convert_currency).grid(row=0, column=3, padx=10)
    
    # Label de resultado
    result_label = ctk.CTkLabel(app, text="Resultado", font=("Arial", 18))
    result_label.pack(pady=10)

    # Gráfico Matplotlib
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    # Label da taxa atual
    current_rate_label = ctk.CTkLabel(app, text="Valor Atual: ---", font=("Arial", 14))
    current_rate_label.pack(pady=10)

    # Inicializando o gráfico com valores padrão
    update_real_time_graph()

    app.mainloop()

if __name__ == "__main__":
    create_gui()
