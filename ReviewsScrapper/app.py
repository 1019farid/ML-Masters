# doing necessary imports

from flask import Flask, render_template, request
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pandas as pd
import os

CSV_FOLDER = os.path.join('static', 'CSV')
app = Flask(__name__)  # initialising the flask app with the name 'app'


@app.route('/',methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')


@app.route('/review',methods=['POST','GET']) # route with allowed methods as POST and GET
@cross_origin()
def index():
    if request.method == 'POST':
         # obtaining the search string entered in the form
        try:
            searchString = request.form['content'].replace(" ", "")
            filename = searchString
            csv_path = os.path.join(CSV_FOLDER, filename)
            file_ext = '.csv'
            final_path = f"{csv_path}{file_ext}"

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString # preparing the URL to search the product on flipkart
            uClient = uReq(flipkart_url) # requesting the webpage from the internet
            flipkartPage = uClient.read() # reading the webpage
            uClient.close() # closing the connection to the web server
            flipkart_html = bs(flipkartPage, "html.parser") # parsing the webpage as HTML
            bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"}) # seacrhing for appropriate tag to redirect to the product link
            del bigboxes[0:3] # the first 3 members of the list do not contain relevant information, hence deleting them.
            box = bigboxes[0] #  taking the first iteration (for demo)
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] # extracting the actual product link
            prodRes = requests.get(productLink) # getting the product page from server
            prod_html = bs(prodRes.text, "html.parser") # parsing the product page as HTML
            commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"}) # finding the HTML section containing the customer comments
            reviews = [] # initializing an empty list for reviews
            #  iterating over the comment section to get the details of customer and their comments
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except:
                    custComment = 'No Customer Comment'

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment} # saving that detail to a dictionary
                reviews.append(mydict) #  appending the comments to the review list
            df = pd.DataFrame(reviews)
            df.to_csv(final_path, index=None)
            return render_template('results.html', reviews=reviews,final_path=final_path) # showing the review to the user
        except Exception as e:
            return render_template('error.html')

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)