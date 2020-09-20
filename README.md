# Top 100 podcasts API

## Setup

- Open a terminal
- Preferably, activate a virtual environment
- Install the dependencies
```shell script
pip3 install -r requirements.txt
```
## Running the code
Type in the terminal
```shell script
python3 app.py
```

The first task that the code performs is the database creation.
If it is the first time running the project, a message that says **'populating db...'** will appear.
When it its finished, it will display the message: **'db was populated succesfully!'**

### Create the username and password

You have to authenticate, in order to generate a token to use for calling the APIs.
- Open up postman or another REST client and use the endpoint: `http://localhost:5000/user`
- Define a name and a password like in the example

![](https://res.cloudinary.com/victor1600/image/upload/v1600606651/markdown/others/crear-usuario_mcdy9y.png)

- If successful, a message with `new user created!` will get displayed.

### Login

- Use the endpoint `http://localhost:5000/login`
- In Postman's `Authorization` tab, provide your username and password
- A token will get generated!

![](https://res.cloudinary.com/victor1600/image/upload/v1600606841/markdown/others/token_sepnls.png)

**IMPORTANT**: COPY THE PROVIDED TOKEN!

### Using the token

- Create a `x-access-token` header, and paste the token you copied from last step.
![](https://res.cloudinary.com/victor1600/image/upload/v1600606908/markdown/others/Screenshot_from_2020-09-20_06-55-20_v1zgbc.png)

> Now you are ready to call the APIs!

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

- use the endpoint `http://localhost:5000/api`
- use a `POST` request
- Send a json containing a `name` key and its value in string format

![](https://res.cloudinary.com/victor1600/image/upload/v1600607198/markdown/others/creat_iicjfe.png)

### Exercise 2
> Service that would allow to save the top 20 podcasts to a separate JSON File

The `store_top_20` function uses the `order_by` function provided by flask-sqlalchemy to sort the podcasts using the
index column.

- use the endpoint `http://localhost:5000/api/top20`
- use a `GET` request

![](https://res.cloudinary.com/victor1600/image/upload/v1600607336/markdown/others/top_o0cbce.png)

> Output got saved to `json_oututs` folder in project!

### Exercise 3

- use the endpoint `http://localhost:5000/api/swap`
- use a `GET` request
> A service to replace the top 20 podcasts for the bottom 20 to said JSON File

Using array slicing, its easy to swap the order of the rows in `swap_top_bottom()` function.

![](https://res.cloudinary.com/victor1600/image/upload/v1600607385/markdown/others/swap_et7un8.png)

> Output got saved to `json_oututs` folder in project!

### Exercise 4

> A service to remove a podcast, using a given identifier

- use the endpoint `http://localhost:5000/api/360084272` (You can use any id of the podcast json)
- use a `DELETE` request.

The function `delete_podcast(id)` identifier used for deleting is 'id' (podcast id), given the fact it's been used as primary key of the podcasts
table.

![](https://res.cloudinary.com/victor1600/image/upload/v1600607472/markdown/others/delete_ddjwrr.png)

### Excercise 5

> Create a service to return the podcasts grouped by genres, even if
they appear as duplicates within some of the categories.

- use the endpoint `http://localhost:5000/api/grouped`
- use a `GET` request

The `podcasts_by_genres()` performs a query to fetch the names of the genres and the id of the podcasts. Next, 
a for lop iterates over each row to perform a search of the podcast object and append it to a genres dictionary that wil return
the desired output.

![](https://res.cloudinary.com/victor1600/image/upload/v1600607556/markdown/others/groupd_hofops.png)