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
        arq_saida.write(sinopse)
        arq_saida.close()

    ## aplicação do regex
    def classificarComentarioRegex(self, texto):
        texto = texto.lower()

        padroes_positivos = [
            r"\bexcelent\w*", r"\botim\w*", r"\bmaravilh\w*", r"\bincr[ii]vel\w*",
            r"\bamei\b", r"\badorei\b", r"\bgostei\b", r"\bperfeit\w*",
            r"\bemocion\w*", r"\bdivertid\w*", r"\brecomend\w*", r"\btop\b"
        ]
        padroes_negativos = [
            r"\bruim\b", r"\bpessim\w*", r"\bhorr[ii]vel\w*", r"\bodi\w*",
            r"\bchato\w*", r"\bfraco\w*", r"\bdecepcion\w*", r"\blento\w*",
            r"\bcansativ\w*", r"\bpior\b", r"\bfrustr\w*", r"\bdesnecessar\w*"
        ]
        padroes_neutros = [
            r"\bregular\b", r"\bmediano\w*", r"\brazoavel\w*", r"\bnormal\b",
            r"\bok\b", r"\bmais ou menos\b", r"\bpassavel\w*"
        ]

        positivos = sum(len(re.findall(padrao, texto)) for padrao in padroes_positivos)
        negativos = sum(len(re.findall(padrao, texto)) for padrao in padroes_negativos)
        neutros = sum(len(re.findall(padrao, texto)) for padrao in padroes_neutros)

        if positivos > negativos:
            return 'Positivo'
        if negativos > positivos:
            return 'Negativo'
        if neutros > 0:
            return 'Neutro'
        return 'Neutro'
        
    def extrairComentariosFilme(self, filme, n):
        comentarios = []
        for i in range(1, n+1):
            url = 'https://www.adorocinema.com/filmes/' + filme + '/criticas/espectadores/?page=' + str(i)
            htmlComentarios = requests.get(url).text
            bsC = BeautifulSoup(htmlComentarios, 'html.parser')
            comentarios_com_tags = bsC.find_all('div', class_="content-txt review-card-content")
            for comentario_com_tag in comentarios_com_tags:
                texto_comentario = comentario_com_tag.get_text().strip()
                comentarios.append(
                    {
                        'texto': texto_comentario,
                        'categoria': self.classificarComentarioRegex(texto_comentario)
                    }
                )
        return comentarios
    
    ## quantidade de comentários e percentual de cada categoria
    def calcularEstatisticasCategorias(self, comentarios):
        total = len(comentarios)
        contagem = {'Positivo': 0, 'Neutro': 0, 'Negativo': 0}

        for comentario in comentarios:
            contagem[comentario['categoria']] += 1

        percentuais = {}
        for categoria, quantidade in contagem.items():
            percentuais[categoria] = (quantidade / total * 100) if total else 0.0

        return total, contagem, percentuais
    
    def salvarComentariosFilme(self, filme, comentarios):
        arq_saida = open(filme+'_comentarios.txt', 'w', encoding='utf-8')
        for indice, comentario in enumerate(comentarios, start=1):
            texto_quebrado = textwrap.fill(comentario['texto'], width=80)
            arq_saida.write(f"Comentario {indice}\n")
            arq_saida.write(f"Categoria: {comentario['categoria']}\n")
            arq_saida.write("Texto:\n")
            arq_saida.write(f"{texto_quebrado}\n\n")
        arq_saida.close()


filme = input('Digite o codigo do filme (ex.: filme-282076 ou 282076): ')
n = int(input('Digite quantas paginas de comentarios voce deseja consultar: '))

crawler = AdoroCinema()
filme_normalizado = crawler.normalizarCodigoFilme(filme)

try:
    sinopse = crawler.extrairSinopseFilme(filme_normalizado)
    crawler.salvarSinopseFilme(filme_normalizado, sinopse)
    comentarios = crawler.extrairComentariosFilme(filme_normalizado, n)
    crawler.salvarComentariosFilme(filme_normalizado, comentarios)
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