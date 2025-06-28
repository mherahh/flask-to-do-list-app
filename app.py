from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
assets = Environment(app)

# compile SCSS to CSS
scss = Bundle('styles.scss', filters='libsass', output='styles.css')
assets.register('scss_all', scss)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flaskd.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

# rows of data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    content = db.Column(db.String(100), nullable= False)
    complete = db.Column(db.Integer)
    created = db.Column(db.DateTime, default =datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task{self.id}"
   

with app.app_context():
     db.create_all()
     scss.build() 


#home page
@app.route("/", methods = ["POST", "GET"])
def index():
    if request.method == "POST":
       current_task = request.form['content']
       new_task = MyTask(content = current_task)
       try:
          db.session.add(new_task)
          db.session.commit()
          return redirect("/")
       except Exception as e:
          print(f"Error:{e}")
          return f"Error:{e}"
    else:
       tasks = MyTask.query.order_by(MyTask.created).all()      
       return render_template("index.html", tasks =tasks)



#delete 
@app.route("/delete/<int:id>")
def delete(id:int):
   delete_task = MyTask.query.get_or_404(id)
   try:
      db.session.delete(delete_task)
      db.session.commit()
      return redirect("/")
   except Exception as e:
      return f"Error: {e}"
   
#update
@app.route("/edit/<int:id>", methods = ["GET", "POST"])
def update(id:int):
   task = MyTask.query.get_or_404(id)
   if request.method == "POST":
      task.content = request.form['content']
      try:
         db.session.commit()
         return redirect("/")
      except Exception as e:
         return f"Error: {e}"
   else:
      return render_template("edit.html", task=task)



if __name__ == "__main__":
    
    app.run(debug=True)