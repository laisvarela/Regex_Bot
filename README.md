# Regex Bot - Analise de comentarios de filmes

## Objetivo do trabalho
Este trabalho tem como objetivo coletar comentarios de espectadores no site AdoroCinema e aplicar expressoes regulares para classificar cada comentario como Positivo, Neutro ou Negativo.

O programa:
- le a sinopse de um filme;
- le comentarios de uma ou mais paginas;
- classifica os comentarios por categoria de sentimento com regex;
- calcula quantidade e percentual por categoria;
- salva os resultados em arquivos de texto.

## Estrutura geral
Arquivo principal: `crawler.py`
Classe principal: `AdoroCinema`

## Metodos (entrada, processamento e saida)

### 1) extrairSinopseFilme(self, filme)
**Entrada**
- `filme` (string): codigo do filme no formato usado na URL do AdoroCinema (exemplo: `filme-282076`).

**Processamento**
- monta a URL do filme;
- faz requisicao HTTP da pagina;
- interpreta o HTML com BeautifulSoup;
- busca o elemento `div` com classe `content-txt`;
- se nao encontrar, lança `ValueError`.

**Saida**
- retorna uma string com a sinopse limpa.

### 2) salvarSinopseFilme(self, filme, sinopse)
**Entrada**
- `filme` (string): codigo do filme;
- `sinopse` (string): texto da sinopse.

**Processamento**
- abre/cria o arquivo `<filme>_sinopse.txt` em UTF-8;
- quebra o texto em linhas de largura 80 (`textwrap.fill`);
- escreve no arquivo e fecha.

**Saida**
- gera o arquivo de sinopse no diretorio do projeto.

### 3) classificarComentarioRegex(self, texto)
**Entrada**
- `texto` (string): comentario de usuario.

**Processamento**
- converte o texto para minusculas;
- aplica listas de padroes regex positivos, negativos, negativos fortes e neutros;
- conta ocorrencias com `re.findall`;
- decide a categoria com base nas contagens.

**Saida**
- retorna uma string com a categoria: `Positivo`, `Neutro` ou `Negativo`.

### 4) extrairComentariosFilme(self, filme, n)
**Entrada**
- `filme` (string): codigo do filme;
- `n` (int): quantidade de paginas de comentarios a consultar.

**Processamento**
- percorre as paginas de 1 ate `n`;
- monta a URL de comentarios para cada pagina;
- faz requisicao HTTP e parseia HTML;
- extrai blocos de comentarios (`div.content-txt.review-card-content`);
- ignora comentarios vazios;
- classifica cada comentario com `classificarComentarioRegex`;
- monta uma lista de dicionarios com texto e categoria.

**Saida**
- retorna uma lista no formato:
  - `{'texto': <comentario>, 'categoria': <categoria>}`.

### 5) calcularEstatisticasCategorias(self, comentarios)
**Entrada**
- `comentarios` (list): lista de dicionarios com chaves `texto` e `categoria`.

**Processamento**
- calcula o total de comentarios;
- conta quantos comentarios existem em cada categoria;
- calcula o percentual por categoria.

**Saida**
- retorna uma tupla com 3 itens:
  1. `total` (int)
  2. `contagem` (dict)
  3. `percentuais` (dict)

### 6) salvarComentariosFilme(self, filme, comentarios)
**Entrada**
- `filme` (string): codigo do filme;
- `comentarios` (list): comentarios classificados.

**Processamento**
- abre/cria o arquivo `<filme>_comentarios.txt` em UTF-8;
- percorre os comentarios com indice;
- quebra o texto em linhas de largura 80 (`textwrap.fill`);
- grava numero do comentario, categoria e texto formatado.

**Saida**
- gera o arquivo de comentarios classificados no diretorio do projeto.

## Fluxo de execucao do programa
1. Le o codigo do filme e a quantidade de paginas.
2. Extrai e salva a sinopse.
3. Extrai comentarios e classifica cada um.
4. Salva comentarios em arquivo.
5. Calcula estatisticas por categoria.
6. Exibe no console total e percentuais.
7. Trata erros HTTP e erros gerais.

## Dependencias
- requests
- beautifulsoup4

## Como executar
No terminal, dentro da pasta do projeto:

```bash
python crawler.py
```
