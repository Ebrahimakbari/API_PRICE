
# API_PRICE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

## Description

API_PRICE is a simple RESTful API designed to fetch and manage real-time price data for various assets, such as cryptocurrencies, stocks, or commodities , cars and motorcycles. Built with Python , it provides easy-to-use endpoints for querying prices, historical data, and more.

This project aims to serve as a lightweight backend service for applications needing price information without relying on third-party services.

## Target Sraping APIs

[Cars](https://khodro45.com/api/v1/pricing/dailycars/)

[Motorcycles](https://bama.ir/mad/api/price/hierarchy)

[Assets](https://call3.tgju.org/ajax.json)

## Features

- **Real-time Price Fetching**: Get current prices for supported assets.
- **Historical Data**: Retrieve price history over specified time periods.
- **Multiple Asset Support**: Currently supports cryptocurrencies , cars and motorcycle via integrated data sources.
- **DRF Framework**: high-performance API with automatic OpenAPI documentation.
- **Easy Integration**: Simple JSON responses and Swagger UI for testing.

## Technology Used

- **Python**: The main programming language for the backend.
- **Django**: The web framework used to build the API.
- **Django REST Framework (DRF)**: Provides the RESTful API functionality.
- **PostgreSQL**: The database used to store price data.
- **Uvicorn**: The ASGI server used to run the application.
- **Swagger**: For API documentation and testing.
- **Docker**: For containerization and easy deployment.
- **Docker Compose**: For managing multi-container Docker applications.
- **Celery**: For background task processing.
- **Redis**: For message broker and task queue.
- **Flower**: For managing API endpoints and routes.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Ebrahimakbari/API_PRICE.git
   cd API_PRICE
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Set up environment variables:
   - Create a `.env` file and add any API keys if using external data providers (e.g., `COINGECKO_API_KEY=your_key`).

## Usage

Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Access the interactive API documentation at `http://localhost:8000/docs`.

### Example Requests

#### Get Current Price
```bash
GET /api/v1/assets/
```
Example: `GET /api/v1/assets/zinc`  
Response:
```json
    {
        "symbol": "zinc",
        "name_fa": "روی",
        "name_en": "Zinc",
        "category": "METAL",
        "latest_price": {
            "price": "2575.6000",
            "high": "2575.6000",
            "low": "2575.6000",
            "timestamp": "2021-06-28T15:00:00+04:30"
        }
```

#### Get Historical Prices
```bash
GET /api/v1/assets/{asset_id}/history/?start_date=2025-01-01&end_date=2025-09-24
```
Response:
```json
[
    {
        "price": "2575.6000",
        "high": "2575.6000",
        "low": "2575.6000",
        "timestamp": "2021-06-28T15:00:00+04:30"
    }
]
```


## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Ebrahim Akbari - [Your Email](mailto:y560mia3@gmail.com)  
Project Link: [https://github.com/Ebrahimakbari/API_PRICE](https://github.com/Ebrahimakbari/API_PRICE)
