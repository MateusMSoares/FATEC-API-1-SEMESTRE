import json
from datetime import datetime, timedelta
import gerenciador_turmas as gerenciador_turmas


def listar_ciclos():
    with open("dados/ciclos.json", "r", encoding="utf-8") as f:
        return json.load(f)


def listar_ciclos_por_id_turma(id_turma):
    if not id_turma:
        return {}
    id_turma_str = str(id_turma)
    ciclos = listar_ciclos()
    ciclos_encontrados = {}
    for id_ciclo in ciclos.keys():
        if id_turma_str == ciclos[id_ciclo]["id_turma"]:
            ciclos_encontrados[id_ciclo] = ciclos[id_ciclo]
    return ciclos_encontrados


def obter_ciclo(id_ciclo):
    id_ciclo_str = str(id_ciclo)
    ciclos = listar_ciclos()
    if id_ciclo_str in ciclos.keys():
        return ciclos[id_ciclo_str]
    else:
        return None


def obter_ultimo_ciclo_por_id_turma(id_turma):
    id_turma_str = str(id_turma)
    ciclos = listar_ciclos_por_id_turma(id_turma_str)
    if len(ciclos) == 0:
        return None
    else:
        id_ultimo_ciclo = None
        ultimo_ciclo = None
        for id_ciclo in ciclos.keys():
            if not ultimo_ciclo:
                ultimo_ciclo = ciclos[id_ciclo]
                id_ultimo_ciclo = id_ciclo
            if ultimo_ciclo["numero_ciclo"] > ciclos[id_ciclo]["numero_ciclo"]:
                ultimo_ciclo = ciclos[id_ciclo]["numero_ciclo"]
                id_ultimo_ciclo = id_ciclo
        return id_ultimo_ciclo, ultimo_ciclo


def adicionar_ciclo(ciclo):
    ciclos = listar_ciclos()
    ciclos_por_id_turma = listar_ciclos_por_id_turma(ciclo["id_turma"])
    numero_ciclo = (
        len(ciclos_por_id_turma) + 1
    )  # em caso de remoção de ciclo, alterar essa linha ou tratar na remoção
    ciclo["numero_ciclo"] = numero_ciclo
    novo_id_ciclo = _obter_novo_id_ciclo()
    ciclos[novo_id_ciclo] = ciclo
    return _salvar_ciclos(ciclos)


def editar_ciclo(id_ciclo, ciclo_atualizado):
    from regra_de_negocio import gerenciador_notas

    try:
        id_ciclo_str = str(id_ciclo)
        ciclos = listar_ciclos()
        if id_ciclo_str in ciclos.keys():
            ciclos[id_ciclo_str]["id_turma"] = ciclo_atualizado["id_turma"]
            ciclos[id_ciclo_str]["duracao"] = int(ciclo_atualizado["duracao"])
            ciclos[id_ciclo_str]["peso_nota"] = float(ciclo_atualizado["peso_nota"])
            ciclos[id_ciclo_str]["numero_ciclo"] = int(ciclo_atualizado["numero_ciclo"])
            ciclos[id_ciclo_str]["prazo_insercao_nota"] = int(
                ciclo_atualizado["prazo_insercao_nota"]
            )
            ciclos[id_ciclo_str]["nome_ciclo"] = str(ciclo_atualizado["nome_ciclo"])
            _salvar_ciclos(ciclos)
        else:
            raise KeyError("Ciclo não encontrado.")
        gerenciador_notas.atualiza_todos_fee_da_turma(
            ciclos[id_ciclo_str]["id_turma"]
        )
    except KeyError as e:
        return f"Falha na edição: {str(e)}"


def _obter_novo_id_ciclo():
    ids_numericos = []
    ids_numericos.append(0)
    ciclos = listar_ciclos()
    for id_str in ciclos.keys():
        id_int = int(id_str)
        ids_numericos.append(id_int)
    ids_numericos.sort()
    id_max_int = ids_numericos.pop()
    novo_id = str(id_max_int + 1)
    return novo_id


def _salvar_ciclos(ciclos):
    dados = json.dumps(ciclos, indent=4)
    with open("dados/ciclos.json", "w", encoding="utf-8") as f:
        f.write(dados)
        return True


def detalhes_ciclos_turma(turma_info, id_turma):
    id_turma_str = str(id_turma)
    data_atual = datetime.now()
    data_inicio = datetime.strptime(turma_info["data_de_inicio"], "%d/%m/%Y")
    duracao_ciclo = int(turma_info["duracao_ciclo"])
    ciclos = listar_ciclos_por_id_turma(id_turma_str)
    quantidade_ciclos = int(turma_info["quantidade_ciclos"])
    ciclo_atual = None
    ciclo_aberto_para_nota = None

    for ciclo_numero, ciclo_info in ciclos.items():
        if ciclo_info["id_turma"] == id_turma_str:
            prazo_insercao = ciclo_info["prazo_insercao_nota"]

    for i in range(quantidade_ciclos):
        # Calcular o final do ciclo
        data_final_ciclo = data_inicio + timedelta(days=duracao_ciclo * (i + 1))

        # Verificar se estamos no ciclo atual
        if data_atual < data_final_ciclo:
            ciclo_atual = i + 1
            break
        # Verificar se o ciclo está aberto para notas
        if (
            data_final_ciclo + timedelta(days=1)
            <= data_atual
            <= data_final_ciclo + timedelta(prazo_insercao)
        ):
            ciclo_aberto_para_nota = i + 1
    else:
        # Nenhum ciclo aberto, estamos no último ciclo
        ciclo_atual = quantidade_ciclos
    info_turma = {
        "data_final_ciclo": str(data_final_ciclo),
        "ciclo_atual": ciclo_atual,
        "ciclo_aberto_para_nota": ciclo_aberto_para_nota,
    }
    return info_turma


def excluir_ciclo_da_turma(id_turma):
    ciclos_da_turma = listar_ciclos_por_id_turma(id_turma)
    if not ciclos_da_turma:
        return

    todos_os_ciclos = listar_ciclos()
    ciclos_a_manter = {
        id_ciclo: ciclo
        for id_ciclo, ciclo in todos_os_ciclos.items()
        if ciclo["id_turma"] != id_turma
    }

    _salvar_ciclos(ciclos_a_manter)


def cria_ciclos_pra_turma(id_nova_turma, info_global_settings):
    for i in range(int(info_global_settings["quant_ciclos"])):
        ciclo = {}
        ciclo["id_turma"] = id_nova_turma
        ciclo["duracao"] = int(info_global_settings["quant_dias_ciclo"])
        ciclo["peso_nota"] = float(i + 1)
        ciclo["numero_ciclo"] = i + 1
        ciclo["prazo_insercao_nota"] = int(info_global_settings["prazo_insercao_nota"])
        ciclo["nome_ciclo"] = "ciclo#" + str(ciclo["numero_ciclo"])
        adicionar_ciclo(ciclo)

def obter_datas_ciclos(id_turma):
    id_turma_str = str(id_turma)
    turma = gerenciador_turmas.obter_turma(id_turma_str)
    formato_data = "%d/%m/%Y"
    data_inicio = turma["data_de_inicio"]
    duracao_ciclo = int(turma['duracao_ciclo'])
    ciclos = listar_ciclos_por_id_turma(id_turma)
    data_de_inicio_ciclos = {}
    data_de_inicio_ciclo = datetime.strptime(data_inicio, formato_data)
    
    for id_ciclo in ciclos:
        data_de_fim_ciclo = data_de_inicio_ciclo + timedelta(days=duracao_ciclo)

        data_de_inicio_ciclos[id_ciclo] = {
            "data_de_inicio_ciclo": data_de_inicio_ciclo.strftime(formato_data),
            "data_de_fim_ciclo": data_de_fim_ciclo.strftime(formato_data)
        }
        data_de_inicio_ciclo = data_de_fim_ciclo + timedelta(days=1)
    return data_de_inicio_ciclos

# def _verificar_duplicidade(id_ciclo, ciclo, ciclos):
#     try:
#         id_ciclo_textual = str(id_ciclo)
#         if ciclo and id_ciclo_textual not in ciclos.keys():
#             for c in ciclos:
#                 if ciclo["id_turma"] == c["id_turma"] and ciclo["numero_ciclo"] == c["numero_ciclo"]:
#                     return True
#             return False
#         else:
#             return True
#     except:
#         return True

# def editar_ciclo(id_ciclo, ciclo):
#     if id_ciclo == None or ciclo == None:
#         return False
#     try:
#         id_ciclo_textual = str(id_ciclo)
#         ciclos = listar_ciclos()
#         if id_ciclo_textual in ciclos:
#             ciclos[id_ciclo_textual] = ciclo
#             return _salvar_ciclos(ciclos)
#         return False
#     except:
#         return False
