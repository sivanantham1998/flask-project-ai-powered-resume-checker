from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3, os
BASE_DIR=os.path.dirname(os.path.abspath(__file__)); DB_PATH=os.path.join(BASE_DIR,'database','placement.db')
app=Flask(__name__); app.secret_key='placement-demo-key'
def db():
 c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
 os.makedirs(os.path.dirname(DB_PATH),exist_ok=True); c=db(); c.executescript('''CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,phone TEXT,department TEXT,cgpa REAL DEFAULT 0,skills TEXT,projects INTEGER DEFAULT 0,internships INTEGER DEFAULT 0,communication INTEGER DEFAULT 0,aptitude INTEGER DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS companies(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,role TEXT NOT NULL,package_lpa REAL DEFAULT 0,required_skills TEXT,min_cgpa REAL DEFAULT 0,openings INTEGER DEFAULT 1,created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER NOT NULL,company_id INTEGER NOT NULL,status TEXT DEFAULT 'Applied',applied_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(student_id) REFERENCES students(id),FOREIGN KEY(company_id) REFERENCES companies(id));''')
 if c.execute('SELECT COUNT(*) FROM students').fetchone()[0]==0: c.executemany('INSERT INTO students(name,email,phone,department,cgpa,skills,projects,internships,communication,aptitude) VALUES(?,?,?,?,?,?,?,?,?,?)',[('Arun Kumar','arun@example.com','9876500001','CSE',8.4,'Python, SQL, Machine Learning',3,1,8,9),('Priya S','priya@example.com','9876500002','AI & DS',9.1,'Python, Pandas, Power BI, ML',4,2,9,9),('Karthik R','karthik@example.com','9876500003','IT',7.5,'Java, HTML, CSS, JavaScript',2,1,7,7),('Divya M','divya@example.com','9876500004','CSE',8.8,'Java, Spring, SQL, React',3,2,8,8)])
 if c.execute('SELECT COUNT(*) FROM companies').fetchone()[0]==0: c.executemany('INSERT INTO companies(name,role,package_lpa,required_skills,min_cgpa,openings) VALUES(?,?,?,?,?,?)',[('TechNova Solutions','Python Developer',5.5,'Python, SQL',7,5),('DataSphere Analytics','Data Analyst',6.5,'Python, Pandas, Power BI, SQL',7.5,3),('WebCraft Technologies','Full Stack Developer',7,'HTML, CSS, JavaScript, React',7,4),('EnterpriseSoft','Java Developer',6,'Java, SQL',7.5,3)])
 c.commit(); c.close()
def score(s,c):
 cg=float(s['cgpa']); minimum=float(c['min_cgpa']); x=30 if cg>=minimum else max(0,30-(minimum-cg)*12)
 req={a.strip().lower() for a in c['required_skills'].split(',')}; have={a.strip().lower() for a in s['skills'].split(',')}; m=len(req&have); x+=30*m/max(1,len(req)); x+=min(15,int(s['projects'])*3); x+=min(10,int(s['internships'])*5); x+=min(10,int(s['communication'])); x+=min(5,int(s['aptitude'])*.55); x=round(min(100,x),2); return x,('High Match' if x>=80 else 'Moderate Match' if x>=60 else 'Needs Improvement'),[('CGPA meets requirement' if cg>=minimum else 'CGPA below requirement'),f'{m} required skill(s) matched']
@app.route('/')
def home():
 c=db(); ns=c.execute('SELECT COUNT(*) FROM students').fetchone()[0]; nc=c.execute('SELECT COUNT(*) FROM companies').fetchone()[0]; na=c.execute('SELECT COUNT(*) FROM applications').fetchone()[0]; hi=sum(score(s,co)[0]>=80 for s in c.execute('SELECT * FROM students') for co in c.execute('SELECT * FROM companies')); c.close(); return render_template('dashboard.html',students=ns,companies=nc,applications=na,high_matches=hi)
@app.route('/students')
def students(): c=db(); r=c.execute('SELECT * FROM students ORDER BY id DESC').fetchall(); c.close(); return render_template('students.html',students=r)
@app.post('/students/add')
def add_student():
 f=request.form
 try:
  c=db(); c.execute('INSERT INTO students(name,email,phone,department,cgpa,skills,projects,internships,communication,aptitude) VALUES(?,?,?,?,?,?,?,?,?,?)',(f['name'],f['email'],f.get('phone',''),f.get('department',''),float(f.get('cgpa',0)),f.get('skills',''),int(f.get('projects',0)),int(f.get('internships',0)),int(f.get('communication',0)),int(f.get('aptitude',0)))); c.commit(); c.close(); flash('Student added successfully.','success')
 except sqlite3.IntegrityError: flash('Email already exists.','danger')
 return redirect(url_for('students'))
@app.route('/companies')
def companies(): c=db(); r=c.execute('SELECT * FROM companies ORDER BY id DESC').fetchall(); c.close(); return render_template('companies.html',companies=r)
@app.post('/companies/add')
def add_company():
 f=request.form; c=db(); c.execute('INSERT INTO companies(name,role,package_lpa,required_skills,min_cgpa,openings) VALUES(?,?,?,?,?,?)',(f['name'],f['role'],float(f.get('package_lpa',0)),f.get('required_skills',''),float(f.get('min_cgpa',0)),int(f.get('openings',1)))); c.commit(); c.close(); flash('Company added successfully.','success'); return redirect(url_for('companies'))
@app.route('/recommendations/<int:sid>')
def recommendations(sid):
 c=db(); s=c.execute('SELECT * FROM students WHERE id=?',(sid,)).fetchone(); cs=c.execute('SELECT * FROM companies').fetchall(); c.close()
 if not s:return 'Student not found',404
 r=[]
 for co in cs: sc,st,re=score(s,co); r.append({'company':co,'score':sc,'status':st,'reasons':re})
 return render_template('recommendations.html',student=s,results=sorted(r,key=lambda z:z['score'],reverse=True))
@app.route('/applications')
def applications():
 c=db(); a=c.execute('SELECT a.*,s.name student_name,c.name company_name,c.role FROM applications a JOIN students s ON s.id=a.student_id JOIN companies c ON c.id=a.company_id ORDER BY a.id DESC').fetchall(); s=c.execute('SELECT id,name FROM students ORDER BY name').fetchall(); co=c.execute('SELECT id,name,role FROM companies ORDER BY name').fetchall(); c.close(); return render_template('applications.html',applications=a,students=s,companies=co)
@app.post('/applications/add')
def add_application():
 c=db(); c.execute('INSERT INTO applications(student_id,company_id) VALUES(?,?)',(int(request.form['student_id']),int(request.form['company_id']))); c.commit(); c.close(); flash('Application created.','success'); return redirect(url_for('applications'))
@app.get('/api/recommendations/<int:sid>')
def api(sid):
 c=db(); s=c.execute('SELECT * FROM students WHERE id=?',(sid,)).fetchone(); cs=c.execute('SELECT * FROM companies').fetchall(); c.close();
 if not s:return jsonify(error='Student not found'),404
 return jsonify(sorted([{'company':co['name'],'role':co['role'],'score':score(s,co)[0],'status':score(s,co)[1],'reasons':score(s,co)[2]} for co in cs],key=lambda z:z['score'],reverse=True))
if __name__=='__main__': init_db(); app.run(host='127.0.0.1',port=5000,debug=True)
