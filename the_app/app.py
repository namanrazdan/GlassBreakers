# import the Flask framework
from flask import Flask, jsonify, request, redirect, url_for
from flaskext.mysql import MySQL

# from employee_api.employee import employees_blueprint

# create a flask object
app = Flask(__name__)

# app.register_blueprint(employees_blueprint, url_prefix='/emp')


# add db config variables to the app object
app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'user_15'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pass17'
app.config['MYSQL_DATABASE_DB'] = 'GlassBreaker'

# create the MySQL object and connect it to the
# Flask app object
db_connection = MySQL()
db_connection.init_app(app)


# route to get the different user types from the database
@app.route('/user_types')
def user_types():
    cur = db_connection.get_db().cursor()
    cur.execute('select * from userType')
    data = cur.fetchall()
    json_data = [{'label': row[1], 'value': row[0]} for row in data]
    return jsonify(json_data)


# route to get the job types from the database
@app.route('/job_types')
def job_types():
    cur = db_connection.get_db().cursor()
    cur.execute('select * from jobType')
    data = cur.fetchall()
    json_data = [{'label': row[1], 'value': row[0]} for row in data]
    return jsonify(json_data)


# route gets the companies from the database
@app.route('/companies')
def companies():
    cur = db_connection.get_db().cursor()
    cur.execute('select distinct companyID, name from company')
    data = cur.fetchall()
    json_data = [{'label': row[1], 'value': row[0]} for row in data]
    return jsonify(json_data)


# route gets the departments from the database
@app.route('/departments/<company>')
def departments(company):
    cur = db_connection.get_db().cursor()
    cur.execute("select distinct deptID, name from department where companyID = '" + company + "'")
    data = cur.fetchall()
    json_data = [{'label': row[1], 'value': row[0]} for row in data]
    return jsonify(json_data)


# route gtes divisions from the database
@app.route('/divisions/<company>/<department>')
def division(company, department):
    cur = db_connection.get_db().cursor()
    cur.execute("select distinct divID, name from division where companyID = '" + company + "' and deptID = '" + \
                department + "'")
    data = cur.fetchall()
    json_data = [{'label': row[1], 'value': row[0]} for row in data]
    return jsonify(json_data)


# route gets the job positions from the database
@app.route('/job_listings')
def get_job_listings():
    """
        Parameters:
           jp.name (string): jopPosition name
           Availability(bool): if a job is available or not
           di.name (string): name of division
           di.divID (int): division identifier
           dept.deptID (int): department identifier
           i.name (string): industry name
           jt.name (string): job type name
           c.name (string): company name
           c.companyID (int): company identifier
           country (string): location of position
           jp.description (string): description of job
           dept.name (string): department name 
    """
    cur = db_connection.get_db().cursor()
    command = "select jp.name as " + "'Position', Availability, di.name as Division, di.divID, dept.deptID, i.name as \
    Industry, jt.name as" + "'Type', c.name as Company, c.companyID, country as Country, jp.description as Description,\
    dept.name as Department\
    from( \
    jobPosition jp join division di on (di.divId = jp.divID and di.deptID = jp.deptID and di.companyID = jp.companyID) \
    join department dept on (dept.deptId = di.deptID and dept.companyID = di.companyID) \
    join company c on (c.companyID = dept.companyID) \
    join industryCompany ic on (jp.companyID = ic.companyID) \
    join industry i on (i.industryID = ic.industryID) \
    join jobType jt on (jt.jobTypeID = jp.jobTypeID))"
    cur.execute(command)
    row_headers = [x[0] for x in cur.description]
    json_data = []
    data = cur.fetchall()
    for row in data:
        row = [elem for elem in row]
        if row[1] == 1:
            row[1] = "Available"
        else:
            row[1] = "Unavailable"
        json_data.append(dict(zip(row_headers, row)))
    return jsonify(json_data)


# route gets the jop positions from the database that are marked true for the reported attribute
@app.route('/reported_listings')
def get_reported_listings():
    """
        Parameters:
           jp.name (string): jopPosition name
           jp.positionID (int): job position identifier
           Availability(bool): if a job is available or not
           di.name (string): name of division
           di.divID (int): division identifier
           dept.deptID (int): department identifier
           i.name (string): industry name
           jt.name (string): job type name
           c.name (string): company name
           c.companyID (int): company identifier
           country (string): location of position
           jp.description (string): description of job
    """
    cur = db_connection.get_db().cursor()
    command = "select jp.name as Position, jp.positionID as positionID, Availability, di.name as Division, di.divID, dept.deptID, i.name as \
    Industry, jt.name as" + "'Type', c.name as Company, c.companyID, country as Country, jp.description as Description,\
    dept.name as Department\
    from( \
    jobPosition jp join division di on (di.divId = jp.divID and di.deptID = jp.deptID and di.companyID = jp.companyID) \
    join department dept on (dept.deptId = di.deptID and dept.companyID = di.companyID) \
    join company c on (c.companyID = dept.companyID) \
    join industryCompany ic on (jp.companyID = ic.companyID) \
    join industry i on (i.industryID = ic.industryID) \
    join jobType jt on (jt.jobTypeID = jp.jobTypeID)) where jp.reported = 1"
    cur.execute(command)
    row_headers = [x[0] for x in cur.description]
    json_data = []
    data = cur.fetchall()
    for row in data:
        row = [elem for elem in row]
        if row[2] == 1:
            row[2] = "Available"
        else:
            row[2] = "Unavailable"
        json_data.append(dict(zip(row_headers, row)))
    return jsonify(json_data)


# route deletes a job position from the database
@app.route('/delete_listing/<position_id>', methods=["DELETE"])
def delete_listing(position_id):
    cur = db_connection.get_db().cursor()
    command = "delete from jobPosition where positionID = " + position_id
    app.logger.info(command)

    cur.execute(command)
    db_connection.get_db().commit()
    return "delete successful"


# route averages the ratings for a division from reviews
@app.route('/avg_div_rating/<company>/<department>/<division>')
def get_avg_div_rating(company, department, division):
    cur = db_connection.get_db().cursor()
    cur.execute("select avg(merged.rating) from(select rating from (jobPosition jp left join division di on \
    (di.divId = jp.divID and di.deptID = jp.deptID and di.companyID = jp.companyID) left join department dept on \
    (dept.deptId = di.deptID and dept.companyID = di.companyID) left join company c on (c.companyID = dept.companyID) \
    left join industryCompany ic on (jp.companyID = ic.companyID) join industry i on (i.industryID = ic.industryID) \
    left join jobType jt on (jt.jobTypeID = jp.jobTypeID) left join employee e on (e.positionID = jp.positionID and \
    e.divID = jp.divID and e.deptID = jp.deptID and e.companyID = jp.companyID) left join review r on \
    (r.employeeId = e.employeeID)) where di.companyID = '" + company + "' and di.deptID = '" + department + "' and \
    di.divID = '" + division + "') merged;")
    row_headers = [x[0] for x in cur.description]
    data = cur.fetchall()
    json_data = [{"label": data[0][0], "value": row_headers[0]}]
    if type(json_data[0]["label"]) != float:
        json_data[0]["label"] = "N/A"
    else:
        json_data[0]["label"] = round(json_data[0]["label"], 1)
    return jsonify(json_data)


# route averages the ratings for a department from reviews
@app.route('/avg_dept_rating/<company>/<department>')
def get_avg_dept_rating(company, department):
    cur = db_connection.get_db().cursor()
    cur.execute("select avg(merged.rating) from(select rating from (jobPosition jp left join division di on \
    (di.divId = jp.divID and di.deptID = jp.deptID and di.companyID = jp.companyID) left join department dept on \
    (dept.deptId = di.deptID and dept.companyID = di.companyID) left join company c on (c.companyID = dept.companyID) \
    left join industryCompany ic on (jp.companyID = ic.companyID) join industry i on (i.industryID = ic.industryID) \
    left join jobType jt on (jt.jobTypeID = jp.jobTypeID) left join employee e on (e.positionID = jp.positionID and \
    e.divID = jp.divID and e.deptID = jp.deptID and e.companyID = jp.companyID) left join review r on \
    (r.employeeId = e.employeeID)) where dept.companyID = '" + company + "' and dept.deptID = '" + department + "') \
    merged;")
    row_headers = [x[0] for x in cur.description]
    data = cur.fetchall()
    json_data = [{"label": data[0][0], "value": row_headers[0]}]
    if type(json_data[0]["label"]) != float:
        json_data[0]["label"] = "N/A"
    else:
        json_data[0]["label"] = round(json_data[0]["label"], 1)
    return jsonify(json_data)


# route averages the ratings for a company from reviews
@app.route('/avg_company_rating/<company>')
def get_avg_company_rating(company):
    cur = db_connection.get_db().cursor()
    cur.execute("select avg(merged.rating) from(select rating from (jobPosition jp left join division di on \
    (di.divId = jp.divID and di.deptID = jp.deptID and di.companyID = jp.companyID) left join department dept on \
    (dept.deptId = di.deptID and dept.companyID = di.companyID) left join company c on (c.companyID = dept.companyID) \
    left join industryCompany ic on (jp.companyID = ic.companyID) join industry i on (i.industryID = ic.industryID) \
    left join jobType jt on (jt.jobTypeID = jp.jobTypeID) left join employee e on (e.positionID = jp.positionID and \
    e.divID = jp.divID and e.deptID = jp.deptID and e.companyID = jp.companyID) left join review r on \
    (r.employeeId = e.employeeID)) where c.companyID = '" + company + "') merged;")
    row_headers = [x[0] for x in cur.description]
    data = cur.fetchall()
    json_data = [{"label": data[0][0], "value": row_headers[0]}]
    if type(json_data[0]["label"]) != float:
        json_data[0]["label"] = "N/A"
    else:
        json_data[0]["label"] = round(json_data[0]["label"], 1)
    return jsonify(json_data)


# route adds a jop position to the database
@app.route('/add_job_position', methods=["POST"])
def add_job_position():
    name = request.form['name']
    job_type_id = request.form['jobType']
    availability = 1
    company_id = request.form['companyName']
    dept_id = request.form['deptName']
    div_id = request.form['divName']
    description = request.form['description']

    cur = db_connection.get_db().cursor()

    cur.execute("insert into jobPosition (name, divID, deptID, companyID, jobTypeID, availability, description) values \
    ('" + name + "', " + str(div_id) + ", " + str(dept_id) + ", " + str(company_id) + ", " + str(job_type_id) + ", " \
                + str(availability) + ", '" + description + "')")

    db_connection.get_db().commit()
    return jsonify([{"name": name, "divID": div_id, "deptID": dept_id, "companyID": company_id,
                     "jobTypeID": job_type_id, "availability": availability, "description": description}])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
