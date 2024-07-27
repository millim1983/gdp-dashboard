import streamlit as st
import pandas as pd
import math
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns 
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import plotly.express as px
import io

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='황삭 가공 제조 데이터 분석',
    page_icon=':factory:', # This is an emoji shortcode. Could be a URL too.
)

# ----------- 사이드 바 메뉴 ---------- # 
with st.sidebar:
    choose = option_menu("빅분기프로젝트", ["About", "PROJECT", "DATA"],
    icons=['house', 'camera fill', 'kanban'],
    menu_icon="app-indicator", default_index=0,
    styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#02ab21"},
    }
    )



# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data

def get_data():
    # 원본데이터를 불러와 전처리하는 과정을 넣을 것 
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    location = Path(__file__).parent/'data/steel_ai_01_on.csv'
    raw_df = pd.read_csv(location, header = 0)

    # MIN_YEAR = 1960
    # MAX_YEAR = 2022

    # The data above has columns like:
    # FACTORY	공장코드
    # WORK_SHAPE	작업조(1근/2근/3근)
    # INPUT_ED	투입되는 소재의 외경(mm)
    # INPUT_LENGTH	투입되는 소재의 개별 길이(mm)
    # INPUT_QTY	투입 총 수량(개)
    # DIRECTION_ED	가공 후 목표 외경(mm)
    # OUTPUT_ED	생산된 소재의 외경(mm)
    # STEEL_CATEGORY	투입 강종 분류
    # WORK_START_DT	작업시작일시
    # WORK_END_DT	작업종료일시
    #
    # 종속변수
    # diff = WORK_END_DT -  WORK_START_DT
    # INPUT_QTY
    # OUTPUT_ED
    # 투입되는 소재 총길이 = 

    # 데이터 타입 변경

    raw_df = raw_df.astype({'STEEL_CATEGORY' : 'category'})  # STEEL_CATEGORY 값이 6개이므로 타입을 category로 변경
    raw_df = raw_df.astype({'WORK_SHAPE':'object'})  # WORK_SHAPE은 숫자이지만, 작업조를 나타냄 1근, 2근 3근 > object로 변경

    # 중복데이터 제거 

    raw_df = raw_df.drop_duplicates()

    # 종속변수 추가 
    raw_df['work_start_dt_ns'] = pd.to_datetime(raw_df['WORK_START_DT'])
    raw_df['work_end_dt_ns'] = pd.to_datetime(raw_df['WORK_END_DT'])

    raw_df['diff'] = (raw_df['work_end_dt_ns'] - raw_df['work_start_dt_ns']).dt.total_seconds().div(60).astype(int)


    # # 원본의 year 별 gdp 를 year vs gdp 로 변환하는 과정 
    # # So let's pivot all those year-columns into two: Year and GDP
    # gdp_df = raw_gdp_df.melt(
    #     ['Country Code'],
    #     [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
    #     'Year',
    #     'GDP',
    # )
    # # Convert years from string to integers
    # gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])


    return raw_df

df = get_data()
# 그래프를 그리기 위해 int, float만 선택 
df1 = df.select_dtypes([int, float])
df1_col = df1.columns


# ----------- 본문 ------------------ # 


# Set the title that appears at the top of the page.
st.header(':factory: 제조데이터 분석 프로젝트')
st.subheader('빅데이터 분석의 첫걸음! ')
st.markdown("""
제조데이터 분석을 위한 데이터 시각화 표출 대시보드입니다.   
다양한 그래프들을 활용하여 데이터 특성을 시각적으로 나타냈습니다.  
변수들을 조정하며 데이터의 특성을 찾아봅시다. 
""")
# 줄바꿈시 띄어쓰기 두개 

# Add some spacing
''
''
# ---- 슬라이드 바로 bins 조정 --- # 
min_value = df1['diff'].min()
max_value = df1['diff'].max()
from_year, to_year = st.slider(
    '작업시간 범위를 정해보세요?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

#----- int, float 형의 데이터 describe 보여주기 --- # 

steel_cat = df1['STEEL_CATEGORY'].unique()


if not len(df1_col):
    st.warning("적어도 한개 이상의 컬럼을 선택하세요?")

selected_col = st.multiselect(
    '컬럼을 선택하세요!',  
    #columns,  
    ['WORK_SHAPE', 'INPUT_ED', 'INPUT_LENGTH', 'INPUT_QTY', 'DIRECTION_ED','OUTPUT_ED', 'STEEL_CATEGORY'])


'''
# 데이터 describe을 표현하기 위한 섹션 
cols = st.columns(4)    # 4열로보여주겠다 
#col_selection = 
for i in col :
    description = df1[i].describe()
    for k, v in enumerate(desc):
        print(i, k,v)

for i, d in enumerate(df.describe()):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[gdp_df['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[gdp_df['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )


min_value = 10
max_value = 100

from_bins, to_bins = st.slider(
    '히스토그램 bins(데이터범위)에 따른 그래프를 살펴보세요',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

vars = df.columns
















if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[gdp_df['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[gdp_df['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
'''