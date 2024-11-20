import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np

# Carregar os três datasets fornecidos
file_path_1 = 'stack-overflow-developer-survey-2021/survey_results_public2021.csv' 
file_path_2 = 'stack-overflow-developer-survey-2022/survey_results_public2022.csv'
file_path_3 = 'stack-overflow-developer-survey-2023 (1)/survey_results_public2023.csv'

df1 = pd.read_csv(file_path_1, header=0, encoding='latin-1')
df2 = pd.read_csv(file_path_2, header=0, encoding='latin-1')
df3 = pd.read_csv(file_path_3, header=0, encoding='latin-1')

# Concatenar os três datasets
df_combined = pd.concat([df1, df2, df3], ignore_index=True)

# Manter apenas as linhas onde MainBranch seja "I am a developer by profession"
df_filtered = df_combined[df_combined['MainBranch'] == "I am a developer by profession"]

# Remover linhas onde ConvertedCompYearly possui valores ausentes
df_filtered = df_filtered.dropna(subset=['ConvertedCompYearly'])

# Preencher valores ausentes em YearsCodePro com a média da coluna
years_code_pro_mean = pd.to_numeric(df_filtered['YearsCodePro'], errors='coerce').mean()
df_filtered['YearsCodePro'] = pd.to_numeric(df_filtered['YearsCodePro'], errors='coerce').fillna(years_code_pro_mean)

# Manter apenas as colunas especificadas
columns_to_keep = [
    'ResponseId', 'MainBranch', 'Employment', 'Country', 'EdLevel', 
    'Age1stCode', 'LearnCode', 'YearsCodePro', 'DevType', 
    'LanguageHaveWorkedWith', 'DatabaseHaveWorkedWith', 'OpSys', 
    'Age', 'Gender', 'ConvertedCompYearly'
]
df_final = df_filtered[columns_to_keep]

# Remover o texto dentro dos parênteses em "EdLevel"
df_final['EdLevel'] = df_final['EdLevel'].str.replace(r'\s*\(.*\)', '', regex=True)

# StreamLit
st.title("Projeto Extensionista - Rockets")
st.header("Bem-vindo!")

# Distribuição de Salários dos Programadores - Mulheres
st.subheader('Distribuição de Salários das Mulheres')
df_women = df_final[df_final['Gender'] == 'Woman']
bins = [0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
labels = ['0-10k', '10k-20k', '20k-30k', '30k-40k', '40k-50k', '50k-60k', '60k-70k', '70k-80k', '80k-90k', '90k-100k']
df_women['SalaryRange'] = pd.cut(df_women['ConvertedCompYearly'], bins=bins, labels=labels, include_lowest=True, ordered=True)
fig1 = px.histogram(df_women,
                    x='SalaryRange',
                    category_orders={'SalaryRange': labels},
                    labels={'SalaryRange': 'Faixa Salarial', 'Quantidade': 'Quantidade'},
                    color_discrete_sequence=['#FA0087'])
st.plotly_chart(fig1)

# Distribuição de Salários dos Programadores - Homens
st.subheader('Distribuição de Salários dos Homens')
df_men = df_final[df_final['Gender'] == 'Man']
df_men['SalaryRange'] = pd.cut(df_men['ConvertedCompYearly'], bins=bins, labels=labels, include_lowest=True, ordered=True)
fig11 = px.histogram(df_men,
                     x='SalaryRange',
                     category_orders={'SalaryRange': labels},
                     labels={'SalaryRange': 'Faixa Salarial', 'count': 'Quantidade'},
                     color_discrete_sequence=['#3283FE'])
st.plotly_chart(fig11)

# Distribuição do Status de Emprego
st.subheader('Distribuição do Status de Emprego')
fig2 = px.pie(df_final,
              names='Employment',
              labels={'Employment': 'Status de Emprego'})
st.plotly_chart(fig2)

# Distribuição da Idade ao Começar a Programar
st.subheader('Distribuição da Idade ao Começar a Programar')
df_final['Age1stCode'] = pd.Categorical(df_final['Age1stCode'], categories=[
    'Younger than 5 years', '5 - 10 years', '11 - 17 years', '18 - 24 years', '25 - 34 years', '35 - 44 years', '45 - 54 years', '55 - 64 years', '65 years or older'], ordered=True)
df_final = df_final.sort_values('Age1stCode')
fig4 = px.histogram(df_final, x='Age1stCode',
                    category_orders={'Age1stCode': df_final['Age1stCode'].cat.categories},
                    labels={'Age1stCode': 'Idade ao Começar a Programar', 'count': 'Quantidade'})
st.plotly_chart(fig4)

# Quantidade de Desenvolvedores por País e Média Salarial
st.subheader('Quantidade de Desenvolvedores por País e Média Salarial')
df_count_dev = df_final.dropna(subset=['Country', 'ConvertedCompYearly'])

# Calcular a média salarial por país
df_avg_salary_country = df_count_dev.groupby('Country', as_index=False)['ConvertedCompYearly'].mean()
df_avg_salary_country.columns = ['País', 'Média Salarial']

# Combinar com a quantidade de desenvolvedores por país
df_count_dev = df_count_dev['Country'].value_counts().reset_index()
df_count_dev.columns = ['País', 'Quantidade']
df_final_treemap = pd.merge(df_count_dev,
                            df_avg_salary_country, on='País',
                            how='left')

fig6 = px.treemap(df_final_treemap, path=['País'],
                  values='Quantidade', color='Média Salarial',
                  labels={'País': 'País', 'Média Salarial': 'Média Salarial (USD)',
                          'Quantidade': 'Quantidade de Desenvolvedores'},
                  color_continuous_scale=['white', 'yellow'], range_color=[0, 400000])
st.plotly_chart(fig6)

# Quantidade de Linguagens de Programação Mais Utilizadas
st.subheader('Quantidade de linguagens de programação mais utilizadas')
df_languages = df_final['LanguageHaveWorkedWith'].str.split(';', expand=True).stack().reset_index(drop=True)
fig7 = px.histogram(df_languages, x=0)
fig7.update_layout(xaxis_title='Linguagens de programação',
                   yaxis_title='Quantidade')
st.plotly_chart(fig7)

# Tipos de Sistemas Operacionais Mais Utilizados
st.subheader('Tipos de sistemas operacionais mais utilizados')
df_opsys = df_final['OpSys'].str.split(';', expand=True).stack().reset_index(drop=True)
fig9 = px.histogram(df_opsys, x=0)
fig9.update_layout(xaxis_title='Sistemas Operacionais',
                   yaxis_title='Quantidade')
st.plotly_chart(fig9)

# Distribuição de Idade dos Desenvolvedores
st.subheader('Distribuição de idade dos desenvolvedores')
fig10 = px.pie(df_final, names='Age',
               labels={'Age': 'Idade'})
st.plotly_chart(fig10)

# Tipos de Desenvolvimento dos Profissionais (DevType)
st.subheader('Tipos de Desenvolvimento dos Profissionais')
df_devtype = df_final['DevType'].str.split(';', expand=True).stack().reset_index(drop=True)
fig11 = px.histogram(df_devtype, y=0,
                     height=750)
fig11.update_layout(yaxis_title='Tipo de Desenvolvimento',
                    xaxis_title='Quantidade',
                    showlegend=False)
st.plotly_chart(fig11)

# Comparação entre Níveis de Educação e Salário
st.subheader('Comparação entre Níveis de Educação e Salário')
df_education_salary = df_final.dropna(subset=['EdLevel', 'ConvertedCompYearly'])
df_avg_salary_education = df_education_salary.groupby('EdLevel', as_index=False)['ConvertedCompYearly'].mean()
fig12 = px.bar(df_avg_salary_education, x='ConvertedCompYearly',
               y='EdLevel',
               labels={'ConvertedCompYearly': 'Média Salarial (USD)'},
               height=600)
fig12.update_layout(yaxis_categoryorder='total ascending')
st.plotly_chart(fig12)
