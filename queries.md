# Queries
## Navigation
- [Company.db](#companydb)
- [Baseball.db](#baseballdb)
- [Classroom.db](#classroomdb)

<div data-db="company">

<h2 id="companydb">Company.db</h2>

**TIP:** Click to directly insert query

### Query 1
Make a list of project numbers for projects that involve an employee whose last name is "Smith", either as a worker or as a manager of the department that controls the project.
```( project[pno](
   (rename[essn](project[ssn](select[lname='Smith'](employee))) 
    join 
    works_on
   )
  )
 union
  project[pnumber](
   ( rename[dnum](project[dnumber](select[lname='Smith'](
       (employee 
        join   
        rename[dname,dnumber,ssn,mgrstartdate](department)
       )
       )
       )
     ) 
     join 
     projects
    )
  )
);
```
### Query 2
List the names of managers who have at least one dependent.
```project[lname, fname](
  ((rename[ssn](project[mgrssn](department))
    join
    rename[ssn](project[essn](dependent))
   )
  join
  employee
  )
);
```
### Query 3
List the names of all employees with two or more dependents.
```project[lname,fname](
(rename[ssn](
 project[essn1](
  select[essn1=essn2 and dname1<>dname2](
   (rename[essn1,dname1](project[essn,dependent_name](dependent))
    times
    rename[essn2,dname2](project[essn,dependent_name](dependent)))
   )
  )
 )
join
employee)
);
```
### Query 4
Retrieve the names of employees who have no dependents.
```project[lname,fname](
 ( ( project[ssn](employee) 
     minus project[essn](dependent)
   ) 
   join 
   employee
 )
);
```
### Query 5
Find the names of employees who work on all the projects controlled by department number 4.
```project[lname,fname](
 (employee
  join
  (project[ssn](employee)
   minus
   project[ssn](
    (
      (project[ssn](employee) 
       times  
       project[pnumber](select[dnum=4](projects))
      )
      minus
      rename[ssn,pnumber](project[essn,pno](works_on))
    )
   )
  )
 )
);
```
</div>

<div data-db="baseball">

<h2 id="baseballdb">Baseball.db</h2>

**TIP:** Click to directly insert query

### Query 1
Show games where the home team scored more than 5 home runs
```project[home, hruns](
  select[hruns > 5](
    (results join teams)
  )
);
```
</div>

<div data-db="classroom">

<h2 id="classroomdb">Classroom.db</h2>

**TIP:** Click to directly insert query

### Query 1
Get bcode and bname of buildings whose bname contains the word 'SOUTH':
```select[bname LIKE '%SOUTH%'](building);
```
### Query 2
Get bcode, rnumber, and cap for rooms with capacity greater than 100:
```project[bcode, rnumber, cap](
 select[cap > 100](
  room
 )
);
```
### Query 3
Get cap, layout, and type for room CLSO 206:
```project[cap, layout, type](
 select[bcode = 'CLSO' AND rnumber = '206'](
  room
 )
);
```
### Query 4
Get mcode and description for media in room CLSO 206:
```project[mcode, description](
 (select[bcode = 'CLSO' AND rnumber = '206'](roommedia))
 join
 media
);
```
### Query 5
Get rnumber of rooms in building with bcode = 'CLSO':
```project[rnumber](
 select[bcode = 'CLSO'](
  room
 )
);
```
### Query 6
Get bcode and rnumber for rooms with media description containing the term 'DVD':
```project[bcode, rnumber](
 select[description LIKE '%DVD%'](
  (roommedia join media)
 )
);
```
### Query 7
Get bcode and rnumber for rooms that are P type and owned by dept = 'CSC':
```project[bcode, rnumber](
 select[type = 'P' AND dept = 'CSC'](
  room
 )
);
```
### Query 8
Get the number of rooms in the CLSO building:
```project[COUNT(rnumber)](select[bcode = 'CLSO'](room));
```
### Query 9
Get the number of rooms for each building:
```project[bcode, COUNT(rnumber)](room);
```
### Query 10 
Get the number of rooms that have ELMO media:
```project[COUNT(mcode)](select[mcode = 'ELMO'](roommedia));
```
### Query 11
Get the number of rooms for each media type:
```project[mcode, COUNT(mcode)](roommedia);
```
### Query 12
Get the total number of seats in all classrooms in CLSO:
```project[SUM(cap)](select[bcode = 'CLSO'](room));
```
### Query 13
Get total number of seats in each building
```project[bcode, SUM(cap)](room);
```
### Query 14
Get total number of seats in all classrooms
```project[SUM(cap)](room);
```
</div>