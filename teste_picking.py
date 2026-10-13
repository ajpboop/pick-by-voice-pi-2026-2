import time
import banco
from tts import falar
from stt import ouvir

def iniciar_separacao_por_voz(numero_pedido, nome_colaborador):
    conexao = banco.conectar()
    cursor = conexao.cursor()
    
    cursor.execute('''
        SELECT prod.nome, i.quantidade, prod.corredor, prod.prateleira, prod.lugar 
        FROM itens_pedido i
        JOIN produtos prod ON i.produto_id = prod.id
        WHERE i.pedido_id = ?
    ''', (numero_pedido,))
    itens = cursor.fetchall()
    conexao.close()
    
    if not itens:
        falar(f"A ordem {numero_pedido} não foi encontrada ou não tem itens.")
        return

    falar(f"Iniciando separação da ordem {numero_pedido}.")
    time.sleep(1)
    
    # Listas de sinônimos para os comandos de voz
    palavras_repetir = ["repete", "repetir", "de novo", "novamente", "repita"]
    palavras_confirmar = ["confirmar", "ok", "feito", "pronto", "certo", "concluído"]
    
    for item in itens:
        nome_produto = item[0]
        quantidade = item[1]
        corredor = item[2] if item[2] else "não definido"
        prateleira = item[3] if item[3] else "não definida"
        lugar = item[4] if item[4] else "não definido"
        
        # --- PASSO 1: LOCALIZAÇÃO ---
        instrucao_local = f"Ir para Corredor {corredor}, Prateleira {prateleira}, Posição {lugar}."
        falar(instrucao_local)
        
        confirmado = False
        while not confirmado:
            resposta = ouvir()
            
            if resposta:
                resposta_lower = resposta.lower()
                
                # Verifica se o operador pediu para repetir
                if any(palavra in resposta_lower for palavra in palavras_repetir):
                    falar(instrucao_local)
                
                # Verifica se o operador confirmou com qualquer um dos sinônimos
                elif any(palavra in resposta_lower for palavra in palavras_confirmar):
                    confirmado = True
                    
                # Caso diga algo irreconhecível
                else:
                    falar("Diga 'pronto' quando chegar, ou 'repetir' para ouvir de novo.")
            else:
                time.sleep(0.5)

        # --- PASSO 2: ITEM E QUANTIDADE ---
        instrucao_item = f"Separar {quantidade} unidades do item {nome_produto}."
        falar(instrucao_item)
        
        confirmado = False
        while not confirmado:
            resposta = ouvir()
            
            if resposta:
                resposta_lower = resposta.lower()
                
                # Verifica se pediu para repetir
                if any(palavra in resposta_lower for palavra in palavras_repetir):
                    falar(instrucao_item)
                    
                # Verifica a confirmação (sinônimos) ou se ele disse a quantidade exata
                elif any(palavra in resposta_lower for palavra in palavras_confirmar) or str(quantidade) in resposta_lower:
                    falar("Item confirmado.")
                    confirmado = True
                    
                # Caso erre a quantidade ou diga algo irreconhecível
                else:
                    falar(f"Não validado. Diga a quantidade, 'feito' ou 'repetir'.")
            else:
                time.sleep(0.5)
                
    falar("Ordem finalizada com sucesso. Sistema atualizado.")
    banco.concluir_pedido_e_atualizar_estoque(numero_pedido, nome_colaborador)

if __name__ == "__main__":
    iniciar_separacao_por_voz(1, "Operador Teste")