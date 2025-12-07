#importar bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class AnalisadorDesempenho:
    def __init__(self, arquivo_csv):
        #Base dados ja foi filtrada no arquivo traab.ipynb
        #Algumas colunas irrelevantes para a analise foram removidas
        try:
            self.df = pd.read_csv(arquivo_csv)
            print(f"Total de registros: {len(self.df)}")
            print(f"Colunas: {', '.join(self.df.columns)}\n")
        except FileNotFoundError:
            print(f"Arquivo '{arquivo_csv}' não encontrado!")
            exit()
    
    def exibir_colunas(self):
        #programa printa colunas relevantes do projeto
        print("COLUNAS")
        print("/"*30)
        for i, col in enumerate(self.df.columns, 1):
            tipo = self.df[col].dtype
            valores_unicos = self.df[col].nunique()
            print(f"{i}. {col}")
        print("/"*30+ "\n")
    
    def validar_coluna(self, nome_coluna):
        #Verifica se coluna existe
        if nome_coluna not in self.df.columns:
            print(f"Coluna '{nome_coluna}' não encontrada!")
            return False
        return True
    
    def analisar_relacao(self, col1, col2):
        # Separar variaveis
        # Um dos maiores desafios do projeto foi em determinar qual analise utilizar para diferentes tipos de dados
        # Obejtivo da func é verficar pares de colunas baseados em tipos de dados
        cat1 = self.categorica(col1)
        cat2 = self.categorica(col2)
        if cat1 and not cat2:
            return self.comparar_grupos(col1, col2)
        elif cat2 and not cat1:
            return self.comparar_grupos(col2, col1)
        elif not cat1 and not cat2:
            return self.numericas(col1, col2)
        else:
            return self.categoricas(col1, col2)
    def categorica(self, coluna):
        return coluna in ['sex', 'internet'] or self.df[coluna].dtype == 'object'
    
    def comparar_grupos(self, col_categorica, col_numerica):
        #Compara var numeric.
        grupos = self.df.groupby(col_categorica)[col_numerica]
        
        dicio_estat = {}
        for nome_grupo, dados in grupos:
            dicio_estat[nome_grupo] = {
                'media': dados.mean(),
                'mediana': dados.median(),
                'desvio_padrao': dados.std(),
                'minimo': dados.min(),
                'maximo': dados.max(),
                'contagem': len(dados)
            }
        return {
            'tipo': 'comparacao_grupos',
            'col_categorica': col_categorica,
            'col_numerica': col_numerica,
            'estatisticas': dicio_estat
        }
    
    def numericas(self, col1, col2):
        # analisar var nums
        # Dividir col1 em faixas e comparar col2
        
        
        data_col1 = self.converter_num(col1)
        data_col2 = self.converter_num(col2)

        if data_col1 is None or data_col2 is None:
            return None

        try:
            col1_faixas = pd.qcut(data_col1, q=3, labels=['Baixo', 'Médio', 'Alto'], duplicates='drop')
        except ValueError:
            # Implementação alternativa para colunas com poucos valores únicos (como tempo de estudo)
            min_val = data_col1.min()
            max_val = data_col1.max()
            # Cria 3 bins para dividir a faixa de valores
            bins = np.linspace(min_val, max_val, 4) 
            # Ajuste de precisão para garantir que o valor máximo entre no último bin
            bins[-1] += 1e-6 
            col1_faixas = pd.cut(data_col1, bins=bins, labels=['Baixo', 'Médio', 'Alto'], include_lowest=True, right=True)
            
        dicio_2 = {}
        for faixa in col1_faixas.unique():
           
            dados = data_col2[col1_faixas == faixa]
            if len(dados) == 0:
                continue
                
            dicio_2[faixa] = {
                'media': dados.mean(),
                'mediana': dados.median(),
                'desvio_padrao': dados.std(),
                'minimo': dados.min(),
                'maximo': dados.max(),
                'contagem': len(dados)
            }
        
        return {
            'tipo': 'comparacao_faixas',
            'col_faixas': col1,
            'col_numerica': col2,
            'estatisticas': dicio_2
        }
    
    def categoricas(self, col1, col2):
        #analise var categorica
        tabela = pd.crosstab(self.df[col1], self.df[col2])
        return {
            'tipo': 'tabela_cruzada',
            'col1': col1,
            'col2': col2,
            'tabela': tabela
    
        }
    def converter_num(self, coluna):
        # transformar para numeric
        dados = self.df[coluna].copy()
        if pd.api.types.is_numeric_dtype(dados):
            return dados
        if coluna == 'sex':
            return dados.map({'M': 1, 'F': 0})
        elif coluna == 'internet':
            return dados.map({'yes': 1, 'no': 0})
        else:
            try:
                return pd.to_numeric(dados)
            except:
                print(f"Não foi possível converter '{coluna}' para numérico")
                return None
    def interpretar_correlacao(self, valor):
        # valor da correlac.
        corre = abs(valor)
        if corre < 0.3:
            forca = "fraca"
        elif corre < 0.7:
            forca = "moderada"
        else:
            forca = "forte"
        direcao = "positiva" if valor > 0 else "negativa"
        return f"{forca} {direcao}"
    
    def exibir_estat(self, col1, col2, resultado):
        print("\n" + "/"*30)
        print("ANÁLISE")
        print(" ")
        if resultado['tipo'] == 'comparacao_grupos':
            col_cat = resultado['col_categorica']
            col_num = resultado['col_numerica']
            print(f"Comparação de '{col_num}' e '{col_cat}'")
            print("-"*30)
            for grupo, stats in resultado['estatisticas'].items():
                print(f"Grupo: {grupo}")
                print(f"Média: {stats['media']:.2f}")
                print(f"Mediana: {stats['mediana']:.2f}")
                print(f"Desvio Padrão: {stats['desvio_padrao']:.2f}")
                print(f"Mínimo: {stats['minimo']:.2f}")
                print(f"Máximo: {stats['maximo']:.2f}")
                print(f"Quantidade de alunos: {stats['contagem']}")
            #Comparaçao
            medias = {k: v['media'] for k, v in resultado['estatisticas'].items()}
            grupo_maior = max(medias, key=medias.get)
            grupo_menor = min(medias, key=medias.get)
            diferenca = medias[grupo_maior] - medias[grupo_menor]
            
            print("\n" + "/"*30)
            print("COMPARACAO:")
            print(f"Maior média: {grupo_maior} ({medias[grupo_maior]:.2f})")
            print(f"Menor média: {grupo_menor} ({medias[grupo_menor]:.2f})")
            print(f"Diferença entre grupos: {diferenca:.2f}")
        elif resultado['tipo'] == 'comparacao_faixas':
            col_faixas = resultado['col_faixas']
            col_num = resultado['col_numerica']
            print(f"Comparação de '{col_num}' por faixas de '{col_faixas}'")
            print("-"*60)
            for faixa, estats in resultado['estatisticas'].items():
                print(f"Faixa: {faixa}")
                print(f"Média: {estats['media']:.2f}")
                print(f"Mediana: {estats['mediana']:.2f}")
                print(f"Desvio Padrão: {estats['desvio_padrao']:.2f}")
                print(f"Mínimo: {estats['minimo']:.2f}")
                print(f"Máximo: {estats['maximo']:.2f}")
                print(f"Quantidade de alunos: {estats['contagem']}")
        elif resultado['tipo'] == 'tabela_cruzada':
            print(f"Distribuição entre '{resultado['col1']}' e '{resultado['col2']}'")
            print("-"*30)
            print(resultado['tabela'])
        
        print("/"*30 + "\n")
    
    def gerar_grafico(self, col1, col2, resultado):
        if resultado['tipo'] == 'comparacao_grupos':
            self._grafico_comparacao_grupos(resultado)
        elif resultado['tipo'] == 'comparacao_faixas':
            self._grafico_comparacao_faixas(resultado)
        elif resultado['tipo'] == 'tabela_cruzada':
            self.grafico_tabela(resultado)
    #Graficos
    def _grafico_comparacao_grupos(self, resultado):
        col_cat = resultado['col_categorica']
        col_num = resultado['col_numerica']
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        grupos = list(resultado['estatisticas'].keys())
        medias = [resultado['estatisticas'][g]['media'] for g in grupos]
        desvios = [resultado['estatisticas'][g]['desvio_padrao'] for g in grupos]
        
        cores = ['blue', 'red', 'limegreen', 'orange', 'purple']
        ax1.bar(grupos, medias, color=cores[:len(grupos)], edgecolor='black', linewidth=1.5, alpha=0.8)
        ax1.set_xlabel(col_cat, fontsize=12, fontweight='bold')
        ax1.set_ylabel(f'Média de {col_num}', fontsize=12, fontweight='bold')
        ax1.set_title(f'Comparação de Médias', fontsize=13, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
      
        for i, (m, d) in enumerate(zip(medias, desvios)):
            ax1.text(i, m + 0.5, f'{m:.2f}', ha='center', fontweight='bold')
        
        # Gráfico do desvio padrão
        ax2.bar(grupos, desvios, color=cores[:len(grupos)], edgecolor='black', linewidth=1.5, alpha=0.8)
        ax2.set_xlabel(col_cat, fontsize=12, fontweight='bold')
        ax2.set_ylabel(f'Desvio Padrão de {col_num}', fontsize=12, fontweight='bold')
        ax2.set_title(f'Comparação de Variabilidade', fontsize=13, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        

        for i, d in enumerate(desvios):
            ax2.text(i, d + 0.1, f'{d:.2f}', ha='center', fontweight='bold')
        
        plt.suptitle(f'Análise: {col_cat} vs {col_num}', fontsize=15, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        nome_arquivo = f'analise_{col_cat}_{col_num}.png'
        plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo como '{nome_arquivo}'")
        print ("FIM DA ANALISE")
        plt.show()
    
    def _grafico_comparacao_faixas(self, resultado):

        col_faixas = resultado['col_faixas']
        col_num = resultado['col_numerica']
        fig, ax = plt.subplots(figsize=(10, 6))
        faixas = list(resultado['estatisticas'].keys())
        medias = [resultado['estatisticas'][f]['media'] for f in faixas]
        
        cores = ['cyan', 'yellow', 'pink']
        bars = ax.bar(range(len(faixas)), medias, color=cores, edgecolor='black', linewidth=1.5, alpha=0.8)
        
        ax.set_xticks(range(len(faixas)))
        ax.set_xticklabels(faixas, fontsize=11)
        ax.set_xlabel(f'Faixas de {col_faixas}', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Média de {col_num}', fontsize=12, fontweight='bold')
        ax.set_title(f'Relação entre {col_faixas} e {col_num}', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
 
        for i, m in enumerate(medias):
            ax.text(i, m + 0.3, f'{m:.2f}', ha='center', fontweight='bold', fontsize=11)
        plt.tight_layout()
        nome_arquivo = f'relacao_{col_faixas}_{col_num}.png'
        plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo como '{nome_arquivo}'")
        print ("FIM DA ANALISE")
        plt.show()

    def grafico_tabela(self, resultado):
        col1 = resultado['col1']
        col2 = resultado['col2']
        tabela = resultado['tabela']
        fig, ax = plt.subplots(figsize=(10, 6))
        tabela.plot(kind='bar', ax=ax, edgecolor='black', linewidth=1.2, alpha=0.8)
        ax.set_xlabel(col1, fontsize=12, fontweight='bold')
        ax.set_ylabel('Contagem', fontsize=12, fontweight='bold')
        ax.set_title(f'Distribuição: {col1} vs {col2}', fontsize=14, fontweight='bold')
        ax.legend(title=col2, fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.xticks(rotation=0)
        plt.tight_layout()
        
        nome_arquivo = f'distribuicao_{col1}_{col2}.png'
        plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo como '{nome_arquivo}'")
        print ("FIM DA ANALISE")
        plt.show()
    
    def executar_analise(self, col1, col2):
        # Valdando colunas
        if not self.validar_coluna(col1) or not self.validar_coluna(col2):
            return

        resultado = self.analisar_relacao(col1, col2)
        if resultado is None:
            return
        self.exibir_estat(col1, col2, resultado)
        
        self.gerar_grafico(col1, col2, resultado)

def main():
    print("\n" + "/"*30)
    print("Analise de desempenho dos alunos")
    print(" ")
    analisador = AnalisadorDesempenho('student_data.csv')
    while True:
        analisador.exibir_colunas()
        print("Digite as colunas ('sair' para finalizar):")
        col1 = input("Coluna 1: ").strip()
        
        if col1.lower() == 'sair':
            print("FIM!\n")
            break
        col2 = input("Coluna 2: ").strip()
        if col2.lower() == 'sair':
            print("FIM!\n")
            break
        
       
        try:
            analisador.executar_analise(col1, col2)
        except Exception as e:
            print(f"ERRO: Ocorreu um erro durante a análise. {e}")
        
        # Continuar caso a entrada esteja errada
        continuar = input("\nDeseja continuar? (s/n): ").strip().lower()
        if continuar != 's':
            print("\nFIM!\n")
            break
        print("\n")

if __name__ == "__main__":
    main()