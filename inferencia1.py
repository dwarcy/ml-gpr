import gprpy.gprpy as gp
import fitz  # PyMuPDF
import os
import numpy as np

# Configurações do usuário
dzt_file = 'caminho/radargrama/FILE__125 P_1.DZT'
output_dir = 'caminho/imagens/dzt_125_xyzcoordinates'

largura_janela = 1.0  # X-range em metros
passo = 1.0  # deslocamento entre frames

# Criar diretório para imagens
os.makedirs(output_dir, exist_ok=True)

# 1. Carregar os dados COM setZeroTime = 1
print(f"Carregando arquivo DZT: {os.path.basename(dzt_file)}")
mygpr = gp.gprpyProfile()
mygpr.importdata(dzt_file)
# mygpr.setZeroTime(1.03)  # Adicionado setZeroTime = 1

# 2. Extrair TODAS as informações automaticamente do .DZT
# X-range: posições do perfil
x_positions = mygpr.profilePos
x_min_original = min(x_positions)
x_max_original = max(x_positions)
comprimento_total = x_max_original - x_min_original

# Ajustar: considerar o ponto inicial do eixo x como 0
# Isso significa que vamos deslocar todas as posições para que x_min = 0
deslocamento = x_min_original
x_min = 0.0
x_max = x_max_original - deslocamento

print(f"Deslocamento aplicado para iniciar em 0: {deslocamento:.3f} m")

# Y-range: tempo de trânsito da onda (extraído diretamente do .DZT)
# O atributo 'twtt' contém os tempos para cada amostra ao longo da profundidade
twtt = mygpr.twtt  # Two-Way Travel Time em nanosegundos
t_min = min(twtt)  # Tempo mínimo (já ajustado pelo setZeroTime)
t_max = max(twtt)  # Tempo máximo - define a profundidade máxima medida

print("\n" + "="*60)
print("INFORMAÇÕES EXTRAÍDAS DO ARQUIVO .DZT")
print("="*60)
print(f"Posições X ORIGINAIS do perfil:")
print(f"  Mínimo: {x_min_original:.3f} m")
print(f"  Máximo: {x_max_original:.3f} m")
print(f"  Comprimento total: {comprimento_total:.3f} m")
print(f"  Número de traços: {len(x_positions)}")
print()
print(f"Posições X AJUSTADAS (início em 0):")
print(f"  Mínimo: {x_min:.3f} m")
print(f"  Máximo: {x_max:.3f} m")
print()
print(f"Tempos (Two-Way Travel Time - TWTT):")
print(f"  Mínimo: {t_min:.3f} ns")
print(f"  Máximo: {t_max:.3f} ns")
print(f"  Intervalo: {t_max - t_min:.3f} ns")
print(f"  Número de amostras por traço: {len(twtt)}")
print(f"  Zero Time aplicado: 1.0 ns")

# 3. Analisar os dados para escolher um y-range apropriado
# Opção 1: Usar todo o intervalo de tempo registrado
y_min = t_min
y_max = t_max

# Opção 2: Analisar os dados para verificar se há muita área vazia no final
if hasattr(mygpr, 'data') and mygpr.data is not None:
    data = mygpr.data
    # Calcular energia média por profundidade
    energia_media = np.mean(np.abs(data), axis=1)
    
    # Encontrar onde a energia cai para 2% do máximo
    energia_max = np.max(energia_media)
    limiar = 0.02 * energia_max
    
    # Encontrar o índice onde a energia fica abaixo do limiar
    indices_abaixo = np.where(energia_media < limiar)[0]
    
    if len(indices_abaixo) > 0 and indices_abaixo[0] > len(twtt) * 0.1:
        # Encontrar o primeiro ponto significativamente abaixo do limiar
        idx_limite = indices_abaixo[0]
        t_limite = twtt[idx_limite]
        
        # Usar 120% deste tempo como limite, mas não mais que t_max
        y_max_sugerido = min(t_limite * 1.2, t_max)
        
        if y_max_sugerido < t_max * 0.8:  # Só usar se for significativamente menor
            print(f"\nAnálise de sinal sugere cortar em:")
            print(f"  Tempo sugerido: {y_max_sugerido:.1f} ns")
            print(f"  Economia: {(t_max - y_max_sugerido)/t_max*100:.1f}% do tempo total")
            usar_todo = input("Usar todo o intervalo (T) ou cortar (C)? [T/C]: ")
            
            if usar_todo.upper() == 'C':
                y_max = y_max_sugerido

# 4. Definir o y-range final
yrng = [y_min, y_max]

print(f"\nY-RANGE DEFINIDO:")
print(f"  De: {yrng[0]:.1f} ns")
print(f"  Até: {yrng[1]:.1f} ns")
print(f"  Total: {yrng[1] - yrng[0]:.1f} ns")

# Converter para profundidade estimada (para informação)
# Valores típicos de velocidade:
# Ar: 0.3 m/ns, Água: 0.033 m/ns, Solo seco: 0.15 m/ns, Solo úmido: 0.06 m/ns
velocidade_estimada = 0.1  # m/ns (valor conservador para solo)
profundidade_max = (yrng[1] - yrng[0]) * velocidade_estimada / 2  # /2 porque é tempo ida+volta
print(f"  Profundidade estimada: {profundidade_max:.2f} m (v={velocidade_estimada} m/ns)")
print("="*60 + "\n")

# 5. Gerar frames - AGORA COM X INICIANDO EM 0
frame_num = 0
x_atual = x_min  # Agora começa em 0

print(f"Gerando frames com largura de {largura_janela}m (início em x=0)...")

while x_atual <= x_max:
    # Definir o x-range para este frame
    x_fim = min(x_atual + largura_janela, x_max)
    
    # Não gerar frames muito pequenos
    if (x_fim - x_atual) < (largura_janela * 0.3) and frame_num > 0:
        break
    
    # Ajustar xrng para as posições originais (o GPRPy espera as posições originais)
    xrng_original = [x_atual + deslocamento, x_fim + deslocamento]
    xrng_ajustado = [x_atual, x_fim]  # Para nomes de arquivo
    
    # Criar nome descritivo para o arquivo (usando x ajustado, iniciando em 0)
    nome_base = f"frame_{frame_num:04d}_x{x_atual:.3f}m"
    pdf_path = os.path.join(output_dir, f"{nome_base}.pdf")
    jpg_path = os.path.join(output_dir, f"{nome_base}.jpg")
    
    try:
        # Gerar o perfil em PDF - usando xrng_original para o GPRPy
        print(f"  Frame {frame_num:03d}: X={x_atual:.3f}-{x_fim:.3f}m", end="")
        
        mygpr.printProfile(
            pdf_path, 
            color='gray', 
            contrast=10, 
            yrng=yrng, 
            xrng=xrng_original,  # Usando as posições originais
            dpi=600
        )
        
        print(" ✓ PDF", end="")
        
        # Converter PDF para JPG
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=300)
        pix.save(jpg_path)
        doc.close()
        
        # Remover o PDF após conversão
        os.remove(pdf_path)
        
        print(" ✓ JPG")
        
    except Exception as e:
        print(f" ✗ ERRO: {str(e)[:50]}...")
    
    # Avançar para o próximo frame
    x_atual += passo
    frame_num += 1

# 6. Salvar informações do processamento em arquivo
info_file = os.path.join(output_dir, "metadata.txt")
with open(info_file, 'w') as f:
    f.write(f"METADADOS DO PROCESSAMENTO - {os.path.basename(dzt_file)}\n")
    f.write("="*60 + "\n\n")
    f.write(f"Arquivo original: {dzt_file}\n")
    f.write(f"Data do processamento: {np.datetime64('now')}\n\n")
    
    f.write("PARÂMETROS DO PERFIL (ORIGINAIS):\n")
    f.write(f"  Comprimento total: {comprimento_total:.3f} m\n")
    f.write(f"  Posição inicial (X): {x_min_original:.3f} m\n")
    f.write(f"  Posição final (X): {x_max_original:.3f} m\n")
    f.write(f"  Número de traços: {len(x_positions)}\n")
    f.write(f"  Deslocamento aplicado para iniciar em 0: {deslocamento:.3f} m\n\n")
    
    f.write("PARÂMETROS DO PERFIL (AJUSTADOS - início em 0):\n")
    f.write(f"  Posição inicial (X): {x_min:.3f} m\n")
    f.write(f"  Posição final (X): {x_max:.3f} m\n\n")
    
    f.write("PARÂMETROS DE TEMPO/PROFUNDIDADE:\n")
    f.write(f"  Zero Time aplicado: 1.0 ns\n")
    f.write(f"  Tempo mínimo (TWTT): {t_min:.3f} ns\n")
    f.write(f"  Tempo máximo (TWTT): {t_max:.3f} ns\n")
    f.write(f"  Y-range usado: {yrng[0]:.1f} a {yrng[1]:.1f} ns\n")
    f.write(f"  Amostras por traço: {len(twtt)}\n")
    f.write(f"  Profundidade estimada: {profundidade_max:.2f} m (v={velocidade_estimada} m/ns)\n\n")
    
    f.write("CONFIGURAÇÃO DOS FRAMES:\n")
    f.write(f"  Largura da janela (x-range): {largura_janela} m\n")
    f.write(f"  Passo entre frames: {passo} m\n")
    f.write(f"  Total de frames gerados: {frame_num}\n")
    f.write(f"  X inicia em: 0 m\n")
    f.write(f"  Formato dos nomes: frame_XXXX_x[inicio]-[fim]m_y[ymin]-[ymax]ns\n\n")
    
    f.write("LISTA DE FRAMES GERADOS (X inicia em 0):\n")
    f.write("Frame | X-inicio (m) | X-fim (m) | Comprimento (m) | X-original-inicio | X-original-fim\n")
    f.write("-"*80 + "\n")
    
    # Recalcular para a lista
    x_temp = x_min
    for i in range(frame_num):
        x_fim_temp = min(x_temp + largura_janela, x_max)
        comprimento = x_fim_temp - x_temp
        x_orig_inicio = x_temp + deslocamento
        x_orig_fim = x_fim_temp + deslocamento
        f.write(f"{i:04d} | {x_temp:11.3f} | {x_fim_temp:9.3f} | {comprimento:14.3f} | {x_orig_inicio:17.3f} | {x_orig_fim:15.3f}\n")
        x_temp += passo

print("\n" + "="*60)
print(f"✅ PROCESSAMENTO CONCLUÍDO!")
print(f"📊 Total de frames gerados: {frame_num}")
print(f"📁 Diretório de saída: {output_dir}")
print(f"📄 Metadados salvos em: {info_file}")
print("="*60)