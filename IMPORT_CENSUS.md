Importing Cenus data into Sifar
===============================================


## Creating the tables

* This guide only works for data that is from superCross

1.  In the admin panel first create a DBTable
    All field table names must start with senior_ to denoted that this is data for senior citezens

2. In the Admin panel create a field table
    Make sure that the fields are comma separated and match what the census information is about.
	eg: If the census data is about languages in a particular area and by age group then the field names must match that.
	
	
3. Link the DBTable to the FieldTable

4. Go back to the FieldTable and re-save the object

5. Check if a database table has been created, if not you have probably missed a previous step.
	
## Importing the data

To import the supercoss data use the importcsv.py file in tge django management folder

1. Run the script with the appropiate paramters and it should import the data for the newly created above table.





