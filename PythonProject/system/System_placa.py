import os
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import ctypes
import threading
from colorama import Fore, Style
from pathlib import Path
import sys
import zipfile
from datetime import datetime

# Caminho das imagens não convertidas e convertidas
base_dir = Path(__file__).resolve().parent
imgpast = base_dir / "sistema" / "receberimg"
imgconv = base_dir / "sistema" / "convertidaimg"
backup = base_dir / "sistema" / "backup"
logConversao = base_dir / "sistema" / "logs" / "logConversao" / "logC.txt"
logErro = base_dir / "sistema" / "logs" / "logErro" / "logE.txt"

backh = ['18:20', '12:00']  # Lista de horários para o backup

# Função data e hora
def dataHora():
    return datetime.now().strftime('%d-%m-%y_%H-%M')
# Função data e hora logs
def dataHoraLog():
    return datetime.now().strftime('%H:%M dia %d-%m-%y')
# Função para exibir a arte ASCII
def status_conversao():
    ascii_art = Fore.BLUE + """
     _          _             

 ___| |_  __ _ | |_  _  _  ___
(_-<|  _|/ _ ||  _|| || |(_-<
/__/ \__|\__,_| \__| \_,_|/__/


           """
    print(ascii_art)


status_conversao()


# Função para mostrar a MessageBox em um thread separado
def show_message_box():
    mensagemerro = (
        "Olá, aparentemente o sistema de conversão sofreu algum erro, "
        "contate o técnico imediatamente!!\n\n"
        "João Victor\n"
        "Número: +55 34 9997-1016\n"
        "Carlos Junior\n"
        "Número: +55 34 9636-6764"
    )
    ctypes.windll.user32.MessageBoxW(0, mensagemerro, "Erro", 0x10 | 0x40000 | 0x20000)

# Função backup
def backup_zip(imgconv, backup):

    # Nome do arquivo ZIP de backup
    backup_zip = backup / f'Backup {dataHora()}.zip'  # O arquivo zip será salvo em 'backup'

    # Cria um arquivo ZIP
    with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Percorre todos os arquivos e subpastas na pasta de origem (imgconv)
        for root, dirs, files in os.walk(imgconv):
            for file in files:
                # Cria o caminho completo do arquivo
                caminho_completo = os.path.join(root, file)
                # Adiciona o arquivo ao ZIP com o caminho relativo
                caminho_relativo = os.path.relpath(caminho_completo, imgconv)
                zipf.write(caminho_completo, caminho_relativo)

#Funçao log imagem
def logConv(imagemConv):
    with open(logConversao, 'a') as f:
        f.write(f'Imagem {imagemConv} convertida, as {dataHoraLog()}\n')

def erroLog():
    with open(logErro, 'a') as f:
        f.write(f'Erro detectado as {dataHoraLog()}\n')




errocounter = 0


def erro():
    global errocounter
    try:
        # Criar um thread para exibir a MessageBox sem bloquear o fluxo
        threading.Thread(target=show_message_box).start()
        errocounter += 1
        print(f"{errocounter}º erro encontrado. Contate o suporte imediatamente!")
        backup_zip(imgconv, backup)
        print(Fore.BLUE + 'O backup foi realizado devido ao erro.')
        erroLog()

        if errocounter >= 3:
            print(Fore.RED + "Interrompemos o sistema por medidas de segurança. Contate o suporte imediatamente!.")
            suporte = (
                "contate o suporte imediatamente!!!\n\n"
                "João Victor\n"
                "Número: +55 34 9997-1016\n"
                "Carlos Junior\n"
                "Número: +55 34 9636-6764")
            print(Fore.GREEN + suporte)
            erroLog()
            sys.exit(1)


    except Exception as e:
        backup_zip(imgconv, backup)  # Realiza backup em caso de erro

# Função para converter as imagens
def converter_imagem(imagem_path):
    try:
        # Aguardar um pouco para garantir que o arquivo foi completamente salvo
        time.sleep(1)  # Aguarda 1 segundo (ajuste conforme necessário)

        # Cria variável im armazenando a imagem nela
        im = Image.open(imagem_path)

        # Se for diferente de PNG, converte para PNG
        if im.format != 'PNG':
            # Define o nome da imagem convertida
            novdir = imgconv / (imagem_path.stem + '.png')

            # Salva a imagem no formato PNG
            im.save(novdir, 'PNG')

            # Fecha a imagem antes de deletá-la
            im.close()
            # Apaga a imagem original após a conversão
            imagem_path.unlink()
            print(Fore.GREEN, f"Imagem {imagem_path.name} convertida com sucesso! e salva no {novdir}")
            logConv(imagem_path.name)


    except Exception as e:
        print(Fore.RED, f"Erro ao converter a imagem {imagem_path.name}: {e}")
        erro()


# Função para processar imagens já existentes na pasta
def processar_imagens_existentes():
    for imagem_path in imgpast.iterdir():
        if imagem_path.is_file() and imagem_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            print(f"Processando imagem existente: {imagem_path.name}")
            converter_imagem(imagem_path)
            logConv(imagem_path.name)



# Classe que define o que fazer quando um novo arquivo é adicionado
class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            imagem_path = Path(event.src_path)
            print(f"Nova imagem detectada: {imagem_path.name}")
            converter_imagem(imagem_path)

# Configuração para monitorar a pasta de imagens
def monitorar_pasta():
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, str(imgpast), recursive=False)
    observer.start()
    print(Style.RESET_ALL, f"Monitorando a pasta {imgpast} por novas imagens...")
    return observer

# Loop para rodar tanto o backup quanto o monitoramento
def main_loop():
    observer = monitorar_pasta()  # Inicia o monitoramento da pasta
    processar_imagens_existentes()  # Processa as imagens já existentes

    try:
        while True:
            # Obtém a hora atual no formato 'HH:MM'
            timea = datetime.now().strftime('%H:%M')

            # Verifica se a hora atual está na lista de horários para o backup
            if timea in backh:
                backup_zip(imgconv, backup)
                print(Fore.BLUE + 'Backup automático feito com sucesso!')
                time.sleep(60)  # Aguarda 1 minuto antes de verificar novamente
            else:
                time.sleep(60)  # Espera 1 minuto antes de verificar novamente

    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Iniciar o loop principal
main_loop()
