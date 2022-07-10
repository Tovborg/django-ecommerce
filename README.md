# Django-ecommerce

Django-ecommerce, is an ecommerce store made with the python framework Django. It features a wishlist, featured items, payments using the stripe API and the PayPal API. The project is not finished, so any feedback is highly appreciated.

## Requirements
1. Python (below 3.9)
2. An IDE
## Installation

1. change directory into the folder you want the project to work in.
```bash
git init
```
```bash
git pull https://github.com/Tovborg/django-ecommerce.git
```

2. Activate a virtual environment and activate it
```bash
virtualenv venv --python="insert/your/python/path"
```
```bash
source venv/bin/activate
```
3. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Install necessary packages
```bash
pip install -r requirements.txt
```




## Usage
1. Before running the server you should apply any pending migrations
```bash
python manage.py migrate
```
2. Add color data for the add_items command
```bash
python manage.py create_color_data
```
3. For it all to be a little bit cooler and more realistic I've added a custom command called add_items command. it takes an integer and creates int amount of products
```bash
python manage.py add_items 10 # replace 10 with how many products you want
```
4. before we run the server we need to create a super user
```bash
python manage.py createsuperuser
```
5. And finally run the server
```bash
python manage.py runserver
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
