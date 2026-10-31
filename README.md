# Space Bounty Hunters API

REST API for space bounty hunters: a database of wanted criminals and a journal of hunting attempts.

**Stack:** Flask, Flask-SQLAlchemy, PostgreSQL 18, Docker Compose

## How to run

1. Put the `.env` file in the project root (it is in the submitted zip).
2. Start everything:
   ```bash
   docker compose up --build
   ```
3. The API runs at `http://localhost:8001`.

On first start the tables are created and the database is prefilled with 6 criminals and 12 hunt logs.

To stop: `docker compose down`. To also delete the data: `docker compose down -v`.

## Endpoints

**Criminals**
- `GET /api/criminals/`: list criminals
    - `min_reward`, `max_reward`: reward range
    - `armed`, `has_crew`, `escape_master`: `true` or `false`
    - `sort`: `reward` or `-reward`
    - Example: `/api/criminals/?min_reward=5000&armed=true&sort=-reward`
- `GET /api/criminals/{id}/`: one criminal with its hunt logs

**Hunt logs**
- `GET /api/hunts/`: list hunt logs; filter `?criminal_id=5`
- `GET /api/hunts/{id}/`: one hunt log
- `POST /api/hunts/`: create a hunt log
    ```json
    {
      "criminal_id": 3,
      "success": false,
      "notes": "Target escaped through an asteroid field."
    }
    ```
- `PATCH /api/hunts/{id}/`: update `success` and/or `notes`
    ```json
    {
      "success": true,
      "notes": "Caught on the second try."
    }
    ```
- `DELETE /api/hunts/{id}/`: delete a hunt log

`created_at` is set by the server automatically.

## Status codes
- `200` OK
- `201` Created
- `204` Deleted
- `400` Invalid data
- `404` Not found
- `405` Method not allowed

## Postman

Import `postman/web_mid.postman_collection.json`. It has two folders, Criminals and Hunts, and one variable `base_url`.
