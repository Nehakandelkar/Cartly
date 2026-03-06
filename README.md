# Price Aggregator

A mobile grocery price comparison app that allows users to create a cart and compare final prices across grocery platforms like Blinkit, Zepto, and Swiggy Instamart.

## Overview

The app enables users to search for products, add them to a cart, and get a price comparison including delivery fees, surges, and handling charges. The backend aggregates data from multiple providers, and scrapers run separately to fetch product data.

## Tech Stack

- **Mobile**: Android (Kotlin + Jetpack Compose), iOS (planned)
- **Backend**: Python + FastAPI
- **Providers**: Blinkit, Zepto, Instamart
- **Caching**: Redis
- **Scrapers**: Separate processes for data fetching

## Architecture

### Backend
- **API Layer**: FastAPI endpoints for mobile app interactions.
- **Services Layer**: Business logic for aggregation and coordination.
- **Providers Layer**: Modular adapters for each grocery platform.
- **Engines Layer**: Pricing and cart calculation engines.
- **Repositories Layer**: Data access and caching.
- **Scrapers Layer**: Independent data fetching scripts.
- **Utils Layer**: Shared utilities.

### Mobile
- **Android**: MVVM architecture with Jetpack Compose.
  - UI: Composables and screens.
  - ViewModel: State management.
  - Data: Repositories and API clients.
  - Model: Data classes.

## Getting Started

### Prerequisites
- Python 3.8+
- Android Studio for mobile development
- Redis (optional for caching)

### Backend Setup
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python main.py`

### Mobile Setup
1. Open `mobile/android/app/` in Android Studio.
2. Build and run the app.

### Scrapers
Run scrapers separately as needed for data updates.

## Contributing
1. Fork the repository.
2. Create a feature branch.
3. Commit changes.
4. Push to GitHub and create a PR.

## License
MIT License