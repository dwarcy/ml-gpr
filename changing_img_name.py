import os

def adicionar_sufixo_a_imagens(caminho_pasta, sufixo):
    """
    Renomeia todas as imagens em uma pasta, adicionando um sufixo ao nome.

    Args:
        caminho_pasta (str): O caminho completo para a pasta com as imagens.
        sufixo (str): O sufixo a ser adicionado (ex: "_novo").
    """
    # 1. Lista de extensões de imagens que queremos renomear
    extensoes_imagens = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

    # 2. Iterar sobre todos os itens na pasta
    for nome_arquivo_antigo in os.listdir(caminho_pasta):
        caminho_antigo = os.path.join(caminho_pasta, nome_arquivo_antigo)

        # 3. Ignorar subpastas e garantir que é um arquivo
        if os.path.isfile(caminho_antigo):
            # 4. Separar o nome base do arquivo e a extensão
            nome_base, extensao = os.path.splitext(nome_arquivo_antigo)
            
            # Converter a extensão para minúsculas para facilitar a comparação
            extensao_lower = extensao.lower()

            # 5. Checar se a extensão está na nossa lista de imagens
            if extensao_lower in extensoes_imagens:
                
                # 6. Criar o novo nome com o sufixo antes da extensão
                novo_nome = nome_base + sufixo + extensao
                caminho_novo = os.path.join(caminho_pasta, novo_nome)
                
                try:
                    # 7. Renomear o arquivo
                    os.rename(caminho_antigo, caminho_novo)
                    print(f"Renomeado: {nome_arquivo_antigo} -> {novo_nome}")
                except Exception as e:
                    print(f"Erro ao renomear {nome_arquivo_antigo}: {e}")
            # else:
            #     print(f"Ignorado: {nome_arquivo_antigo} (não é uma imagem na lista)")

# --- CONFIGURAÇÃO ---

# ⚠️ PASSO 1: Mude este caminho para o caminho da sua pasta de imagens!
# Exemplo no Windows: 'C:\\Users\\SeuNome\\Imagens\\fotos_ferias'
# Exemplo no Linux/Mac: '/home/seu-usuario/Imagens/fotos_ferias'
PASTA_DAS_IMAGENS = '/home/renata/ml-gpr/imagens/dzt_125' # Substitua pelo caminho real

# ⚠️ PASSO 2: Defina o sufixo que você quer adicionar.
# Lembre-se de incluir um separador (como '_' ou '-') se necessário.
SUFIXO_A_ADICIONAR = "_dzt125"

# --------------------

if __name__ == "__main__":
    print(f"Iniciando a renomeação na pasta: {PASTA_DAS_IMAGENS}")
    print(f"Sufixo a ser adicionado: {SUFIXO_A_ADICIONAR}\n")

    # Verifica se a pasta existe antes de tentar rodar
    if os.path.isdir(PASTA_DAS_IMAGENS):
        adicionar_sufixo_a_imagens(PASTA_DAS_IMAGENS, SUFIXO_A_ADICIONAR)
        print("\nProcesso concluído!")
    else:
        print(f"ERRO: A pasta '{PASTA_DAS_IMAGENS}' não foi encontrada.")
        print("Por favor, verifique se o caminho no script está correto.")