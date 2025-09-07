# Categories

This is a python Django project containing my solution to [task.md](./task.md).

### Running locally

1. Install Docker and docker-compose.

2. Run the app and db.
```bash
docker-compose up -d
```

3. Execute db migrations
```bash
docker-compose exec app python manage.py migrate
```

4. Create superuser (for Django Admin access)
```bash
docker-compose exec app python manage.py createsuperuser
```
For testing purposes, username=`root`, password=`root` is fine.

5. Seed db wth sample data
```bash
docker-compose exec app python manage.py seed
```

6. Explore API.
- Open [localhost:8001/api](localhost:8001/api) in the browser for Django Rest Framework UI.
- Open [localhost:8001/api/docs/swagger/](localhost:8001/api/docs/swagger/) for Swagger UI.
- Open [localhost:8001/api/docs/redoc/](localhost:8001/api/docs/swagger/) for Redoc UI.

7. View string visualization of the Category tree.
```bash
docker-compose exec app python manage.py tree_as_string
```

8. Generate image of the Category tree with color-coded similarity
```bash
docker-compose exec app python manage.py tree_as_image
```
Open `./tree.png`


### Development

1. Build migration files (after model updates)
```bash
docker-compose exec app python manage.py makemigrations
```

2. Lint
```bash
docker-compose run --rm app ruff check .
docker-compose run --rm app ruff format .
```

3. Update OpenAPI docs (after API updates)
```bash
docker-compose exec app python manage.py spectacular --file schema.yaml
```
