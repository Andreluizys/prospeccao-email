# Como escrever cada e-mail

Você está escrevendo um e-mail de prospecção comercial B2B, em nome do representante descrito em `config.json`, para UMA empresa cujo site foi pesquisado.

## 1. Entenda a empresa (a partir dos dados coletados do site)
- **Segmento**: setor amplo (ex.: indústria metalúrgica, varejo de moda, clínica odontológica, construtora).
- **Nicho**: o que ela faz de específico (ex.: "usinagem de peças para o setor automotivo", "moda praia feminina").
- **Porte e público**: B2B ou B2C, regional ou nacional, sinais de tamanho (filiais, anos de mercado, clientes citados).
- **Contato**: nome de pessoa (diretor, compras, sócio) se aparecer; senão, use saudação neutra. O melhor e-mail é o da própria planilha; se não houver, escolha no `emails_site` o mais comercial (compras@, comercial@, contato@), nunca e-mails de RH, NF-e, financeiro ou contabilidade, a menos que seja o único.
- **Gancho**: um detalhe real e específico do site (um produto, uma certificação, tempo de mercado, um segmento atendido, uma novidade). Nunca invente fatos.

## 2. Ligue a necessidade dela à oferta do representante
Escolha em `config.json → oferta` o produto/serviço que faz mais sentido para ESSE nicho e explique o benefício em termos do negócio dela (custo, prazo, qualidade, imagem da marca, giro de estoque...). Um benefício principal bem conectado vale mais que uma lista.

## 3. Estrutura do e-mail
- **Assunto**: até ~60 caracteres, específico, sem caixa alta, sem "!!!", sem palavras de spam (grátis, promoção, urgente, ganhe). Ex.: "Etiquetas para a linha de peças da Metalúrgica X".
- **Saudação**: "Olá, [Nome]," ou "Prezados, equipe [Empresa],".
- **Abertura (1–2 frases)**: mostre que você olhou o site dela, com o gancho.
- **Proposta (2–3 frases)**: quem você representa, o que oferece e por que serve para ela.
- **Chamada para ação (1 frase)**: um pedido simples e de baixo esforço (ex.: "Posso enviar um orçamento sem compromisso?", "Faz sentido conversarmos 10 minutos esta semana?").
- **Assinatura**: use exatamente `config.json → assinatura`.
- **Descadastro**: termine com a linha `config.json → linha_descadastro` (o script de envio adiciona automaticamente se faltar).

## 4. Regras de estilo
- Tom: `config.json → tom` (padrão: profissional, cordial, direto). Português do Brasil correto.
- 90 a 160 palavras no corpo. Parágrafos curtos. Texto puro, sem markdown, sem emojis, sem links encurtados.
- Nada de frases genéricas que serviriam para qualquer empresa ("espero que esteja bem", "somos líderes de mercado").
- Cada e-mail deve ser visivelmente diferente dos outros: gancho, benefício e assunto próprios.
- Se o site não carregou ou não há informação suficiente, escreva um e-mail curto e honesto baseado no nome/segmento da planilha e marque `observacao: "pouca informação"`.
- Se a empresa claramente não é público-alvo (concorrente, órgão público, site fora do ar/à venda, outro país), não escreva: devolva `status: "Descartado"` com o motivo em `observacao`.

## 5. Formato de saída (uma linha JSON por empresa, em `emails.jsonl`)
```json
{"_entrada": "<copie de pesquisa.jsonl>", "empresa": "", "email": "", "contato": "", "site": "", "segmento": "", "nicho": "", "assunto": "", "corpo": "", "status": "Rascunho", "observacao": ""}
```
Use `\n` para quebras de linha dentro de `corpo`.
