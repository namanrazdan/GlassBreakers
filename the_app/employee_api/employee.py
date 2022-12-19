from flask import Blueprint
from flask import Flask, jsonify
from flaskext.mysql import MySQL

# Create a new blueprint for managers
employees_blueprint = Blueprint('employees_blueprint', __name__)


# add a route to this blueprint
@employees_blueprint.route('/employees')
def get_all_job_listings():
    cur = db_connection.get_db().cursor()
    command = 'select jp.name as JobPosition, availability, di.name as DivisionName, i.name as Industry, jt.name as \
    JobType, c.name as Company, country from( \
    jobPosition jp join division di on (di.divId = jp.divID and di.deptID = jp.deptID and di.companyID = jp.companyID) \
    join department dept on (dept.deptId = di.deptID and dept.companyID = di.companyID) \
    join company c on (c.companyID = dept.companyID) \
    join industryCompany ic on (jp.companyID = ic.companyID) \
    join industry i on (i.industryID = ic.industryID) \
    join jobType jt on (jt.jobTypeID = jp.jobTypeID) \
    )'
    cur.execute(command)
    row_headers = [x[0] for x in cur.description]
    json_data = []
    theData = cur.fetchall()
    for row in theData:
        json_data.append(dict(zip(row_headers, row)))
    return jsonify(json_data)
