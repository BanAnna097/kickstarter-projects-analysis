from flask import Flask, render_template, send_file
import time
import seaborn as sns
import pandas as pd
import plotly.express as px
import matplotlib
matplotlib.use('Agg') #was necessary for me to run, maybe should be deleted on your device
from collections import Counter
import matplotlib.pyplot as plt


app = Flask(__name__)

links = {"Download" : "/download",
         "View Raw Data" : "/view_data",
         "Descriptive statistics": "/stats",
         "Categories" : "/categories",
         "Current states of projects" : "/states",
         "Pairplot" : "/pairplot",
         "Success rate by categories" : "/categories_success",
         "Goal vs Pledged": "/goal_vs_pledged"}

df = pd.read_csv("data/ks-projects-201801.csv")
df = df.dropna()
# to delete unrealistic and too small values


def render_index (image=None, html_string=None, images = None):
    return render_template("index.html", links=links, image=image, code=time.time(), html_string=html_string)

@app.route('/', methods=['GET'])
def main_page():
    return render_index()


@app.route(links["Download"], methods=['GET'])
def download_data():
    return send_file("data/ks-projects-201801.csv", as_attachment=True)


@app.route(links["Goal vs Pledged"], methods=['GET'])
def goal_vs_pledged():

    df2 = (df.filter(["usd_pledged_real", "usd_goal_real"], axis=1)).dropna()
    df2 = df2.rename(columns={'usd_pledged_real': 'Pledged in USD', 'usd_goal_real': 'Goal in USD'})
    goal = sns.boxplot(data=df2)
    goal.set_yscale("log")

    plt.savefig("static/tmp/pledged_goal.png")
    plt.close()

    return render_index(image="pledged_goal.png", html_string='<font size="+2">Pledged vs Goal boxplots normalized</font><br><br>We use logarithmic scale to have better visually appealing representation of data. This is necessary because the data is heavily skewned towards large values (there are some values which are much larger than the majority.)')


@app.route(links["Success rate by categories"], methods=['GET'])
def categories_success():
    category_counter = Counter(df['main_category'])
    categories_success = {}
    for category in category_counter.keys():
        a = df[df["main_category"] == category]
        b = a[a["state"] == "successful"]
        categories_success[category] = b.shape[0]
        category_counter[category] -= b.shape[0]

    fig, ax = plt.subplots(figsize=(30, 12))

    ax.bar(categories_success.keys(), category_counter.values(), 0.7, label='Failed')
    ax.bar(categories_success.keys(), categories_success.values(), 0.7, label='Successful')

    ax.set_ylabel('Number of projects', fontsize='xx-large')
    # ax.set_title('Categories by number of projects by success rate', fontsize='xx-large')
    ax.legend(fontsize='xx-large')

    plt.savefig('static/tmp/categories_success.png')
    plt.close()
    return render_index(image="categories_success.png", html_string='<font size="+2">Categories by number of projects by success rate</font><br><br>From this bar chart it can be seen that there exists a relation between category of your project and its chances for success. Though "correlation is not causation" and this result could be heavily dependant on other factors. So, if I conducted deep further investigation I would take project goal in account. It is most probably that one of the worst perfoming ctegories - Technology has one of the highest average goals among all categories, meanwhile music - top-perfoming category should probably have really low goal and is in many cases posted for better publicity of the project. So, relations between goal sum in usd and success of the projects and between caetgory to goal should be found for further investigation.')


@app.route(links["Descriptive statistics"], methods=['GET'])
def stats():

    return render_index(html_string='''<html>
<head>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style>
</head>
<body>

<h2>Descriptive statistics</h2>

From these numbers we can conclude that data is heavily right-skewed, which means that both goals and pledged money have some really high values although majority of projects is located much lower. This fact is also proved by gigantic standard deviation, which displays that numbers are spread out over a wide range and are often located far away from mean.<br><br>

<table>
  <tr>
    <th>Functions</th>
    <th>Goals of projects in USD</th>
    <th>Pledged by projects in USD</th>
    <th>Number of backers</th>
  </tr>
  <tr>
    <td>Mean</td>
    <td>''' + "{:0.1f}".format(df["usd_goal_real"].mean()) + '''</td>
    <td>''' + "{:0.1f}".format(df["usd_pledged_real"].mean()) + '''</td>
    <td>''' + "{:0.1f}".format(df["backers"].mean()) + '''</td>
  </tr>
  <tr>
    <td>Median</td>
    <td>''' + "{:0.1f}".format(df["usd_goal_real"].median()) + '''</td>
    <td>''' + "{:0.1f}".format(df["usd_pledged_real"].median()) + '''</td>
    <td>''' + "{:0.1f}".format(df["backers"].median()) + '''</td>
  </tr>
  <tr>
    <td>Standard deviation</td>
    <td>''' + "{:0.1f}".format(df["usd_goal_real"].std()) + '''</td>
    <td>''' + "{:0.1f}".format(df["usd_pledged_real"].std()) + '''</td>
    <td>''' + "{:0.1f}".format(df["backers"].std()) + '''</td>
  </tr>
</table>

</body>
</html>''')


@app.route(links["Pairplot"], methods=['GET'])
def pairplot():

    sns_plot = sns.pairplot(df, hue="state")
    sns_plot.savefig("static/tmp/pairplot.png")
    return render_index(image="pairplot.png", html_string='<font size="+2">Pairplot</font>')


@app.route(links["Current states of projects"], methods=['GET'])
def states():
    states_counter = Counter(df["state"].dropna())
    plt.bar(x=states_counter.keys(), height=states_counter.values())
    plt.savefig('static/tmp/states.png')
    plt.close()
    return render_index(image="states.png", html_string='<font size="+2">Current states of projects</font>')


@app.route(links["View Raw Data"], methods=['GET', 'POST'])
def view_data():
    html_string = df.to_html()
    return render_index(html_string=html_string)


@app.route(links["Categories"], methods=['GET'])
def categories():

    category_counter = Counter(df['main_category'])
    plot = px.pie(values=category_counter.values(), names=category_counter.keys())
    return render_index(html_string = '<font size="+2">Categories distribution among projects</font><br><br>If I continued further work trying to work out some serious results I would cut off Dance and Journalism for sure, as small dataset can give unrelevant results.' + plot.to_html(full_html=False, include_plotlyjs='cdn'))


if __name__ == '__main__':
    app.run()