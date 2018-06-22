<p align="center">
  <img src="https://i.imgur.com/MzLyuR4.gif">
</p>

# Q-Learning Snake Game

A attempt to apply machine learning to the classic Snake game using the Q-learning technique.
  
O programa deve ser utilizado pela linha de comando, existem apenas dois comandos train e run.

Se quiser interromper o treinamento, a qualquer momento basta focar na janela e apertar ESC, o treinamento é interrompido e as estatisticas e memória são salvas. 

Todos os dados importados ou exportados pelo programa se encontram na pasta data.

Argumentos

World

Padrão: default

Indica em qual mundo o agente deve treinar, é ignorado caso utilize um arquivo de configuração. O nome do mundo não precisa ter extensão visto que todos devem ser do tipo json.

    --world times

Speed

Padrão: 10

Indica a velocidade da simulação, é usado diretamente pelo PyGame para limitar o número de quadros por segundo, use -1 para retirar essa limitação.

    --speed 20

Memory

Padrão: gerado automáticamente

Indica o nome do arquivo de memória que deve ser importado ou exportado.

    --memory super_cool_memory_name

Epsilon

Padrão: default

Indica um valor constante ou o nome de uma função para ser utilizada como epsilon, este indica a probabilidade do agente não seguir as regras e selecionar uma ação qualquer. Você pode criar sua própria função editando o módulo epsilons.py. 

    --epsilon linear
    --epsilon 0.4

Learn

Padrão: 0.75

Indica a taxa de aprendizado do agente.

    --learn 0.6

Discount

Padrão: 0.9

Indica o fator de desconto do agente.

    --discount 0.8

View Size

Padrão: 16

Indica o tamanho que as unidades do mundo devem ser exibidas.

    --view-size 32

View Enable

Padrão: True

Indica se a simulação deve ser exbida na tela.

    --view-enable 0

Configuration

Padrão: nenhum

Indica um arquivo de configuração a ser usado. Para sessões de treinamento mais complexas deve ser utilizado esses arquivos para usar outros tipos de memórias e adaptadores assim como ciclos e mapas.

    --config small_worlds_config.json

Stats Directory

Padrão: data/statistics

lndica o diretório onde será salvo as estatísticas da sessão.

    --stats-dir some/other/directory

No Stats

Padrão: false

Desabilita a saída de arquivos de estatística.

    --no-stats



