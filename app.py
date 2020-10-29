from flask import Flask
import ctr_allykbasenow

app = Flask(__name__)

ctr_allykbasenow.app.run()


