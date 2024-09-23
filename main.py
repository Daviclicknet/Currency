import customtkinter as ctk
import requests
from dotenv import load_dotenv
from typing import List
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import matplotlib
import numpy as np
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
update_timer = None  # Para controlar o timer da atualização

def plot_graph():
    # Suavização dos dados da taxa para um gráfico menos irregular
    if len(rates) > 3:
        smooth_rates = np.convolve(rates, np.ones(3)/3, mode='valid')
    else:
        smooth_rates = rates

    ax.clear()  # Limpa o gráfico antes de desenhar novamente

    ax.plot(timestamps[:len(smooth_rates)], smooth_rates, marker='o', color='#0DFF00')
    ax.fill_between(timestamps[:len(smooth_rates)], smooth_rates, color='#0DFF00', alpha=0.1)

    ax.set_title(f'{from_currency.get()} para {to_currency.get()} (tempo real)', color='white')
    ax.set_xlabel('Tempo', color='white')
    ax.set_ylabel('Taxa de Câmbio', color='white')
    ax.grid(False)
    ax.set_facecolor('#1a1a1a')
    fig.patch.set_facecolor('#1a1a1a')
    ax.tick_params(colors='white')
    canvas.draw()

def update_real_time_graph(base_currency='USD', target_currency='BRL'):
    global update_timer
    data = update_exchange_rate(base_currency, target_currency)
    
    if data and f"{base_currency}{target_currency}" in data:
        rate = float(data[f"{base_currency}{target_currency}"]['bid'])
        now = datetime.datetime.now()

        # Atualizando os dados do gráfico
        rates.append(rate)
        timestamps.append(now)

        # Exibindo o valor atual da taxa de câmbio
        current_rate_label.configure(text=f"Valor Atual: {rate:.2f} {target_currency} - {now.strftime('%H:%M:%S')}")

        # Plotando o gráfico
        plot_graph()

        # Cancelar timer anterior, se existir
        if update_timer is not None:
            app.after_cancel(update_timer)

        # Atualizando o gráfico a cada minuto
        update_timer = app.after(60000, lambda: update_real_time_graph(base_currency, target_currency))

def show_month_graph(base_currency='USD', target_currency='BRL'):
    url = f"https://economia.awesomeapi.com.br/json/daily/{base_currency}-{target_currency}/30"
    response = requests.get(url)
    data = response.json()
    
    if data:
        month_rates = [float(entry['bid']) for entry in data]
        month_dates = [datetime.datetime.fromtimestamp(int(entry['timestamp'])) for entry in data]

        ax.clear()

        # Suavização dos dados mensais
        smooth_month_rates = np.convolve(month_rates, np.ones(3)/3, mode='valid')

        ax.plot(month_dates[:len(smooth_month_rates)], smooth_month_rates, marker='o', color='#E10C00')
        ax.fill_between(month_dates[:len(smooth_month_rates)], smooth_month_rates, color='#E10C00', alpha=0.1)

        ax.set_title(f'{base_currency} para {target_currency} (Variações Mensais)', color='white')
        ax.set_xlabel('Dias', color='white')
        ax.set_ylabel('Taxa de Câmbio', color='white')

        ax.grid(False)
        ax.set_facecolor('#1a1a1a')
        fig.patch.set_facecolor('#1a1a1a')
        ax.tick_params(colors='white')

        canvas.draw()

def create_gui():
    global from_currency, to_currency, ax, canvas, current_rate_label, app, fig
    
    app = ctk.CTk()
    app.title("Gráfico de Câmbio em Tempo Real")
    app.geometry("800x600")
    
    ctk.CTkLabel(app, text="Gráfico de Câmbio", font=("Arial", 24)).pack(pady=10)
    
    frame = ctk.CTkFrame(app)
    frame.pack(pady=10)
    
    # Lista de moedas
    from_currency = ctk.CTkComboBox(frame, values=get_currency_list())
    from_currency.set("USD")
    from_currency.grid(row=0, column=0, padx=10)

    to_currency = ctk.CTkComboBox(frame, values=get_currency_list())
    to_currency.set("BRL")
    to_currency.grid(row=0, column=1, padx=10)
    
    # Botões "ATUAL" e "MÊS"
    button_frame = ctk.CTkFrame(app)
    button_frame.pack(pady=10)
    
    # Botão ATUAL
    ctk.CTkButton(button_frame, text="ATUAL", command=lambda: update_real_time_graph(from_currency.get(), to_currency.get())).grid(row=0, column=0, padx=10)
    
    # Botão MÊS
    ctk.CTkButton(button_frame, text="MÊS", command=lambda: show_month_graph(from_currency.get(), to_currency.get())).grid(row=0, column=1, padx=10)

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
