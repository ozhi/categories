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

### Development

1. Build migration files
```bash
docker-compose exec app python manage.py makemigrations
```

2. Lint
```bash
docker-compose run --rm app ruff check .
docker-compose run --rm app ruff format .
```
