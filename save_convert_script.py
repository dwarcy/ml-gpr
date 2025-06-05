# ADICIONAR ESSES TRECHOS DE CÓDIGO AO SCRIPT PYTHON GERADO PELO SOFTWARE 'GPRPy'
# REALIZAR ESSA MESCLA PARA CADA SCRIPT DE CADA ARQUIVO .DZT TRATADO

# 1º PARTE - IMPORTAR AS BIBLIOTECLAS
# Adicionar essas duas bibliotecas às bibliotecas do script 
import fitz  # PyMuPDF
from pathlib import Path

# ENTRE PASSO 1 E PASSO 2: 
# colocar as seguintes linhas de código que estão no script gerados pelo 'GPRPy':
# mygpr = gp.gprpyProfile()
# mygpr.importdata('caminho/para/seu/arquivo.DZT')
# mygpr.setZeroTime( )
# Obs: Se não foi necessário ajustar o zeroTime, então essa terceira linha não vai precisar ser adicionada




# 2º PASSO - ADICIONAR ESSE TRECHO PARA DESCOBRIR TAMANHOS MÁXIMO E MÍNIMO DOS EIXOS X E Y
# importante para conseguir saber a quantidade de iterações necessárias para percorrer todo o radargrama e
# para manter a contagem das imagens
# X -- referente ao tamanho original do arquivo .DZT 
x_min = min(mygpr.profilePos)           # Tamanho min de X
x_max = max(mygpr.profilePos)           # Tamanho max de X
# Y -- referente ao tamanho setado no 'set Zero Time' e no 'set Y-range', no 'GPRPy'
t_min = min(mygpr.twtt)                 # zeroTime
t_max = max(mygpr.twtt)                 # Max

# 3º PASSO - ADICIONAR ESSE TRECHO E !!DEFINIR!! O INTERVALO DAS IMAGENS 
# aqui será definido o intervalo do eixo x que será salvado nas imagens
# em outras palavras, é definir o 'set X-range' e o deslocamento.
# os valores de 'largura_janela' e 'passo' são iguais
inicio = x_min
fim = x_max
largura_janela = 1          # X-range
passo = 1                   # deslocamento

# 4º PASSO - LOOP PARA PERCORRER O RADARGRAMA E SALVAR AS IMAGENS
# usando a função 'mygpr.printProfile( )' do script original, um .pdf será gerado e em seguida convertido para .jpg
i = 0
x = inicio
while x + largura_janela <= fim:
    # xrng e yrng são informações utilizadas para gerar o pdf na função 'mygpr.printProfile( )'
    xrng = [x, x + largura_janela]
    yrng = [t_min, t_max]
    
    # 5º PASSO - DEFINIR O NOME DO .PDF GERADO
    # definir o diretório em que o .pdf será salvo. Sugestão: utilizar o caminho que aparece em 'mygpr.printProfile( )' do script original
    # mudar o nome do arquivo .pdf para 'frame_{i:02d}.pdf'
    nome_arquivo = f"/utilizar/seu/caminho/frame_{i:02d}.pdf"
    
    # ENTRE PASSO 5 E PASSO 6
    # acrescentar aqui a linha 'mygpr.printProfile( )' completa do script original
    # alterar o primeiro parâmetro, que contêm 'caminho/para/o/seu/arquivo.pdf' pela variavel nome_arquivo
    # no parâmetro yrng: yrng = yrng
    # no parâmetro xrng: xrng = xrng
    # exemplo: mygpr.printProfile(nome_arquivo, color='', contrast=, yrng=yrng, xrng=xrng, dpi=600)

    print(f"Gerado: {nome_arquivo}")

    # 6º PASSO - CONVERTER PDF PARA JPG
    # usa biblioteca importada para fazer a conversão 
    doc = fitz.open(nome_arquivo)
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=300)
    # mudar a string do caminho para o diretório para onde a imagem será salva 
    pix.save(f"caminho/para/diretorio/frame_{i:02d}.jpg")

    x += passo
    i += 1