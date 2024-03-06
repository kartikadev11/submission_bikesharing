import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.express as px
import seaborn as sns


# Fungsi Jumlah penyewa perbulan
def create_monthly_users_df(df):
    df['date_day'] = pd.to_datetime(df['date_day'])
    monthly_users_df = df.resample(rule='M', on='date_day').agg({
        "casual_user": "sum",
        "registered_user": "sum",
        "total_user": "sum"
    })
    monthly_users_df.index = monthly_users_df.index.strftime('%b-%y')
    monthly_users_df = monthly_users_df.reset_index()
    return monthly_users_df
# Fungsi untuk menghitung rata-rata total user per jam

def create_hourly_users(df):
    hourly_users_df = df.groupby('hour').agg({'total_user': 'mean'})
    hourly_users_df = hourly_users_df.reset_index()
    return hourly_users_df

def create_season_users(df):
    season_users_df = df.groupby('season_label').agg({'total_user': 'mean'})
    season_users_df = season_users_df.reset_index().sort_values("total_user")
    return season_users_df

def create_casual_users(df):
    casual_users_df = df.groupby('season_label').agg({'casual_user': 'sum'})
    casual_users_df = casual_users_df.reset_index()
    return casual_users_df

def create_registered_users(df):
    registered_users_df = df.groupby('season_label').agg({'registered_user': 'sum'})
    registered_users_df = registered_users_df.reset_index()
    return registered_users_df

def create_season_user_type(df):
    season_user = pd.merge(
        left=casual_users_df,
        right=registered_users_df,
        how="left",
        left_on="season_label",
        right_on="season_label"
    )
    seasons_user_type = pd.melt(season_user, id_vars='season_label', var_name='user_type', value_name='total_user')
    return seasons_user_type

def create_weather_users(df):
    weather_users_df = df.groupby('weather_label').agg({'total_user': 'mean'})
    weather_users_df = weather_users_df.reset_index()
    return weather_users_df

def create_workingday_users(df):
    workingday_users_df = df.groupby('workingday_label').agg({'total_user': 'mean'})
    workingday_users_df = workingday_users_df.reset_index()
    return workingday_users_df


# Memuat data (gantilah nama file CSV dengan nama file yang sesuai)
day_df = pd.read_csv('dashboard/day_clean.csv')
hour_df = pd.read_csv('dashboard/hour_clean.csv')

# make filter components (komponen filter)

min_date = pd.to_datetime(day_df["date_day"].min())
max_date = pd.to_datetime(day_df["date_day"].max())

# ----- SIDEBAR -----

with st.sidebar:
    # add capital bikeshare logo
    st.image("https://img.freepik.com/free-vector/bike-race-sport-illustration_23-2149543608.jpg?t=st=1709597087~exp=1709600687~hmac=cefc7617f43276f843f49e43db27bd9077f5ac927115b6438deec87e080f0006&w=740")

    st.sidebar.header("Filter:")

    # mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Date Filter", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# hubungkan filter dengan main_df

main_df = day_df[
    (day_df["date_day"] >= str(start_date)) &
    (day_df["date_day"] <= str(end_date))
]

monthly_users_df = create_monthly_users_df(main_df)
hourly_users_df = create_hourly_users(hour_df)
season_users_df = create_season_users(main_df)
casual_users_df = create_casual_users(main_df)
registered_users_df = create_registered_users(main_df)
seasons_user_type = create_season_user_type(main_df)
weather_users_df = create_weather_users(main_df)
workingday_users_df = create_workingday_users(main_df)

# Menjalankan fungsi-fungsi untuk membuat visualisasi

st.header('Projek Analisis Data Bike Sharing Dataset :sparkles:')

st.markdown("##")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    total_user = day_df['total_user'].sum()
    st.metric("Total users", value=total_user)
 
with col2:
    total_casual = day_df['casual_user'].sum()
    st.metric("Total casual users", value=total_casual)

with col3:
    total_registered = day_df['registered_user'].sum()
    st.metric("Total registered users", value=total_registered)

fig = px.line(monthly_users_df,
              x='date_day',
              y=['casual_user', 'registered_user', 'total_user'],
              color_discrete_sequence=["skyblue", "orange", "red"],
              markers=True,
              title="Monthly Count of Bikeshare Rides").update_layout(xaxis_title='', yaxis_title='Total Rides')

st.plotly_chart(fig, use_container_width=True)

st.subheader("Rata-rata sewa sepeda berdasarkan jam")
 
# Plot menggunakan Matplotlib
fig, ax = plt.subplots()
ax.bar(hourly_users_df.index, hourly_users_df['total_user'], color='#FCDC2A')
ax.set_title('Rata - Rata Penyewaan per Jam')
ax.set_xlabel('Jam')
ax.set_ylabel('Rata - Rata Penyewaan')

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig)


st.subheader("Aktivitas Sewa Sepeda Pada WorkingDay dan Weekend berdasarkan Jam")
 
x = hour_df['hour']
y = hour_df['total_user']
hue = hour_df['workingday_label']

palette = {'Weekend': 'b', 'Weekday': 'r'}

fig, ax = plt.subplots(figsize=(20, 5))
sns.pointplot(data=hour_df, x=x, y=y, hue=hue, palette=palette, errorbar=None, ax=ax)

ax.set_title('Produktivitas Penyewaan Sepeda Berdasarkan Waktu')
ax.set_ylabel('Total Pengguna')
ax.set_xlabel('Jam')


st.pyplot(fig)

st.subheader("Rata - Rata Penyewaan Sepeda berdasarkan Musim")

plt.figure(figsize=(10, 6))
sns.barplot(x='season_label', y='total_user', hue='season_label', data=season_users_df, palette='muted', legend=False)


plt.title('Rata - Rata Penyewaan Sepeda berdasarkan Kondisi Musim')
plt.xlabel('Kondisi Musim')
plt.ylabel('Rata-rata orang menyewa sepeda')
st.set_option('deprecation.showPyplotGlobalUse', False)
st.pyplot()

st.subheader("Rata - Rata Penyewaan Sepeda berdasarkan Musim")

plt.figure(figsize=(15, 6))
sns.barplot(x="season_label", y="total_user", hue="user_type", data=seasons_user_type, palette={'registered_user': 'b', 'casual_user': 'r'})
plt.ylabel(None)
plt.xlabel(None)
plt.title("Perbandingan jumlah registered user dan casual user berdasarkan musim")

casual_patch = mpatches.Patch(color='r', label='Casual User')
registered_patch = mpatches.Patch(color='b', label='Registered User')
plt.legend(handles=[casual_patch, registered_patch], title="User Type")

st.pyplot()

st.subheader("Rata - Rata Penyewaan Sepeda berdasarkan Kondisi Cuaca")

plt.figure(figsize=(10, 6))
sns.barplot(x='weather_label', y='total_user', hue='weather_label', data=weather_users_df, palette='Blues', legend=False)

# Set plot titles and labels
plt.title('Rata - Rata Penyewaan Sepeda berdasarkan Kondisi Cuaca')
plt.xlabel('Kondisi Cuaca')
plt.ylabel('Rata-rata orang menyewa sepeda')

st.pyplot()

st.subheader("Rata - Rata Penyewaan Sepeda berdasarkan Hari Kerja / Weekend")

plt.figure(figsize=(10, 6))
sns.barplot(x='workingday_label', y='total_user', hue='workingday_label', data=workingday_users_df, palette='plasma', legend=False)


plt.title('Rata - Rata Penyewaan Sepeda berdasarkan Hari Kerja / Weekend')
plt.xlabel('Hari Kerja / Weekend')
plt.ylabel('Rata-rata orang menyewa sepeda')

st.pyplot()

st.caption('Copyright (c) Kartika Deviani 2024')