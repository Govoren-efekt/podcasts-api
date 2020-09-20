# Top 100 podcasts API

## Setup

- Open a terminal
- Install `pipenv` using pip3 or pip(if you are in Windows)
```shell script
pip3 install pipenv
```
## Running the code
Type in the terminal
```shell script
python3 app.py
```

The first task that the code performs is the database creation.
If it is the first time running the project, a message that says **'populating db...'** will appear.
When it its finished, it will display the message: **'db was populated succesfully!'**



## Solutions used per exercise

### Database and schema creation
Schema used for the exercise
![Schema](https://res.cloudinary.com/victor1600/image/upload/v1600600912/markdown/schema_icnlcp.png)

I decided to split the data in three different tables: genre, podcast and genre_podcast, which is the middle table
between the many to many relationship of genre and podcast. I have used pandas for this stage, given the simplicity for
dropping duplicates and storing the dataframe directly to a table.

1. Retrieves the json from a remote URL
2. Separates the multivaluated column genres
3. Creates pandas dataframes of genre, podcast and genre_podcast
4. Create empty tables and their relationships.
5. Inserts dataframes into the tables.

**Note**: Given the fact SQL tables don't store the rows in insertion order, the `pd index` was used as a helper
column to preserver the order. This index field is not visible when querying the data. 
 
### Exercise 1

> Service to provide a search lookup within the podcasts

The function `search_lookup` implements the search and filters the podcasts table using a `LIKE` operator
to search for a given name.

![](https://res.cloudinary.com/victor1600/image/upload/v1600601640/markdown/others/1_epphxk.png)

### Exercise 2
> Service that would allow to save the top 20 podcasts to a separate JSON File

The `store_top_20` function uses the `order_by` function provided by flask-sqlalchemy to sort the podcasts using the
index column.

![](https://res.cloudinary.com/victor1600/image/upload/v1600601707/markdown/others/Screenshot_from_2020-09-20_05-34-55_rpnydb.png)

### Exercise 3

> A service to replace the top 20 podcasts for the bottom 20 to said JSON File

Using array slicing, its easy to swap the order of the rows in `swap_top_bottom()` function.

![](https://res.cloudinary.com/victor1600/image/upload/v1600601758/markdown/others/Screenshot_from_2020-09-20_05-35-49_cfuf5u.png)
### Exercise 4

> A service to remove a podcast, using a given identifier

The function `delete_podcast(id)` identifier used for deleting is 'id' (podcast id), given the fact it's been used as primary key of the podcasts
table.

![](https://res.cloudinary.com/victor1600/image/upload/v1600601869/markdown/others/Screenshot_from_2020-09-20_05-37-42_xyrtfu.png)

### Excercise 5

> Create a service to return the podcasts grouped by genres, even if
they appear as duplicates within some of the categories.


The `podcasts_by_genres()` performs a query to fetch the names of the genres and the id of the podcasts. Next, 
a for lop iterates over each row to perform a search of the podcast object and append it to a genres dictionary that wil return
the desired output.

![](https://res.cloudinary.com/victor1600/image/upload/v1600601922/markdown/others/Screenshot_from_2020-09-20_05-38-23_hwt0bl.png)