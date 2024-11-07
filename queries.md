# Queries
## Navigation
- [Company.db](#companydb)
- [Baseball.db](#baseballdb)
- [Classroom.db](#classroomdb)

**TIP:** Click on a query to directly insert it into the input field. Ensure that the correct database is selected before you submit.
<h2 id="companydb">Company.db</h2>

### Query 1
Make a list of project numbers for projects that involve an employee whose last name is "Smith", either as a worker or as a manager of the department that controls the project.
```
( project[pno](
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
```
project[lname, fname](
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
```
project[lname,fname](
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
```
project[lname,fname](
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
```
project[lname,fname](
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

<h2 id="baseballdb">Baseball.db</h2>

### Query 1
Show games where the home team scored more than 5 home runs
```
project[home, hruns](
  select[hruns > 5](
    (results join teams)
  )
);
```
### Query 2
Lists home teams that scored more than the visiting team, excluding records associated with IDs from temp2
```
project[home, hruns](
  select[hruns > vruns](
    results
  )
)
minus
project[home, pid](
  (project[home](results)
   times
   project[pid](temp2))
);
```
<h2 id="classroomdb">Classroom.db</h2>

### Query 1
Displays the building code, room number, capacity and description of rooms with a capacity greater than 100 that have the "Video Projector (Digital)" media description
```
project[bcode, rnumber, cap, description](
  select[description = 'Video Projector (Digital)' and cap > 100](
    (project[bcode, rnumber, cap, layout, mcode](
      ROOM 
      join 
      ROOMMEDIA
    ))
    join
    project[mcode, description](MEDIA)
  )
);
```
### Query 2
Lists the bulding code, room number, layout, capacity and media description of auditoriums with the media code "LAC"
```
project[bcode, rnumber, layout, cap, description](
  select[layout = 'Auditorium' and mcode = 'LAC'](
    (ROOM
     join
     ROOMMEDIA)
    join
    project[mcode, description](MEDIA)
  )
);
```