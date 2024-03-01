import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import pandas as pd

# Visual Section : For visual purposes

# This function is used to make palette as an argument for seaborn plot.
# Return a list of colors
def make_palette(data, column, color1="#00005e", color2="#0e0ec4"):
	colors = []
	max_value = data[column].max()
	for record in data[column] :
		if record == max_value :
			colors.append(color1)
		else :
			colors.append(color2)
	return colors

# Make explode list for pie chart
def make_explode(data, column):
    explodes=[]
    max_value = data[column].max()
    for value in data[column]:
        if value == max_value:
            explodes.append(0.03)
        else :
            explodes.append(0.01)
    return explodes


# Data Section : Functions to generate data

# Correct dataset types
def generate_data(df):
	days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	seasons = ["spring", "summer", "fall", "winter"]
	for col in df.columns:
		if df[col].dtype == "object" and col != "date":
			df[col] = df[col].astype("category")
	df["weekday"] = pd.Categorical(df["weekday"], categories=days, ordered=True)
	df["season"] = pd.Categorical(df["season"], categories=seasons, ordered=True)
	df["date"] = pd.to_datetime(df["date"])
	return df

# Group data by hour to see the pattern
def by_hour(df):
	by_hour = df.groupby("hour", as_index=False).agg({"count":"mean"})
	return by_hour

# Group data by weekday to see the pattern
def by_day(df):
	by_day = df.groupby("weekday", as_index=False, observed=True).agg({"count":"mean"})
	return by_day

# Group data by date, so it will return the trend on daily timeframe
def daily(df):
	df_daily = df.groupby(["date"], as_index=False).agg({"count":"sum"})
	return df_daily

# Resample the data to monthly timeframe
def monthly(df):
	df_monthly = df.resample("ME", on="date").agg({"casual":"sum",
                                                    "registered":"sum",
                                                    "count":"sum"})
	df_monthly.reset_index(inplace=True)
	df_monthly["date"] = df_monthly["date"].apply(lambda x: datetime.strptime(str(x), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m"))
	return df_monthly

# Group data by season to see the pattern
def by_season(df):
	by_season = df.groupby("season", as_index=False, observed=True).agg({"count":"mean"})
	return by_season

# Group data by weather situation to see the pattern
def by_weathersit(df):
	by_weathersit = df.groupby("weathersit", as_index=False, observed=True).agg({"count":"mean"})
	return by_weathersit

#Pattern by day and month
def day_month_pattern(df):
	df_day_month = df.groupby(["month", "weekday"]).agg({"count":"mean"}).unstack()
	df_day_month.columns = df_day_month.columns.droplevel()
	return df_day_month

#Pattern by day and hour
def day_hour_pattern(df):
	df_day_hour = df.groupby(["weekday", "hour"]).agg({"count":"mean"}).unstack()
	df_day_hour.columns = df_day_hour.columns.droplevel()
	return df_day_hour

def show_weather(df):
	current_weather = df["weathersit"].values[-1]
	weather_sentence = "Current Weather : "+current_weather
	if current_weather == "Mist":
		weather_sentence+=" :fog:"
	elif current_weather == "Clear":
		weather_sentence+=" :sun_small_cloud:"
	elif current_weather == "Light":
		weather_sentence+=" :partly_sunny_rain:"
	else:
		weather_sentence+=" :thunder_cloud_and_rain:"
	return weather_sentence


# Plotting Section : Show plots to the dashboard

# Figure for daily timeframe
def make_daily_plot(df_daily):
	fig = plt.figure(figsize=(30,8))
	plt.plot(df_daily["date"], df_daily["count"], marker=".", color="green")
	plt.title("Daily Rental Count", loc="center", pad=10, fontsize=28)
	plt.ylabel("Count", fontsize=22)
	plt.xticks(fontsize=18)
	plt.yticks(fontsize=18)
	plt.grid(True)
	st.pyplot(fig)

# Make plot for month timeframe
def make_monthly_plot(df_monthly):
	fig = plt.figure(figsize=(30,8))
	plt.plot(df_monthly["date"], df_monthly["count"], marker="o", color="navy", linewidth=3, label="Total Count")
	plt.plot(df_monthly["date"], df_monthly["casual"], marker="o", color="green", linewidth=3, label="Casual")
	plt.plot(df_monthly["date"], df_monthly["registered"], marker="o", color="orange", linewidth=3, label="Registered")
	plt.legend(loc="upper left", bbox_to_anchor=(0,0,1,1), fontsize=20)
	plt.title("Monthly Rental Count", loc="center", pad=10, fontsize=28)
	plt.ylabel("Count", fontsize=22)
	plt.xticks(fontsize=18, rotation=45)
	plt.yticks(fontsize=18)
	plt.grid(True)
	st.pyplot(fig)

# Bar plot for day and hour pattern
def make_hour_day_basis(df_daily, df_hour, color1, color2):
	fig, axs = plt.subplots(1, 2, figsize=(16,8))
	sns.set_style({"grid.color":"darkgray"})
	sns.barplot(x="weekday", y="count", data=df_daily, ax=axs[0],
				palette=make_palette(df_daily, "count", color1, color2), hue="weekday", legend=False)
	axs[0].set_title("Average Rental Count by Day")
	sns.barplot(x="hour", y="count", data=df_hour, ax=axs[1],
			palette=make_palette(df_hour,  "count", color1, color2), hue="hour", legend=False)
	axs[1].set_title("Average Rental Count by Hour")
	st.pyplot(fig)

# Seasonality pattern with bar plot
def make_season_bar(df_season, color1, color2):
	fig = plt.figure(figsize=(15,8))
	sns.barplot(x="count", y="season", data=df_season,
				order=df_season.sort_values("count", ascending=False)["season"],
				palette=make_palette(df_season, "count", color1, color2), hue="season", legend=False)
	plt.title("Average Rental Count by Seasons", fontsize=20, loc="center", pad=20)
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)
	plt.xlabel("Average Count", fontsize=18)
	plt.ylabel("Seasons", fontsize=18)
	st.pyplot(fig)

# Proportion of each weather situation to the rental count
def make_weather_pie(df_weathersit, color1, color2, pct_color, label_color):
	fig = plt.figure(figsize=(8,8))
	_, _, autotext = plt.pie(x=df_weathersit["count"], labels=df_weathersit["weathersit"],
							autopct="%.2f%%", colors = make_palette(df_weathersit, "count", color1, color2),
							textprops={"fontsize":"12", "color":label_color}, explode=make_explode(df_weathersit, "count"))
	plt.title("Proportion of Average Rental Count by Weather Situation", loc="center")
	for txt in autotext:
		txt.set_color(pct_color)
	st.pyplot(fig)

# Proportion of casual and registered rental
def make_casual_registered(df, color1, color2, pct_color, label_color):
	casual = df["casual"].sum()
	registered = df["registered"].sum()
	ratio = pd.DataFrame({"Type":["Casual", "Registered"], "Total":[casual, registered]})
	fig = plt.figure(figsize=(10,10))
	_, _, autotext = plt.pie(x=ratio["Total"], labels=ratio["Type"],
							autopct="%.2f%%", colors = make_palette(ratio, "Total", color1, color2),
							textprops={"fontsize":"12", "color": label_color}, explode=make_explode(ratio, "Total"))
	plt.title("Proportion of Casual and Registered Rental", loc="center")
	for txt in autotext:
		txt.set_color(pct_color)
	st.pyplot(fig)

# Generate heatmap for month and day pattern
def make_heatmap_daymonth(df, colormap="Blues", annotation="Yes"):
	fig = plt.figure(figsize=(10,10))
	annot = True
	if annotation == "No":
		annot = False
	sns.heatmap(df, annot=annot, fmt=".0f", cmap=colormap)
	plt.title("Heatmap for Average Rental Count by Month and Day", fontsize=20)
	plt.xticks(rotation=45)
	plt.yticks(rotation=0)
	st.pyplot(fig)

# Generate heatmap for day and hour pattern
def make_heatmap_dayhour(df, colormap="Blues", annotation="Yes"):
	fig = plt.figure(figsize=(20,10))
	annot = True
	if annotation == "No":
		annot = False
	sns.heatmap(df, annot=annot, fmt=".0f", cmap=colormap)
	plt.title("Heatmap for Average Rental Count by Day and Hour", fontsize=20)
	plt.xticks(rotation=0)
	plt.yticks(rotation=45)
	st.pyplot(fig)

df = pd.read_csv("fixed_bike_sharing.csv")
df = generate_data(df)

# Main program
def main() :
	min_date = df["date"].min()
	max_date = df["date"].max()
	st.title("Bike Sharing Dashboard :bike:")
	
	with st.sidebar :
		st.header("Filter by Date :spiral_calendar_pad:")
		ranges = st.date_input(
            label="Select Date Range",
            min_value=min_date, max_value=max_date,
            value=[min_date, max_date]
            )
		st.header("Barplot Styling")
		color1_bar = st.color_picker("Select color to highlight the maximum value.", "#00005e", key="bar1")
		color2_bar = st.color_picker("Select color for the rest.", "#0e0ec4", key="bar2")

		st.header("Pie Chart Styling")
		color1_pie = st.color_picker("Select color to highlight the maximum value.", "#00005e", key="pie1")
		color2_pie = st.color_picker("Select color for the rest.", "#0e0ec4", key="pie2")
		pct_color = st.color_picker("Select color for percentage.", "#ffffff")
		label_color = st.color_picker("Select color for the label.", "#000000")

		st.header("Heatmap Styling")
		annotation = st.radio(label="Show annotation?", options=("Yes", "No"))
		colormap = st.selectbox(label="Select colormap", options=("Blues", "Greens",
																"crest", "magma", "viridis",
																"rocket_r", "flare",
																"rocket", "mako"))
	#filtering from sidebar
	try :
		start_date, end_date = ranges
	except ValueError :
		st.error("You must pick two dates")
		st.stop()
	
	#filtering based on date range
	df_filter = df[(df["date"] >= str(start_date)) & (df["date"] <= str(end_date))]
	df_hour = by_hour(df_filter) # By hour pattern
	df_day = by_day(df_filter) # By day pattern
	df_dailytf = daily(df_filter) # daily timeframe
	df_monthlytf = monthly(df_filter) # monthly timeframe
	df_season = by_season(df_filter) # By season pattern
	df_weathersit = by_weathersit(df_filter) # By weather situation pattern
	df_daymonth = day_month_pattern(df_filter) # By month and day pattern
	df_dayhour = day_hour_pattern(df_filter) # By day and hour pattern
	
	today = df_filter["weekday"].values[-1]
	date_today = end_date.strftime("%Y-%m-%d")
	st.subheader("{}, {}".format(today, date_today))
	with st.container() :
		col1, col2, col3 = st.columns(3)
		df_daily = df_filter.groupby(["date"], as_index=False).agg({"count":"sum",
																		"registered":"sum",
																		"casual":"sum"})
		diff = df_daily - df_daily.shift(1)
		with col1 :
			st.metric(label="Count",
					value="{:,d}".format(df_daily["count"].values[-1].sum()),
					delta="{:.0f} from yesterday".format(diff["count"].values[-1]))
		with col2 :
			st.metric(label="Registered",
					value="{:,d}".format(df_daily["registered"].values[-1].sum()),
					delta="{:.0f} from yesterday".format(diff["registered"].values[-1]))
		with col3 :
			st.metric(label="Casual",
					value="{:,d}".format(df_daily["casual"].values[-1].sum()),
					delta="{:.0f} from yesterday".format(diff["casual"].values[-1]))
	
	st.header(":abacus: Rental Count ({} to {})".format(start_date, end_date))
	with st.container():
		customer_col1, customer_col2 = st.columns(2)
		with customer_col1:
			make_casual_registered(df_filter, color1_pie, color2_pie, pct_color, label_color)
		with customer_col2:
			st.metric(label="Total Count",
					value="{:,d}".format(df_daily["count"].sum()))
			st.metric(label="Total Registered",
					value="{:,d}".format(df_daily["registered"].sum()))
			st.metric(label="Total Casual",
					value="{:,d}".format(df_daily["casual"].sum()))
	st.header("Rental Performance")
	make_daily_plot(df_dailytf)
	if len(df_monthlytf) >= 2:
		make_monthly_plot(df_monthlytf)
	
	st.header(":books: Pattern Breakdown")
	st.subheader(":clock3: Day and Hour Pattern")
	make_hour_day_basis(df_day, df_hour, color1_bar, color2_bar)
	make_heatmap_dayhour(df_dayhour, colormap, annotation)

	st.subheader("Month and Day Pattern")
	if len(df_monthlytf) > 2 :
		make_heatmap_daymonth(df_daymonth, colormap, annotation)

	st.subheader(":maple_leaf: Season Pattern")
	make_season_bar(df_season, color1_bar, color2_bar)

	st.header("Weather Analysis")
	with st.container():
		weathercol1, weathercol2 = st.columns(2)
		with weathercol1:
			make_weather_pie(df_weathersit, color1_pie, color2_pie, pct_color, label_color)
		with weathercol2:
			st.subheader(show_weather(df_filter))
			st.metric(label=":dash: Windspeed", value="{:.2f} km/h".format(df_filter["windspeed"].values[-1]))
			st.metric(label=":thermometer: Temperature", value="{:.2f} ⁰C".format(df_filter["temp"].values[-1]))
			st.metric(label=":droplet: Humidity", value="{:.2f}%".format(df_filter["humidity"].values[-1]))
			current_weather = df_filter["weathersit"].values[-1]
			avg_current_weather = df_weathersit[df_weathersit["weathersit"] == current_weather]["count"].values[0]
			st.metric(label="Average Rental Count on {} Weather".format(current_weather), value="{:.0f}".format(avg_current_weather))

	st.caption("Made by William Devin (2024)")
main()