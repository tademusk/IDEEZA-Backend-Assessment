# IDEEZA Backend Assessment

This project implements the backend assessment for IDEEZA, providing analytics APIs using Django and Django REST Framework.

## Features

- **API #1: Blog Views**: Grouped analytics by User or Country with time-range filtering.
- **API #2: Top Analytics**: Top 10 rankings for Users, Countries, or Blogs.
- **API #3: Performance Analytics**: Time-series performance with growth metrics.
- **Dynamic Filtering**: Supports AND, OR, NOT logic with Django lookups.
- **N+1 Query Prevention**: Optimized with `select_related` and `prefetch_related`.
- **Admin Panel**: Full admin interface for all models.
- **Comprehensive Tests**: 14 automated tests including edge cases.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd IDEEZA
    ```

2.  **Create and activate virtual environment**:
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run migrations**:
    ```bash
    python manage.py migrate
    ```

5.  **Create superuser** (Optional - for admin panel):
    ```bash
    python manage.py createsuperuser
    ```

6.  **Populate dummy data** (Optional):
    ```bash
    python manage.py populate_data
    ```

7.  **Run the server**:
    ```bash
    python manage.py runserver
    ```

8.  **Access admin panel** (Optional):
    ```
    http://localhost:8000/admin/
    ```

## Docker Installation (Alternative)

If you prefer using Docker:

1.  **Build and run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```

2.  **Run migrations in container**:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

3.  **Create superuser in container**:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

4.  **Populate dummy data in container**:
    ```bash
    docker-compose exec web python manage.py populate_data
    ```

5.  **Access the application**:
    ```
    http://localhost:8000/
    ```

**Note**: The application will automatically reload when you make code changes.

## API Usage

### 1. Blog Views
**Endpoint**: `/analytics/blog-views/`
- **Parameters**:
    - `object_type`: `user` or `country` (Required)
    - `range`: `month`, `week`, `year` (Optional)
    - Dynamic filters: `user__name__icontains=John`, `not__field=value`, `or__field=value`

**Example**:
```
GET /analytics/blog-views/?object_type=user&range=month
```

**Response**:
```json
[
  {"x": "John Doe", "y": 5, "z": 120},
  {"x": "Jane Smith", "y": 3, "z": 85}
]
```

### 2. Top Analytics
**Endpoint**: `/analytics/top/`
- **Parameters**:
    - `top`: `user`, `country`, or `blog` (Required)
    - Dynamic filters supported

**Example**:
```
GET /analytics/top/?top=blog
```

### 3. Performance Analytics
**Endpoint**: `/analytics/performance/`
- **Parameters**:
    - `compare`: `month`, `week`, `day`, `year` (Required)
    - Dynamic filters supported

**Example**:
```
GET /analytics/performance/?compare=week&user__name=John
```

## Running Tests

```bash
python manage.py test analytics
```

**Expected Output**: 14 tests passing

## Technical Highlights

- **Django ORM Optimization**: Prevents N+1 queries with eager loading
- **Dynamic Filtering**: Supports complex query patterns (AND/OR/NOT)
- **Time-Series Aggregation**: Uses Django's `Trunc` functions for efficient grouping
- **Admin Interface**: Full CRUD operations with search and filters
- **Test Coverage**: Comprehensive tests including edge cases and error handling

