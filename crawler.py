import requests
import re
import textwrap
from bs4 import BeautifulSoup


class AdoroCinema:
    
    def extrairSinopseFilme (self, filme):
        url = "https://www.adorocinema.com/filmes/" + filme + '/'
        htmlFilme = requests.get(url).text
        bsS = BeautifulSoup(htmlFilme, 'html.parser')
        sinopse_tag = bsS.find('div', class_="content-txt")
        if not sinopse_tag:
            raise ValueError("Nao foi possivel localizar a sinopse. Verifique o codigo do filme e se a pagina mudou.")
        sinopse = sinopse_tag.get_text(strip=True)
        return sinopse

    def salvarSinopseFilme(self, filme, sinopse):
        arq_saida = open (filme+'_sinopse.txt', 'w', encoding='utf-8')
        sinopse_quebrada = textwrap.fill(sinopse, width=80)
        arq_saida.write(sinopse_quebrada)
        arq_saida.close()

    def extrairComentariosFilme(self, filme, n):
        comentarios = []
        for i in range(1, n+1):
            url = 'https://www.adorocinema.com/filmes/' + filme + '/criticas/espectadores/?page=' + str(i)
            htmlComentarios = requests.get(url).text
            bsC = BeautifulSoup(htmlComentarios, 'html.parser')
            comentarios_com_tags = bsC.find_all('div', class_="content-txt review-card-content")
            for comentario_com_tag in comentarios_com_tags:
                texto_comentario = comentario_com_tag.get_text().strip()
                if len(texto_comentario) == 0:
                    continue
                comentarios.append(
                    {
                        'texto': texto_comentario,
                        'categoria': self.classificarComentarioRegex(texto_comentario)
                    }
                )

        if len(comentarios) == 0:
            print("Nao ha comentarios ainda.")
        return comentarios
    
    def classificarComentarioRegex(self, texto):
        texto = texto.lower()

        # * = zero ou mais repetições
        # \w = caractere -> letras, números e _
        padroes_positivos = [
            r"\bexcelent\w*", r"\botim\w*", r"\bmaravilh\w*", r"\bincr[ií]vel\w*",
            r"\bamei\b", r"\badorei\b", r"\bgostei\b", r"\bperfeit\w*",
            r"\bemocion\w*", r"\bdivertid\w*", r"\brecomend\w*", r"\btop\b",
            r"\bextraordin[aá]ri\w*", r"\bfeliz\b", r"\bsurpreendente\b", 
            r"\bexcelente\b", r"\b[oó]timo roteiro\b", r"\blind\w*", r"\bimpec[aá]vel\b",
            r"\bmuito bom\b", r"\bentrega muito\b", r"\bgag\b", r"fant[aá]stic\w",
            r"\bme fez chorar\b", r"\beletrizante\b", r"\bmelhor filme\b", r"\bfavorito\b"
        ]
        padroes_negativos = [
            r"\bruim\b", r"\bp[eé]ssim\w*", r"\bhorr[ií]vel\w*", r"\bodi\w*",
            r"\bchato\w*", r"\bfraco\w*", r"\bdecepcion\w*", r"\blento\w*",
            r"\bcansativ\w*", r"\bpior\b", r"\bfrustr\w*", r"\bdesnecessar\w*",
            r"\bn[aã]o gostei\b", r"\binfeliz\b", r"\bchatead\w*", r"\bdesperd[ií]ci\w*",
            r"\bn[aã]o recomendo\b", r"\bbobagem\b", r"\bburacos? de roteiro\b",
            r"\bfalta de coer[eê]ncia\b", r"\broteiro confuso\b", r"\bsem sentido\b"
        ]
        padroes_negativos_fortes = [
            r"\bdesperd[ií]ci\w* de potencial\b",
            r"\bburacos? de roteiro\b",
            r"\bfalta de coer[eê]ncia\b",
            r"\bn[aã]o recomendo\b",
            r"\bp[eé]ssim\w*\b"
        ]
        padroes_neutros = [
            r"\bregular\b", r"\bmediano\w*", r"\brazoavel\w*", r"\bnormal\b",
            r"\bok\b", r"\bmais ou menos\b", r"\bpassavel\w*", r"\bmeh\b"
        ]

        positivos = sum(len(re.findall(padrao, texto)) for padrao in padroes_positivos)
        negativos = sum(len(re.findall(padrao, texto)) for padrao in padroes_negativos)
        neutros = sum(len(re.findall(padrao, texto)) for padrao in padroes_neutros)
        negativos_fortes = sum(len(re.findall(padrao, texto)) for padrao in padroes_negativos_fortes)

        # Comentarios com termos fortemente negativos devem pender para "Negativo",
        # mesmo quando aparece uma palavra positiva fora de contexto (ex.: "exemplo perfeito de desperdicio").
        if negativos_fortes > 0 and negativos >= positivos:
            return 'Negativo'
        if positivos > negativos:
            return 'Positivo'
        if negativos > positivos:
            return 'Negativo'
        if neutros > 0:
            return 'Neutro'
        return 'Neutro'
    
    def salvarComentariosFilme(self, filme, comentarios):
        arq_saida = open(filme+'_comentarios.txt', 'w', encoding='utf-8')
        for indice, comentario in enumerate(comentarios, start=1):
            texto_quebrado = textwrap.fill(comentario['texto'], width=80)
            arq_saida.write(f"Comentario {indice}\n")
            arq_saida.write(f"Categoria: {comentario['categoria']}\n")
            arq_saida.write("Texto:\n")
            arq_saida.write(f"{texto_quebrado}\n\n")
        arq_saida.close()
        
    def calcularEstatisticasCategorias(self, comentarios):
        total = len(comentarios)
        contagem = {'Positivo': 0, 'Neutro': 0, 'Negativo': 0}

        for comentario in comentarios:
            contagem[comentario['categoria']] += 1

        percentuais = {}
        for categoria, quantidade in contagem.items():
            percentuais[categoria] = (quantidade / total * 100) if total else 0.0

        return total, contagem, percentuais


filme = input('Digite o codigo do filme (ex.: filme-282076): ')
n = int(input('Digite quantas paginas de comentarios voce deseja consultar: '))

crawler = AdoroCinema()

try:
    sinopse = crawler.extrairSinopseFilme(filme)
    crawler.salvarSinopseFilme(filme, sinopse)
    comentarios = crawler.extrairComentariosFilme(filme, n)
    crawler.salvarComentariosFilme(filme, comentarios)
    total, contagem, percentuais = crawler.calcularEstatisticasCategorias(comentarios)

    print(f'Total de comentarios lidos: {total}')
    for categoria in ['Positivo', 'Neutro', 'Negativo']:
        print(f"{categoria}: {contagem[categoria]} ({percentuais[categoria]:.2f}%)")
    print('Programa executado com sucesso. Consulte os arquivos gerados com a sinopse e os comentarios do filme.')
except requests.exceptions.HTTPError as erro:
    if erro.response is not None and erro.response.status_code == 404:
        print('Filme nao encontrado no AdoroCinema. Informe o codigo da URL no formato filme-XXXXX (ou apenas XXXXX).')
    else:
        print('Erro HTTP ao acessar o site:', erro)
except Exception as erro:
    print('Ocorreu um erro:', erro)